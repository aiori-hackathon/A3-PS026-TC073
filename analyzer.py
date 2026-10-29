"""Percent-encoding, Unicode, and cross-strategy conflict analysis."""
import re
import unicodedata
from urllib.parse import unquote
from .parser import parse_at_uri, reconstruct, STRATEGIES

_HEX = re.compile(r'^[0-9a-fA-F]{2}$')


def analyze_percent_encoding(text: str) -> dict:
    valid, issues = [], []
    i = 0
    while i < len(text):
        if text[i] == "%":
            if i + 2 < len(text) and _HEX.match(text[i+1:i+3]):
                valid.append(text[i:i+3])
                i += 3
                continue
            issues.append({"pos": i, "snippet": text[i:i+3], "reason": "malformed escape"})
        i += 1
    decoded = unquote(text)
    return {
        "original": text,
        "decoded": decoded,
        "valid_escapes": valid,
        "issues": issues,
        "changed": decoded != text,
        "encoded_delimiters": [e for e in valid if e.lower() in ("%2f", "%3a", "%23")],
    }


def analyze_unicode(text: str) -> dict:
    nfc = unicodedata.normalize("NFC", text)
    nfd = unicodedata.normalize("NFD", text)
    return {
        "original": text,
        "nfc": nfc,
        "nfd": nfd,
        "nfc_equals_original": nfc == text,
        "nfd_equals_original": nfd == text,
        "nfc_equals_nfd": nfc == nfd,
        "original_codepoints": [f"U+{ord(c):04X}" for c in text],
        "nfd_codepoints": [f"U+{ord(c):04X}" for c in nfd],
        "original_bytes_utf8": text.encode("utf-8").hex(),
        "nfc_bytes_utf8": nfc.encode("utf-8").hex(),
    }


def detect_conflicts(uri: str) -> dict:
    """Parse under every strategy and report real disagreements."""
    results = {s: parse_at_uri(uri, s) for s in STRATEGIES}
    conflicts = []

    def disagree(field):
        vals = {getattr(r, field) for r in results.values()}
        return len(vals) > 1

    if disagree("valid"):
        conflicts.append({
            "category": "validation_disagreement",
            "component": "valid",
            "severity": "high",
            "detail": {s: r.valid for s, r in results.items()},
            "explanation": "Some parsers accept this URI, others reject it.",
            "suggestion": "Compare authority regex matches; check DID colon handling.",
        })

    for field in ("authority", "collection", "rkey"):
        if disagree(field):
            conflicts.append({
                "category": f"component_extraction_conflict",
                "component": field,
                "severity": "medium",
                "detail": {s: getattr(r, field) for s, r in results.items()},
                "explanation": f"Strategies extracted different values for {field}.",
                "suggestion": "Inspect path-splitting rules and NSID/rkey validation.",
            })

    for s, r in results.items():
        recon = reconstruct(r)
        if r.valid and recon != uri:
            conflicts.append({
                "category": "round_trip_mismatch",
                "component": "reconstruction",
                "severity": "high",
                "detail": {"strategy": s, "original": uri, "reconstructed": recon},
                "explanation": f"Strategy '{s}' produces a different URI on round-trip.",
                "suggestion": "Check whether encoding or normalization was silently applied.",
            })

    return {"uri": uri, "results": {s: r.to_dict() for s, r in results.items()}, "conflicts": conflicts}