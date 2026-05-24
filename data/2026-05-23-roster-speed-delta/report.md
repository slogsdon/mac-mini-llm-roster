

## ⚠ Update 2026-05-23 (later same day) — roster shuffle: qwen3.6 replaces `general` + `vision`, plus 3 new aliases

The first benchmark surfaced two real problems and one opportunity:

1. **qwen3.5:9b-mlx over-reasons at production budgets.** It timed out on the French-translation prompt and used 30k chars of thinking on a 60-word writing task. Forcing `think:false` makes it usable (re-tested in the delta benchmark below), but at that point the only thing qwen3.5 buys you over `vision` (qwen3-vl:30b) is memory.
2. **gemma4:e4b-mlx emits thinking even when not asked.** Its `e4b-mlx` template has thinking baked in. `think:false` fixes it (re-tested below). The LiteLLM `fast-general` route now forces it off so callers don't have to know.
3. **qwen3-vl:30b is 36 tps even on text-only prompts** — faster than every general-purpose model. The 30B vision-tuned model is a better text default than the 9B chat model, on this host.

That last finding combined with availability of **qwen3.6:35b-mlx** (MLX MoE, vision-capable, thinking-capable, 21 GB weights) → consolidate `general` and `vision` onto qwen3.6.

### Roster as of 2026-05-23 evening

| Ollama Tag                  | LiteLLM Alias       | Role                                  | When to Use                                                                              |
| --------------------------- | ------------------- | ------------------------------------- | ---------------------------------------------------------------------------------------- |
| `qwen2.5-coder:3b-base`     | `code-autocomplete` | Code autocomplete                     | Fast inline completion, Cursor/Copilot slot                                              |
| `gemma4:e4b-mlx`            | `fast-general`      | Fast general / vault                  | Skill delegation, quick Q&A, Obsidian ops (think:false forced in LiteLLM route)          |
| `granite4.1:8b`             | `code-review`       | Code review / enterprise              | Structured output, API doc work                                                          |
| `qwen3.6:35b-mlx`           | `general`           | General purpose (vision-capable)      | Default chat — replaces qwen3.5:9b-mlx; doubles as vision endpoint                       |
| `mistral-nemo:12b`          | `writing`           | Writing / instruction                 | Long-form drafts, blog posts, ghostwriting                                               |
| `phi4-reasoning:plus`       | `reasoning`         | Reasoning (slow but careful)          | Multi-step math/planning where you'll happily wait 5-15 min for a thorough answer        |
| `qwen3:14b`                 | `capable`           | Reasoning + coding                    | Heavier tasks where quality > speed                                                      |
| `gpt-oss:20b`               | `capable-large`     | Capable general (fast for size)       | When 14B isn't enough; the fastest "reasoning channel" model in the roster               |
| `glm-4.7-flash:q4_K_M`      | `flash`             | Multilingual / flash                  | Chinese content, fast large-context tasks (re-evaluate: slower than capable-large)       |
| `qwen3.6:35b-mlx`           | `vision`            | Vision (same backing model)           | Any task with images — alias kept distinct so Langfuse can separate vision traffic       |
| **`ministral-3:14b`**       | **`instruct`**      | Instruction + vision + tools          | Clean instruction following with optional images; tool-use; no thinking overhead         |
| **`lfm2:24b`**              | **`efficient`**     | Efficient large general (MoE, no CoT) | When gpt-oss's reasoning isn't wanted; head-to-head competitor for the 20B-class slot    |
| **`lfm2.5-thinking:1.2b`**  | **`tiny-reason`**   | Ultra-fast reasoning (1.2B)           | Trivial logic checks, fast quality filters, pre-flight validation — phi4 too slow        |

### Models retained but un-aliased

- `qwen3.5:9b-mlx` — kept pulled for raw-tag invocation / benchmarking. No production alias.
- `qwen3-vl:30b` — kept pulled for raw-tag invocation / benchmarking. The `vision` alias now points at qwen3.6:35b-mlx.

### Why these particular new aliases

