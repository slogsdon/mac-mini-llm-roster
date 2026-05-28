# mac-mini-llm-roster

Six benchmark runs of every local model I bothered to download, on one Mac Mini M4 with 32 GB of unified memory. Scripts, raw JSON, run logs, and the markdown tables that came out of them.

If [willitrunai.com](https://www.willitrunai.com) told you a model will fit on your Mac, this is the next question: *given it fits, does it actually behave at the contexts and budgets you'd run it at?* For most of the models in here, the answer was a surprise — usually not in the direction the model card implied.

This is the data side of a forthcoming blog post (link goes here when it ships).

## What's in here

```
scripts/
  roster_speed_test.py          8 prompts × N models at production num_ctx
  roster_speed_test_maxctx.py   Same prompts, num_ctx pinned to each model's
                                ollama_max
data/
  2026-05-23-roster-speed/        Run 1: 10 models at the defaults I was shipping
  2026-05-23-roster-speed-delta/  Run 2: 6 models re-measured with think:false fixes
  2026-05-24-roster-speed-maxctx/ Run 3: 11-model roster at maxed contexts
  2026-05-25-roster-additions/    Run 4: deepseek-r1:14b + qwen2.5-coder:14b adds
  2026-05-26-alias-verification/  Run 5: alias-route verification + dedup audit
  2026-05-26-pipeline-challenger/ Run 6: lfm2:24b vs mistral-small:24b head-to-head
litellm-example/
  config.yaml                   The use-case-alias pattern I run in production,
                                with OTel + Langfuse wiring, sanitized
```

Each `data/<run>/` folder carries `results.json` (one row per call), usually a `run.log` (full stdout), and a `report.md` (tables and the notes I took at the time). Some runs add a `README.md` for run-specific context, and the dedup run adds an `audit.md`.

## Hardware

One M4 Mac Mini, 32 GB unified memory, macOS, Ollama 0.24 running on the host. No GPU box, no quant tricks past whatever the published tags use.

## Running it

```bash
python3 scripts/roster_speed_test.py
python3 scripts/roster_speed_test_maxctx.py
```

Each script walks the model list sequentially so the cold-load cost falls on prompt 1 and prompts 2–8 hit a warm runner. Default output is `/tmp/roster_speed_*.json`; pass `--out PATH` to redirect or `--only alias1,alias2` to subset. A full run is roughly 60–110 minutes on this hardware depending on how much the reasoning models decide to think.

## How to read `results.json`

One object per (model, prompt) call. The fields that matter:

| field | meaning |
|---|---|
| `alias` | the alias the call was made under (the naming scheme evolved across runs — see each `report.md`) |
| `tag` | the underlying Ollama tag |
| `num_ctx` / `num_predict` | what the call was configured with |
| `wall_s` | total request wall time (load + prompt eval + thinking + generation) |
| `eval_tps` | tokens/sec during generation only, from Ollama's `eval_count` / `eval_duration` |
| `eval_count` | how many tokens the model actually produced |
| `thinking_chars` | chars in the separated thinking channel (0 if the model doesn't have one) |
| `content` | first 300 chars of the visible response |
| `error` | `null` on success; populated on timeouts or HTTP errors |

`eval_tps` is the clean per-model speed number — it excludes prompt eval and KV alloc, so a cold first prompt doesn't drag down the average. `wall_s` is what a user actually feels.

## Why hit Ollama directly?

In production everything routes through LiteLLM at `:4000` so I can put Langfuse + OTel in front of it. But LiteLLM strips Ollama's `eval_count` / `eval_duration` (it only surfaces OpenAI-format `usage`) and doesn't pass the separated `thinking` field through cleanly. For benchmarking that's a dealbreaker, so the scripts go straight to `:11434`. Production traffic still goes through LiteLLM.

## License

MIT. Take the scripts, take the data, tell me where I got it wrong.

## What I'd still like to know

- Which model pairs co-load without eviction on this hardware (concurrency profiling)
- The same matrix on an M4 Pro or Max — at what point does the small-dense-model KV penalty disappear
- A clean non-thinking baseline: every reasoning model with `think:false` forced, for direct comparison
- Drift over time: re-run monthly and watch the numbers move

### Keywords for the search engines

`ollama`, `litellm`, `local-llm`, `apple-silicon`, `mac-mini`, `m4`, `mlx`, `mixture-of-experts`, `qwen3`, `qwen2.5-coder`, `deepseek-r1`, `phi4-reasoning`, `lfm2`, `gpt-oss`, `mistral-small`, `mistral-nemo`, `gemma`, `granite`, `benchmark`, `tokens-per-second`, `kv-cache`, `thinking-channel`, `langfuse`, `otel`, `role-aliases`
