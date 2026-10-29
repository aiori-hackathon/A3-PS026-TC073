"""Flask server exposing the AT URI engine via JSON API + HTML pages."""
from flask import Flask, render_template, request, jsonify, send_file
from io import BytesIO
import json

from engine.parser import parse_at_uri, reconstruct, STRATEGIES
from engine.analyzer import analyze_percent_encoding, analyze_unicode, detect_conflicts
from engine.runner import run_single, run_corpus
from engine.ml_model import predict_conflict
from engine.corpus import load_corpus
from reports import build_json_report, build_csv_report, build_html_report

app = Flask(__name__)


# ---------- HTML pages ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/simulator")
def simulator():
    return render_template("simulator.html", strategies=STRATEGIES)

@app.route("/compare")
def compare():
    return render_template("compare.html", strategies=STRATEGIES)

@app.route("/batch")
def batch():
    return render_template("batch.html", strategies=STRATEGIES)

@app.route("/library")
def library():
    return render_template("library.html")

@app.route("/conflicts")
def conflicts_page():
    return render_template("conflicts.html")

@app.route("/roundtrip")
def roundtrip_page():
    return render_template("roundtrip.html", strategies=STRATEGIES)

@app.route("/encoding")
def encoding_page():
    return render_template("encoding.html")

@app.route("/reports")
def reports_page():
    return render_template("reports.html")

@app.route("/docs")
def docs_page():
    return render_template("docs.html", strategies=STRATEGIES)


# ---------- JSON API ----------
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "strategies": STRATEGIES})

@app.route("/api/ml-predict", methods=["POST"])
def api_ml_predict():
    data = request.get_json(force=True, silent=True) or {}
    uri = (data.get("uri") or "").strip()
    if not uri:
        return jsonify({"error": "URI is required"}), 400
    result = predict_conflict(uri)
    return jsonify(result)

@app.route("/api/validate", methods=["POST"])
def api_validate():
    data = request.get_json(force=True, silent=True) or {}
    uri = (data.get("uri") or "").strip()
    strategy = data.get("strategy", "standard")
    if strategy not in STRATEGIES:
        return jsonify({"error": f"unknown strategy: {strategy}"}), 400
    result = parse_at_uri(uri, strategy)
    return jsonify({
        "result": result.to_dict(),
        "reconstructed": reconstruct(result),
    })

@app.route("/api/compare", methods=["POST"])
def api_compare():
    data = request.get_json(force=True, silent=True) or {}
    uri = (data.get("uri") or "").strip()
    return jsonify(detect_conflicts(uri))

@app.route("/api/roundtrip", methods=["POST"])
def api_roundtrip():
    data = request.get_json(force=True, silent=True) or {}
    uri = (data.get("uri") or "").strip()
    strategy = data.get("strategy", "standard")
    result = parse_at_uri(uri, strategy)
    recon = reconstruct(result)
    return jsonify({
        "original": uri,
        "reconstructed": recon,
        "exact_match": uri == recon,
        "parsed": result.to_dict(),
    })

@app.route("/api/encoding", methods=["POST"])
def api_encoding():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    return jsonify({
        "percent": analyze_percent_encoding(text),
        "unicode": analyze_unicode(text),
    })

@app.route("/api/batch", methods=["POST"])
def api_batch():
    data = request.get_json(force=True, silent=True) or {}
    uris = data.get("uris") or []
    if isinstance(uris, str):
        uris = [line.strip() for line in uris.splitlines() if line.strip()]
    results = [run_single(u) for u in uris]
    total = len(results)
    conflicts = sum(1 for r in results if r["conflicts"])
    roundtrip_failures = sum(
        1 for r in results
        if r["reconstructed"].get("standard") != r["uri"]
    )
    return jsonify({
        "summary": {
            "total": total,
            "with_conflicts": conflicts,
            "roundtrip_failures": roundtrip_failures,
        },
        "results": results,
    })

@app.route("/api/corpus")
def api_corpus():
    return jsonify({"cases": load_corpus()})

@app.route("/api/run-corpus")
def api_run_corpus():
    return jsonify(run_corpus())

@app.route("/api/report/<fmt>")
def api_report(fmt):
    report = run_corpus()
    if fmt == "json":
        payload = build_json_report(report)
        return send_file(BytesIO(payload.encode("utf-8")),
                         mimetype="application/json",
                         as_attachment=True,
                         download_name="at-uri-report.json")
    if fmt == "csv":
        payload = build_csv_report(report)
        return send_file(BytesIO(payload.encode("utf-8")),
                         mimetype="text/csv",
                         as_attachment=True,
                         download_name="at-uri-report.csv")
    if fmt == "html":
        payload = build_html_report(report)
        return send_file(BytesIO(payload.encode("utf-8")),
                         mimetype="text/html",
                         as_attachment=True,
                         download_name="at-uri-report.html")
    return jsonify({"error": "unknown format"}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)