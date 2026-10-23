"""
Generates a printable, styled HTML report from Assignment_Report.md
that can be opened in any browser and saved as Assignment_Report.pdf.
"""

import os

REPORT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(REPORT_DIR, "Assignment_Report.md")
HTML_PATH = os.path.join(REPORT_DIR, "Assignment_Report.html")

def convert_md_to_styled_html():
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Simple clean markdown-to-html conversion
    lines = md_text.split("\n")
    html_lines = []
    in_code_block = False
    in_table = False

    for line in lines:
        if line.startswith("```"):
            if in_code_block:
                html_lines.append("</pre>")
                in_code_block = False
            else:
                html_lines.append("<pre><code>")
                in_code_block = True
            continue

        if in_code_block:
            html_lines.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("#### "):
            html_lines.append(f"<h4>{line[5:]}</h4>")
        elif line.startswith("> "):
            html_lines.append(f"<blockquote>{line[2:]}</blockquote>")
        elif line.startswith("---"):
            html_lines.append("<hr>")
        elif line.startswith("- "):
            html_lines.append(f"<li>{line[2:]}</li>")
        elif line.strip().startswith("|") and line.strip().endswith("|"):
            parts = [p.strip() for p in line.strip().split("|")[1:-1]]
            if not in_table:
                html_lines.append("<table border='1'><thead><tr>")
                for p in parts:
                    html_lines.append(f"<th>{p}</th>")
                html_lines.append("</tr></thead><tbody>")
                in_table = True
            elif all(set(p).issubset({"-", ":"}) for p in parts if p):
                continue
            else:
                html_lines.append("<tr>")
                for p in parts:
                    html_lines.append(f"<td>{p}</td>")
                html_lines.append("</tr>")
        else:
            if in_table and not (line.strip().startswith("|") and line.strip().endswith("|")):
                html_lines.append("</tbody></table>")
                in_table = False
            if line.strip():
                html_lines.append(f"<p>{line}</p>")

    if in_table:
        html_lines.append("</tbody></table>")

    body_html = "\n".join(html_lines)

    # Format bold, italics, links, and images
    import re
    body_html = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<div class="img-container"><img src="\2" alt="\1"><p class="caption">\1</p></div>', body_html)
    body_html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', body_html)
    body_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', body_html)
    body_html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', body_html)
    body_html = re.sub(r'`(.*?)`', r'<code>\1</code>', body_html)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Operating Systems Assignment Report</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #1e293b;
    max-width: 900px;
    margin: 40px auto;
    padding: 0 24px;
    background: #ffffff;
  }}
  h1 {{ font-size: 2rem; color: #0f172a; margin-bottom: 8px; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; }}
  h2 {{ font-size: 1.45rem; color: #1e293b; margin-top: 32px; margin-bottom: 12px; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; }}
  h3 {{ font-size: 1.2rem; color: #334155; margin-top: 24px; margin-bottom: 8px; }}
  h4 {{ font-size: 1.05rem; color: #475569; margin-top: 16px; margin-bottom: 6px; }}
  p {{ margin-bottom: 12px; }}
  blockquote {{
    border-left: 4px solid #3b82f6;
    background: #f8fafc;
    padding: 12px 18px;
    margin: 16px 0;
    font-style: italic;
    color: #334155;
    border-radius: 0 8px 8px 0;
  }}
  pre {{
    background: #0f172a;
    color: #f8fafc;
    padding: 16px;
    border-radius: 8px;
    overflow-x: auto;
    font-size: 0.9rem;
    margin: 16px 0;
  }}
  code {{
    font-family: Consolas, Monaco, "Courier New", monospace;
    background: #f1f5f9;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
  }}
  pre code {{
    background: transparent;
    padding: 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 0.92rem;
  }}
  th, td {{
    padding: 10px 14px;
    border: 1px solid #cbd5e1;
    text-align: left;
  }}
  th {{ background: #f1f5f9; font-weight: 600; }}
  li {{ margin-left: 24px; margin-bottom: 6px; }}
  hr {{ border: 0; border-top: 1px solid #e2e8f0; margin: 30px 0; }}
  .img-container {{ margin: 24px 0; text-align: center; }}
  .img-container img {{ max-width: 100%; border: 1px solid #cbd5e1; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
  .caption {{ font-size: 0.85rem; color: #64748b; margin-top: 8px; font-style: italic; }}
  @media print {{
    body {{ max-width: 100%; margin: 0; padding: 20px; }}
    pre, blockquote, table {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
{body_html}
</body>
</html>"""

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Generated printable report at: {HTML_PATH}")

if __name__ == "__main__":
    convert_md_to_styled_html()
