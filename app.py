# app.py
from flask import Flask, request, render_template_string
from pathlib import Path
from datetime import datetime
import json

from codec import run_full_pipeline

app = Flask(__name__)

# Where to save all runs
RUNS_DIR = Path("runs")


def make_run_dir() -> Path:
    """
    Create a unique run folder:
    runs/2025-12-12_20-15-30/
    """
    RUNS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = RUNS_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def save_part_outputs(run_dir: Path, original_text: str, interval: int, results: dict) -> None:
    """
    Create files for each project part exactly as separate artifacts.
    Also saves a HTML report preview (GUI snapshot).
    """
    # -------- Part 0 (input copy)
    write_file(run_dir / "Text.txt", original_text)

    # -------- Part 1: symbols + probabilities
    # Format: repr(symbol)\tprobability
    probs = results["probabilities"]
    part1_lines = ["# symbol\tprobability"]
    for sym, p in sorted(probs.items(), key=lambda kv: kv[0]):
        part1_lines.append(f"{repr(sym)}\t{p:.10f}")
    write_file(run_dir / "part1_symbols.txt", "\n".join(part1_lines))

    # -------- Support: Huffman codes table
    codes = results["codes"]
    codes_lines = ["# symbol\tcode"]
    for sym, code in sorted(codes.items(), key=lambda kv: kv[0]):
        codes_lines.append(f"{repr(sym)}\t{code}")
    write_file(run_dir / "huffman_codes.txt", "\n".join(codes_lines))

    # -------- Part 2: binary sequence after Huffman
    write_file(run_dir / "part2_bits.txt", results["encoded_bits"])

    # -------- Part 3: decoded text
    write_file(run_dir / "part3_decoded.txt", results["decoded_text"])

    # -------- Part 4: Hamming-coded bits + padding metadata
    write_file(run_dir / "part4_hamming_bits.txt", results["hamming_bits"])
    write_file(run_dir / "part4_pad.txt", str(results["pad_bits"]))

    # -------- Part 5: corrupted bits (errors injected)
    write_file(run_dir / "part5_corrupted_bits.txt", results["corrupted_bits"])

    # -------- Part 6: recovered bits (must equal Part 2 bits)
    write_file(run_dir / "part6_recovered_bits.txt", results["recovered_bits"])

    # -------- Extra: a machine-readable summary
    summary = {
        "error_interval": interval,
        "text_length_symbols": results["text_length"],
        "encoded_length_bits": len(results["encoded_bits"]),
        "hamming_length_bits": len(results["hamming_bits"]),
        "pad_bits": results["pad_bits"],
        "huffman_ok": results["huffman_ok"],
        "hamming_ok": results["hamming_ok"],
    }
    write_file(run_dir / "summary.json", json.dumps(summary, indent=2))

    # -------- Extra: HTML report (GUI preview snapshot)
    # We reuse the same HTML template and render it into a file.
    probs_sample = sorted(probs.items(), key=lambda kv: -kv[1])[:10]
    original_preview = original_text[:300]
    decoded_preview = results["decoded_text"][:300]

    report_html = render_template_string(
        HTML_TEMPLATE,
        results=results,
        probs_sample=probs_sample,
        original_preview=original_preview,
        decoded_preview=decoded_preview,
        last_run_path=str(run_dir),
        interval_value=interval,
        embed_mode=True,  # tells template it's being saved as report
    )
    write_file(run_dir / "report.html", report_html)


