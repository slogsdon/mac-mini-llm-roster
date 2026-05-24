# Run 1 — Original 10-model production-default speed test (2026-05-23)

First run in the series. The roster as it stood on 2026-05-23 morning, each model at its production-default `num_ctx` and `num_predict`.

## Files

- **`results.json`** — raw per-call results. One object per (model, prompt). Fields: `alias`, `tag`, `prompt`, `num_ctx`, `num_predict`, `wall_s`, `eval_tps`, `eval_count`, `thinking_chars`, `content` (first 300 chars), `error`.
- **`run.log`** — full stdout (warmup times, per-prompt progress).
- **`report.md`** — formatted markdown tables + findings.

## Configuration

- 10 models × 8 prompts = 80 calls
- Sequential per model (cold-load tax on prompt 1 only)
- Direct Ollama at `:11434` (not through LiteLLM) for accurate `eval_count` / `eval_duration` and the separated `thinking` channel
- Total wall time: **107 minutes**

## How to reproduce

```bash
python3 ../../scripts/roster_speed_test.py
```

Note: this run's MODELS list included `qwen3.5:9b-mlx` and `qwen3-vl:30b`, both of which were retired after the delta run. To reproduce against the *historical* roster you'd need to `ollama pull` those tags first.

## Notable findings (full prose in `report.md`)

- `qwen3.5:9b-mlx` over-thinks at production budget — 30k chars of thinking on a 60-word writing task, timed out on the French-translation prompt.
- `qwen3-vl:30b` was the speed surprise — 36 tps median on text-only prompts, faster than every other general-purpose model.
- `phi4-reasoning:plus` is slow + careful — 9 tps median, 34k chars of thinking on a JSON-list prompt (15 min wall time).
- `gemma4:e4b-mlx` emits thinking unsolicited even when not asked; the previous "fast-general" alias wasn't actually fast.
