# Uniform 24px rows on the RLCD

2026-10-06. Trial on RLCD `94:a9:90:de:d0:04` only; synthetic fixtures,
uncommitted changes. All rows and row text are 24px, fitting eleven complete
rows. Blocked stays white on black; waiting adds a 3px by 16px left marker
on white; working uses white without a marker. New blocked episodes blink
only the attention icon twice over 900ms and then stay steady. The title and
small-count header are retained.

- Native ASan/UBSan, warnings-as-errors, UTF-8 and 4,488 rectangle checks pass.
- All 42 static frame hashes match the previous title-header baseline.
- Three flash image hashes verified; the full 1,234,880-byte
  application readback matches. Boot ELF prefix `a7c03b6e8` matches the build.
- A 110.129s capture covers 23 phases and one 92-second cycle:
  437 frames, 192 moving, no errors or frame-budget misses.
- Worst frame 20.809ms; heap constant at 331,131 bytes;
  minimum stack watermark 1,728 bytes.
- Temporary RLCD serial ACL restored exactly; serial released; separate 349
  service and serial-owner PIDs unchanged. Private recovery data remains outside Git.

`checks.json` records the acceptance assertions; `acceptance.json`,
`summary.json` and serial logs record build/runtime identity and measurements.
`source.json`, `files.json` and `readback.json` bind source, build and readback.
Native PBMs/PNGs are the firmware renderer's output. The historical fixture
label `compact-capacity` now exercises eleven full-height working rows.
`attention-icon-on/off` shows that the cue changes only icon pixels.

Technical checks pass. Physical readability and marker/cue acceptance remain
user observations on the looping board. There is no live source integration.

[Design contract](../../../projects/agent-dashboard/docs/uniform-rows-study.md)
records the layout and episode rules.
