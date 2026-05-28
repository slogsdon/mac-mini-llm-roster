# Alias verification + roster dedup — 2026-05-26

Two-part deliverable: (1) verify the three changed/new alias routes work end-to-end, (2) audit the full roster for dedup/orphans. Audit is complete; live benchmark + proxy smoke are still in flight at the time of writing — see "Status" below for what's confirmed vs pending.

## Status at write time

| Check | State | Notes |
|---|---|---|
| `litellm/config.yaml` parsed cleanly after commit `0f9f807` | ✅ | All 14 aliases present. |
| LiteLLM container loaded the new config | ✅ after restart | Container was running pre-commit config (started 2026-05-24, commit landed after). `docker compose restart litellm` picked up the new aliases. Pre-restart, `reasoning-deep` and `code-mid` returned HTTP 400 "Invalid model name"; pre-restart `reasoning` was still phi4 (response leaked "I'm Phi" into the content channel). |
| `/v1/models` lists `reasoning`, `reasoning-deep`, `code-mid` | ✅ | All 14 aliases enumerated by the proxy. |
| Proxy smoke (`/v1/chat/completions` with each new alias name) | ✅ all three routed; ✅ content read confirmed for all three; ⚠ `reasoning-deep` thinking leaks into `content` (see Proxy smoke) | `code-mid` and `reasoning` clean. `reasoning-deep` returned `content` containing `<think>...</think>ALIAS_OK` with empty `reasoning_content`, despite `think:true` in config — phi4 thinking is not being routed to `reasoning_content` via the proxy. Earlier "Invalid control character" was my shell-heredoc bug (unescaped `"` in reasoning_content), not a LiteLLM JSON issue. |
| Live benchmark (`roster_speed_test.py --only r1-reasoning,reasoning,code-mid`) | ✅ 24/24 prompts, 0 errors | Total wall 42.1 min. Fresh numbers in "Speed" section below; matches prior baseline. |
| Roster dedup audit | ✅ complete | See `audit.md` in this directory, summary table reproduced below. |

## Script alias → litellm alias mapping

`scripts/roster_speed_test.py` carries its own MODELS list that hasn't been updated for the 2026-05-25 alias rename. For this run I used `--only r1-reasoning,reasoning,code-mid` against the existing script entries — the backing models match what's now in production, but under stale script alias names:

| litellm/config.yaml alias | Script alias used (`--only`) | Backing model | Notes |
|---|---|---|---|
| `reasoning` | `r1-reasoning` | deepseek-r1:14b | Script `r1-reasoning` row already points at deepseek-r1; matches new production. |
| `reasoning-deep` | `reasoning` | phi4-reasoning:plus | Script's `reasoning` row still points at phi4; matches new production. |
| `code-mid` | `code-mid` | qwen2.5-coder:14b | Exact match. |

