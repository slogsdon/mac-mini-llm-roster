# Roster speed benchmark — 2026-05-25 additions

Two new models pulled from bswen.com + apxml.com Mac-LLM recommendations, run
through the same 8-prompt matrix as the prior roster benchmarks.

## Sources

- https://docs.bswen.com/blog/2026-03-25-best-local-llm-mac-mini-m4/
- https://apxml.com/posts/best-local-llms-apple-silicon-mac

## Files

- **`results.json`** — raw per-call results for the 2 new models
- **`run.log`** — full stdout of the run (9.8 min total)
- **`report.md`** — context, data tables, comparison vs current roster, decisions

## Pulled

| Ollama tag | Size | Why | Source |
|---|---|---|---|
| `deepseek-r1:14b` | 9.0 GB | Reasoning candidate; competitor for slow `phi4-reasoning:plus` | bswen |
| `qwen2.5-coder:14b` | 9.0 GB | Code-specialized 14B; fills gap between 3B autocomplete and general 14B | bswen + apxml |

## Skipped (and why)

| Candidate | Source | Reason |
|---|---|---|
| `mistral-small:24b` (~14 GB) | bswen 32GB tier | Disk: only 15 GB free after the two pulls; pulling this would leave ~1 GB free which is unsafe for the OS. Worth revisiting if Shane frees ~20 GB. |
| `llama3.1:13b` | bswen 32GB tier | Doesn't exist — Meta only ships Llama 3.1 in 8B / 70B / 405B. Article appears to have fabricated this row. |
| `phi4-mini` (~2.5 GB) | apxml 8GB tier | Overlaps with `granite4.1:8b` + `gemma4:e4b-mlx` already in roster. No clear gap to fill. |
| `qwen3-8b`, `ministral-8b` | apxml 8GB tier | Covered by larger qwen3:14b / ministral-3:14b already installed. |
| `qwen2.5:14b` (general, non-coder) | apxml 16-24GB tier | Shane already has qwen3:14b at same size class; the coder variant fills a real gap, the general variant does not. |
| `glm-4-9b` (Q8_0) | apxml 16-24GB tier | Roster already has `glm-4.7-flash` as a retirement candidate; not worth re-adding the 9B sibling. |
| `nemotron-3-nano:3.5b` | apxml 16-24GB tier | Overlaps with `lfm2.5-thinking:1.2b` (tiny) and `qwen2.5-coder:3b-base` (small fast) already installed. |
| `qwen3-coder:32b` Q6_K | apxml 36-64GB tier | ~28 GB; too tight on a 32GB unified-memory host with LiteLLM + Ollama overhead. |
| `mixtral:8x7b` Q4_K_M | apxml 36-64GB tier | ~26 GB; at the OOM boundary per the project's rule of thumb. |
| `llama3.1:70b` Q3_K_S, `qwen3-coder:32b` Q6_K, DeepSeek-V3/R1 671B, Llama-3.1 405B, Command-R-Plus 104B | apxml 36-64GB & 96-512GB tiers | Too large for 32GB unified. |

## How to reproduce

```bash
cd ~/Code/otel-local-ai
python3 scripts/roster_speed_test.py \
  --only r1-reasoning,code-mid \
  --out benchmarks/2026-05-25-roster-additions/results.json \
  > benchmarks/2026-05-25-roster-additions/run.log 2>&1
```

## Top-line outcomes

- **`r1-reasoning` (deepseek-r1:14b) at 11 tps median is a viable replacement for `reasoning` (phi4-reasoning:plus)** — same quality class, 5.3× faster total wall time (512s vs 2699s on the same 8 prompts), same memory footprint (~9 GB vs ~11 GB).
- **`code-mid` (qwen2.5-coder:14b) at 11 tps median, no thinking, fills the gap between `code-autocomplete` (3B, 49 tps for FIM) and `capable` (qwen3:14b, 11 tps with thinking tax)** — same speed as `capable` but skips the thinking channel entirely, so total wall on 8 prompts is 65s vs 552s (8.5× faster).
