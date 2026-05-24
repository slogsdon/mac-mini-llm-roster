# Run 3 — Final 11-model roster at MAXED context windows (2026-05-24)

Third and final run in this series. Same 8 prompts, same script (now `roster_speed_test_maxctx.py`). 11 models — the final roster after the post-delta cleanup. Each model uses its `ollama_max` from `models.yaml` (the model card's training-time max), not its production default.

## Files

- **`results.json`** — raw per-call results
- **`run.log`** — full stdout (69.5 min total)
- **`report.md`** — formatted markdown tables (no findings prose — those live in the blog post)

## Configuration

| alias | tag | num_ctx (max) | num_predict | think |
|---|---|---|---|---|
| code-autocomplete | qwen2.5-coder:3b-base | 32,768 | 8,192 | — |
| fast-general | gemma4:e4b-mlx | 131,072 | 16,384 | false |
| code-review | granite4.1:8b | 131,072 | 16,384 | — |
| general | qwen3.6:35b-mlx | 262,144 | 16,384 | true |
| writing | mistral-nemo:12b | 131,072 | 32,768 | — |
| reasoning | phi4-reasoning:plus | 32,768 | 16,384 | true |
| capable | qwen3:14b | 40,960 | 16,384 | true |
| efficient | lfm2:24b | 32,768 | 16,384 | — |
| capable-large | gpt-oss:20b | 131,072 | 16,384 | true |
| vision | qwen3.6:35b-mlx | 262,144 | 16,384 | true |
| instruct | ministral-3:14b | 262,144 | 16,384 | — |
| tiny-reason | lfm2.5-thinking:1.2b | 128,000 | 8,192 | true |

Notes:
- `writing` is **capped at 131K** even though mistral-nemo's model card claims a 1M ceiling — the KV cache for a 1M context on a 12B dense model would exceed the 32 GB host
- `general` and `vision` share the same backing model (qwen3.6:35b-mlx) — alias kept distinct for observability tagging
- `tiny-reason` shows 128,000 (not 131,072) because that's the model card's published max

## How to reproduce

```bash
python3 ../../scripts/roster_speed_test_maxctx.py
```

Total wall time: **69.5 min** on the listed hardware. Reasoning models dominate the budget — phi4 alone took ~25 min including a 15-min timeout on the writing prompt.

## Top-line outcomes

- **No catastrophic load failures.** Even qwen3.6:35b-mlx at 256K loaded cleanly (warmup ~10s). Bigger KV cache caused a small cold-load tax (+36%) but no throughput penalty on the MoE.
- **Smaller dense models DID pay for bigger context.** granite4.1:8b at 128K: 14 tps (vs 18 tps at 64K in run 1). ministral-3:14b at 256K: degraded from 13 tps (at 40K) to 9.2 tps, with successive prompts trending downward.
- **`efficient` (lfm2:24b) and `tiny-reason` (lfm2.5-thinking:1.2b) were unaffected** — both have small enough weights that even max context doesn't pressure memory.
- **`phi4-reasoning:plus` hit one timeout** on writing-blurb (>15 min). Same pattern as run 1: phi4 always thinks, and trivial prompts can sometimes blow the timeout when its chain gets recursive.
- **Some thinking models showed real-world stochastic variance.** `vision` (same backing model as `general`) used 5,738 tokens on fim-code in this run vs 645 in run 1 on the identical prompt. Reasoning depth is non-deterministic at fixed temperature.