- **`instruct` (ministral-3:14b)** — at ~9 GB it's the same size class as `capable` (qwen3:14b) but with vision and *no* thinking channel. Fills a gap: structured tool-use with images that doesn't pay the reasoning tax.
- **`efficient` (lfm2:24b)** — MoE 24B, ~14 GB. No thinking channel. Direct competitor with `capable-large` (gpt-oss:20b, 13 GB, with thinking). If `efficient` is faster on equivalent tasks, it becomes the default for "fast 20B-class".
- **`tiny-reason` (lfm2.5-thinking:1.2b)** — 731 MB. Tiny enough that it can run alongside any model without eviction. Use case: throwaway logic decisions where you want chain-of-thought but can't afford phi4's 15 minutes.

Use-case slotting is provisional pending the delta-benchmark results below.


## Delta Speed Benchmark — 6 models, post-roster-shuffle (2026-05-23)

> Same 8 prompts, same script (`~/Code/otel-local-ai/scripts/roster_speed_test.py`). Re-ran qwen3.5 + gemma4 with `think:false` to test the production fix, plus the 4 new models. The 8 unchanged models from the first benchmark above are not re-run — their numbers stand.
>
> Total wall time: **11.8 min** (vs 107 min for the full 10-model run). Per-model `num_ctx` / `num_predict` unchanged from the first run.
>
> Raw results: `~/Code/otel-local-ai/benchmarks/2026-05-23-roster-speed-delta/results.json`.

### Models in this delta run

| alias | ollama tag | think setting | why re-tested |
|---|---|---|---|
| `fast-general` | `gemma4:e4b-mlx` | think:false | First run showed unsolicited thinking burned its budget; now forced off in LiteLLM route too |
| `general` | `qwen3.5:9b-mlx` | think:false | First run timed out + over-thought; testing whether `think:false` makes the same model usable |
| `general-next` | `qwen3.6:35b-mlx` | think:true | New: qwen3.6:35b-mlx — candidate replacement for both `general` and `vision` |
| `instruct` | `ministral-3:14b` | no think | New: ministral-3:14b — vision + tools, no thinking channel |
| `efficient` | `lfm2:24b` | no think | New: lfm2:24b MoE — head-to-head with capable-large |
| `tiny-reason` | `lfm2.5-thinking:1.2b` | think:true | New: lfm2.5-thinking:1.2b — fastest-possible reasoning candidate |

### Tokens-per-second matrix

| alias | fim | qa | json | math | write | code | trans | sum | median |
|---|---|---|---|---|---|---|---|---|---|
| fast-general | 28 | 29 | 28 | 28 | 28 | 27 | 28 | 28 | **28** |
| general | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | **16** |
| general-next | 35 | 35 | 35 | 35 | 35 | 34 | 34 | 35 | **35** |
| instruct | 13 | 25 | 13 | 13 | 13 | 13 | 13 | 13 | **13** |
| efficient | 55 | 107 | 51 | 56 | 54 | 50 | 59 | 57 | **56** |
| tiny-reason | 114 | 119 | 116 | 116 | 112 | 117 | 117 | 116 | **116** |

### Wall-clock seconds matrix (load + prompt eval + thinking + generation)

| alias | fim | qa | json | math | write | code | trans | sum | total |
|---|---|---|---|---|---|---|---|---|---|
| fast-general | 6 | 0 | 2 | 2 | 2 | 25 | 10 | 1 | **49** |
| general | 7 | 0 | 4 | 8 | 5 | 29 | 1 | 2 | **55** |
| general-next | 28 | 3 | 22 | 12 | 49 | 115 | 28 | 45 | **302** |
| instruct | 14 | 0 | 6 | 7 | 10 | 61 | 5 | 4 | **107** |
| efficient | 4 | 0 | 1 | 2 | 2 | 9 | 0 | 1 | **18** |
| tiny-reason | 20 | 2 | 6 | 3 | 74 | 11 | 17 | 8 | **143** |

