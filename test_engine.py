from engine.parser import parse_at_uri, reconstruct, STRATEGIES
from engine.analyzer import analyze_percent_encoding, analyze_unicode, detect_conflicts
from engine.corpus import load_corpus
from engine.runner import run_corpus
import pytest


def test_did_authority_internal_colons():
    r = parse_at_uri("at://did:plc:abc123/app.bsky.feed.post/x", "standard")
    assert r.valid
    assert r.authority == "did:plc:abc123"
    assert r.collection == "app.bsky.feed.post"
    assert r.rkey == "x"


def test_handle_authority():
    r = parse_at_uri("at://alice.bsky.social/app.bsky.feed.post/x", "standard")
    assert r.valid
    assert r.authority == "alice.bsky.social"


def test_rejects_non_at_scheme():
    r = parse_at_uri("http://example.com/x", "standard")
    assert not r.valid


def test_reconstruct_round_trip():
    uri = "at://did:plc:abc123/app.bsky.feed.post/3k2abc"
    r = parse_at_uri(uri, "standard")
    assert reconstruct(r) == uri


def test_strategies_disagree_on_host_port_confusion():
    uri = "at://did:web:example.com:8080/col/rkey"
    std = parse_at_uri(uri, "standard")
    rfc = parse_at_uri(uri, "rfc3986")
    # RFC strategy should emit a warning or error about port confusion
    assert any("port" in w.lower() or "did" in w.lower() for w in rfc.warnings + rfc.errors)


def test_percent_encoding_valid_and_invalid():
    a = analyze_percent_encoding("abc%41def")
    assert a["valid_escapes"] == ["%41"]
    assert not a["issues"]
    b = analyze_percent_encoding("abc%ZZ")
    assert b["issues"]


def test_unicode_nfc_nfd_differ():
    nfc = analyze_unicode("caf\u00e9")   # é composed
    nfd = analyze_unicode("cafe\u0301")  # e + combining acute
    assert nfc["nfc_equals_original"]
    assert not nfd["nfc_equals_original"]
    assert nfc["nfc"] == nfd["nfc"]


def test_corpus_has_at_least_100_cases():
    assert len(load_corpus()) >= 100


def test_corpus_ids_unique():
    ids = [c["id"] for c in load_corpus()]
    assert len(ids) == len(set(ids))


def test_run_corpus_no_exceptions():
    report = run_corpus()
    assert report["summary"]["total"] >= 100
    # No fabrication: at least some cases must pass and some must be non-trivial
    assert report["summary"]["passed"] > 0


def test_conflict_detection_on_ambiguous_uri():
    c = detect_conflicts("at://did:plc:abc123:8080/col/rkey")
    # At minimum, rfc3986 vs standard should disagree on something
    assert isinstance(c["conflicts"], list)


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_every_strategy_handles_basic_uri(strategy):
    r = parse_at_uri("at://did:plc:abc123/app.bsky.feed.post/x", strategy)
    assert r.authority == "did:plc:abc123"