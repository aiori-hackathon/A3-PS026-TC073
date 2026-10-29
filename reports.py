"""Report builders: real data only, sourced from run_corpus()."""
import csv
import json
from io import StringIO


def build_json_report(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False)


def build_csv_report(report: dict) -> str:
    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "input", "category", "expect", "status", "standard_valid",
                "standard_authority", "standard_collection", "standard_rkey",
                "reconstructed_standard", "conflicts"])
    for c in report["cases"]:
        std = c["actual"]["results"]["standard"]
        recon = c["actual"]["reconstructed"]["standard"]
        w.writerow([
            c["id"], c["input"], c["category"], c["expect"], c["status"],
            std["valid"], std["authority"], std["collection"], std["rkey"],
            recon, len(c["actual"]["conflicts"]),
        ])
    return buf.getvalue()


def build_html_report(report: dict) -> str:
    s = report["summary"]
    rows = []
    for c in report["cases"]:
        std = c["actual"]["results"]["standard"]
        status_class = {"pass": "ok", "fail": "err", "review": "warn"}[c["status"]]
        rows.append(f"""
        <tr>
          <td><code>{c['id']}</code></td>
          <td><code>{_esc(c['input'])}</code></td>
          <td>{c['category']}</td>
          <td>{c['expect']}</td>
          <td class="{status_class}">{c['status']}</td>
          <td>{'yes' if std['valid'] else 'no'}</td>
          <td><code>{_esc(std['authority'] or '')}</code></td>
          <td>{_esc(c['purpose'])}</td>
        </tr>""")
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>AT URI Validator Report</title>
<style>
 body{{font-family:system-ui,sans-serif;max-width:1100px;margin:2em auto;padding:1em}}
 table{{border-collapse:collapse;width:100%;font-size:13px}}
 th,td{{border:1px solid #ddd;padding:6px;text-align:left}}
 .ok{{color:#0a7}} .err{{color:#c33}} .warn{{color:#b70}}
 code{{background:#f4f4f4;padding:1px 4px;border-radius:3px}}
</style></head><body>
<h1>AT URI Validator — Test Report</h1>
<p>Total {s['total']} · Passed {s['passed']} · Failed {s['failed']} ·
Review {s['review']} · Pass rate {s['pass_rate']*100:.1f}%</p>
<table>
<thead><tr><th>ID</th><th>Input</th><th>Category</th><th>Expected</th>
<th>Status</th><th>Valid</th><th>Authority</th><th>Purpose</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
</body></html>"""


def _esc(x: str) -> str:
    return (x.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))