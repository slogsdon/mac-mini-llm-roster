# Run 1 — production defaults, 10 models (2026-05-23)

First run in the series. The roster as I was actually shipping it that morning, each model at the `num_ctx` and `num_predict` baked into my Pi and Hermes configs.

The point of this one was sanity-checking what I'd assumed. It turned into the run that broke most of those assumptions.

## Files

- `results.json` — one object per (model, prompt). Fields documented in the top-level README.
- `run.log` — full stdout, including warmup times and per-prompt progress.
- `report.md` — the markdown tables I generated and pasted into my vault note.

## Setup

- 10 models × 8 prompts = 80 calls
- Sequential per model so the cold-load tax falls on prompt 1 only
- Direct to Ollama at `:11434`, not via LiteLLM (need the raw `eval_count` / `eval_duration` and the separated `thinking` field)
- Total wall time: **107 minutes**

## To reproduce

```bash
python3 ../../scripts/roster_speed_test.py
```

This run's model list included `qwen3.5:9b-mlx` and `qwen3-vl:30b`. Both got retired after the delta run, so if you want to actually re-run *this* exact matrix you'll need to `ollama pull` them first.

## What surprised me

- **`qwen3.5:9b-mlx` over-thinks at the budget I'd given it.** 30k chars of thinking on a 60-word writing prompt. Timed out on a French translation. The `think:false` fix later turned it from broken into merely slow, but that's enough to demote it.
- **`qwen3-vl:30b` is 36 tps on text-only prompts.** Faster than every general-purpose model in the roster, despite being a 30B vision-tuned model. The MoE architecture noticed the parameter count less than I did.
- **`phi4-reasoning:plus` is slow and exhaustive.** 9 tps median, 34k chars of thinking on a JSON-list prompt (15 minutes wall time). The model isn't wrong. My expectation was.
- **`gemma4:e4b-mlx` ships with thinking on by default**, which I hadn't noticed. The "fast general" alias wasn't actually fast until I forced it off in the LiteLLM route.

The numbers behind each of those are in `report.md` and `results.json`.
