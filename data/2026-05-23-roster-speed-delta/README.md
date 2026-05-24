# Run 2 — delta, 6 models (2026-05-23 evening)

Same evening as run 1. I needed to re-measure two models with `think:false` to confirm the fix worked, plus benchmark four new candidates I'd pulled in response to run 1's findings. The other eight models from run 1 didn't need a redo — their numbers stood.

## Files

- `results.json` — raw per-call results for the 6 models
- `run.log` — full stdout, 11.8 minutes total
- `report.md` — context for the roster shuffle plus the data tables and findings

## What I tested and why

| alias | tag | `think` | why I re-tested |
|---|---|---|---|
| `fast-general` | `gemma4:e4b-mlx` | `false` | Run 1 caught it emitting unsolicited thinking and burning the budget. Wanted to confirm forcing it off recovers the speed. |
| `general` | `qwen3.5:9b-mlx` | `false` | Same diagnosis as fast-general, plus the timeout. Same fix. |
| `general-next` | `qwen3.6:35b-mlx` | `true` | New pull. Candidate to replace both `general` and `vision` with one MLX MoE. |
| `instruct` | `ministral-3:14b` | n/a | New. Vision + tools, no thinking channel — fills a gap. |
| `efficient` | `lfm2:24b` | n/a | New. MoE 24B, head-to-head against `capable-large` (gpt-oss:20b). |
| `tiny-reason` | `lfm2.5-thinking:1.2b` | `true` | New. 1.2B reasoning model — wanted to see how fast "fast" can get. |

## To reproduce

```bash
python3 ../../scripts/roster_speed_test.py \
  --only fast-general,general,general-next,instruct,efficient,tiny-reason \
  --out /tmp/roster_delta_results.json \
  > /tmp/roster_delta_run.log 2>&1
```

## What I learned

- **`think:false` is the entire fix for `qwen3.5` and `gemma4`.** Same model, same prompts, same budgets: 18× faster total wall on qwen3.5 (988s → 55s, no timeouts), 2.7× faster on gemma4 (133s → 49s). I'd been blaming the models for what was a config bug all along.
- **`lfm2:24b` beats `gpt-oss:20b` 6.8× on this matrix.** Same weight class, comparable output quality. Promoted `efficient` to the primary 20B-class slot; `capable-large` (gpt-oss) is now the secondary you reach for when you specifically want its reasoning-channel style.
- **`qwen3.6:35b-mlx` replaces both `general` and `vision`.** 35 tps with thinking, vision-native, one model two roles.
- **`tiny-reason` is fast and brittle.** 116 tps but said `"Paris\n\nWait, wait, wait. Wait, the user said..."` on the trivial capital-of-France prompt, and burned its whole budget to empty content on the writing-blurb. Use it for fast pipeline classifiers, not user-facing answers.
