# app.py
from flask import Flask, request, render_template_string
from codec import run_full_pipeline

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Information Theory Project – Demo</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <!-- Bootstrap 5 CSS -->
  <link
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    rel="stylesheet"
    integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
    crossorigin="anonymous"
  >
  <style>
    body {
      background: radial-gradient(circle at top left, #e3f2fd 0, #fafafa 40%, #f5f5f5 100%);
      min-height: 100vh;
    }
    .main-wrapper {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem 1rem;
    }
    .card-shadow {
      box-shadow:
        0 10px 15px rgba(15, 23, 42, 0.1),
        0 4px 6px rgba(15, 23, 42, 0.05);
      border-radius: 1.25rem;
      border: none;
    }
    .badge-pill {
      border-radius: 999px;
    }
    pre {
      white-space: pre-wrap;
      word-wrap: break-word;
      background-color: #0f172a;
      color: #e5e7eb;
      padding: 1rem;
      border-radius: 0.75rem;
      font-size: 0.8rem;
    }
    .section-title {
      font-size: 1rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #64748b;
    }
    .code-label {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 0.8rem;
      color: #0f172a;
    }
  </style>
</head>
<body>
<div class="main-wrapper">
  <div class="container" style="max-width: 1100px;">
    <div class="card card-shadow">
      <div class="card-body p-4 p-lg-5">
        <!-- Header -->
        <div class="d-flex justify-content-between align-items-start flex-wrap gap-3 mb-4">
          <div>
            <h1 class="h3 mb-1">Information Theory Project</h1>
            <p class="text-muted mb-0">
              Source coding (Huffman) + channel coding (Hamming) with real-time visualization.
            </p>
          </div>
          <div class="text-end">
            <span class="badge bg-primary-subtle text-primary border border-primary-subtle badge-pill">
              Parts 1–6
            </span>
            {% if results %}
              <div class="mt-2 small text-muted">
                Huffman OK:
                <span class="fw-semibold {{ 'text-success' if results.huffman_ok else 'text-danger' }}">
                  {{ results.huffman_ok }}
                </span>
                <br>
                Hamming OK:
                <span class="fw-semibold {{ 'text-success' if results.hamming_ok else 'text-danger' }}">
                  {{ results.hamming_ok }}
                </span>
              </div>
            {% endif %}
          </div>
        </div>

        <!-- Upload + Settings -->
        <form method="post" enctype="multipart/form-data" class="mb-4">
          <div class="row g-3 align-items-end">
            <div class="col-md-6">
              <label class="form-label fw-semibold">Upload Text File (Text.txt)</label>
              <input
                type="file"
                name="textfile"
                accept=".txt"
                class="form-control"
                required
              >
              <div class="form-text">Any UTF-8 .txt file can be used as the source message.</div>
            </div>
            <div class="col-md-3">
              <label class="form-label fw-semibold">Error Interval (Part 5)</label>
              <input
                type="number"
                name="interval"
                value="50"
                min="1"
                class="form-control"
              >
              <div class="form-text">Flip one bit every N bits in the Hamming stream.</div>
            </div>
            <div class="col-md-3 text-md-end">
              <button type="submit" class="btn btn-primary px-4 py-2 mt-2 mt-md-0">
                Run Pipeline
              </button>
            </div>
          </div>
        </form>

        {% if results %}
        <!-- Results layout -->
        <div class="row g-4">
          <!-- Left column: summary + probabilities -->
          <div class="col-lg-4">
            <div class="mb-4">
              <div class="section-title mb-2">Summary</div>
              <ul class="list-group list-group-flush small">
                <li class="list-group-item px-0 d-flex justify-content-between">
                  <span>Original length (symbols)</span>
                  <span class="fw-semibold">{{ results.text_length }}</span>
                </li>
                <li class="list-group-item px-0 d-flex justify-content-between">
                  <span>Encoded length (bits, Part 2)</span>
                  <span class="fw-semibold">{{ results.encoded_bits|length }}</span>
                </li>
                <li class="list-group-item px-0 d-flex justify-content-between">
                  <span>Hamming length (bits, Part 4)</span>
                  <span class="fw-semibold">{{ results.hamming_bits|length }}</span>
                </li>
                <li class="list-group-item px-0 d-flex justify-content-between">
                  <span>Pad bits (Hamming)</span>
                  <span class="fw-semibold">{{ results.pad_bits }}</span>
                </li>
              </ul>
            </div>

            <div>
              <div class="section-title mb-2">Part 1 – Sample Probabilities</div>
              <div class="small text-muted mb-2">
                Top 10 symbols by probability:
              </div>
              <pre>
{% for sym, p in probs_sample %}
{{ sym | tojson }} : {{ "%.6f"|format(p) }}
{% endfor %}
              </pre>
            </div>
          </div>

          <!-- Right column: bitstreams + text -->
          <div class="col-lg-8">
            <!-- Bitstreams -->
            <div class="mb-4">
              <div class="section-title mb-2">Bitstreams (Parts 2, 4, 5, 6)</div>

              <div class="mb-3">
                <div class="code-label mb-1">Part 2 – Huffman encoded bits (first 200 bits)</div>
                <pre>{{ results.encoded_bits[:200] }}{% if results.encoded_bits|length > 200 %}...{% endif %}</pre>
              </div>

              <div class="mb-3">
                <div class="code-label mb-1">Part 4 – Hamming(7,4) encoded bits (first 200 bits)</div>
                <pre>{{ results.hamming_bits[:200] }}{% if results.hamming_bits|length > 200 %}...{% endif %}</pre>
              </div>

              <div class="mb-3">
                <div class="code-label mb-1">Part 5 – Corrupted bits (errors injected, first 200 bits)</div>
                <pre>{{ results.corrupted_bits[:200] }}{% if results.corrupted_bits|length > 200 %}...{% endif %}</pre>
              </div>

              <div class="mb-0">
                <div class="code-label mb-1">Part 6 – Recovered bits (first 200 bits)</div>
                <pre>{{ results.recovered_bits[:200] }}{% if results.recovered_bits|length > 200 %}...{% endif %}</pre>
              </div>
            </div>

            <!-- Text comparison -->
            <div>
              <div class="section-title mb-2">Original vs Decoded Text (Part 3)</div>
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
  </div>
</div>

<!-- Bootstrap JS (optional, for future enhancements) -->
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
