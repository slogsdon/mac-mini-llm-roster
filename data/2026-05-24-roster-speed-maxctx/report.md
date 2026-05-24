
## Max-Context Speed Benchmark — Final Roster (2026-05-24)

> Third and final benchmark in this series. Same 8 prompts, same script (`roster_speed_test_maxctx.py`). 11 models, each at its `ollama_max` from `models.yaml` (the model card's training-time max). Exception: `writing` capped at 131K — its 1M ceiling is unrealistic on a 32 GB host. `num_predict` unchanged from production.
>
> Total wall time: **69.5 min** (vs 107 min for the first run at production defaults).
>
> Raw results: `~/Code/otel-local-ai/benchmarks/2026-05-24-roster-speed-maxctx/results.json`.

### Models in this run (with `num_ctx` actually used)

| alias | tag | num_ctx (max) | num_predict |
|---|---|---|---|
| `code-autocomplete` | `qwen2.5-coder:3b-base` | 32,768 | 8,192 |
| `fast-general` | `gemma4:e4b-mlx` | 131,072 | 16,384 |
| `code-review` | `granite4.1:8b` | 131,072 | 16,384 |
| `general` | `qwen3.6:35b-mlx` | 262,144 | 16,384 |
| `writing` | `mistral-nemo:12b` | 131,072 | 32,768 |
| `reasoning` | `phi4-reasoning:plus` | 32,768 | 16,384 |
| `capable` | `qwen3:14b` | 40,960 | 16,384 |
| `efficient` | `lfm2:24b` | 32,768 | 16,384 |
| `capable-large` | `gpt-oss:20b` | 131,072 | 16,384 |
| `vision` | `qwen3.6:35b-mlx` | 262,144 | 16,384 |
| `instruct` | `ministral-3:14b` | 262,144 | 16,384 |
| `tiny-reason` | `lfm2.5-thinking:1.2b` | 128,000 | 8,192 |

### Tokens-per-second matrix

| alias | fim | qa | json | math | write | code | trans | sum | median |
|---|---|---|---|---|---|---|---|---|---|
| code-autocomplete | 47 | 93 | 49 | 48 | 48 | 47 | 51 | 49 | **49** |
| fast-general | 29 | 30 | 29 | 29 | 29 | 29 | 29 | 29 | **29** |
| code-review | 14 | 29 | 15 | 14 | 14 | 14 | 15 | 14 | **14** |
| general | 35 | 34 | 35 | 35 | 35 | 34 | 34 | 34 | **35** |
| writing | 11 | 23 | 12 | 11 | 11 | 11 | 12 | 12 | **12** |
| reasoning | 9 | 9 | 9 | 9 | **ERR** | 8 | 9 | 9 | **9** |
| capable | 11 | 10 | 11 | 11 | 11 | 10 | 11 | 11 | **11** |
| efficient | 55 | 108 | 55 | 55 | 55 | 54 | 59 | 57 | **55** |
| capable-large | 26 | 26 | 26 | 26 | 26 | 26 | 26 | 26 | **26** |
| vision | 34 | 34 | 34 | 33 | 33 | 32 | 33 | 32 | **33** |
| instruct | 9 | 6 | 6 | 6 | 8 | 9 | 6 | 6 | **6** |
| tiny-reason | 116 | 119 | 116 | 117 | 114 | 117 | 117 | 117 | **117** |

### Wall-clock seconds matrix

| alias | fim | qa | json | math | write | code | trans | sum | total |
|---|---|---|---|---|---|---|---|---|---|
| code-autocomplete | 3 | 0 | 1 | 2 | 2 | 2 | 1 | 1 | **11** |
| fast-general | 6 | 0 | 1 | 2 | 2 | 52 | 11 | 1 | **76** |
| code-review | 26 | 1 | 3 | 8 | 5 | 42 | 3 | 4 | **93** |
| general | 19 | 5 | 38 | 13 | 88 | 156 | 22 | 17 | **358** |
| writing | 16 | 1 | 2 | 10 | 5 | 39 | 7 | 4 | **84** |
| reasoning | 117 | 23 | 389 | 41 | **TO** | 253 | 165 | 221 | **1209** |
| capable | 80 | 12 | 30 | 34 | 43 | 124 | 45 | 27 | **394** |
| efficient | 4 | 0 | 1 | 2 | 2 | 8 | 0 | 1 | **18** |
| capable-large | 12 | 2 | 10 | 9 | 20 | 20 | 5 | 12 | **91** |
| vision | 171 | 6 | 36 | 146 | 43 | 79 | 34 | 46 | **560** |
| instruct | 20 | 2 | 14 | 16 | 14 | 90 | 10 | 9 | **175** |
| tiny-reason | 16 | 2 | 8 | 4 | 47 | 15 | 11 | 9 | **112** |

### Output token count (`eval_count`)

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| code-autocomplete | 119 | 2 | 22 | 90 | 75 | 100 | 20 | 50 |
| fast-general | 171 | 1 | 32 | 57 | 51 | 1495 | 309 | 28 |
| code-review | 351 | 2 | 27 | 92 | 64 | 555 | 38 | 40 |
| general | 645 | 172 | 1313 | 426 | 3029 | 5305 | 748 | 583 |
| writing | 173 | 2 | 16 | 89 | 49 | 430 | 73 | 31 |
| reasoning | 1064 | 208 | 3445 | 364 | — | 2128 | 1466 | 1978 |
| capable | 873 | 124 | 318 | 369 | 471 | 1256 | 504 | 299 |
| efficient | 189 | 2 | 21 | 89 | 83 | 390 | 16 | 35 |
| capable-large | 312 | 47 | 247 | 228 | 512 | 514 | 127 | 303 |
| vision | 5738 | 194 | 1205 | 4807 | 1399 | 2542 | 1112 | 1480 |
| instruct | 169 | 2 | 72 | 78 | 110 | 784 | 55 | 39 |
| tiny-reason | 1872 | 178 | 874 | 448 | 5293 | 1743 | 1320 | 1007 |

### Thinking-channel chars

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| code-autocomplete | — | — | — | — | — | — | — | — |
| fast-general | — | — | — | — | — | — | — | — |
| code-review | — | — | — | — | — | — | — | — |
| general | 1k | 617 | 5k | 980 | 9k | 17k | 2k | 2k |
| writing | — | — | — | — | — | — | — | — |
| reasoning | 4k | 934 | 16k | 1k | — | 8k | 5k | 8k |
| capable | 2k | 561 | 1k | 827 | 1k | 3k | 1k | 1k |
| efficient | — | — | — | — | — | — | — | — |
| capable-large | 535 | 144 | 965 | 467 | 1k | 987 | 439 | 1k |
| vision | 21k | 717 | 4k | 12k | 4k | 9k | 3k | 6k |
| instruct | — | — | — | — | — | — | — | — |
| tiny-reason | 6k | 735 | 3k | 1k | 21k | 5k | 4k | 4k |

### Output spot-check on `math-reason` (right answer: 42)

| alias | first 80 chars of visible answer |
|---|---|
| code-autocomplete | `Let's use subtraction and addition to solve the problem step by step: \\  \\ 1. ` |
| fast-general | `Here is the solution: \\  \\ **Start:** 47 apples \\ **Sell:** $47 - 23 = 24$ ap` |
| code-review | `To find the current number of apples, we perform the following steps: \\  \\ 1. ` |
| general | `Start: 47 apples   \\ After selling 23: 47 − 23 = 24   \\ After receiving 18: 24` |
| writing | `Let's calculate this step-by-step: \\  \\ 1. Start with: 47 apples \\ 2. Sell 23` |
| reasoning | `Start with 47 apples. \\ After selling 23, there are 47 - 23 = 24 apples left. \` |
| capable | `The store starts with 47 apples. After selling 23:   \\ 47 - 23 = **24** apples.` |
| efficient | `To find the number of apples remaining, follow these steps: \\  \\ 1. **Initial ` |
| capable-large | `Initial apples: **47**   \\ Sold apples: **23**   \\  \\ \(47 \;-\; 23 \;=\; 24\` |
| vision | `Here is the step-by-step calculation: \\  \\ 1.  Start with **47** apples and su` |
| instruct | `Let's calculate the number of apples step by step: \\  \\ 1. **Initial apples**:` |
| tiny-reason | `The store starts with 47 apples. After selling 23, it has 47 - 23 = 24. Adding t` |
