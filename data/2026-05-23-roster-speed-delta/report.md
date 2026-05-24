

## Roster shuffle that prompted this delta run (2026-05-23, later same day)

Run 1 left me with two real problems and one opening.

The problems: qwen3.5:9b-mlx over-reasons at production budgets — 30k chars of thinking on a 60-word writing task, plus a >15-minute timeout on the French translation. And gemma4:e4b-mlx emits thinking even when I don't ask it to, because the `e4b-mlx` template has thinking baked into the chat format. Both are fixable by forcing `think:false`; both got re-tested below to confirm.

The opening: qwen3-vl:30b runs at 36 tps on text-only prompts, faster than every general-purpose model I had. A 30B vision-tuned MoE turned out to be a better text default than my 9B chat model. Combined with qwen3.6:35b-mlx becoming available (also MLX, also MoE, also vision-capable, also thinking-capable, similar 21 GB footprint), this opened the door to consolidating `general` and `vision` onto one backing model.

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

### Why these new aliases

`instruct` (ministral-3:14b): same size class as `capable` (qwen3:14b at ~9 GB) but with vision and no thinking channel. Fills a real gap — structured tool-use with images that doesn't pay the reasoning tax.

`efficient` (lfm2:24b): MoE 24B at ~14 GB, no thinking channel. Direct competitor with `capable-large` (gpt-oss:20b, 13 GB, with thinking). If it's faster on equivalent tasks it earns the primary slot.

`tiny-reason` (lfm2.5-thinking:1.2b): 731 MB. Small enough to run alongside anything else without eviction. Use case is throwaway logic decisions where I want chain-of-thought but can't afford phi4's 15 minutes.

Slotting was provisional pending the numbers below.


## Delta speed benchmark — 6 models (2026-05-23)

> Same 8 prompts, same script. Re-ran qwen3.5 and gemma4 with `think:false` to confirm the production fix, plus the 4 new models. The other 8 from run 1 don't need re-measuring — their numbers stand.
>
> Total wall time: **11.8 min** (vs 107 min for the full 10-model run 1). Per-model `num_ctx` and `num_predict` unchanged.
>
> Raw data: `results.json` next to this file.

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

### What I took away

**The `think:false` fixes were dramatic.**

| model | with thinking (run 1) | `think:false` (this run) | delta |
|---|---|---|---|
| `fast-general` (gemma4) total wall | 133s | 49s | 2.7× faster |
| `general` (qwen3.5) total wall | 988s + 1 timeout | 55s | 18× faster, no timeouts |

Same models, same prompts. Everything I'd previously written off as "this model is too slow" or "this one hangs" was a thinking-channel config bug, not a model problem. Both production routes now force `think:false` in LiteLLM so callers don't have to know. qwen3.5 is usable again, but at 16 tps median it's still the slowest non-thinking option in the roster — which is why it's losing the `general` alias anyway.

**`efficient` (lfm2:24b) won this run.** 56 tps median, 18 seconds total wall for 8 prompts. Head-to-head with `capable-large` (gpt-oss:20b) on the same prompts:

| metric | `capable-large` (gpt-oss:20b) | `efficient` (lfm2:24b) | winner |
|---|---|---|---|
| median tps | 25 | 56 | efficient by 2.2× |
| total wall (8 prompts) | 122s | 18s | efficient by 6.8× |
| weights | 13 GB | 14 GB | tie |
| math-reason correctness | ✓ 42 | ✓ 42 | tie |
| writing-blurb quality | ✓ clean | ✓ clean | tie |

Faster on every prompt with comparable output quality. Promoted `efficient` to the primary 20B-class slot; `capable-large` becomes the secondary you reach for when you specifically want gpt-oss's reasoning-channel style.

**`general-next` (qwen3.6:35b-mlx) replaces both `general` and `vision`.** 35 tps median (the old `vision` qwen3-vl was 36 tps, the old `general` qwen3.5 was 16 tps). 21 GB weights vs 19 GB for qwen3-vl — comparable footprint, MoE so active params are well below total. Cold load was 9.6 seconds, the fastest of any 20B+ model in the matrix. Thinking is on by default; clients should pass `think:false` for trivial chat to stay in the 35 tps regime, and `think:true` when they want the reasoning channel. There's no reason to keep two large models for two roles when one handles both.

**`instruct` (ministral-3:14b) fills the vision + tools gap.** 13 tps median, no thinking, vision input native. Same speed class as `capable` (qwen3:14b at 11 tps) but adds vision and skips the thinking tax. Right fit for structured tool-use (Hermes / Pi function-calling) where I want clean instruction-following without chain-of-thought, vision tasks that don't need qwen3.6's reasoning depth, and as a smaller alternative to `general` when memory pressure rules out the 35B.

**`tiny-reason` (lfm2.5-thinking:1.2b) is fast and brittle — 116 tps median.** Fastest model in the roster by a wide margin. 731 MB weights so it runs alongside anything without eviction. 0.9 second cold load. Math output was correct and concise.

But: on the trivial "capital of France" prompt it answered `Paris\n\nWait, wait, wait. Wait, the user said "Repl...` — second-guessing itself out loud. And it burned its full 8K `num_predict` on the writing prompt to return empty content, the same failure mode qwen3.5 had at 32K. Always emits 1k–30k chars of thinking even on trivial prompts.

Use cases are narrow: fast yes/no logic decisions in pipelines, pre-flight validation, quality-filter classifiers. Wrap the output with an empty-content guard.

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
- **Multilingual / Chinese** → use `general` (qwen3.6:35b-mlx); `flash` was retired after this run

