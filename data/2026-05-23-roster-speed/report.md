
## Speed benchmark — all 10 models, all 8 prompts (2026-05-23)

> 80 calls total, sequential per model so the cold-load tax only hits prompt 1. About 107 minutes wall time on a 32 GB M4 Mini.
>
> Direct to Ollama on `:11434` — not via LiteLLM. I need the raw `eval_count` / `eval_duration` for honest tokens/sec, plus the separated `thinking` field that LiteLLM doesn't pass through cleanly. Each model uses the `num_ctx` and `num_predict` I was actually shipping (isolated-mode default from `models.yaml`, Pi `maxTokens`).
>
> Script: `scripts/roster_speed_test.py`. Raw data: `results.json` next to this file.

### Prompts

| short | full prompt | exercises |
|---|---|---|
| `fim` | Complete `def fibonacci(n): if n<=1: return n; return ___` | code completion / FIM |
| `qa` | What is the capital of France? Reply with just the name. | fast factual lookup |
| `json` | List 3 Python anti-patterns as a JSON array | structured output |
| `math` | Apple-store arithmetic, show your work | multi-step reasoning |
| `write` | 60-word product description for ergonomic keyboard | bounded creative writing |
| `code` | Write `kth_largest(arr, k)` with docstring | longer code task |
| `trans` | Translate one sentence to French | multilingual |
| `sum` | One-sentence summary of three short sentences | summarization |

### Tokens-per-second matrix (higher = faster generation)

| alias | fim | qa | json | math | write | code | trans | sum | median |
|---|---|---|---|---|---|---|---|---|---|
| code-autocomplete | 46 | 95 | 49 | 47 | 48 | 47 | 49 | 50 | **49** |
| fast-general | 29 | 28 | 29 | 29 | 29 | 29 | 29 | 29 | **29** |
| code-review | 18 | 36 | 18 | 18 | 18 | 18 | 18 | 18 | **18** |
| general | 16 | 16 | 16 | 16 | 15 | 15 | **ERR** | 16 | **16** |
| writing | 11 | 23 | 11 | 11 | 11 | 12 | 11 | 12 | **11** |
| reasoning | 9 | 9 | 8 | 9 | 8 | 9 | 9 | 9 | **9** |
| capable | 11 | 11 | 11 | 11 | 11 | 10 | 10 | 11 | **11** |
| capable-large | 25 | 26 | 26 | 25 | 25 | 25 | 25 | 25 | **25** |
| flash | 16 | 13 | 13 | 14 | 20 | 19 | 19 | 15 | **16** |
| vision | 36 | 36 | 35 | 36 | 36 | 26 | 36 | 36 | **36** |

### Wall-clock seconds matrix (lower = faster total response, includes prompt eval + thinking + generation)

| alias | fim | qa | json | math | write | code | trans | sum | total |
|---|---|---|---|---|---|---|---|---|---|
| code-autocomplete | 12 | 0 | 1 | 39 | 2 | 6 | 1 | 1 | **62** |
| fast-general | 29 | 0 | 13 | 5 | 7 | 51 | 19 | 9 | **133** |
| code-review | 24 | 0 | 2 | 4 | 5 | 8 | 1 | 2 | **46** |
| general | 21 | 10 | 58 | 34 | 628 | 35 | **TO** | 203 | **988** |
| writing | 16 | 1 | 4 | 9 | 6 | 29 | 6 | 5 | **76** |
| reasoning | 196 | 28 | 887 | 57 | 792 | 169 | 144 | 425 | **2699** |
| capable | 68 | 11 | 32 | 33 | 38 | 286 | 60 | 24 | **552** |
| capable-large | 11 | 2 | 4 | 6 | 54 | 29 | 9 | 7 | **122** |
| flash | 39 | 9 | 47 | 39 | 30 | 36 | 48 | 46 | **293** |
| vision | 29 | 5 | 35 | 9 | 9 | 369 | 28 | 11 | **495** |

### Output token count (`eval_count` — what the model actually produced)

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| code-autocomplete | 544 | 2 | 31 | 1809 | 80 | 281 | 41 | 26 |
| fast-general | 846 | 1 | 360 | 142 | 200 | 1463 | 549 | 253 |
| code-review | 421 | 2 | 26 | 61 | 78 | 135 | 16 | 35 |
| general | 330 | 158 | 953 | 543 | 9612 | 528 | — | 3262 |
| writing | 168 | 2 | 34 | 77 | 58 | 326 | 63 | 37 |
| reasoning | 1786 | 257 | 7393 | 500 | 6539 | 1525 | 1297 | 3741 |
| capable | 767 | 117 | 351 | 359 | 419 | 2994 | 621 | 244 |
| capable-large | 271 | 36 | 87 | 139 | 1344 | 704 | 216 | 173 |
| flash | 542 | 101 | 596 | 533 | 575 | 636 | 892 | 646 |
| vision | 1013 | 160 | 1229 | 305 | 317 | 9696 | 983 | 350 |

### Thinking-channel chars (thinking models only; `—` = none emitted)

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| code-autocomplete | — | — | — | — | — | — | — | — |
| fast-general | 1k | — | 1k | 236 | 530 | 2k | 1k | 529 |
| code-review | — | — | — | — | — | — | — | — |
| general | 616 | 554 | 3k | 1k | 30k | 607 | — | 14k |
| writing | — | — | — | — | — | — | — | — |
| reasoning | 6k | 1k | 34k | 1k | 26k | 5k | 4k | 17k |
| capable | 1k | 513 | 1k | 786 | 1k | 10k | 2k | 913 |
| capable-large | 667 | 102 | 279 | 151 | 4k | 409 | 662 | 542 |
| flash | 1k | 415 | 2k | 1k | 2k | 1k | 3k | 2k |
| vision | 3k | 699 | 5k | 553 | 1k | 35k | 3k | 1k |

