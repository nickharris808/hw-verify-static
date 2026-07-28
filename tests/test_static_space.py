"""Tests for the static hw-verify Space.

This Space vendors two things it does not own: `cone.py`, copied from `ctbench`,
and `fixtures.json`, extracted from the ctbench manifest. Vendored copies rot. The
load-bearing tests here are the two that compare them byte-for-byte against
upstream, so a change to ctbench that is not mirrored here fails loudly instead of
silently serving a stale analyzer to the public.

The metadata tests exist because a real deploy failed on them: the Hub rejects a
`short_description` longer than 60 characters, and the CLI reported that as an
unrelated HTTP 402.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
OSS = ROOT.parent
sys.path.insert(0, str(ROOT))

# the vendored copy, imported the way the browser does
import cone


@pytest.fixture(scope="module")
def fixtures() -> dict:
    return json.loads((ROOT / "fixtures.json").read_text())


@pytest.fixture(scope="module")
def html() -> str:
    return (ROOT / "index.html").read_text()


@pytest.fixture(scope="module")
def card() -> str:
    return (ROOT / "README.md").read_text()


# ---------------------------------------------------------------------------
# The vendored copies must not drift from upstream.
# ---------------------------------------------------------------------------

def test_vendored_cone_matches_ctbench_exactly():
    """A stale analyzer served to the public is worse than no demo."""
    upstream = OSS / "ctbench" / "ctbench" / "cone.py"
    assert upstream.is_file(), "ctbench source not found alongside this Space"
    assert (ROOT / "cone.py").read_text() == upstream.read_text(), (
        "space-static/cone.py has drifted from ctbench/ctbench/cone.py — re-vendor it"
    )


def test_vendored_fixtures_match_the_ctbench_manifest(fixtures):
    manifest = json.loads(
        (OSS / "ctbench" / "ctbench" / "fixtures" / "manifest.json").read_text()
    )
    scored = {e["file"]: e for e in manifest["scored"]}
    assert set(fixtures) == set(scored), "vendored fixture set differs from the manifest"

    fx_dir = OSS / "ctbench" / "ctbench" / "fixtures"
    for name, f in fixtures.items():
        e = scored[name]
        assert f["source"] == (fx_dir / name).read_text(), f"{name}: stale source"
        assert f["observation"] == e["observation"], name
        assert f["secrets"] == e["secrets"], name
        assert f["expected"] == e["expected"], name


# ---------------------------------------------------------------------------
# The demo actually works — this is what a visitor sees.
# ---------------------------------------------------------------------------

def test_every_fixture_gets_the_expected_verdict(fixtures):
    """Replicates exactly what 'Run all 18' executes inside Pyodide."""
    wrong = []
    for name, f in sorted(fixtures.items()):
        v = cone.analyse(f["source"], f["observation"], list(f["secrets"]))
        got = "CONSTANT_TIME" if v.constant_time else "LEAKY"
        if got != f["expected"]:
            wrong.append(f"{name}: got {got}, expected {f['expected']}")
    assert not wrong, "\n".join(wrong)


def test_the_corpus_is_18_scored_fixtures(fixtures):
    assert len(fixtures) == 18


def test_matched_pairs_are_separated(fixtures):
    """A demo that cannot separate a pair demonstrates nothing."""
    pairs: dict[str, dict[str, str]] = {}
    for f in fixtures.values():
        if f.get("pair") and f.get("role") in ("positive", "negative"):
            v = cone.analyse(f["source"], f["observation"], list(f["secrets"]))
            pairs.setdefault(f["pair"], {})[f["role"]] = (
                "CONSTANT_TIME" if v.constant_time else "LEAKY"
            )
    assert len(pairs) == 8
    for pair, d in pairs.items():
        assert d["positive"] == "CONSTANT_TIME", pair
        assert d["negative"] == "LEAKY", pair


def test_out_of_remit_control_is_not_flagged(fixtures):
    ctrl = [n for n, f in fixtures.items() if f.get("role") == "out_of_remit"]
    assert ctrl == ["barrett_buggy.v"]
    f = fixtures["barrett_buggy.v"]
    v = cone.analyse(f["source"], f["observation"], list(f["secrets"]))
    assert v.constant_time, "the out-of-remit control must not be flagged"


def test_leaky_fixtures_name_their_reaching_secrets(fixtures):
    for name, f in fixtures.items():
        if f["expected"] != "LEAKY":
            continue
        v = cone.analyse(f["source"], f["observation"], list(f["secrets"]))
        assert v.reaching, f"{name}: LEAKY but named no reaching secret"


# ---------------------------------------------------------------------------
# The page wiring.
# ---------------------------------------------------------------------------

def test_page_fetches_exactly_the_files_we_ship(html):
    for asset in ("cone.py", "fixtures.json"):
        assert f'fetch("{asset}")' in html, f"index.html never fetches {asset}"
        assert (ROOT / asset).is_file(), f"{asset} is referenced but not shipped"


def test_page_loads_pyodide_from_a_pinned_version(html):
    m = re.search(r"pyodide/v(\d+\.\d+\.\d+)/full/pyodide\.js", html)
    assert m, "Pyodide is not loaded from a version-pinned CDN URL"


def test_page_states_the_scope_and_the_commercial_boundary(html):
    for phrase in ("completion timing", "over-approximates", "never inferred",
                   "commercial", "never receives"):
        assert phrase in html, f"index.html omits {phrase!r}"


def test_page_links_to_every_sibling_project(html):
    for repo in ("ctbench", "patchproof", "ct-mask", "hw-verify-mcp", "ct-audit-action"):
        assert f"github.com/nickharris808/{repo}" in html, repo
    assert "huggingface.co/datasets/nickh007/hw-verify" in html


def test_page_claims_no_upload_and_makes_no_network_call_for_analysis(html):
    assert "Nothing is uploaded" in html
    # the only fetches are our own two local assets, plus the pinned Pyodide CDN
    fetches = re.findall(r'fetch\("([^"]+)"\)', html)
    assert sorted(fetches) == ["cone.py", "fixtures.json"], fetches


# ---------------------------------------------------------------------------
# Hub metadata — a real deploy failed on these.
# ---------------------------------------------------------------------------

def test_card_has_valid_space_front_matter(card):
    assert card.startswith("---\n")
    front = card[4:].split("\n---\n", 1)[0]
    for key in ("title:", "sdk: static", "app_file: index.html", "license:"):
        assert key in front, key
    # the card must declare BOTH licences it actually ships under
    assert "apache-2.0" in front and "cc-by-4.0" in front, (
        "frontmatter must declare Apache-2.0 (code) and CC-BY-4.0 (inlined Verilog)"
    )


def test_short_description_is_within_the_hub_limit(card):
    """The Hub rejects >60 chars; the CLI reports that as an unrelated HTTP 402."""
    front = card[4:].split("\n---\n", 1)[0]
    m = re.search(r"^short_description:\s*(.+)$", front, re.M)
    assert m, "no short_description in the Space card"
    assert len(m.group(1).strip()) <= 60, (
        f"short_description is {len(m.group(1).strip())} chars; the Hub limit is 60"
    )


def test_card_declares_the_static_sdk(card):
    """A Gradio SDK here would need HF PRO and fail to deploy."""
    front = card[4:].split("\n---\n", 1)[0]
    assert re.search(r"^sdk:\s*static$", front, re.M)


def test_licence_file_ships():
    lic = (ROOT / "LICENSE").read_text()
    assert "Apache License" in lic and "Version 2.0" in lic


# ---------------------------------------------------------------------------
# Licensing of what is actually bundled.
# ---------------------------------------------------------------------------

ISC_FIXTURES = frozenset({
    "pcpi_div.v", "pcpi_mul.v", "pcpi_div_wiped.v", "pcpi_div_halfwipe.v",
})


def test_no_isc_fixture_is_bundled(fixtures):
    """This Space carries only the scored 18; the picorv32 derivatives are unscored.

    If that ever changes, the ISC notice has to travel with them.
    """
    assert not (set(fixtures) & ISC_FIXTURES), (
        "an ISC-licensed picorv32 derivative is now bundled — ship its notice"
    )


def test_fixture_licence_notice_ships_and_is_accurate(card):
    notice = (ROOT / "LICENSE-FIXTURES").read_text()
    assert "CC-BY-4.0" in notice, "the inlined Verilog is CC-BY-4.0 and must say so"
    assert "Apache" in notice, "index.html and cone.py are Apache-2.0"
    # it must state plainly that the ISC files are NOT here, not merely omit them
    assert "None of those four ship in this Space" in notice
    assert "LICENSE-FIXTURES" in card, "the card must point at the notice"


def test_card_does_not_overclaim_isc_content(card):
    """Claiming ISC content we do not ship misstates the terms as badly as omitting it."""
    body = card.split("\n---\n", 1)[1]
    i = body.find("## Licence")
    assert i != -1
    lic = body[i:]
    assert "not bundled here" in lic, "the card must say the ISC fixtures are absent"
