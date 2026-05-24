#!/usr/bin/env python3
"""Speed-test the FINAL roster at MAXED-OUT context windows.

Companion to roster_speed_test.py. Same 8 prompts, same process, same
metrics capture. Differences from the parent script:

  - MODELS list reflects the post-2026-05-23 final roster (11 models): no
    flash, no qwen3.5:9b-mlx, no qwen3-vl:30b. qwen3.6:35b-mlx serves both
    `general` and `vision` aliases.
  - num_ctx is set to each model's `ollama_max` from models.yaml (the
    model card's training-time max), not the production default. Exception:
    writing (mistral-nemo:12b) is capped at 128K — its 1M ceiling is
    unrealistic on a 32 GB host (KV cache alone would exceed RAM).
  - num_predict is unchanged from production (Pi maxTokens) — only the
    context window is maxed.

Expect cold-load tax to be much higher: a 262K context on a 35B MoE
allocates many GB of KV cache up front. Some loads may fail; that's data.

Output: /tmp/roster_speed_maxctx_results.json by default. Override with
`--out PATH`. Filter to a subset with `--only alias1,alias2`.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

OLLAMA_URL = "http://localhost:11434"

# (alias, ollama_tag, think_override, num_ctx, num_predict)
# Final 11-model roster as of 2026-05-23. think_override and num_predict
# match the per-alias production defaults from the delta benchmark.
# num_ctx = ollama_max from models.yaml (the model card's training max).
# Exception: writing is capped at 131K — its 1M ceiling is unrealistic on
# 32 GB. Several entries (general, vision, instruct at 262K; capable-large
# at 131K) WILL push KV cache into double-digit GB and may fail to load.
# That failure is itself a signal worth recording.
MODELS = [
    ("code-autocomplete", "qwen2.5-coder:3b-base",   None,   32_768,  8_192),
    ("fast-general",      "gemma4:e4b-mlx",          False, 131_072, 16_384),
    ("code-review",       "granite4.1:8b",           None,  131_072, 16_384),
    ("general",           "qwen3.6:35b-mlx",         True,  262_144, 16_384),
    ("writing",           "mistral-nemo:12b",        None,  131_072, 32_768),
    ("reasoning",         "phi4-reasoning:plus",     True,   32_768, 16_384),
    ("capable",           "qwen3:14b",               True,   40_960, 16_384),
    ("efficient",         "lfm2:24b",                None,   32_768, 16_384),
    ("capable-large",     "gpt-oss:20b",             True,  131_072, 16_384),
    ("vision",            "qwen3.6:35b-mlx",         True,  262_144, 16_384),
    ("instruct",          "ministral-3:14b",         None,  262_144, 16_384),
    ("tiny-reason",       "lfm2.5-thinking:1.2b",    True,  128_000,  8_192),
]

PROMPTS = [
    ("fim-code",
     "Complete this Python function:\n"
     "def fibonacci(n):\n"
     "    if n <= 1:\n"
     "        return n\n"
     "    return "),
    ("quick-qa",
     "What is the capital of France? Reply with just the name."),
    ("structured-json",
     "List 3 common Python anti-patterns as a JSON array of strings. "
     "Reply with only the JSON, no prose."),
    ("math-reason",
     "A store has 47 apples. They sell 23, then receive a shipment of 18. "
     "How many apples are there now? Show your work briefly."),
    ("writing-blurb",
     "Write a 60-word product description for a wireless ergonomic keyboard."),
    ("code-task",
     "Write a Python function `kth_largest(arr, k)` that returns the kth "
     "largest element in an unsorted list. Include a brief docstring."),
    ("multilingual",
     "Translate to French: 'I went to the market and bought fresh bread.'"),
    ("summarize",
     "Summarize in one sentence: 'The quick brown fox jumps over the lazy "
     "dog. The cat sits on the mat. Dogs are mammals that have been "
     "domesticated for thousands of years.'"),
]

PER_CALL_TIMEOUT_S = 900 # generous; large ctx allocation + thinking can take minutes
KEEP_ALIVE = "5m"        # keep model warm across all its prompts

RESULTS_PATH = "/tmp/roster_speed_maxctx_results.json"


def call(model_tag: str, prompt: str, think: bool | None, num_ctx: int, num_predict: int) -> tuple[dict | None, float, str | None]:
    body = {
        "model": model_tag,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"num_predict": num_predict, "num_ctx": num_ctx},
        "keep_alive": KEEP_ALIVE,
    }
    if think is not None:
        body["think"] = think
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=PER_CALL_TIMEOUT_S) as resp:
            data = json.loads(resp.read())
        wall = time.monotonic() - t0
        return data, wall, None
    except urllib.error.HTTPError as e:
        wall = time.monotonic() - t0
        try:
            err = json.loads(e.read()).get("error", str(e))
        except Exception:
            err = str(e)
        return None, wall, f"HTTP {e.code}: {err[:120]}"
    except Exception as e:  # noqa: BLE001
        wall = time.monotonic() - t0
        return None, wall, f"{type(e).__name__}: {e}"[:160]


def warmup(model_tag: str, think: bool | None, num_ctx: int) -> tuple[float, bool]:
    """Tiny call to force model load AT THE TARGET num_ctx, so the KV cache
    allocation is paid up front (and so the subsequent prompts hit a warm
    runner that already owns the full context window)."""
    body = {
        "model": model_tag,
        "messages": [{"role": "user", "content": "hi"}],
        "stream": False,
        "options": {"num_predict": 2, "num_ctx": num_ctx},
        "keep_alive": KEEP_ALIVE,
    }
    if think is not None:
        body["think"] = think
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=PER_CALL_TIMEOUT_S) as resp:
            resp.read()
        return time.monotonic() - t0, True
    except Exception as e:  # noqa: BLE001
        print(f"  warmup failed: {e}", flush=True)
        return time.monotonic() - t0, False


def main() -> int:
    # Optional CLI filter: `--only alias1,alias2,...` runs just the named subset
    # (useful for delta benchmarks after a model change without re-running the
    # full ~107-min matrix).
    only: set[str] = set()
    out_path = RESULTS_PATH
    args = list(sys.argv[1:])
    while args:
        a = args.pop(0)
        if a == "--only" and args:
            only = {x.strip() for x in args.pop(0).split(",") if x.strip()}
        elif a == "--out" and args:
            out_path = args.pop(0)
        else:
            print(f"unknown arg: {a}", file=sys.stderr)
            return 2
    selected = [m for m in MODELS if not only or m[0] in only]
    if only and len(selected) != len(only):
        missing = only - {m[0] for m in selected}
        print(f"unknown aliases: {missing}", file=sys.stderr)
        return 2
    if only:
        print(f"Running delta subset: {sorted(m[0] for m in selected)}", flush=True)

    results: list[dict] = []
    start = time.monotonic()
    for alias, tag, supports_think, num_ctx, num_predict in selected:
        print(f"\n=== {alias} ({tag})  num_ctx={num_ctx//1024}K  num_predict={num_predict} ===", flush=True)
        warmup_s, ok = warmup(tag, supports_think, num_ctx)
        print(f"  warmup: {warmup_s:.1f}s {'ok' if ok else 'FAIL'}", flush=True)
        if not ok:
            for pid, _ in PROMPTS:
                results.append({
                    "alias": alias, "tag": tag, "prompt": pid,
                    "num_ctx": num_ctx, "num_predict": num_predict,
                    "wall_s": None, "eval_tps": None,
                    "eval_count": 0, "thinking_chars": 0,
                    "content": "", "error": "warmup failed",
                })
            continue
        for pid, ptext in PROMPTS:
            data, wall, err = call(tag, ptext, supports_think, num_ctx, num_predict)
            if err:
                print(f"  {pid:<18} ERR  {err[:80]}", flush=True)
                results.append({
                    "alias": alias, "tag": tag, "prompt": pid,
                    "num_ctx": num_ctx, "num_predict": num_predict,
                    "wall_s": round(wall, 2), "eval_tps": None,
                    "eval_count": 0, "thinking_chars": 0,
                    "content": "", "error": err,
                })
                continue
            msg = data.get("message", {})
            content = (msg.get("content") or "").strip()
            thinking = (msg.get("thinking") or "").strip()
            eval_count = data.get("eval_count", 0) or 0
            eval_ns = data.get("eval_duration", 0) or 0
            tps = (eval_count / (eval_ns / 1e9)) if eval_ns else None
            tps_str = f"{tps:6.1f} tps" if tps else "    -- tps"
            think_marker = f" [+{len(thinking)}c think]" if thinking else ""
            print(f"  {pid:<18} {wall:6.1f}s  {tps_str}  ec={eval_count:4d}{think_marker}  {content[:50]!r}",
                  flush=True)
            results.append({
                "alias": alias, "tag": tag, "prompt": pid,
                "num_ctx": num_ctx, "num_predict": num_predict,
                "wall_s": round(wall, 2),
                "eval_tps": round(tps, 1) if tps else None,
                "eval_count": eval_count,
                "thinking_chars": len(thinking),
                "content": content[:300],
                "error": None,
            })
        Path(out_path).write_text(json.dumps(results, indent=2))
    elapsed = time.monotonic() - start
    print(f"\n\nTotal wall time: {elapsed/60:.1f} minutes ({elapsed:.0f}s)", flush=True)
    print(f"Saved: {out_path}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
