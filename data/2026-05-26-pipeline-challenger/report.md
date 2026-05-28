# Pipeline alias challenger benchmark — lfm2:24b vs mistral-small:24b

Head-to-head on the same 8-prompt suite used by every prior `roster_speed_test.py` run. Same `num_ctx` (32K), same `num_predict` (16384), warm runner for the measured prompts (warmup call paid up front).

## Verdict

**Keep `pipeline` = lfm2:24b. mistral-small:24b loses on both speed and quality.**

Recommendation: `ollama rm mistral-small:24b`.

## Speed

| alias | model | warm tps (median) | total wall (8 prompts) | tps spread |
|---|---|---:|---:|---|
| `pipeline` | lfm2:24b | **~56 tps** | **17.8 s** | 54–58 (108 on 2-tok reply, noise) |
| `pipeline-challenger` | mistral-small:24b | ~7.1 tps | 146.7 s | 7.0–7.3 (13.7 on 2-tok reply, noise) |

lfm2 is **~7.6× faster steady-state**, **8.2× faster wall**. mistral-small is in roughly the same speed band as gpt-oss:20b — i.e. the slow 20B tier that `pipeline` was specifically chosen to escape.

## Quality, prompt by prompt

| prompt | winner | notes |
|---|---|---|
| fim-code | tie | Both produce the same recursive `fibonacci`. mistral's LaTeX framing is slightly more polished prose. |
| quick-qa | tie | Both reply "Paris". |
| structured-json | **lfm2** | Prompt: "Reply with only the JSON, no prose." lfm2: clean `["x", "y", "z"]`. mistral: ```` ```json ```` fence + escaped quote chars inside strings (`"\"Using global variables\""`) — malformed for downstream consumers and violates the explicit "no prose" instruction. |
| math-reason | tie | Both arrive at 42. lfm2 uses richer markdown; mistral simpler prose. |
| writing-blurb | lfm2 (slight) | Both ~60 words. mistral fabricated "3 months battery life" — a spec not in the prompt. lfm2 stuck to plausible claims. |
| code-task | tie | Both produce reasonable `kth_largest` implementations. |
| multilingual | **lfm2** | Prompt: "Translate to French: …". lfm2: one clean line. mistral: translation + an unsolicited word-by-word breakdown. Over-explained, weaker instruction-following. |
| summarize | tie | Both compress to a single sentence with the three facts. |

**lfm2 wins or ties on every prompt.** mistral's two losses are both instruction-following: the JSON prompt and the translation prompt asked for terse output and got verbose output instead. That's exactly the failure mode `pipeline` is supposed to avoid (it's the automation / summarization / structured-tasks alias).

## Disk impact

- Pre-pull: 17 GiB free (post-orphan-cleanup, was 52 GiB before pull)
- Post-pull: 39 GiB free (mistral-small adds 14 GB)
- Post-`ollama rm mistral-small:24b`: should return to ~52 GiB free

## Run artifacts

- `results.json` — raw per-prompt timings + outputs
- `run.log` — live console output

## Method note

Benchmark hits Ollama directly at `:11434`, not LiteLLM — same as every prior `roster_speed_test.py` run. The temporary `pipeline-challenger` LiteLLM alias was added so the challenger was reachable through the proxy if needed, but the timing numbers above are pure Ollama. The alias is being reverted (not committed) along with the temporary `roster_speed_test.py` MODELS entry.
