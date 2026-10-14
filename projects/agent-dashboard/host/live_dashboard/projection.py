"""Pure bounded projection of already admitted source views."""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

ALIASES = {"starship": "ST", "snap": "SN"}
CAPACITY = 32
MAX_ROSTER = 65535
MAX_VALID_MS = 3000
MARGIN_MS = 100
GROUP = {"blocked": 0, "waiting": 1, "working": 2, "unknown": 3}
WORK = {"blocked": 1, "waiting": 2, "working": 0, "unknown": 5}
HEALTH = {"current": 0, "stale": 1, "unavailable": 2, "ambiguous": 3, "unsupported": 4}


def token(identity):
    key = tuple(
        identity[k]
        for k in ("hostScope", "provider", "namespace", "nativeIdKind", "nativeId")
    )
    return hashlib.sha256(
        json.dumps(key, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest(), key


def clean(value, limit=63):
    value = "".join(
        " " if unicodedata.category(c).startswith("C") else c for c in (value or "?")
    )
    return value.encode("utf-8")[:limit].decode("utf-8", errors="ignore").strip() or "?"


def project_name(row):
    workspace = row.get("workspace") or {}
    repo = workspace.get("repo") or {}
    path = repo.get("root") if workspace.get("health") == "current" else None
    path = path or row.get("cwd")
    return clean(posixpath.basename(path.rstrip("/"))) if path else None


def project_label(row):
    title = clean(row.get("title"), 256) if (row.get("title") or "").strip() else None
    fallback = "Codex " + row["identity"]["nativeId"]
    if title and title != fallback:
        return title
    return project_name(row) or ("Codex #" + token(row["identity"])[0][:5])


def exclusion(row):
    if row["kind"] in {"child", "system"}:
        return row["kind"]
    runtime = row["runtime"]
    if runtime["health"] == "current" and runtime["value"] == "parked":
        return "parked"
    return None


def selection_reason(row):
    if row["identity"]["provider"] != "codex":
        return "provider_excluded"
    excluded = exclusion(row)
    if excluded:
        return excluded
    if row["runtime"]["health"] != "current":
        return "runtime_unavailable"
    if row["runtime"]["value"] != "running":
        return "runtime_unknown"
    return "selected"


def age_label(milliseconds):
    if milliseconds is None or milliseconds < 0:
        return "?"
    seconds = milliseconds // 1000
    for divisor, unit in ((86400, "d"), (3600, "h"), (60, "m"), (1, "s")):
        if seconds >= divisor or divisor == 1:
            value = seconds // divisor
            return f"{value}{unit}" if value < 100 else "+++"
    return "?"


@lru_cache(maxsize=1)
def font_advances():
    # Read the renderer's generated metrics rather than guessing Unicode widths.
    font = (
        Path(__file__).resolve().parents[2]
        / "components/agent_dashboard/fusion_pixel_12_zh_hans.c"
    )
    glyphs = font.read_text().split("const uint8_t", 1)[0]
    return {
        int(cp, 16): (int(metrics, 16) & 31) * 2
        for cp, metrics in re.findall(
            r"\{0x([0-9a-f]+)u, \d+u, 0x([0-9a-f]+)u\}", glyphs
        )
    }


def fit_label(value, width=288):
    advances = font_advances()
    advance = lambda c: advances.get(ord(c), advances[0xFFFD])
    if sum(map(advance, value)) <= width:
        return clean(value)
    used, output = 0, ""
    for character in value:
        step = advance(character)
        if used + step > width - 3 * advances[ord(".")]:
            break
        output += character
        used += step
    return clean(output + "...")


def visual_key(label):
    supported = font_advances()
    return tuple(ord(c) if ord(c) in supported else 0xFFFD for c in label)


def text_width(label):
    supported = font_advances()
    return sum(supported.get(ord(c), supported[0xFFFD]) for c in label)


@dataclass
class Source:
    host: str
    status: str
    remaining_ms: int = 0
    sampled_at: int | None = None
    rows: list[dict] = field(default_factory=list)
    # All currently admitted identities, including parked/child/system rows.
    admitted_ids: set[str] = field(default_factory=set)
    excluded_ids: set[str] = field(default_factory=set)


class Projector:
    def __init__(self, hosts=("starship", "snap")):
        if (
            not hosts
            or len(hosts) > 2
            or len(set(hosts)) != len(hosts)
            or any(h not in ALIASES for h in hosts)
        ):
            raise ValueError("unsupported_host_selection")
        self.hosts = tuple(hosts)
        self.previous = {}
        self.ranks = {}
        self.keys = {}
        self.roster = []

    def project(self, sources):
        sources = {s.host: s for s in sources}
        result, candidates = [], []
        for index, host in enumerate(self.hosts):
            source = sources.get(host, Source(host, "warming"))
            valid = min(MAX_VALID_MS, max(0, source.remaining_ms - MARGIN_MS))
            ready = source.status in {"current", "partial"} and valid > 0
            status = (
                source.status
                if ready
                else "warming"
                if source.status == "warming"
                else "offline"
            )
            selected = {}
            excluded_ids = set(source.excluded_ids) if ready else set()
            if ready:
                excluded_ids.update(
                    token(r["identity"])[0] for r in source.rows if exclusion(r)
                )
            for row in source.rows if ready else []:
                if selection_reason(row) != "selected":
                    continue
                identifier, key = token(row["identity"])
                if identifier in self.keys and self.keys[identifier] != key:
                    raise ValueError("identity_collision")
                self.keys[identifier] = key
                phase = row.get("phase") or {}
                health = phase.get("health", "unavailable")
                state = (
                    phase.get("value", "unknown") if health == "current" else "unknown"
                )
                if state not in GROUP:
                    state, health = "unknown", "unsupported"
                activity = row["activity"]
                at = activity.get("at") if activity["health"] == "current" else None
                sampled = source.sampled_at
                if at is not None and (sampled is None or at > sampled):
                    at = None
                selected[identifier] = {
                    "id": identifier,
                    "host": index,
                    "state": state,
                    "health": HEALTH[health],
                    "valid_ms": valid,
                    "label": project_label(row),
                    "age": age_label(sampled - at if at is not None else None)
                    if health == "current"
                    else "?",
                    "activity": at,
                    "project": project_name(row),
                }
            # Previously active rows are context only when missing/uncertain.
            # Admitted parked/child/system metadata positively excludes prior context.
            for identifier, prior in self.previous.items():
                absent_complete = (
                    ready
                    and source.status == "current"
                    and identifier not in source.admitted_ids
                )
                if (
                    prior["host"] == index
                    and identifier not in selected
                    and identifier not in excluded_ids
                    and not absent_complete
                ):
                    selected[identifier] = {
                        **prior,
                        "state": "unknown",
                        "health": 1,
                        "valid_ms": 0,
                        "age": "?",
                        "activity": None,
                    }
            if len(selected) > MAX_ROSTER:
                raise ValueError("roster_capacity")
            counts = [0, 0, 0, 0]
            for row in selected.values():
                counts[GROUP[row["state"]]] += 1
            result.append(
                {
                    "alias": ALIASES[host],
                    "status": {"current": 0, "partial": 1, "offline": 2, "warming": 3}[
                        status
                    ],
                    "valid_ms": valid if ready else 0,
                    "totals": counts,
                    "total": sum(counts),
                }
            )
            candidates.extend(selected.values())
        candidates.sort(
            key=lambda r: (
                GROUP[r["state"]],
                r["activity"] is None,
                r["activity"] or 0,
                self.ranks.get(r["id"], 2**32),
                r["id"],
            )
        )
        originals = {r["id"]: r["label"] for r in candidates}
        for row in candidates:
            row["label"] = fit_label(row["label"])
        # Distinguish matching titles with readable project context first.
        labels = {}
        for row in candidates:
            labels.setdefault(visual_key(row["label"]), []).append(row)
        for matches in labels.values():
            projects = {r["project"] for r in matches if r.get("project")}
            if len(matches) < 2 or len(projects) < 2:
                continue
            for row in matches:
                if row.get("project"):
                    context = " (" + fit_label(row["project"], 120) + ")"
                    row["label"] = clean(
                        fit_label(originals[row["id"]], 288 - text_width(context))
                        + context
                    )
                    originals[row["id"]] = row["label"]
        for digits in range(5, 13):
            labels = {}
            for row in candidates:
                labels.setdefault(visual_key(row["label"]), []).append(row)
            collisions = [matches for matches in labels.values() if len(matches) > 1]
            if not collisions:
                break
            for matches in collisions:
                for row in matches:
                    suffix = " #" + row["id"][:digits]
                    row["label"] = clean(
                        fit_label(originals[row["id"]], 288 - len(suffix) * 12) + suffix
                    )
        if len({visual_key(r["label"]) for r in candidates}) != len(candidates):
            raise ValueError("display_label_collision")
        rows = candidates[:CAPACITY]
        self.roster = [dict(r) for r in candidates]
        self.ranks = {r["id"]: i for i, r in enumerate(candidates)}
        # Whole-roster membership is independent of the USB/display prefix.
        # Retained metadata cannot supply phase, age or native freshness.
        self.previous = {
            r["id"]: {k: r[k] for k in ("id", "host", "label", "project")}
            for r in candidates
        }
        self.keys = {r["id"]: self.keys[r["id"]] for r in candidates}
        return {"hosts": result, "rows": rows}

    def explain(self, sources, view, *, include_all=False):
        selected = {r["id"]: (index, r) for index, r in enumerate(self.roster)}
        entries, seen, reasons = [], set(), {}
        for source in sources:
            for row in source.rows:
                identifier, _ = token(row["identity"])
                reason = selection_reason(row)
                match = selected.get(identifier)
                if reason == "selected" and match is None:
                    reason = "source_unavailable"
                reasons[reason] = reasons.get(reason, 0) + 1
                if (
                    not include_all
                    and match is None
                    and not (
                        reason == "system" and row["runtime"]["value"] == "running"
                    )
                ):
                    continue
                index, displayed = match if match else (None, None)
                seen.add(identifier)
                entries.append(
                    {
                        "identity": row["identity"],
                        "display_id": identifier,
                        "title": row.get("title"),
                        "project": project_name(row),
                        "kind": row["kind"],
                        "source_status": source.status,
                        "runtime": row["runtime"],
                        "phase": row.get("phase"),
                        "activity": row["activity"],
                        "selection": "retained_uncertain"
                        if displayed and not displayed["valid_ms"]
                        else reason,
                        "display_label": displayed["label"] if displayed else None,
                        "display_age": displayed["age"] if displayed else None,
                        "display_position": index + 1 if index is not None else None,
                        "sent_to_device": index is not None and index < CAPACITY,
                        "visible": index is not None and index < 11,
                    }
                )
        for identifier, (index, row) in selected.items():
            if identifier not in seen:
                entries.append(
                    {
                        "identity": dict(
                            zip(
                                (
                                    "hostScope",
                                    "provider",
                                    "namespace",
                                    "nativeIdKind",
                                    "nativeId",
                                ),
                                self.keys[identifier],
                                strict=True,
                            )
                        ),
                        "display_id": identifier,
                        "display_label": row["label"],
                        "project": row.get("project"),
                        "selection": "retained_uncertain",
                        "display_age": "?",
                        "display_position": index + 1,
                        "sent_to_device": index < CAPACITY,
                        "visible": index < 11,
                    }
                )
        entries.sort(
            key=lambda entry: (
                entry["display_position"] is None,
                entry["display_position"] or 0,
                entry["display_id"],
            )
        )
        return {
            "hosts": view["hosts"],
            "selection_counts": reasons,
            "age_meaning": "source_sampled_conversation_activity",
            "rows": entries,
        }
