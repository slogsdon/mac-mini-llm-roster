# mac-mini-llm-roster

> Companion repo for the blog post **"What I Learned Running Every Local Model on a 32 GB Mac Mini"** (link forthcoming). This repo holds the benchmark scripts and the raw data behind the post's tables and findings.

This is a **downstream complement to [willitrunai.com](https://www.willitrunai.com), not a replacement.** willitrunai answers *"will this model fit on my Mac SKU?"* — the right first filter, and a tool I rely on. This repo and the blog post answer the next question: *"given it fits, how does it actually behave on real prompts at production settings?"*

## What's in here

```
scripts/
  roster_speed_test.py         Original speed test — 11+ models × 8 prompts at production num_ctx
  roster_speed_test_maxctx.py  Same shape, each model at its model-card ollama_max
data/
  2026-05-23-roster-speed/       First run — full 10-model production-default sweep
  2026-05-23-roster-speed-delta/ Second run — 6 deltas (think:false fixes + 4 new models)
  2026-05-24-roster-speed-maxctx/ Third run — final 11-model roster, maxed contexts
litellm-example/
  config.yaml                  Sanitized LiteLLM proxy config showing the role-alias pattern
```

Each `data/<run>/` directory contains:
- **`results.json`** — raw per-call results (model, prompt, num_ctx, num_predict, wall_s, eval_tps, eval_count, thinking_chars, content preview, error)
- **`run.log`** — full stdout of the run
- **`report.md`** — formatted markdown tables + findings (what's referenced in the blog post)
- **`README.md`** — what was tested in that run and why

## Hardware

Single Mac Mini M4, 32 GB unified memory. macOS. Ollama 0.24.x running directly on the host (not containerized).

## How to reproduce a run

```bash
# 1. Have Ollama running on :11434 with the models pulled (see data/<run>/README.md
#    for the exact tags).
# 2. Run the script. Default output is /tmp/roster_speed_results.json; pass --out
#    to override and --only alias1,alias2,... to subset.

python3 scripts/roster_speed_test.py
python3 scripts/roster_speed_test_maxctx.py
```

Sequential per model, so cold-load tax falls on the first prompt per model and subsequent prompts hit a warm runner. Total wall time is roughly 1.5–2 hours per full run on the listed hardware.

## How to read the data

`results.json` is a flat list of objects, one per (model, prompt) call. The most useful fields:

| field | meaning |
|---|---|
| `alias` | role alias (`general`, `efficient`, etc.) |
| `tag` | the underlying Ollama tag |
| `prompt` | one of 8 short prompt IDs |
| `num_ctx` / `num_predict` | what was configured for that call |
| `wall_s` | total request wall time (load + prompt eval + thinking + generation) |
| `eval_tps` | tokens/sec during *generation only* — from Ollama's `eval_count` / `eval_duration` |
| `eval_count` | how many tokens the model actually produced |
| `thinking_chars` | chars in the model's separated thinking channel (0 if the model doesn't have one) |
| `content` | first 300 chars of the visible response |
| `error` | null on success; populated on timeouts or HTTP errors |

`eval_tps` is the cleanest per-model speed metric — it excludes prompt eval and KV cache allocation, so cold-loaded prompts don't drag the number down. `wall_s` is what a user actually experiences.

## Why hit Ollama directly?

In production I route everything through LiteLLM at `:4000` for observability. But LiteLLM strips Ollama's `eval_count` / `eval_duration` from the response (it only surfaces OpenAI-format `usage`), and it doesn't expose the separated `thinking` field cleanly. For benchmarking I bypass it. Production traffic still goes through LiteLLM.

## License

MIT. Take the scripts, take the data, point out where I'm wrong.

## Open questions / future work

- Pair-loading concurrency benchmark (which model pairs co-load without eviction on this hardware)
- Same matrix on M4 Pro / M4 Max
- Same matrix with `think:false` forced on every reasoning model, for a clean "non-thinking" baseline
- Drift detection — re-running the matrix monthly and tracking deltas
