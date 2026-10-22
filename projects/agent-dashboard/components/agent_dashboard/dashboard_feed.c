#include "dashboard_feed.h"

#include <limits.h>
#include <stdio.h>
#include <string.h>

typedef struct { const char *next, *end; } cursor_t;
typedef struct { const char *data; size_t size; } field_t;

#define MAX_AGE_MS UINT64_C(8640000000)

static bool take(cursor_t *cursor, field_t *field)
{
    if (cursor->next >= cursor->end) return false;
    field->data = cursor->next;
    const char *end = memchr(cursor->next, '\t', (size_t)(cursor->end - cursor->next));
    if (!end) return false;
    field->size = (size_t)(end - cursor->next);
    cursor->next = end + 1;
    return field->size > 0;
}

static int hex(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

static bool hex_string(field_t field, char *output, size_t size, bool decode)
{
    if (field.size != size * (decode ? 2 : 1)) return false;
    for (size_t i = 0; i < field.size; ++i) if (hex(field.data[i]) < 0) return false;
    for (size_t i = 0; i < size; ++i) {
        output[i] = decode ? (char)(hex(field.data[i * 2]) * 16 + hex(field.data[i * 2 + 1]))
                           : field.data[i];
        if (!output[i]) return false;
    }
    output[size] = '\0';
    return true;
}

static bool number(cursor_t *cursor, uint32_t maximum, uint32_t *output)
{
    field_t field;
    if (!take(cursor, &field) || field.size > 10 || (field.size > 1 && field.data[0] == '0')) return false;
    uint32_t value = 0;
    for (size_t i = 0; i < field.size; ++i) {
        unsigned digit = (unsigned)(field.data[i] - '0');
        if (digit > 9 || digit > maximum || value > (maximum - digit) / 10) return false;
        value = value * 10 + digit;
    }
    *output = value;
    return true;
}

static bool utf8_label(const char *text, size_t size)
{
    size_t i = 0;
    while (i < size) {
        const unsigned char lead = (unsigned char)text[i++];
        if (lead < 0x80) { if (lead < 0x20 || lead == 0x7f) return false; continue; }
        unsigned count, value, minimum;
        if (lead >= 0xc2 && lead <= 0xdf) { count = 1; value = lead & 31; minimum = 0x80; }
        else if (lead >= 0xe0 && lead <= 0xef) { count = 2; value = lead & 15; minimum = 0x800; }
        else if (lead >= 0xf0 && lead <= 0xf4) { count = 3; value = lead & 7; minimum = 0x10000; }
        else return false;
        if (i + count > size) return false;
        while (count--) {
            const unsigned char c = (unsigned char)text[i++];
            if ((c & 0xc0) != 0x80) return false;
            value = (value << 6) | (c & 63);
        }
        if (value < minimum || value > 0x10ffff || (value >= 0xd800 && value <= 0xdfff)
            || (value >= 0x80 && value <= 0x9f)) return false;
    }
    return true;
}

static bool age(cursor_t *cursor, dashboard_feed_row_t *row)
{
    field_t value, key;
    if (!take(cursor, &value) || !take(cursor, &key)) return false;
    if (value.size == 1 && value.data[0] == '?')
        return key.size == 1 && key.data[0] == '?';
    if (value.size > 10 || (value.size > 1 && value.data[0] == '0') ||
        !hex_string(key, row->age_key, 64, false)) return false;
    uint64_t result = 0;
    for (size_t i = 0; i < value.size; ++i) {
        unsigned digit = (unsigned)(value.data[i] - '0');
        if (digit > 9 || result > (MAX_AGE_MS - digit) / 10) return false;
        result = result * 10 + digit;
    }
    row->age_known = true; row->age_ms = result;
    return true;
}

static uint64_t elapsed_age(const dashboard_feed_row_t *row, uint64_t now_ms)
{
    const uint64_t elapsed = now_ms >= row->age_anchor_ms ? now_ms - row->age_anchor_ms : 0;
    return row->age_ms + (elapsed < MAX_AGE_MS - row->age_ms ? elapsed : MAX_AGE_MS - row->age_ms);
}

static void format_age(char output[4], uint64_t milliseconds)
{
    const uint64_t seconds = milliseconds / 1000;
    unsigned value; char unit;
    if (seconds < 60) { value = (unsigned)seconds; unit = 's'; }
    else if (seconds < 3600) { value = (unsigned)(seconds / 60); unit = 'm'; }
    else if (seconds < 86400) { value = (unsigned)(seconds / 3600); unit = 'h'; }
    else if (seconds < 8640000) { value = (unsigned)(seconds / 86400); unit = 'd'; }
    else { memcpy(output, "+++", 4); return; }
    // Every branch above bounds value to two decimal digits.
    if (value < 10) { output[0] = (char)('0' + value); output[1] = unit; output[2] = '\0'; }
    else { output[0] = (char)('0' + value / 10); output[1] = (char)('0' + value % 10);
           output[2] = unit; output[3] = '\0'; }
}

static uint32_t crc32(const char *data, size_t size)
{
    uint32_t crc = UINT32_MAX;
    for (size_t i = 0; i < size; ++i) {
        crc ^= (unsigned char)data[i];
        for (unsigned bit = 0; bit < 8; ++bit)
            crc = (crc >> 1) ^ ((crc & 1) ? 0xedb88320u : 0);
    }
    return ~crc;
}

static unsigned row_order_tier(const dashboard_feed_row_t *row)
{
    if (row->category != DASH_CATEGORY_ACTIVE || row->health != DASH_CURRENT ||
        row->work == DASH_UNKNOWN || row->work == DASH_PARKED) return 2;
    if (row->work == DASH_NEEDS_INPUT || row->work == DASH_ERROR) return 0;
    return 1;
}

static unsigned row_total_group(const dashboard_feed_row_t *row)
{
    if (row->category == DASH_CATEGORY_RECENT) return 3;
    if (row->category == DASH_CATEGORY_UNCERTAIN || row->health != DASH_CURRENT ||
        row->work == DASH_UNKNOWN || row->work == DASH_PARKED) return 4;
    if (row->work == DASH_NEEDS_INPUT || row->work == DASH_ERROR) return 0;
    if (row->work == DASH_SETTLED || row->work == DASH_INTERRUPTED) return 1;
    if (row->work == DASH_WORKING) return 2;
    return 4;
}

void dashboard_feed_init(dashboard_feed_t *feed, const char *boot)
{
    memset(feed, 0, sizeof(*feed));
    if (boot && strlen(boot) == 16) memcpy(feed->boot, boot, 17);
}

int dashboard_feed_request(dashboard_feed_t *feed, uint64_t now_ms,
                           char *output, size_t capacity)
{
    if (feed->request == UINT32_MAX) return -1;
    ++feed->request; feed->requested_ms = now_ms; feed->pending = true;
    return snprintf(output, capacity, "RLCD?6 %s %u\n", feed->boot, (unsigned)feed->request);
}

bool dashboard_feed_accept(dashboard_feed_t *feed, const char *line,
                          size_t length, uint64_t now_ms)
{
    if (!feed->pending || now_ms < feed->requested_ms ||
        now_ms - feed->requested_ms >= DASH_FEED_REQUEST_MS ||
        length < 9 || length > DASH_FEED_BYTES || line[length - 9] != '\t') return false;
    for (size_t i = 0; i < length; ++i)
        if (line[i] != '\t' && (line[i] < 0x20 || line[i] > 0x7e)) return false;
    uint32_t expected_crc = 0;
    for (size_t i = length - 8; i < length; ++i) {
        int digit = hex(line[i]); if (digit < 0) return false;
        expected_crc = (expected_crc << 4) | (unsigned)digit;
    }
    if (expected_crc != crc32(line, length - 9)) return false;
    cursor_t cursor = {line, line + length - 8};
    field_t field; char boot[17]; uint32_t request, hosts, rows;
    dashboard_feed_view_t *view = &feed->candidate;
    memset(view, 0, sizeof(*view));
    if (!take(&cursor, &field) || field.size != 6 || memcmp(field.data, "RLCD!6", 6) ||
        !take(&cursor, &field) || !hex_string(field, boot, 16, false) || strcmp(boot, feed->boot) ||
        !number(&cursor, UINT32_MAX, &request) || request != feed->request ||
        !take(&cursor, &field) || !hex_string(field, view->bridge, 16, false) ||
        !number(&cursor, UINT32_MAX, &view->sequence) || !view->sequence ||
        !number(&cursor, DASH_FEED_HOSTS, &hosts) || !hosts ||
        !number(&cursor, DASHBOARD_MOTION_CAPACITY, &rows)) return false;
    if (feed->has_view && !strcmp(view->bridge, feed->view.bridge) &&
        view->sequence <= feed->view.sequence) return false;
    view->host_count = hosts; view->row_count = rows;
    uint32_t total = 0;
    for (size_t i = 0; i < hosts; ++i) {
        dashboard_feed_host_t *host = &view->hosts[i];
        if (!take(&cursor, &field) || !hex_string(field, host->alias, 2, true) ||
            host->alias[0] < 'A' || host->alias[0] > 'Z' || host->alias[1] < 'A' || host->alias[1] > 'Z' ||
            !number(&cursor, 3, &host->status) || !number(&cursor, DASH_FEED_VALID_MS, &host->valid_ms)) return false;
        for (size_t j = 0; j < i; ++j) if (!strcmp(host->alias, view->hosts[j].alias)) return false;
        uint32_t sum = 0;
        for (size_t j = 0; j < 5; ++j) {
            if (!number(&cursor, 65535, &host->totals[j])) return false;
            sum += host->totals[j];
        }
        if (!number(&cursor, 65535, &host->total) || sum != host->total ||
            ((host->status < 2) != (host->valid_ms > 0)) ||
            (host->status >= 2 && (host->totals[0] || host->totals[1] ||
             host->totals[2] || host->totals[3] || host->totals[4] != host->total))) return false;
        total += host->total;
    }
    if (rows > total) return false;
    uint32_t selected[DASH_FEED_HOSTS][5] = {{0}};
    unsigned previous_tier = 0;
    bool previous_age_unknown = false;
    for (size_t i = 0; i < rows; ++i) {
        dashboard_feed_row_t *row = &view->rows[i];
        if (!take(&cursor, &field) || !hex_string(field, row->identity, 64, false) ||
            !number(&cursor, hosts - 1, &row->host) ||
            !take(&cursor, &field) || !hex_string(field, row->badge, 2, true) ||
            (strcmp(row->badge, view->hosts[row->host].alias) &&
             (strcmp(view->hosts[row->host].alias, "SN") || strcmp(row->badge, "SW"))) ||
            !number(&cursor, 2, &row->category) ||
            !number(&cursor, 6, &row->work) ||
            (row->work != DASH_WORKING && row->work != DASH_NEEDS_INPUT && row->work != DASH_SETTLED && row->work != DASH_ERROR && row->work != DASH_UNKNOWN && row->work != DASH_PARKED) ||
            !number(&cursor, DASH_UNSUPPORTED, &row->health) ||
            !number(&cursor, DASH_FEED_VALID_MS, &row->valid_ms) ||
            (row->valid_ms && view->hosts[row->host].status >= 2) ||
            !take(&cursor, &field) || field.size > DASH_FEED_LABEL_BYTES * 2 || field.size % 2 ||
            !hex_string(field, row->label, field.size / 2, true) || !utf8_label(row->label, field.size / 2) ||
            !age(&cursor, row)) return false;
        if (row->work == DASH_PARKED && (row->category != DASH_CATEGORY_RECENT || row->health != DASH_CURRENT || !row->valid_ms)) return false;
        if (row->work != DASH_WORKING && row->work != DASH_NEEDS_INPUT &&
            row->work != DASH_SETTLED && row->work != DASH_ERROR &&
            row->work != DASH_UNKNOWN && row->work != DASH_PARKED) return false;
        if ((row->health != DASH_CURRENT || !row->valid_ms) && row->work != DASH_UNKNOWN) return false;
        if (row->age_known && (row->health != DASH_CURRENT || !row->valid_ms)) return false;
        if (row->category == DASH_CATEGORY_UNCERTAIN &&
            (row->valid_ms || row->health == DASH_CURRENT || row->work != DASH_UNKNOWN || row->age_known)) return false;
        for (size_t j = 0; j < i; ++j) if (!strcmp(row->identity, view->rows[j].identity)) return false;
        const unsigned ordered_tier = row_order_tier(row);
        const bool age_unknown = !row->age_known;
        if (i && (ordered_tier < previous_tier ||
                  (ordered_tier == previous_tier && ordered_tier < 2 &&
                   previous_age_unknown && !age_unknown))) return false;
        previous_tier = ordered_tier;
        previous_age_unknown = ordered_tier < 2 && age_unknown;
        const unsigned total_group = row_total_group(row);
        if (++selected[row->host][total_group] > view->hosts[row->host].totals[total_group]) return false;
    }
    if (cursor.next != cursor.end) return false;
    // A restarted/warming bridge has no retained identity context. Keep our
    // bounded last-known rows for failed hosts, without carrying current facts.
    for (size_t i = 0; feed->has_view && i < hosts; ++i) {
        dashboard_feed_host_t *host = &view->hosts[i];
        if (host->status < 2 || host->total) continue;
        for (size_t old = 0; old < feed->view.host_count; ++old) {
            if (strcmp(host->alias, feed->view.hosts[old].alias)) continue;
            host->total = feed->view.hosts[old].total;
            host->totals[4] = host->total;
            for (size_t j = 0; j < feed->view.row_count && view->row_count < DASHBOARD_MOTION_CAPACITY; ++j) {
                if (feed->view.rows[j].host != old) continue;
                dashboard_feed_row_t *row = &view->rows[view->row_count++];
                *row = feed->view.rows[j]; row->host = (uint32_t)i;
                row->category = DASH_CATEGORY_UNCERTAIN;
                row->work = DASH_UNKNOWN; row->health = DASH_UNAVAILABLE;
                row->valid_ms = 0; row->age_known = false;
            }
            break;
        }
    }
    for (size_t i = 0; i < view->row_count; ++i)
        for (size_t j = 0; j < i; ++j)
            if (!strcmp(view->rows[i].identity, view->rows[j].identity)) return false;
    // Only admitted packets may update presentation anchors. Repeated samples
    // of the same activity must not reset the local clock or its fractional ms.
    for (size_t i = 0; i < view->row_count; ++i) {
        dashboard_feed_row_t *row = &view->rows[i];
        row->age_anchor_ms = now_ms;
        if (!row->age_known || !feed->has_view || strcmp(view->bridge, feed->view.bridge)) continue;
        for (size_t j = 0; j < feed->view.row_count; ++j) {
            const dashboard_feed_row_t *old = &feed->view.rows[j];
            if (old->age_known && !strcmp(row->identity, old->identity) &&
                !strcmp(row->age_key, old->age_key) && elapsed_age(old, now_ms) >= row->age_ms) {
                row->age_ms = old->age_ms; row->age_anchor_ms = old->age_anchor_ms;
                break;
            }
        }
    }
    feed->view = *view; feed->accepted_request_ms = feed->requested_ms;
    feed->has_view = true; feed->pending = false; feed->dirty = true;
    return true;
}

bool dashboard_feed_tick(dashboard_feed_t *feed, dashboard_motion_t *motion, uint64_t now_ms)
{
    motion->live_presentation = true;
    if (!feed->has_view) {
        if (motion->feed_health != DASH_UNAVAILABLE)
            return dashboard_motion_feed_lost(motion, DASH_UNAVAILABLE, now_ms) == DASHBOARD_MOTION_APPLIED;
        dashboard_motion_tick(motion, now_ms); return false;
    }
    const dashboard_feed_view_t *view = &feed->view;
    bool changed = feed->dirty, healthy = false, partial = false;
    uint32_t totals[5] = {0}; size_t total = 0;
    bool live[DASH_FEED_HOSTS] = {false};
    unsigned effective_tier[DASHBOARD_MOTION_CAPACITY] = {0};
    for (size_t i = 0; i < view->host_count; ++i) {
        const dashboard_feed_host_t *host = &view->hosts[i];
        live[i] = host->status < 2 && now_ms >= feed->accepted_request_ms &&
                  now_ms - feed->accepted_request_ms < host->valid_ms;
        healthy |= live[i]; partial |= !live[i] || host->status != 0;
        if (live[i]) for (size_t j = 0; j < 5; ++j) totals[j] += host->totals[j];
        else totals[4] += host->total;
        total += host->total;
    }
    if (motion->live_partial != partial || memcmp(motion->live_totals, totals, sizeof(totals))) changed = true;
    for (size_t i = 0; i < view->row_count; ++i) {
        const dashboard_feed_row_t *row = &view->rows[i];
        bool current = view->hosts[row->host].status < 2 && row->valid_ms &&
                       now_ms >= feed->accepted_request_ms &&
                       now_ms - feed->accepted_request_ms < row->valid_ms;
        effective_tier[i] = current ? row_order_tier(row) : 2;
        healthy |= current;
        partial |= !current;
        const uint32_t health = current ? row->health : DASH_STALE;
        if (health != feed->effective_health[i]) changed = true;
        feed->effective_health[i] = health; feed->order[i] = (uint8_t)i;
        feed->samples[i] = (dashboard_motion_sample_t){
            .logical_id = row->identity, .project = row->label,
            .provider = row->badge, .short_id = "",
            .work = current ? (dashboard_work_t)row->work : DASH_UNKNOWN,
            .health = (dashboard_health_t)health,
            .category = current ? (dashboard_category_t)row->category : DASH_CATEGORY_UNCERTAIN,
        };
    }
    // Attenuation can only move rows into uncertainty. Stable tier ordering
    // preserves the bridge's interleave and original order within each tier.
    for (size_t i = 1; i < view->row_count; ++i) {
        uint8_t candidate = feed->order[i]; size_t j = i;
        while (j && effective_tier[candidate] < effective_tier[feed->order[j - 1]]) {
            feed->order[j] = feed->order[j - 1]; --j;
        }
        feed->order[j] = candidate;
    }
    if (changed) {
        dashboard_motion_sample_t ordered[DASHBOARD_MOTION_CAPACITY];
        for (size_t i = 0; i < view->row_count; ++i) ordered[i] = feed->samples[feed->order[i]];
        dashboard_motion_snapshot_t snapshot = {ordered, view->row_count};
        if (dashboard_motion_apply(motion, &snapshot, now_ms) != DASHBOARD_MOTION_APPLIED) {
            // A controller rejection must never strand older work as current.
            dashboard_motion_feed_lost(motion, DASH_UNAVAILABLE, now_ms);
            return true;
        }
        memcpy(motion->live_totals, totals, sizeof(totals));
        motion->live_total = total; motion->live_partial = partial;
    }
    // Age-only changes redraw without reapplying layout or changing authority.
    for (size_t i = 0; i < DASHBOARD_MOTION_TRACK_CAPACITY; ++i) {
        dashboard_motion_track_t *track = &motion->tracks[i];
        if (!track->used) continue;
        char label[4] = "?";
        if (track->active && track->health == DASH_CURRENT)
            for (size_t j = 0; j < view->row_count; ++j)
                if (view->rows[j].age_known && !strcmp(track->logical_id, view->rows[j].identity))
                    format_age(label, elapsed_age(&view->rows[j], now_ms));
        if (strcmp(track->supplied_age, label)) changed = true;
        memcpy(track->supplied_age, label, sizeof(label));
    }
    if (!healthy) {
        if (motion->feed_health != DASH_UNAVAILABLE) changed = true;
        dashboard_motion_feed_lost(motion, DASH_UNAVAILABLE, now_ms);
    } else dashboard_motion_tick(motion, now_ms);
    feed->dirty = false;
    return changed;
}
