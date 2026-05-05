#!/usr/bin/env python3
"""
Convert a brainstorming HTML fragment into a stand-alone PDF.

Usage:
    python3 scripts/brainstorm_to_pdf.py <fragment.html> <output.pdf> [--title "Section title"]

The fragment is wrapped in the brainstorming frame CSS (light theme, print-friendly)
and rendered with WeasyPrint.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PRINT_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
  color: #1d1d1f;
  background: #ffffff;
  line-height: 1.45;
  font-size: 10pt;
}
:root {
  --bg-primary: #ffffff;
  --bg-secondary: #ffffff;
  --bg-subtle: #f5f5f7;
  --bg-tertiary: #efeff2;
  --border: #d1d1d6;
  --text-primary: #1d1d1f;
  --text-secondary: #4a4a4f;
  --text-tertiary: #6e6e73;
  --accent: #0071e3;
  --selected-bg: #e8f4fd;
  --selected-border: #0071e3;
  --success: #1a7f37;
  --error: #b3261e;
}
.doc-header {
  border-bottom: 1px solid var(--border);
  padding-bottom: 8pt;
  margin-bottom: 14pt;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.doc-header h1 {
  font-size: 9pt;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.doc-header .meta {
  font-size: 8pt;
  color: var(--text-tertiary);
}
h2 { font-size: 18pt; font-weight: 600; margin-bottom: 6pt; color: var(--text-primary); page-break-after: avoid; }
h3 { font-size: 12pt; font-weight: 600; margin-top: 10pt; margin-bottom: 4pt; color: var(--text-primary); page-break-after: avoid; }
h4 { font-size: 10pt; font-weight: 600; margin-bottom: 3pt; }
p { margin-bottom: 6pt; }
.subtitle { color: var(--text-secondary); margin-bottom: 12pt; font-size: 11pt; }
.section { margin-bottom: 14pt; }
.label {
  font-size: 7.5pt;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 4pt;
}
ul, ol { margin-left: 16pt; margin-bottom: 6pt; }
li { margin-bottom: 2pt; }
code {
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 9pt;
  background: var(--bg-subtle);
  padding: 1pt 4pt;
  border-radius: 3px;
}
pre {
  font-family: "SF Mono", Menlo, Consolas, monospace;
  font-size: 8.5pt;
  background: var(--bg-subtle);
  padding: 8pt;
  border-radius: 4px;
  white-space: pre;
  overflow-x: auto;
  page-break-inside: avoid;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 8pt 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid var(--border);
  padding: 5pt 7pt;
  text-align: left;
  vertical-align: top;
}
th { background: var(--bg-subtle); font-weight: 600; }

/* Options (A/B/C choice cards) */
.options { display: block; }
.option {
  display: flex;
  gap: 10pt;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8pt 10pt;
  margin-bottom: 6pt;
  page-break-inside: avoid;
}
.option .letter {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
  min-width: 20pt;
  height: 20pt;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 9pt;
  flex-shrink: 0;
}
.option .content { flex: 1; }
.option .content h3 { font-size: 10.5pt; margin-top: 0; margin-bottom: 2pt; }
.option .content p { font-size: 9.5pt; color: var(--text-secondary); }

/* Cards */
.cards { display: block; }
.card {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 8pt;
  page-break-inside: avoid;
  overflow: hidden;
}
.card-image { background: var(--bg-subtle); padding: 8pt; }
.card-body { padding: 8pt 10pt; }

/* Mockup */
.mockup {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  margin: 8pt 0;
  overflow: hidden;
  page-break-inside: avoid;
}
.mockup-header {
  background: var(--bg-subtle);
  padding: 4pt 8pt;
  font-size: 8pt;
  color: var(--text-secondary);
  border-bottom: 1px solid var(--border);
}
.mockup-body { padding: 8pt; }

/* Pros/Cons */
.pros-cons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6pt;
  margin: 6pt 0;
}
.pros, .cons {
  background: var(--bg-subtle);
  border-radius: 5px;
  padding: 6pt 8pt;
}
.pros h4 { color: var(--success); font-size: 9pt; }
.cons h4 { color: var(--error); font-size: 9pt; }
.pros ul, .cons ul { font-size: 9pt; color: var(--text-secondary); margin-left: 12pt; }

.placeholder {
  background: var(--bg-subtle);
  border: 1px dashed var(--border);
  border-radius: 4px;
  padding: 6pt 8pt;
  font-size: 9pt;
  color: var(--text-secondary);
}

/* Hide interactive helpers when printed */
[onclick] { cursor: default; }
"""

DOC_TEMPLATE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="doc-header">
  <h1>PyArchInit — s3dgraphy bridge design</h1>
  <span class="meta">{title} · {date}</span>
</div>
{body}
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="Path to HTML fragment")
    ap.add_argument("output", help="Path to output PDF")
    ap.add_argument("--title", default="Section", help="Document title shown in the header")
    args = ap.parse_args()

    fragment_path = Path(args.input)
    output_path = Path(args.output)
    if not fragment_path.is_file():
        print(f"ERROR: fragment not found: {fragment_path}", file=sys.stderr)
        return 1

    body = fragment_path.read_text(encoding="utf-8")
    from datetime import date as _d
    html = DOC_TEMPLATE.format(
        title=args.title,
        css=PRINT_CSS,
        body=body,
        date=_d.today().isoformat(),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write a temp HTML file alongside the fragment, then ask Chrome to print it.
    # Chrome's --print-to-pdf needs a real file (or a data: URL), not stdin.
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as tf:
        tf.write(html)
        tmp_html = Path(tf.name)

    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
    ]
    chrome = next((p for p in chrome_paths if Path(p).exists()), None)
    if not chrome:
        print("ERROR: no Chrome/Chromium binary found", file=sys.stderr)
        tmp_html.unlink(missing_ok=True)
        return 2

    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={output_path}",
        f"file://{tmp_html}",
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    tmp_html.unlink(missing_ok=True)
    if proc.returncode != 0 or not output_path.exists():
        print(proc.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        return proc.returncode or 3
    print(f"PDF written: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