### Output token count (`eval_count`)

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| fast-general | 163 | 1 | 48 | 57 | 50 | 688 | 273 | 24 |
| general | 97 | 1 | 58 | 114 | 70 | 455 | 16 | 23 |
| general-next | 951 | 113 | 768 | 397 | 1694 | 3941 | 960 | 1541 |
| instruct | 176 | 2 | 72 | 78 | 117 | 769 | 56 | 43 |
| efficient | 187 | 2 | 22 | 68 | 93 | 422 | 16 | 26 |
| tiny-reason | 2284 | 272 | 733 | 388 | 8192 | 1296 | 1969 | 940 |

### Thinking-channel chars

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| fast-general | — | — | — | — | — | — | — | — |
| general | — | — | — | — | — | — | — | — |
| general-next | 2k | 443 | 2k | 931 | 5k | 14k | 3k | 6k |
| instruct | — | — | — | — | — | — | — | — |
| efficient | — | — | — | — | — | — | — | — |
| tiny-reason | 8k | 783 | 3k | 1k | 30k | 4k | 6k | 4k |

### Output spot-check on `math-reason` (right answer: 42)

| alias | first 80 chars of visible answer |
|---|---|
| fast-general | `Here is the breakdown: \\  \\ **Start:** 47 apples \\ **Sold:** $47 - 23 = 24$ a` |
| general | `To find the number of apples currently in the store, we follow these steps: \\  ` |
| general-next | `**Work:** \\ 47 (initial) − 23 (sold) = 24   \\ 24 + 18 (received) = 42   \\  \\` |
| instruct | `Let's calculate the number of apples step by step: \\  \\ 1. **Initial apples**:` |
| efficient | `To find the number of apples remaining: \\  \\ 1. **Initial Apples:** 47   \\ 2.` |
| tiny-reason | `The store starts with 47 apples. After selling 23, it has 47 - 23 = 24. Then rec` |

### Findings & decisions

**The think:false fixes are dramatic.**

| model | before (with thinking) | after (think:false) | delta |
|---|---|---|---|
| `fast-general` (gemma4) total wall | 133s | **49s** | 2.7× faster |
| `general` (qwen3.5) total wall | 988s + 1 timeout | **55s** | 18× faster, no timeouts |

Same models, same prompts. The previous "this model is too slow / hangs" findings were entirely a thinking-channel issue. Both production routes now force `think:false` in LiteLLM. **qwen3.5 is *usable* again — but at 16 tps median it's still the slowest non-thinking option in the roster, which is why it's losing the `general` alias anyway.**

**`efficient` (lfm2:24b) is the unambiguous winner of this run — 56 tps median, 18 s total.**

Direct head-to-head with `capable-large` (gpt-oss:20b) on the same 8 prompts:

| metric | `capable-large` (gpt-oss:20b) | `efficient` (lfm2:24b) | winner |
|---|---|---|---|
| median tps | 25 | **56** | efficient by 2.2× |
| total wall (8 prompts) | 122s | **18s** | efficient by 6.8× |
| weights | 13 GB | 14 GB | tie |
| math-reason correctness | ✓ 42 | ✓ 42 | tie |
| writing-blurb quality | ✓ clean | ✓ clean | tie |

lfm2 is faster on every prompt and produces clean output. **Promote `efficient` to the default 20B-class slot; relegate `capable-large` to "secondary when you specifically need gpt-oss's reasoning channel."**

**`general-next` (qwen3.6:35b-mlx) is the right replacement for both `general` and `vision`.**

- 35 tps median (vs the old `vision` qwen3-vl at 36 tps, and the old `general` qwen3.5 at 16 tps)
- 21 GB weights vs 19 GB for qwen3-vl — comparable footprint, MoE so active params << total
- Cold load: 9.6 s — fastest of any 20B+ model
- Thinking is enabled by default; clients should pass `think:false` for trivial chat to stay in the 35 tps regime, and `think:true` for harder questions to get the reasoning channel
- Math-reason output is clean and correct
- Replaces both aliases — there's no reason to keep two large models for two roles when one model handles both

**`instruct` (ministral-3:14b) fills a real gap — 13 tps, no thinking, vision + tools.**

