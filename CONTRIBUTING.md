# Contributing to the hw-verify static Space

## `cone.py` is vendored — never edit it here

It is a byte-for-byte copy of `ctbench/ctbench/cone.py`, served to the browser through
Pyodide. Fix analyzer bugs upstream in `ctbench`, then re-vendor:

```bash
cp ../ctbench/ctbench/cone.py cone.py
python -c "import json,pathlib; ..."   # regenerate fixtures.json, see build notes below
pytest tests -q
```

`test_vendored_cone_matches_ctbench_exactly` fails the moment the copy drifts. A stale
analyzer served to the public is worse than no demo at all.

## `fixtures.json` is extracted, not authored

It carries the 18 scored fixtures from ctbench's manifest with their sources, observation
signals, declared secrets, and expected verdicts.
`test_vendored_fixtures_match_the_ctbench_manifest` compares every field against upstream.

## Keep the SDK static

`sdk: static` in the card is deliberate. A Gradio SDK needs an HF PRO subscription and
will not deploy on a free account — a test asserts the SDK line.

## `short_description` must be ≤ 60 characters

The Hub rejects longer ones, and the CLI reports that failure as an unrelated HTTP 402,
which costs an afternoon to diagnose. There is a test.

## Keep the scope and boundary text

The page states what the verdict covers (completion timing, over-approximate, declared
secrets) and where the commercial boundary sits. Tests assert both. They are the
difference between a visitor reading "CONSTANT_TIME" as "secure" and reading it as what it
actually says.

## No network calls beyond the two local assets

A test asserts the page fetches exactly `cone.py` and `fixtures.json` and nothing else.
The claim "nothing is uploaded" has to stay literally true.
