# Run 2 — Delta benchmark, 6 changed/new models (2026-05-23 evening)

Second run, same script, just the 6 changed/new models. Compare against the parent benchmark in `../2026-05-23-roster-speed/`.

## Files

- **`results.json`** — raw per-call results for the 6 deltas
- **`run.log`** — full stdout of the run (11.8 min total)
- **`report.md`** — formatted markdown: roster-shuffle context + data tables + findings

## What was tested

| alias | tag | think | reason |
|---|---|---|---|
| `fast-general` | gemma4:e4b-mlx | **false** | First run showed unsolicited thinking burned the budget |
| `general` | qwen3.5:9b-mlx | **false** | First run timed out + over-thought |
| `general-next` | qwen3.6:35b-mlx | true | New: candidate to replace `general` + `vision` |
| `instruct` | ministral-3:14b | n/a | New: vision + tools, no thinking channel |
| `efficient` | lfm2:24b | n/a | New: MoE 24B, head-to-head with capable-large |
| `tiny-reason` | lfm2.5-thinking:1.2b | true | New: ultra-fast 1.2B reasoning |

## How to reproduce

```bash
python3 ../../scripts/roster_speed_test.py \
  --only fast-general,general,general-next,instruct,efficient,tiny-reason \
  --out /tmp/roster_delta_results.json \
  > /tmp/roster_delta_run.log 2>&1
```

## Top-line outcomes

- **`think:false` fixes qwen3.5 and gemma4** — 18× and 2.7× faster total wall time, no quality loss
- **`efficient` (lfm2:24b) beats `capable-large` (gpt-oss:20b) decisively** — 6.8× faster total at same weight class
- **`general-next` (qwen3.6:35b-mlx) replaces both `general` and `vision`** — 35 tps with thinking, vision-native
- **`tiny-reason` is fast (116 tps) but unstable** — burned full budget to empty on writing prompt, second-guessed itself on trivial Q&A
