# Fusion Pixel Font asset

The native motion study vendors the exact `fusion-pixel-8px-monospaced-zh_hans.bdf` from Fusion Pixel Font release `2026.09.25`:

- Upstream: [TakWolf/fusion-pixel-font release 2026.09.25](https://github.com/TakWolf/fusion-pixel-font/releases/tag/2026.09.25)
- Release archive SHA-256: `bd76834c43d6882184356394cfdd8c9c5e5623d9d1c9020564fe545b7ba769ce`
- Selected BDF SHA-256: `3c00ccab762c0c75967eea724f5cd57feb544be7a0814d06233160ef9482a50b`
- BDF metrics: ascent 7, descent 1, cap height 6, 28,410 encoded glyph entries

The source includes 28,409 character glyphs and its U+FFFE default/noncharacter entry. The generator preserves all encoded entries, bitmap rows, advances, and BBX offsets. It emits sorted Unicode lookup records and compact MSB-first one-bit glyph data into `fusion_pixel_8_zh_hans.c`. The renderer has no runtime font dependency or allocation.

`OFL.txt` and the files under `LICENSES/` are the complete notice files shipped beside the selected BDF in the upstream release archive. Use `python3 scripts/generate_fusion_font.py` from this component to regenerate the C data, or add `--check` to verify the checked-in generated files without network access.


## 12px monospaced zh_hans asset

The native dashboard vendors the exact `fusion-pixel-12px-monospaced-zh_hans.bdf` from Fusion Pixel Font release `2026.09.25`:

- Upstream: [TakWolf/fusion-pixel-font release 2026.09.25](https://github.com/TakWolf/fusion-pixel-font/releases/tag/2026.09.25)
- Release archive SHA-256: `d75f5262f108757edb0f47ee8e3d2dfdfbecfd94558faf5ffb0c06dc5866fb3b`
- Selected BDF SHA-256: `bb2cdfa029674d83ad9fc6b01bba11752f61779cae1219a722c7ccee96b2d0ae`
- BDF metrics: ascent 10, descent 2, cap height 8, 36,981 encoded glyph entries

The source includes all encoded glyphs, including its U+FFFE default/noncharacter entry. The generated table retains each advance, BBX offset, full bitmap, and Unicode mapping. Glyphs U+3031 and U+3032 have 22-pixel-tall bitmaps that extend beyond the 12px cell; their full metrics and bitmaps remain in the asset for renderer clipping. The largest advance is 30 pixels and the largest BBX is 27x22 pixels. The generator emits sorted Unicode lookup records and compact MSB-first one-bit glyph data into `fusion_pixel_12_zh_hans.c`; use `python3 scripts/generate_fusion_font_12.py` to regenerate or add `--check` to verify without network access.

The 12px archive's root `OFL.txt` and `LICENSES/galmuri/LICENSE.txt` are byte-identical to the shared notices above. The archive's additional `LICENSES/ark-pixel/OFL.txt` and `LICENSES/cubic-11/OFL.txt` are retained under `LICENSES/` beside the BDF.
