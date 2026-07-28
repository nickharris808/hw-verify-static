---
title: hw-verify constant-time checker
emoji: 🔒
colorFrom: purple
colorTo: indigo
sdk: static
app_file: index.html
pinned: false
license:
- apache-2.0
- cc-by-4.0
short_description: Constant-time Verilog checker, in your browser
tags:
  - hardware
  - verilog
  - constant-time
  - side-channel
  - formal-verification
  - security
  - pyodide
---

# hw-verify — constant-time checker in your browser

**Paste Verilog, get a formal verdict with the leaking signals named — not a guess. No install, no upload.**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Runs in](https://img.shields.io/badge/runs%20in-your%20browser-9d7cff.svg)](https://huggingface.co/spaces/nickh007/hw-verify)
[![Engine](https://img.shields.io/badge/engine-Pyodide%20WASM-orange.svg)](https://pyodide.org)
[![Fixtures](https://img.shields.io/badge/benchmark-18%2F18-brightgreen.svg)](https://github.com/nickharris808/ctbench)

## Why this exists

Nobody installs a formal verification tool to find out whether it is worth installing.
This is the thirty-second version — and it is not a mock-up: it runs the **same analyzer**
that ships in `ctbench`, compiled to WebAssembly, on your machine.

This Space runs the **real analyzer**: the same `ctbench` cone-of-influence checker you can
install from [GitHub](https://github.com/nickharris808/ctbench), compiled to WebAssembly via
Pyodide and executed **in your browser**. Nothing is uploaded; nothing leaves the page.

## Run it locally

No build step — it is three static files and a CDN script tag:

```bash
git clone https://github.com/nickharris808/hw-verify-static.git && cd hw-verify-static
python -m http.server 8000        # then open http://127.0.0.1:8000
```

```console
$ curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/index.html
200
```

## Try it in 30 seconds

1. The page opens with a deliberately leaky tag comparator already loaded. Press **Check**.
2. Pick `ct_cmp.v` from the fixture dropdown, press **Load**, then **Check**. Same interface,
   opposite verdict — that is the point of a matched pair.
3. Press **Run all 18** to score the whole bundled benchmark.

## Why the verdicts are trustworthy

The checker takes the fan-in cone of the completion signal — **including every enclosing
`if`/`case` guard condition**, which is the part naive implementations miss — and intersects
it with the secrets you declare. Secrets are **never inferred**: guessing which inputs are
sensitive produces confident verdicts about the wrong property.

It **over-approximates**, so `CONSTANT_TIME` is conservative and `LEAKY` names the reaching
signals so you can confirm rather than take it on faith.

## Example output

Press **Check** on the leaky comparator that loads by default:

```console
❌ LEAKY

`done` depends on `x`, `y`. The cycle it asserts on is a function of secret data,
so timing reveals secret-dependent behaviour.

Fix: make the completion condition a function of a data-oblivious counter and drop
the early-exit branch, then re-run.
```

Load `ct_cmp.v` — same module interface, opposite verdict:

```console
✅ CONSTANT_TIME

No declared secret reaches `done`. Its fan-in cone spans 6 signals and contains
none of `x`, `y`.
```

Press **Run all 18** and the whole bundled benchmark scores in the browser:

```console
18/18 correct on the bundled benchmark
```

## Scope

Verdicts cover **completion timing** against declared secrets — not power, EM, cache, or
microarchitectural channels. The parser handles a synthesisable Verilog-2001 subset.

<!-- portfolio:start -->
## Part of the hw-verify toolkit

Five open tools, a dataset, and a browser demo for proving security properties of hardware and bounds checks. They share one boundary: **everything open analyses a design you disclose in full.**

| Project | What it does |
|---|---|
| **▶ [Live demo](https://huggingface.co/spaces/nickh007/hw-verify)** | Try the constant-time checker in your browser — runs the real analyzer via Pyodide |
| [`ctbench`](https://github.com/nickharris808/ctbench) | Matched-pair constant-time RTL benchmark + leaderboard |
| [`patchproof`](https://github.com/nickharris808/patchproof) | Prove a bounds-check fix eliminates *every* violating input |
| [`ct-mask`](https://github.com/nickharris808/ct-mask) | First-order masking verification by two certificates |
| [`hw-verify-mcp`](https://github.com/nickharris808/hw-verify-mcp) | MCP server — all three checkers, callable by AI agents |
| [`ct-audit-action`](https://github.com/nickharris808/ct-audit-action) | GitHub Action — fail a PR on a leaky completion signal |
| [`hw-verify` dataset](https://huggingface.co/datasets/nickh007/hw-verify) | 49 records, 3 splits, byte-reproducible from these tools |
| [`hw-verify-static`](https://github.com/nickharris808/hw-verify-static) · [`hw-verify-space`](https://github.com/nickharris808/hw-verify-space) | Source for the live demo (Pyodide) and a fuller Gradio build |

**The commercial boundary.** Proving a property to a third party who never receives the design — a verdict bound to a commitment of a design that stays hidden — is a different problem and a commercial one. It is not in any of these packages.
<!-- portfolio:end -->

## Licence

Two licences, because this Space ships two kinds of material — see
[`LICENSE-FIXTURES`](LICENSE-FIXTURES) for the full text:

- **Apache-2.0** — `index.html` and `cone.py` (the latter vendored verbatim from
  [ctbench](https://github.com/nickharris808/ctbench)). See [`LICENSE`](LICENSE).
- **CC-BY-4.0** — the 18 Verilog sources inlined in `fixtures.json`.

The four picorv32-derived fixtures that remain under the upstream ISC licence are
**not bundled here** — they are unscored in ctbench, so this demo does not carry them.
