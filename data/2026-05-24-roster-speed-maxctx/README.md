# Run 3 — final 11-model roster at maxed contexts (2026-05-24)

The roster as it stood the next morning, every model pinned to the `ollama_max` value from its model card instead of the production-default `num_ctx` I was actually shipping. Wanted to know what KV cache really costs me before I bump anything.

Same 8 prompts as the first two runs. Script is `roster_speed_test_maxctx.py` — a sibling of the original, just with the model list and context values swapped.

## Files

- `results.json` — raw per-call results
- `run.log` — full stdout, 69.5 minutes total
- `report.md` — formatted tables (the prose lives in the blog post)

## What I tested

| alias | tag | `num_ctx` (max) | `num_predict` | `think` |
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

A few asterisks:

- `writing` is capped at 131K, not the 1M its model card claims. The KV cache for a 1M context on a 12B dense model wouldn't fit.
- `general` and `vision` are the same backing model. Two aliases so Langfuse can tag vision traffic separately.
- `tiny-reason` shows 128,000 because that's what the card publishes, not 131,072.

## To reproduce

```bash
python3 ../../scripts/roster_speed_test_maxctx.py
```

Plan for about 70 minutes on equivalent hardware. The reasoning models dominate — phi4-reasoning alone ate roughly 25 minutes including a 15-minute timeout on the writing prompt.

## What I learned

- **Nothing failed to load.** Even qwen3.6:35b-mlx at 256K warmed up in about 10 seconds. The big-MoE-with-huge-KV scenario I'd been quietly afraid of just worked.
- **Throughput cost is per-model, not global.** MoE and large models shrugged at the bigger context. Small dense models paid for it: granite4.1:8b dropped 22% (18 → 14 tps), ministral-3:14b dropped 54% (13 → 9 tps with each prompt trending slower than the last).
- **`efficient` and `tiny-reason` didn't notice.** Both have small enough weights that even max context isn't memory pressure.
- **`phi4-reasoning:plus` timed out again** on writing-blurb at >15 min. Same flavor as run 1 — phi4 always thinks, and trivial prompts can occasionally recurse past the cap. Not a max-ctx issue, just phi4 being phi4.
- **Same model, same prompt, very different output.** `vision` (which is the same backing model as `general`, just called under a different alias in the same run) used 5,738 tokens on fim-code vs 645 in run 1. Reasoning depth is non-deterministic at fixed temperature — keep in mind when you're reading any single number too closely.