Same speed class as `capable` (qwen3:14b at 11 tps median) but adds vision input and skips the thinking tax. Good fit for:
- Structured tool-use calls (Hermes/Pi function-calling) where you want clean instruction-following, no chain-of-thought
- Vision tasks that need fast turnaround and don't need qwen3.6's reasoning depth
- A "smaller alternative to general" when memory pressure rules out the 35B model

**`tiny-reason` (lfm2.5-thinking:1.2b) is a niche speed weapon, not a general default — 116 tps median but unstable.**

Pros:
- Fastest model in the roster by a wide margin (116 tps median)
- 731 MB weights — runs anywhere, alongside anything, never gets evicted
- Cold load: 0.9 s
- Math output was correct (42) and concise

Cons:
- On the trivial "capital of France" prompt it answered "Paris" then immediately second-guessed itself: `Paris\n\nWait, wait, wait. Wait, the user said "Repl...` — output stability is a real concern
- Burned its full 8K `num_predict` budget on the writing prompt and returned **empty content** — same failure mode as qwen3.5 had at 32K
- Always emits 1k-30k chars of thinking, even on trivial prompts

Use cases (narrow): fast yes/no logic decisions in pipelines, pre-flight validation steps, quality-filter classifiers. Wrap output with a content-empty guard.

### Final proposed roster adjustments (consolidating both benchmarks)

| Alias | Status | Backing model | Notes |
|---|---|---|---|
| `code-autocomplete` | unchanged | qwen2.5-coder:3b-base | Role-fit confirmed |
| `fast-general` | unchanged, `think:false` forced in route | gemma4:e4b-mlx | think:false → 2.7× faster, behavior matches the "fast" label |
| `code-review` | unchanged | granite4.1:8b | Role-fit confirmed |
| `general` | **switched** to qwen3.6:35b-mlx | qwen3.6:35b-mlx | Replaces qwen3.5; doubles as `vision`. Recommend clients default `think:false` for chat, opt into thinking for analysis |
| `writing` | unchanged | mistral-nemo:12b | Role-fit confirmed |
| `reasoning` | unchanged, docs updated | phi4-reasoning:plus | Reserved for genuinely hard problems; document the 5-15 min latency expectation |
| `capable` | unchanged | qwen3:14b | Consider deprioritizing — `instruct` covers similar ground without the thinking tax |
| `capable-large` | **demoted** | gpt-oss:20b | Was primary 20B; now secondary. `efficient` is 6.8× faster on the same prompts |
| `flash` | retirement candidate | glm-4.7-flash:q4_K_M | Slower than `efficient` AND `general-next` despite 19 GB footprint. Keep only if you specifically need its Chinese content |
| `vision` | **switched** to qwen3.6:35b-mlx | qwen3.6:35b-mlx | Same backing model as `general`; alias kept for traffic-tagging in Langfuse |
| `instruct` | **new** | ministral-3:14b | Vision + tools, no thinking. Fills the "fast structured output with images" gap |
| `efficient` | **new, recommend as primary 20B-class** | lfm2:24b | 56 tps, 6.8× faster than capable-large on this matrix. Recommend promoting to primary "fast capable" slot |
| `tiny-reason` | **new, niche** | lfm2.5-thinking:1.2b | 116 tps but unstable on simple prompts. Use for pre-flight checks / classifiers only |

### Updated decision guide

- **Default chat / vision** → `general` (qwen3.6:35b-mlx)
- **Fast Q&A, skill delegation** → `fast-general` (gemma4) — now actually fast
- **Code autocomplete** → `code-autocomplete` (qwen2.5-coder:3b-base)
- **Code review, structured output** → `code-review` (granite4.1) or `instruct` (ministral-3)
- **Long-form writing** → `writing` (mistral-nemo)
- **Large general task, want speed** → `efficient` (lfm2:24b)
- **Large general task, want reasoning channel** → `capable-large` (gpt-oss)
- **Multi-step planning, math, willing to wait** → `reasoning` (phi4)
- **Vision + tool-calling** → `instruct` (ministral-3)
- **Fast yes/no pipeline step** → `tiny-reason` (lfm2.5-thinking)
- **Multilingual / Chinese** → still `flash` for now, though re-evaluate against `general-next`