HTML_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Information Theory Studio</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- Google Font -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

  <!-- Bootstrap 5 -->
  <link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    rel="stylesheet"
    crossorigin="anonymous"
  >

  <!-- Bootstrap Icons -->
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css"
  >

  <style>
    :root {
      --bg-gradient: radial-gradient(circle at top left, #1a237e 0%, #0f172a 35%, #020617 80%);
      --accent: #38bdf8;
      --text-main: #e5e7eb;
      --text-muted: #9ca3af;
    }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
      background-image: var(--bg-gradient);
      color: var(--text-main);
    }
    .page-shell {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem 1rem;
      position: relative;
      overflow: hidden;
    }
    .blob {
      position: absolute;
      border-radius: 999px;
      filter: blur(48px);
      opacity: 0.38;
      pointer-events: none;
    }
    .blob-1 { width: 380px; height: 380px; background: #38bdf8; top: -120px; left: -60px; }
    .blob-2 { width: 420px; height: 420px; background: #a855f7; bottom: -140px; right: -120px; }

    .app-card {
      position: relative;
      max-width: 1200px;
      width: 100%;
      border-radius: 1.5rem;
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.90), rgba(15, 23, 42, 0.96));
      border: 1px solid rgba(148, 163, 184, 0.30);
      box-shadow: 0 24px 80px rgba(15, 23, 42, 0.90);
      backdrop-filter: blur(20px);
      padding: 2rem 1.5rem;
    }
    @media (min-width: 992px) { .app-card { padding: 2.5rem 2.5rem 2.75rem; } }

    .pill-soft {
      background: rgba(15, 23, 42, 0.70);
      border: 1px solid rgba(148, 163, 184, 0.40);
      color: var(--accent);
      font-size: 0.75rem;
      padding: 0.4rem 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
    }
    .pill-status {
      padding: 0.35rem 0.9rem;
      font-size: 0.75rem;
      border-radius: 999px;
      border: 1px solid rgba(148, 163, 184, 0.40);
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }
    .pill-status.ok { border-color: rgba(52, 211, 153, 0.50); color: #6ee7b7; }
    .pill-status.bad { border-color: rgba(248, 113, 113, 0.50); color: #fecaca; }

    .glass-input {
      background-color: rgba(15, 23, 42, 0.75);
      border-radius: 0.75rem;
      border: 1px solid rgba(148, 163, 184, 0.50);
      color: var(--text-main);
    }
    .glass-input:focus {
      background-color: rgba(15, 23, 42, 0.95);
      border-color: var(--accent);
      box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.45);
      color: var(--text-main);
    }

    .btn-primary-modern {
      background: linear-gradient(135deg, #38bdf8, #4f46e5);
      border: none;
      border-radius: 999px;
      padding-inline: 1.75rem;
      padding-block: 0.75rem;
      font-weight: 600;
      box-shadow: 0 12px 30px rgba(37, 99, 235, 0.70);
    }
    .btn-primary-modern:hover { background: linear-gradient(135deg, #0ea5e9, #4338ca); transform: translateY(-1px); }

    .section-title {
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--text-muted);
      margin-bottom: 0.6rem;
    }
    .section-title span {
      border-bottom: 1px solid rgba(148, 163, 184, 0.40);
      padding-bottom: 0.25rem;
      display: inline-block;
    }

    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
      background: radial-gradient(circle at top left, #020617 0, #020617 55%, #0b1120 100%);
      border-radius: 0.9rem;
      padding: 0.9rem 1rem;
      font-size: 0.78rem;
      line-height: 1.4;
      color: #e5e7eb;
      border: 1px solid rgba(15, 23, 42, 0.80);
    }

    .summary-list .list-group-item {
      background: transparent;
      border-color: rgba(148, 163, 184, 0.22);
      color: var(--text-main);
      padding-left: 0;
      padding-right: 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.85rem;
    }
    .summary-list .label { color: var(--text-muted); }
    .summary-list .value { font-weight: 600; }

    .divider-soft {
      border-top: 1px solid rgba(148, 163, 184, 0.35);
      margin: 1rem 0 1.5rem;
    }

    .hint {
      color: var(--text-muted);
      font-size: 0.85rem;
    }
  </style>
</head>

<body>
<div class="page-shell">
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>

  <div class="app-card">
    <!-- Header -->
    <div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-4">
      <div>
        <div class="pill-soft mb-2">
          <i class="bi bi-broadcast-pin"></i>
          Information Theory Lab
        </div>
        <h1 class="h3 mb-1 fw-semibold">Information Theory Project Studio</h1>
        <p class="mb-0" style="color: var(--text-muted); font-size: 0.9rem;">
          Huffman source coding + Hamming(7,4) channel coding with saved artifacts per run.
        </p>
      </div>

      <div class="text-end">
        {% if results %}
          <div class="mb-2">
            <span class="pill-status {{ 'ok' if results.huffman_ok else 'bad' }}">
              <i class="bi {{ 'bi-check-circle' if results.huffman_ok else 'bi-x-circle' }}"></i>
              Huffman OK: {{ results.huffman_ok }}
            </span>
          </div>
          <div>
            <span class="pill-status {{ 'ok' if results.hamming_ok else 'bad' }}">
              <i class="bi {{ 'bi-check-circle' if results.hamming_ok else 'bi-x-circle' }}"></i>
              Hamming OK: {{ results.hamming_ok }}
            </span>
          </div>
        {% else %}
          <div class="hint mt-2">Upload a .txt file to run Parts 1–6.</div>
        {% endif %}
      </div>
    </div>

    {% if not embed_mode %}
    <!-- Controls (only show in live GUI, not in saved report) -->
    <form method="post" enctype="multipart/form-data" class="mb-4">
      <div class="row g-3 align-items-end">
        <div class="col-md-6">
          <label class="form-label fw-semibold small mb-1">Source Text File (Text.txt)</label>
          <input type="file" name="textfile" accept=".txt" class="form-control glass-input" required>
          <div class="form-text" style="color: var(--text-muted);">
            Any UTF-8 .txt file can be used as the message source.
          </div>
        </div>
        <div class="col-md-3">
          <label class="form-label fw-semibold small mb-1">Error Interval (Part 5)</label>
          <input type="number" name="interval" value="{{ interval_value or 50 }}" min="1" class="form-control glass-input">
          <div class="form-text" style="color: var(--text-muted);">
            Flip one bit every N bits in the Hamming stream.
          </div>
        </div>
        <div class="col-md-3 text-md-end">
          <button type="submit" class="btn btn-primary-modern mt-2 mt-md-0">
            <i class="bi bi-play-fill me-1"></i>Run Pipeline
          </button>
        </div>
      </div>
    </form>
    {% endif %}

    {% if results %}
    <div class="divider-soft"></div>

    {% if last_run_path %}
      <div class="mb-3 hint">
        Saved run folder: <span style="color: var(--accent); font-weight: 600;">{{ last_run_path }}</span><br>
        Saved preview report: <span style="color: var(--accent); font-weight: 600;">report.html</span>
      </div>
    {% endif %}

    <div class="row g-4">
      <div class="col-lg-4">
        <div class="mb-4">
          <div class="section-title"><span>Overview</span></div>
          <ul class="list-group list-group-flush summary-list">
            <li class="list-group-item">
              <span class="label">Original length (symbols)</span>
              <span class="value">{{ results.text_length }}</span>
            </li>
            <li class="list-group-item">
              <span class="label">Encoded length (bits, Part 2)</span>
              <span class="value">{{ results.encoded_bits|length }}</span>
            </li>
            <li class="list-group-item">
              <span class="label">Hamming length (bits, Part 4)</span>
              <span class="value">{{ results.hamming_bits|length }}</span>
            </li>
            <li class="list-group-item">
              <span class="label">Pad bits (Hamming)</span>
              <span class="value">{{ results.pad_bits }}</span>
            </li>
          </ul>
        </div>

        <div>
          <div class="section-title"><span>Part 1 – Probabilities</span></div>
          <div class="hint mb-2">Top 10 symbols by probability:</div>
          <pre>
{% for sym, p in probs_sample %}
{{ sym | tojson }} : {{ "%.6f"|format(p) }}
{% endfor %}
          </pre>
        </div>
      </div>

      <div class="col-lg-8">
        <div class="mb-4">
          <div class="section-title"><span>Bitstreams</span></div>

          <div class="mb-3">
            <div class="hint mb-1">Part 2 – Huffman encoded bits (first 200 bits)</div>
            <pre>{{ results.encoded_bits[:200] }}{% if results.encoded_bits|length > 200 %}...{% endif %}</pre>
          </div>

          <div class="mb-3">
            <div class="hint mb-1">Part 4 – Hamming(7,4) encoded bits (first 200 bits)</div>
            <pre>{{ results.hamming_bits[:200] }}{% if results.hamming_bits|length > 200 %}...{% endif %}</pre>
          </div>

          <div class="mb-3">
            <div class="hint mb-1">Part 5 – Corrupted bits (first 200 bits)</div>
            <pre>{{ results.corrupted_bits[:200] }}{% if results.corrupted_bits|length > 200 %}...{% endif %}</pre>
          </div>

          <div>
            <div class="hint mb-1">Part 6 – Recovered bits (first 200 bits)</div>
            <pre>{{ results.recovered_bits[:200] }}{% if results.recovered_bits|length > 200 %}...{% endif %}</pre>
          </div>
        </div>

        <div>
          <div class="section-title"><span>Part 3 – Text Round Trip</span></div>
          <div class="row g-3">
            <div class="col-md-6">
              <div class="hint mb-1">Original text (first 300 chars)</div>
              <pre>{{ original_preview }}</pre>
            </div>
            <div class="col-md-6">
              <div class="hint mb-1">Decoded via Huffman (first 300 chars)</div>
              <pre>{{ decoded_preview }}</pre>
            </div>
          </div>
        </div>

      </div>
    </div>
    {% endif %}
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(
            HTML_TEMPLATE,
            results=None,
            last_run_path=None,
            interval_value=50,
            embed_mode=False,
        )

    file = request.files.get("textfile")
    if not file:
        return render_template_string(
            HTML_TEMPLATE,
            results=None,
            last_run_path=None,
            interval_value=50,
            embed_mode=False,
        )

    text = file.read().decode("utf-8", errors="ignore")

    try:
        interval = int(request.form.get("interval", "50"))
        if interval <= 0:
            interval = 50
    except ValueError:
        interval = 50

    results = run_full_pipeline(text, error_interval=interval)

    # Save outputs to a new run folder
    run_dir = make_run_dir()
    save_part_outputs(run_dir, text, interval, results)

    # For on-page display
    probs_sample = sorted(results["probabilities"].items(), key=lambda kv: -kv[1])[:10]
    original_preview = text[:300]
    decoded_preview = results["decoded_text"][:300]

    return render_template_string(
        HTML_TEMPLATE,
        results=results,
        probs_sample=probs_sample,
        original_preview=original_preview,
        decoded_preview=decoded_preview,
        last_run_path=str(run_dir),
        interval_value=interval,
        embed_mode=False,
    )


if __name__ == "__main__":
    app.run(debug=True)
