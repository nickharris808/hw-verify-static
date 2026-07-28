---
title: hw-verify constant-time checker
emoji: 🔒
colorFrom: purple
colorTo: indigo
sdk: static
app_file: index.html
pinned: false
license: apache-2.0
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

**Paste Verilog, get a formal verdict with the leaking signals named — not a guess.**

This Space runs the **real analyzer**: the same `ctbench` cone-of-influence checker you can
install from [GitHub](https://github.com/nickharris808/ctbench), compiled to WebAssembly via
Pyodide and executed **in your browser**. Nothing is uploaded; nothing leaves the page.

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

## Scope

Verdicts cover **completion timing** against declared secrets — not power, EM, cache, or
microarchitectural channels. The parser handles a synthesisable Verilog-2001 subset.

<!-- portfolio:start -->
## Part of the hw-verify toolkit

| Project | What it does |
|---|---|
| [`ctbench`](https://github.com/nickharris808/ctbench) | Matched-pair constant-time RTL benchmark + leaderboard |
| [`patchproof`](https://github.com/nickharris808/patchproof) | Prove a bounds-check fix eliminates *every* violating input |
| [`ct-mask`](https://github.com/nickharris808/ct-mask) | First-order masking verification by two certificates |
| [`hw-verify-mcp`](https://github.com/nickharris808/hw-verify-mcp) | MCP server — all three checkers, for AI agents |
| [`ct-audit-action`](https://github.com/nickharris808/ct-audit-action) | GitHub Action — fail a PR on a leaky completion signal |
| [`hw-verify` dataset](https://huggingface.co/datasets/nickh007/hw-verify) | 49 records, 3 splits, byte-reproducible from these tools |

**The commercial boundary.** Proving a property to a third party who never receives the
design — a verdict bound to a commitment of a design that stays hidden — is a different
problem and a commercial one. It is not in any of these packages.
<!-- portfolio:end -->

## Licence

Apache-2.0. The bundled RTL fixtures are CC-BY-4.0, except four picorv32 derivatives which
remain under the upstream ISC licence — see the
[ctbench repository](https://github.com/nickharris808/ctbench) for full attribution.
