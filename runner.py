"""Runs the corpus through the real engine and returns actual results."""
from .parser import parse_at_uri, reconstruct, STRATEGIES
from .analyzer import detect_conflicts
from .corpus import load_corpus

def run_single(uri: str, strategies=None) -> dict:
    strategies = strategies or STRATEGIES
    results = {s: parse_at_uri(uri, s).to_dict() for s in strategies}
    recon = {s: reconstruct(parse_at_uri(uri, s)) for s in strategies}
    return {
        "uri": uri,
        "results": results,
        "reconstructed": recon,
        "conflicts": detect_conflicts(uri)["conflicts"],
    }

def _classify_status(case, outcomes):
    """Compare actual against annotated expectation."""
    expect = case["expect"]
    actual_valid = outcomes["results"]["standard"]["valid"]
    if expect == "valid" and actual_valid:
        return "pass"
    if expect == "invalid" and not actual_valid:
        return "pass"
    if expect == "review":
        return "review"
    return "fail"

def run_corpus(corpus=None) -> dict:
    corpus = corpus if corpus is not None else load_corpus()
    cases = []
    pass_c = fail_c = review_c = 0
    for case in corpus:
        outcome = run_single(case["input"])
        status = _classify_status(case, outcome)
        if status == "pass": pass_c += 1
        elif status == "fail": fail_c += 1
        else: review_c += 1
        cases.append({
            "id": case["id"],
            "input": case["input"],
            "category": case["category"],
            "expect": case["expect"],
            "purpose": case["purpose"],
            "status": status,
            "actual": outcome,
        })
    return {
        "summary": {
            "total": len(cases),
            "passed": pass_c,
            "failed": fail_c,
            "review": review_c,
            "pass_rate": round(pass_c / len(cases), 3) if cases else 0,
        },
        "cases": cases,
    }