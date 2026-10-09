"""Render paper3/to_fetch.md as a page of clickable links: python3 paper3/make_fetch_html.py"""
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def trim_url(url):
    """Drop trailing punctuation and any ')' that has no matching '(' in the URL."""
    while url and url[-1] in ".,;:":
        url = url[:-1]
    while url.endswith(")") and url.count(")") > url.count("("):
        url = url[:-1]
    return url


def link(match):
    raw = match.group(0)
    url = trim_url(raw)
    rest = raw[len(url):]
    return f'<a href="{html.escape(url, quote=True)}" target="_blank">{html.escape(url)}</a>{html.escape(rest)}'


def inline(text):
    parts, last = [], 0
    for m in re.finditer(r"https?://\S+", text):
        parts.append(html.escape(text[last:m.start()]))
        parts.append(link(m))
        last = m.end()
    parts.append(html.escape(text[last:]))
    s = "".join(parts)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<i>\1</i>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def main():
    md = (HERE / "to_fetch.md").read_text()
    out = ["<!doctype html><meta charset=utf-8><title>Paper 3 references to fetch</title>",
           "<style>body{font-family:sans-serif;max-width:62em;margin:2em auto;line-height:1.45}"
           "li{margin:.35em 0}a{word-break:break-all}</style>"]
    inlist = False
    for line in md.splitlines():
        if line.startswith("- "):
            if not inlist:
                out.append("<ul>")
                inlist = True
            out.append("<li>" + inline(line[2:]) + "</li>")
            continue
        if inlist:
            out.append("</ul>")
            inlist = False
        if line.startswith("## "):
            out.append("<h2>" + inline(line[3:]) + "</h2>")
        elif line.startswith("# "):
            out.append("<h1>" + inline(line[2:]) + "</h1>")
        elif line.strip():
            out.append("<p>" + inline(line) + "</p>")
    if inlist:
        out.append("</ul>")
    (HERE / "to_fetch.html").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