### Output spot-check on `math-reason` (right answer: 42)

| alias | first 80 chars of visible answer |
|---|---|
| code-autocomplete | `To find out how many apples the store has after selling some and receiving more,` |
| fast-general | `**Work:** \\ * Start: 47 apples \\ * Sold: $47 - 23 = 24$ \\ * Received: $24 + 1` |
| code-review | `Start with the initial number of apples: 47   \\ Subtract the apples sold: 47 - ` |
| general | `Here is the calculation: \\  \\ 1.  Start with **47** apples. \\ 2.  Subtract th` |
| writing | `Let's calculate this step-by-step: \\  \\ 1. Start with 47 apples. \\ 2. Sell 23` |
| reasoning | `Start with 47 apples. \\ After selling 23, you have 47 - 23 = 24 apples. \\ Then` |
| capable | `The store starts with 47 apples. After selling 23:   \\ 47 - 23 = **24** apples ` |
| capable-large | `**Step 1 – Start with the initial number of apples** \\  \\ \[ \\ 47 \text{ appl` |
| flash | `1.  Start with 47 apples. \\ 2.  Subtract the 23 sold: $47 - 23 = 24$ apples rem` |
| vision | `The store starts with **47 apples**. \\  \\ 1. **Subtract the sold apples**:   \` |

### What I took away

**`vision` (qwen3-vl:30b) was the speed surprise — 36 tps median.** Faster than every model in the roster except `code-autocomplete`. 2.2× faster than the `general` I was shipping (qwen3.5:9b-mlx at 16 tps), 3.2× faster than `writing` (mistral-nemo:12b at 11 tps), and it's a 30B vision-tuned model. Output quality on math, code, and translation tracked the dedicated models. The 19 GB footprint already excludes it from concurrent loading, so the only real cost of using it for text was that I hadn't been.

**`capable-large` (gpt-oss:20b) at 25 tps was the well-rounded performer.** Faster than `capable` (qwen3:14b, 11 tps), `writing`, and `general`, with the lowest thinking overhead of any reasoning model in the matrix — median 542 chars vs 1k+ for the qwen3 family. The role label "when 14B isn't enough" undersold it; it's also faster and more concise than 14B.

**`general` (qwen3.5:9b-mlx) over-thinks at production budgets.** 30k chars of thinking on a 60-word writing prompt (10.5 min). 14k chars on a one-sentence summary (3.4 min). Timed out at >15 min on the French translation — the only timeout in the whole matrix. The "fast reasoning" claim on the role label was wrong at `max_tokens=32768`. Either swap the default or force `think:false` in the route.

**`reasoning` (phi4-reasoning:plus) is for genuinely hard problems only.** 9 tps median, 34k chars of thinking on the JSON-list prompt alone (14.8 min). Phi4 has no off switch for thinking; it always reasons exhaustively. Total wall for 8 trivial prompts: 45 minutes. Use it where you'd happily wait 15 minutes for a careful answer, not as a back-pocket default.

**`fast-general` (gemma4:e4b-mlx) isn't actually fast for the instant-Q&A role.** 29 tps, but it emits 200–2000 chars of thinking on most prompts including trivial ones. code-task burned its 16K budget thinking and returned empty content. The `e4b-mlx` template has thinking baked in even though I didn't pass `think:true`. Force it off in the client or swap for a true non-thinking small model.

**`flash` (glm-4.7-flash:q4_K_M) doesn't earn its 19 GB.** 16 tps median, slower than `capable-large` (25 tps) and `vision` (36 tps) — both of which are bigger. The multilingual prompt wasn't noticeably better than smaller models'. Hard to justify keeping unless you specifically need it for very-large-context Chinese content.

**`code-autocomplete`, `code-review`, and `writing` performed inside their roles.** code-autocomplete: 47 tps median, 95 on trivial prompts. code-review (granite4.1): 18 tps, no thinking overhead, clean structured JSON first try. writing (mistral-nemo:12b): 11 tps with clean output. Slow but no surprises.

**Output quality was uniform on simple tasks.** Every model got 42 right on math-reason. The base model (`code-autocomplete`) wandered into commentary before getting there, which is what a non-instruction-tuned base model does. No model produced wrong math.

**Thinking models hit budget caps on trivial prompts.** Three returned empty `content` when they exhausted `num_predict` mid-think: `fast-general` on code-task, `general` on multilingual (the timeout), and a recurring pattern across the qwen3 family. Operational note: cap thinking tokens in client requests, not just total `max_tokens`.

### Proposed roster adjustments

| Alias | Current default | Proposed change | Why |
|---|---|---|---|
| `general` | qwen3.5:9b-mlx | Switch to `qwen3-vl:30b` (or `gpt-oss:20b` if memory is tight) | qwen3.5 over-thinks and timed out on routine prompt at production budget |
| `fast-general` | gemma4:e4b-mlx | Force `think:false` in LiteLLM route, or swap to a true non-thinking small model | Currently emits thinking even when not asked |
| `reasoning` | phi4-reasoning:plus | Keep, but document "expect 5-15 min per call" in role-label notes | The model is correct for the role; user expectations need to match its speed profile |
| `flash` | glm-4.7-flash:q4_K_M | Consider retiring unless specifically needed for Chinese content | Slower than `capable-large` and `vision` despite same/larger footprint |
| `capable-large` | gpt-oss:20b | Promote in role docs — it's the fastest reasoning model in the roster | Currently positioned as fallback; deserves primary status |
| `vision` | qwen3-vl:30b | Document dual-use: vision + text-only general chat | Fastest non-autocomplete model in the roster |

