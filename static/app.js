// Vanilla JS — one file, one job per page, all endpoints real.

const $ = (id) => document.getElementById(id);

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function badge(status) {
  return `<span class="badge ${status}">${status}</span>`;
}

function renderConflicts(container, conflicts) {
  if (!conflicts || conflicts.length === 0) {
    container.innerHTML = `<p class="muted">No conflicts detected.</p>`;
    return;
  }
  container.innerHTML = conflicts.map(c => `
    <div class="conflict-item ${c.severity}">
      <strong>${c.category}</strong> · ${c.component} · severity ${c.severity}
      <p>${c.explanation}</p>
      <p class="muted">Suggestion: ${c.suggestion}</p>
      <pre>${JSON.stringify(c.detail, null, 2)}</pre>
    </div>`).join("");
}

// ---------- Dashboard ----------
async function initDashboard() {
  const report = await getJSON("/api/run-corpus");
  const s = report.summary;
  $("s-total").textContent = s.total;
  $("s-pass").textContent = s.passed;
  $("s-fail").textContent = s.failed;
  $("s-review").textContent = s.review;
  $("s-rate").textContent = (s.pass_rate * 100).toFixed(1) + "%";

  const conflictCount = report.cases.filter(c => c.actual.conflicts.length > 0).length;
  $("conflict-summary").innerHTML = `
    <p>${conflictCount} of ${s.total} cases produced at least one
    cross-strategy conflict.</p>`;

  const tbody = $("recent-table").querySelector("tbody");
  tbody.innerHTML = report.cases.slice(0, 15).map(c => `
    <tr>
      <td><code>${c.id}</code></td>
      <td><code>${c.input}</code></td>
      <td>${c.category}</td>
      <td>${c.expect}</td>
      <td>${badge(c.status)}</td>
    </tr>`).join("");
}

// ---------- Simulator ----------
function initSimulator() {
  $("btn-validate").onclick = async () => {
    const uri = $("sim-uri").value.trim();
    const strategy = $("sim-strategy").value;
    const out = await postJSON("/api/validate", { uri, strategy });
    $("sim-output").classList.remove("hidden");
    $("sim-result").textContent = JSON.stringify(out, null, 2);
  };
  $("btn-roundtrip").onclick = async () => {
    const uri = $("sim-uri").value.trim();
    const strategy = $("sim-strategy").value;
    const out = await postJSON("/api/roundtrip", { uri, strategy });
    $("sim-output").classList.remove("hidden");
    $("sim-result").textContent = JSON.stringify(out, null, 2);
  };
  $("btn-reset").onclick = () => {
    $("sim-uri").value = "";
    $("sim-output").classList.add("hidden");
  };
}

// ---------- Compare ----------
function initCompare() {
  $("btn-compare").onclick = async () => {
    const uri = $("cmp-uri").value.trim();
    const out = await postJSON("/api/compare", { uri });
    $("cmp-output").classList.remove("hidden");
    const tbody = $("cmp-table").querySelector("tbody");
    tbody.innerHTML = Object.entries(out.results).map(([s, r]) => `
      <tr>
        <td><strong>${s}</strong></td>
        <td>${r.valid ? '<span class="ok">yes</span>' : '<span class="err">no</span>'}</td>
        <td><code>${r.authority ?? ""}</code></td>
        <td><code>${r.collection ?? ""}</code></td>
        <td><code>${r.rkey ?? ""}</code></td>
        <td><code>${out.reconstructed[s] ?? ""}</code></td>
        <td>${(r.errors || []).join("; ")}</td>
      </tr>`).join("");
    renderConflicts($("cmp-conflicts"), out.conflicts);
  };
}

