# Roster dedup audit — 2026-05-26

Cross-referenced `litellm/config.yaml` (14 aliases) against `ollama list` (13 installed models).

## Alias → backing model

| Alias | Backing model | Size | Role |
|---|---|---|---|
| code-autocomplete | qwen2.5-coder:3b-base | 1.9 GB | FIM (base, no chat tuning) |
| fast-general | gemma4:e4b-mlx | 9.6 GB | Sub-second general; think:false forced |
| code-review | granite4.1:8b | 5.3 GB | Structured-output code review |
| code-mid | qwen2.5-coder:14b | 9.0 GB | Code-specialized, no thinking |
| general | qwen3.6:35b-mlx | 21 GB | Top-tier MoE general |
| writing | mistral-nemo:12b | 7.1 GB | Long-form prose |
| reasoning | deepseek-r1:14b | 9.0 GB | Primary thinking channel |
| reasoning-deep | phi4-reasoning:plus | 11 GB | Deep/slow thinking |
| capable | qwen3:14b | 9.3 GB | General 14B with optional thinking |
| efficient | lfm2:24b | 14 GB | Primary 20B-class route |
| capable-large | gpt-oss:20b | 13 GB | Reasoning-channel 20B |
| vision | qwen3.6:35b-mlx | (shared) | Same model as `general` |
| instruct | ministral-3:14b | 9.1 GB | Instruction-tuned 14B |
| tiny-reason | lfm2.5-thinking:1.2b | 731 MB | Tiniest reasoning model |

## Orphans (in Ollama, no alias)

**None.** All 13 installed Ollama models are referenced by at least one alias.

## Verdict

| Status | Alias / Model | Reason |
|---|---|---|
| keep | code-autocomplete | Only FIM-base model; distinct role. |
| keep | fast-general | Sub-second tier; smallest fast general. |
| keep | code-review | Structured-output specialist; benchmark caps it at 64K for tps. |
| keep | code-mid | Code-14B without thinking; gap filler between FIM and review. |
| keep | general | 35B MoE; 35 tps at 128K per max-ctx benchmark. |
| keep | writing | Sole writing-tuned model. |
| keep | reasoning | Primary reasoning, 5.3× faster than phi4 at similar quality. |
| keep | reasoning-deep | Niche: depth over latency, worth the 15-min wait on hard problems. |
| **remove** | **capable (qwen3:14b)** | Outclassed: `reasoning` covers thinking workloads, `instruct` covers no-think general 14B, `code-mid` covers no-think code. Already flagged for deprecation in `benchmarks/2026-05-25-roster-additions/report.md`. Removing frees 9.3 GB of installed weights. |
| keep | efficient | Primary 20B-class; 6.8× faster than capable-large per 2026-05-23 bench. |
| keep | capable-large | Reserved for gpt-oss's reasoning-channel CoT. Distinct from `efficient`. |
| keep | vision | Same backing model as `general`; alias kept distinct for trace separation in Langfuse (explicit design choice, called out in config comment). |
| keep | instruct | Instruction-tuned 14B without thinking; distinct from `code-mid` (general vs code). |
| keep | tiny-reason | Tiniest reasoning model; held at 117 tps in max-ctx bench. Cheap to keep at 731 MB. |

## Notes for follow-up

- If `capable` is removed, the Ollama tag `qwen3:14b` becomes orphaned and can be pulled out via `ollama rm qwen3:14b` (frees 9.3 GB).
- `mistral-small:24b` (~14 GB) was deferred in the 2026-05-25 run for disk reasons. Removing `qwen3:14b` would free enough headroom to revisit that pull.
- Four 14B-class dense models still remain after removing `capable` (reasoning, reasoning-deep, code-mid, instruct). All hit ~11 tps median on this host, but each fills a distinct functional role (think-channel-primary, think-channel-deep, code-no-think, general-no-think).