The script MODELS list is stale on other entries too (e.g. `general`→qwen3.5:9b-mlx which isn't installed) — out of scope for this task, but worth a cleanup pass.

## Speed: live benchmark (2026-05-26)

Run: `python3 scripts/roster_speed_test.py --only r1-reasoning,reasoning,code-mid --out benchmarks/2026-05-26-alias-verification/results.json`. Total wall: 42.1 min. All 24 prompts returned non-empty content, no errors.

| litellm alias | Backing model | Median tps | Min / max tps | Total wall (8 prompts) | Prompts with non-empty content | Errors |
|---|---|---|---|---|---|---|
| `reasoning-deep` | phi4-reasoning:plus | **8.6** | 8.4 / 8.9 | **1986 s** (~33 min) | 8/8 | 0 |
| `reasoning` | deepseek-r1:14b | **11.1** | 11.0 / 11.2 | **452 s** (~7.5 min) | 8/8 | 0 |
| `code-mid` | qwen2.5-coder:14b | **11.5** | 11.2 / 22.6 | **65 s** (~1.1 min) | 8/8 | 0 |

`reasoning` is **4.4× faster** total wall than `reasoning-deep` on the same prompts, holding the speed advantage the 2026-05-25 promotion was based on. `code-mid` finishes the same suite in **30× less wall time** than `reasoning-deep`, confirming its role as the no-thinking-tax code/general slot.

### Per-prompt wall-time (seconds)

| alias | fim | qa | json | math | write | code | trans | sum | total |
|---|---|---|---|---|---|---|---|---|---|
| reasoning-deep | 174 | 61 | 492 | 97 | 551 | 191 | 197 | 222 | 1986 |
| reasoning | 78 | 38 | 25 | 25 | 92 | 127 | 47 | 20 | 452 |
| code-mid | 16 | 0.5 | 2 | 17 | 4 | 19 | 2 | 4 | 65 |

### Per-prompt tps

| alias | fim | qa | json | math | write | code | trans | sum |
|---|---|---|---|---|---|---|---|---|
| reasoning-deep | 8.8 | 8.9 | 8.5 | 8.8 | 8.4 | 8.6 | 8.6 | 8.5 |
| reasoning | 11.1 | 11.2 | 11.2 | 11.2 | 11.1 | 11.0 | 11.1 | 11.2 |
| code-mid | 11.3 | 22.6 | 11.8 | 11.3 | 11.5 | 11.2 | 11.9 | 11.5 |

`reasoning-deep` is the only one paying a meaningful thinking-channel tax (think chars range 1.3k–19.5k per prompt). `reasoning` emits 0.4k–4.7k think chars per prompt. `code-mid` emits 0 think chars on all prompts (as expected — no thinking-capable model in this slot).

### Math-reason spot-check (correct answer: 42)

| alias | content head |
|---|---|
| reasoning-deep | `Start with 47 apples.\n1. After selling 23 apples: 47 – …` ✓ |
| reasoning | `**Solution:**\n\nLet's break down the problem step by …` ✓ |
| code-mid | `To find out how many apples are left in the store after …` ✓ |

All three reach the correct answer. Comparison to the 2026-05-25 baseline is within noise (≤5% delta on median tps), confirming the prior characterization holds.

## Proxy smoke

Goal: confirm each new alias name routes correctly via LiteLLM at `:4000` and returns non-empty content.

Procedure: `POST /v1/chat/completions` with `model: <alias>` and the prompt `"Reply with exactly: ALIAS_OK"`; check HTTP 200 + non-empty `choices[0].message.content`.

### Pre-restart (failure case, documented for the record)

- `reasoning-deep` and `code-mid` → HTTP 400 "Invalid model name" (aliases not yet loaded).
- `reasoning` → HTTP 200 but content was phi4's `<think>` monolog (e.g. "I'm Phi and I must produce a reply that is exactly ALIAS_OK…") — proves the running container still held the pre-`0f9f807` config.

### Post-restart

| Alias | HTTP | content channel | reasoning_content channel | Verdict |
|---|---|---|---|---|
| `code-mid` | 200 | `'ALIAS_OK'` | (empty, as expected — `think:false` enforced upstream of this alias's backing model) | ✅ clean |
| `reasoning` | 200 | `'ALIAS_OK'` | populated (85-token internal monolog: "Okay, the user sent…") | ✅ clean; think correctly separated |
| `reasoning-deep` | 200 | `'…</think>ALIAS_OK'` — raw `<think>...</think>` tags leak into content; final answer present at the end | empty | ⚠ routed, but think-channel separation broken — see follow-up below |

All three aliases route correctly. The proxy routing question is fully resolved. The smoke surfaced a separate behavior gap on `reasoning-deep`:

**`reasoning-deep` think-channel leak (follow-up)**

The proxy returned `content: "I must produce reply exactly \"ALIAS_OK\". But instructions from the user: \"Reply with exactly: ALIAS_OK\" I'…</think>ALIAS_OK"` with `reasoning_content` empty, despite `litellm/config.yaml:99` setting `think: true` with a comment that the phi4-reasoning Modelfile was rebuilt to declare the `thinking` capability so this would route correctly.

Possible causes (not investigated in this task):

1. The Modelfile rebuild on the proxy host didn't actually land — `ollama show phi4-reasoning:plus --modelfile | grep -i thinking` would confirm.
2. LiteLLM's `ollama_chat` provider isn't forwarding `think: true` to Ollama for this model — could be verified by hitting Ollama directly with `think: true` and checking whether the response splits into `message.thinking`. (Note the prior benchmark on `phi4-reasoning:plus` did get clean thinking-field separation against Ollama direct, so the model side is probably fine.)

Recommend filing as a separate issue — the alias works (content is returned, including a parseable final answer), but UX for callers expecting `reasoning_content` is broken.

**Note on `reasoning` (deepseek-r1) vs the config comment.** The config comment at `litellm/config.yaml:86-89` states that deepseek-r1's `<think>` tags emit inline in `content` rather than splitting to `reasoning_content`. The actual smoke response shows the opposite — `content` was clean `'ALIAS_OK'` and `reasoning_content` was populated with the internal monolog. The comment appears stale; updating it should be queued behind verifying this is reproducible (one smoke call is not a guarantee).

## Roster dedup audit (complete)

Full table in `audit.md`. Summary:

- **14 aliases, 13 distinct Ollama tags, 0 orphans.** Every installed model is referenced by at least one alias.
- **One removal recommendation: `capable` (qwen3:14b)** — outclassed by the trio that landed in the 2026-05-25 additions:
  - Thinking workloads → `reasoning` (deepseek-r1, 5.3× faster than phi4 at similar quality)
  - General 14B no-think → `instruct` (ministral-3:14b)
  - Code 14B no-think → `code-mid` (qwen2.5-coder:14b)

  This was already flagged for deprecation as a follow-up in `benchmarks/2026-05-25-roster-additions/report.md`. Removing the alias and pulling `qwen3:14b` from Ollama frees 9.3 GB, which would give enough disk headroom to pull `mistral-small:24b` (~14 GB, the other deferred item from the additions run).

- **`vision` and `general` share `qwen3.6:35b-mlx`** — keep both; the split is intentional for Langfuse trace separation and called out in the config comment at `litellm/config.yaml:125-133`.

### Keep / remove / no-alias table

| Status | Alias | Backing model | Reason |
|---|---|---|---|
| keep | code-autocomplete | qwen2.5-coder:3b-base | Only FIM-base; distinct role. |
| keep | fast-general | gemma4:e4b-mlx | Sub-second tier; `think:false` forced. |
| keep | code-review | granite4.1:8b | Structured-output specialist. |
| keep | code-mid | qwen2.5-coder:14b | Code-14B without thinking tax. |
| keep | general | qwen3.6:35b-mlx | Top-tier MoE; 35 tps at 128K. |
| keep | writing | mistral-nemo:12b | Sole writing-tuned. |
| keep | reasoning | deepseek-r1:14b | Primary thinking, 5.3× faster than phi4. |
| keep | reasoning-deep | phi4-reasoning:plus | Depth-over-latency niche. |
| **remove** | **capable** | **qwen3:14b** | **Outclassed by `reasoning` / `instruct` / `code-mid`. Already flagged for deprecation in the 2026-05-25 report.** |
| keep | efficient | lfm2:24b | Primary 20B-class; 6.8× faster than capable-large. |
| keep | capable-large | gpt-oss:20b | Reserved for gpt-oss's reasoning-channel CoT. |
| keep | vision | qwen3.6:35b-mlx | Shared with `general`; split for trace separation (intentional). |
| keep | instruct | ministral-3:14b | Instruction-tuned 14B without thinking. |
| keep | tiny-reason | lfm2.5-thinking:1.2b | 731 MB; cheap to keep, 117 tps at 128K. |
| n/a | — | (no orphans) | All 13 installed Ollama models have ≥1 alias. |

## Follow-ups

1. **Investigate `reasoning-deep` think-channel leak.** phi4-reasoning's think tags are landing in `content` with empty `reasoning_content` via the proxy, contrary to the config comment. Likely candidates: Modelfile rebuild didn't take, or LiteLLM isn't forwarding `think: true` to Ollama. See "Proxy smoke" above for details.
3. **Re-check the config comment on `reasoning` (deepseek-r1).** Smoke shows the opposite of what the comment claims — `reasoning_content` IS populated. Verify the model file declares the thinking capability and the comment is stale (then update it).
4. Decide on `capable` removal (separate change; not part of this audit).
5. Out of scope but worth queuing: refresh `scripts/roster_speed_test.py` MODELS list so script alias names match production (`reasoning`→deepseek-r1, add `reasoning-deep`, drop `r1-reasoning` and the qwen3.5/qwen3-vl/flash entries that aren't installed).