// ---------- Batch ----------
function initBatch() {
  $("batch-file").onchange = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    const text = await f.text();
    $("batch-input").value = text;
  };
  $("btn-batch-clear").onclick = () => {
    $("batch-input").value = "";
    $("batch-summary").classList.add("hidden");
    $("batch-table").classList.add("hidden");
  };
  $("btn-batch").onclick = async () => {
    const uris = $("batch-input").value
      .split("\n").map(x => x.trim()).filter(Boolean);
    if (uris.length === 0) return;
    const out = await postJSON("/api/batch", { uris });
    $("batch-summary").classList.remove("hidden");
    $("b-total").textContent = out.summary.total;
    $("b-conflicts").textContent = out.summary.with_conflicts;
    $("b-rt").textContent = out.summary.roundtrip_failures;
    const tbody = $("batch-table").querySelector("tbody");
    tbody.innerHTML = out.results.map(r => {
      const std = r.results.standard;
      return `<tr>
        <td><code>${r.uri}</code></td>
        <td>${std.valid ? '<span class="ok">yes</span>' : '<span class="err">no</span>'}</td>
        <td><code>${std.authority ?? ""}</code></td>
        <td>${r.conflicts.length}</td>
        <td><code>${r.reconstructed.standard ?? ""}</code></td>
      </tr>`;
    }).join("");
    $("batch-table").classList.remove("hidden");
  };
}

// ---------- Library ----------
let libraryData = [];

function renderLibrary() {
  const q = $("lib-search").value.toLowerCase();
  const cat = $("lib-category").value;
  const status = $("lib-status").value;
  const filtered = libraryData.filter(c => {
    const hay = `${c.id} ${c.input} ${c.purpose}`.toLowerCase();
    if (q && !hay.includes(q)) return false;
    if (cat && c.category !== cat) return false;
    if (status && c.status !== status) return false;
    return true;
  });
  $("lib-count").textContent = `${filtered.length} of ${libraryData.length} cases shown`;
  $("lib-table").querySelector("tbody").innerHTML = filtered.map(c => `
    <tr>
      <td><code>${c.id}</code></td>
      <td><code>${c.input}</code></td>
      <td>${c.category}</td>
      <td>${c.expect}</td>
      <td>${badge(c.status)}</td>
      <td>${c.actual.results.standard.valid ? '<span class="ok">yes</span>' : '<span class="err">no</span>'}</td>
      <td>${c.purpose}</td>
    </tr>`).join("");
}

async function initLibrary() {
  $("btn-lib-run").onclick = async () => {
    const report = await getJSON("/api/run-corpus");
    libraryData = report.cases;
    renderLibrary();
  };
  $("lib-search").oninput = renderLibrary;
  $("lib-category").onchange = renderLibrary;
  $("lib-status").onchange = renderLibrary;
  await $("btn-lib-run").click();
}

// ---------- Conflicts ----------
function initConflicts() {
  $("btn-conflict").onclick = async () => {
    const uri = $("cf-uri").value.trim();
    const out = await postJSON("/api/compare", { uri });
    $("cf-output").classList.remove("hidden");
    renderConflicts($("cf-list"), out.conflicts);
  };
}

// ---------- Round-trip ----------
function initRoundTrip() {
  $("btn-rt").onclick = async () => {
    const uri = $("rt-uri").value.trim();
    const strategy = $("rt-strategy").value;
    const out = await postJSON("/api/roundtrip", { uri, strategy });
    $("rt-output").classList.remove("hidden");
    $("rt-original").textContent = out.original;
    $("rt-reconstructed").textContent = out.reconstructed;
    $("rt-match").textContent = out.exact_match
      ? "yes — no information loss"
      : "no — reconstruction differs";
    $("rt-match").className = out.exact_match ? "ok" : "err";
    $("rt-parsed").textContent = JSON.stringify(out.parsed, null, 2);
  };
}

// ---------- Encoding ----------
function initEncoding() {
  $("btn-enc").onclick = async () => {
    const text = $("enc-text").value;
    const out = await postJSON("/api/encoding", { text });
    $("enc-output").classList.remove("hidden");
    $("enc-percent").textContent = JSON.stringify(out.percent, null, 2);
    $("enc-unicode").textContent = JSON.stringify(out.unicode, null, 2);
  };
}

// ---------- Reports preview ----------
async function initReports() {
  const report = await getJSON("/api/run-corpus");
  $("report-preview").textContent = JSON.stringify(report.summary, null, 2);
}

// ---------- Router ----------
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  try {
    if (path === "/dashboard") initDashboard();
    else if (path === "/simulator") initSimulator();
    else if (path === "/compare") initCompare();
    else if (path === "/batch") initBatch();
    else if (path === "/library") initLibrary();
    else if (path === "/conflicts") initConflicts();
    else if (path === "/roundtrip") initRoundTrip();
    else if (path === "/encoding") initEncoding();
    else if (path === "/reports") initReports();
  } catch (err) {
    console.error(err);
  }
});
