
## Roster additions speed benchmark — 2 new models (2026-05-25)

> Same 8 prompts, same script (`~/Code/otel-local-ai/scripts/roster_speed_test.py`), same methodology as the 2026-05-23 runs. Two new models sourced from external Mac-LLM recommendations (bswen.com 32GB tier + apxml.com 16-24GB tier).
>
> Total wall time: **9.8 min** for 2 models × 8 prompts × 1 cold load each.
>
> Raw results: `~/Code/otel-local-ai/benchmarks/2026-05-25-roster-additions/results.json`.

### Sources

- [bswen.com — Best Local LLM Mac Mini M4](https://docs.bswen.com/blog/2026-03-25-best-local-llm-mac-mini-m4/) (Mar 2026)
- [apxml.com — Best Local LLMs on Every Apple Silicon Mac in 2026](https://apxml.com/posts/best-local-llms-apple-silicon-mac) (Feb 2026)

### Candidate model triage

bswen recommended for 32GB tier: `deepseek-r1:14b`, `llama3.1:13b`, `qwen2.5-coder:14b`, `mistral-small:24b`.
apxml recommended (across 8GB / 16-24GB / 36-64GB tiers): `phi4-mini`, `qwen3-8b`, `ministral-8b`, `qwen2.5:14b`, `glm-4-9b`, `nemotron-3-nano`, `llama-3.1-70b`, `qwen3-coder:32b`, `mixtral:8x7b`, `deepseek-r1`/`deepseek-v3` 671B, `llama-3.1` 405B, `command-r-plus`.

After cross-referencing against the existing 11-model roster, two clear gaps remain:

| Gap | Candidate | Why it's a real gap |
|---|---|---|
| Fast 14B reasoning | `deepseek-r1:14b` | `phi4-reasoning:plus` is the only thinking-channel reasoning model in the roster; at 9 tps median and 2699s total on 8 prompts it's "willing to wait 5-15 min" territory. DeepSeek's R1 distill at 11 tps would be a 5× wall-clock improvement at similar quality. |
| Code-specialized mid-size | `qwen2.5-coder:14b` | Only code-tagged model in the roster is `qwen2.5-coder:3b-base` (FIM). For harder code generation tasks the roster currently uses `granite4.1:8b` (structured/review) or `capable` (qwen3:14b with thinking tax). No code-specialized middle tier exists. |

Pulled both. Did **not** pull `mistral-small:24b` — disk dropped to 15 GB free after the two pulls and that model would have left ~1 GB free, which is unsafe. Logged for follow-up.

The remaining apxml/bswen candidates are either too large for 32GB unified memory, duplicates of existing roster slots, or in one case (`llama3.1:13b`) appear to be a fabricated model that Meta has never released.

### Models in this run

| alias | ollama tag | think setting | num_ctx | num_predict | size |
|---|---|---|---|---|---|
| `r1-reasoning` | `deepseek-r1:14b` | think:true | 40K | 16384 | 9.0 GB |
| `code-mid` | `qwen2.5-coder:14b` | think:false | 64K | 16384 | 9.0 GB |

### Tokens-per-second matrix

| alias | fim | qa | json | math | write | code | trans | sum | median |
|---|---|---|---|---|---|---|---|---|---|
| r1-reasoning | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | **11** |
| code-mid | 11 | 22 | 12 | 11 | 11 | 11 | 12 | 12 | **11** |

### Wall-clock seconds matrix (load + prompt eval + thinking + generation)

| alias | fim | qa | json | math | write | code | trans | sum | total |
|---|---|---|---|---|---|---|---|---|---|
| r1-reasoning | 87 | 12 | 50 | 19 | 58 | 243 | 32 | 11 | **512** |
| code-mid | 23 | 0 | 2 | 9 | 5 | 19 | 2 | 4 | **65** |

### Output token count (`eval_count`)

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| r1-reasoning | 962 | 132 | 560 | 211 | 645 | 2629 | 347 | 118 |
| code-mid | 250 | 2 | 23 | 99 | 53 | 208 | 17 | 38 |

### Thinking-channel chars

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| r1-reasoning | 2k | 609 | 3k | 287 | 3k | 7k | 1k | 452 |
| code-mid | — | — | — | — | — | — | — | — |

### Output spot-check on `math-reason` (correct answer: 42)

| alias | first 80 chars of visible answer |
|---|---|
| r1-reasoning | `**Solution:**\n\nLet's break down the problem step by step.\n\n1. **Initial num` |
| code-mid | `Let's break it down step-by-step:\n\n1. The store starts with 47 apples.\n2. T` |

Both arrive at 42. r1-reasoning produces a more formal LaTeX-style solution after its thinking channel; code-mid produces a clean step-by-step prose answer with no thinking overhead.

### Findings & decisions

**`r1-reasoning` is the right replacement for `reasoning` (phi4-reasoning:plus).**

Direct head-to-head on the same 8 prompts:

| metric | `reasoning` (phi4-reasoning:plus) | `r1-reasoning` (deepseek-r1:14b) | winner |
|---|---|---|---|
| median tps | 9 | **11** | r1 by 22% |
| total wall (8 prompts) | 2699s | **512s** | r1 by 5.3× |
| weights | 11 GB | **9 GB** | r1 by 2 GB |
| math-reason correctness | ✓ | ✓ | tie |
| produces visible thinking channel | yes | yes | tie |
| writing-blurb quality | ✓ clean | ✓ clean | tie |

Phi-4's reasoning is more thorough per token, but the 5.3× wall-clock gap is too large to keep it as the primary reasoning slot. **Promote `r1-reasoning` to the primary reasoning alias; keep `phi4-reasoning:plus` aliased as `reasoning-deep` for problems where the extra thoroughness is worth the wait.**

**`code-mid` fills a real gap between `code-autocomplete` (3B) and `capable` (qwen3:14b, with thinking tax).**

Direct head-to-head on the same 8 prompts:

| metric | `capable` (qwen3:14b, think:true) | `code-mid` (qwen2.5-coder:14b, think:false) | winner |
|---|---|---|---|
| median tps | 11 | 11 | tie |
| total wall (8 prompts) | 552s | **65s** | code-mid by 8.5× |
| weights | 9.3 GB | 9.0 GB | tie |
| thinking output | yes (significant) | none | code-mid (when you don't want CoT) |
| code-task output quality | clean Python | clean Python with docstring | tie |
| FIM completion quality | n/a (general model) | structured | code-mid |

`code-mid` is not a replacement for `capable` — they have different roles. `capable` is general-purpose with optional reasoning; `code-mid` is code-specialized without reasoning. **Add `code-mid` as a new alias for "harder code tasks where you don't want the thinking channel's latency"** — between `code-autocomplete` (FIM, 49 tps) and `code-review` (granite4.1, structured), `code-mid` covers the "generate a complete, longer code snippet quickly" slot.

**Speed parity with similar-size 14B roster members is notable.** Both new models clock 11 tps median on this M4 Mini, which matches the existing 14B-class models (`capable` and `instruct`). The 14B-at-Q4_K_M tier is consistently ~11 tps on this host regardless of base architecture (Qwen, Mistral, Granite, DeepSeek distill).

### Proposed roster adjustments

| Alias | Status | Backing model | Notes |
|---|---|---|---|
| `reasoning` | **switched** to deepseek-r1:14b | `deepseek-r1:14b` | 5.3× faster total wall than phi4-reasoning at same/better quality on these prompts |
| `reasoning-deep` | **new** | `phi4-reasoning:plus` | Reserved for problems where phi4's extra thoroughness is worth the 15-min latency |
| `code-mid` | **new** | `qwen2.5-coder:14b` | Code-specialized 14B without thinking tax; sits between `code-autocomplete` (3B) and `code-review` (granite4.1) |

### Follow-ups

- **Pull `mistral-small:24b` (~14 GB)** once disk has 25+ GB free. Head-to-head against `efficient` (lfm2:24b) would close the loop on the bswen.com 32GB recommendations.
- **Re-test `r1-reasoning` on the genuinely hard problems** that phi4-reasoning was reserved for. The 8-prompt suite is mostly soft tasks; the real question is whether r1 holds up on multi-step math/planning where phi4's 5-15 min was earning its keep.
- **Consider deprecating `capable` (qwen3:14b)** if `code-mid` and `instruct` (ministral-3:14b) together cover its workload. `capable` at 11 tps with thinking tax is now the slowest 14B in the roster.
