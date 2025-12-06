# app.py
from flask import Flask, request, render_template_string
from codec import run_full_pipeline

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Information Theory Studio</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <!-- Google Font -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

  <!-- Bootstrap 5 (for layout + components) -->
  <link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    rel="stylesheet"
    integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
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
      --card-glass: rgba(15, 23, 42, 0.78);
      --accent: #38bdf8;
      --accent-soft: rgba(56, 189, 248, 0.2);
      --accent-strong: rgba(56, 189, 248, 0.45);
      --text-main: #e5e7eb;
      --text-muted: #9ca3af;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
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

    /* Floating blobs for background */
    .blob {
      position: absolute;
      border-radius: 999px;
      filter: blur(48px);
      opacity: 0.4;
      pointer-events: none;
    }
    .blob-1 {
      width: 380px;
      height: 380px;
      background: #38bdf8;
      top: -120px;
      left: -60px;
    }
    .blob-2 {
      width: 420px;
      height: 420px;
      background: #a855f7;
      bottom: -140px;
      right: -120px;
    }

    .app-card {
      position: relative;
      max-width: 1200px;
      width: 100%;
      border-radius: 1.5rem;
      background: linear-gradient(
        135deg,
        rgba(15, 23, 42, 0.9),
        rgba(15, 23, 42, 0.96)
      );
      border: 1px solid rgba(148, 163, 184, 0.3);
      box-shadow:
        0 24px 80px rgba(15, 23, 42, 0.9),
        0 0 0 1px rgba(15, 23, 42, 0.7);
      backdrop-filter: blur(20px);
      padding: 2rem 1.5rem;
    }

    @media (min-width: 992px) {
      .app-card {
        padding: 2.5rem 2.5rem 2.75rem;
      }
    }

    .badge-pill {
      border-radius: 999px;
    }

    .pill-soft {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(148, 163, 184, 0.4);
      color: var(--accent);
      font-size: 0.75rem;
      padding: 0.4rem 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
    }

    .pill-status {
      padding: 0.35rem 0.9rem;
      font-size: 0.75rem;
      border-radius: 999px;
      border: 1px solid rgba(148, 163, 184, 0.4);
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
    }

    .pill-status.ok {
      border-color: rgba(52, 211, 153, 0.5);
      color: #6ee7b7;
    }

    .pill-status.bad {
      border-color: rgba(248, 113, 113, 0.5);
      color: #fecaca;
    }

    .pill-status i {
      font-size: 0.85rem;
    }

    .section-title {
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--text-muted);
      margin-bottom: 0.6rem;
    }

    .section-title span {
      border-bottom: 1px solid rgba(148, 163, 184, 0.4);
      padding-bottom: 0.25rem;
      display: inline-block;
    }

    .glass-input {
      background-color: rgba(15, 23, 42, 0.75);
      border-radius: 0.75rem;
      border: 1px solid rgba(148, 163, 184, 0.5);
      color: var(--text-main);
    }

    .glass-input:focus {
      background-color: rgba(15, 23, 42, 0.95);
      border-color: var(--accent);
      box-shadow: 0 0 0 1px var(--accent-strong);
      color: var(--text-main);
    }

    .btn-primary-modern {
      background: linear-gradient(135deg, #38bdf8, #4f46e5);
      border: none;
      border-radius: 999px;
      padding-inline: 1.75rem;
      padding-block: 0.75rem;
      font-weight: 600;
      box-shadow:
        0 12px 30px rgba(37, 99, 235, 0.7),
        0 0 0 1px rgba(56, 189, 248, 0.8);
    }

    .btn-primary-modern:hover {
      background: linear-gradient(135deg, #0ea5e9, #4338ca);
      transform: translateY(-1px);
      box-shadow:
        0 18px 40px rgba(37, 99, 235, 0.85),
        0 0 0 1px rgba(56, 189, 248, 0.9);
    }

    .btn-primary-modern:active {
      transform: translateY(0);
      box-shadow:
        0 10px 22px rgba(37, 99, 235, 0.7),
        0 0 0 1px rgba(56, 189, 248, 0.8);
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
      border: 1px solid rgba(15, 23, 42, 0.8);
      box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.8);
    }

    .code-label {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.78rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--text-muted);
    }

    .chip {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 0.3rem 0.7rem;
      border-radius: 999px;
      border: 1px solid rgba(148, 163, 184, 0.4);
      font-size: 0.75rem;
      color: var(--text-muted);
      gap: 0.35rem;
    }

    .chip-dot {
      width: 7px;
      height: 7px;
      border-radius: 999px;
      background: var(--accent);
      box-shadow: 0 0 12px rgba(56, 189, 248, 0.7);
    }

    .summary-list .list-group-item {
      background: transparent;
      border-color: rgba(30, 64, 175, 0.5);
      color: var(--text-main);
      padding-left: 0;
      padding-right: 0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.85rem;
    }

    .summary-list .label {
      color: var(--text-muted);
    }

    .summary-list .value {
      font-weight: 600;
    }

    .divider-soft {
      border-top: 1px solid rgba(148, 163, 184, 0.4);
      margin: 1rem 0 1.5rem;
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
          <i class="bi bi-broadcast-pin me-1"></i>
          Information Theory Lab
        </div>
        <h1 class="h3 mb-1 fw-semibold">Information Theory Project Studio</h1>
        <p class="mb-0" style="color: var(--text-muted); font-size: 0.9rem;">
          Visualize <span style="color: var(--accent);">Huffman</span> source coding and
          <span style="color: var(--accent);">Hamming(7,4)</span> channel coding on your own text.
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
          <div class="chip mt-1">
            <span class="chip-dot"></span>
            Ready to process
          </div>
        {% endif %}
      </div>
    </div>

    <!-- Controls -->
    <form method="post" enctype="multipart/form-data" class="mb-4">
      <div class="row g-3 align-items-end">
        <div class="col-md-6">
          <label class="form-label fw-semibold small mb-1">
            Source Text File <span style="color: var(--accent);">(Text.txt)</span>
          </label>
          <input
            type="file"
            name="textfile"
            accept=".txt"
            class="form-control glass-input"
            required
          >
          <div class="form-text" style="color: var(--text-muted);">
            Any UTF-8 .txt file can be used as the message source.
          </div>
        </div>
        <div class="col-md-3">
          <label class="form-label fw-semibold small mb-1">
            Error Interval (Part 5)
          </label>
          <input
            type="number"
            name="interval"
            value="50"
            min="1"
            class="form-control glass-input"
          >
          <div class="form-text" style="color: var(--text-muted);">
            Flip one bit every N bits in the Hamming code stream.
          </div>
        </div>
        <div class="col-md-3 text-md-end">
          <button type="submit" class="btn btn-primary-modern mt-2 mt-md-0">
            <i class="bi bi-play-fill me-1"></i>Run Pipeline
          </button>
        </div>
      </div>
    </form>

    {% if results %}
    <div class="divider-soft"></div>

    <div class="row g-4">
      <!-- Summary & Probabilities -->
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
          <div class="small mb-2" style="color: var(--text-muted);">
            Top 10 symbols by probability:
          </div>
          <pre>
{% for sym, p in probs_sample %}
{{ sym | tojson }} : {{ "%.6f"|format(p) }}
{% endfor %}
          </pre>
        </div>
      </div>

      <!-- Bitstreams & Text -->
      <div class="col-lg-8">
        <div class="mb-4">
          <div class="section-title"><span>Bitstreams</span></div>

          <div class="mb-3">
            <div class="code-label mb-1">
              Part 2 – Huffman encoded bits (first 200 bits)
            </div>
            <pre>{{ results.encoded_bits[:200] }}{% if results.encoded_bits|length > 200 %}...{% endif %}</pre>
          </div>

          <div class="mb-3">
            <div class="code-label mb-1">
              Part 4 – Hamming(7,4) encoded bits (first 200 bits)
            </div>
            <pre>{{ results.hamming_bits[:200] }}{% if results.hamming_bits|length > 200 %}...{% endif %}</pre>
          </div>

          <div class="mb-3">
            <div class="code-label mb-1">
              Part 5 – Corrupted bits (errors injected, first 200 bits)
            </div>
            <pre>{{ results.corrupted_bits[:200] }}{% if results.corrupted_bits|length > 200 %}...{% endif %}</pre>
          </div>

          <div>
            <div class="code-label mb-1">
              Part 6 – Recovered bits (first 200 bits)
            </div>
            <pre>{{ results.recovered_bits[:200] }}{% if results.recovered_bits|length > 200 %}...{% endif %}</pre>
          </div>
        </div>

        <div>
          <div class="section-title"><span>Part 3 – Text Round Trip</span></div>
          <div class="row g-3">
            <div class="col-md-6">
              <div class="small fw-semibold mb-1">Original text (first 300 chars)</div>
              <pre>{{ original_preview }}</pre>
            </div>
            <div class="col-md-6">
              <div class="small fw-semibold mb-1">Decoded via Huffman (first 300 chars)</div>
              <pre>{{ decoded_preview }}</pre>
            </div>
          </div>
        </div>

      </div>
    </div>
    {% endif %}
  </div>
</div>

<script
  src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
  integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
  crossorigin="anonymous">
</script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template_string(HTML_TEMPLATE, results=None)

    file = request.files.get("textfile")
    if not file:
        return render_template_string(HTML_TEMPLATE, results=None)

    text = file.read().decode("utf-8", errors="ignore")

    try:
        interval = int(request.form.get("interval", "50"))
        if interval <= 0:
            interval = 50
    except ValueError:
        interval = 50

    results = run_full_pipeline(text, error_interval=interval)

    probs = results["probabilities"]
    probs_sample = sorted(probs.items(), key=lambda kv: -kv[1])[:10]

    original_preview = text[:300]
    decoded_preview = results["decoded_text"][:300]

    return render_template_string(
        HTML_TEMPLATE,
        results=results,
        probs_sample=probs_sample,
        original_preview=original_preview,
        decoded_preview=decoded_preview,
    )


if __name__ == "__main__":
    app.run(debug=True)
