"""Render paper2/to_fetch.md as a page of clickable links: python3 paper2/make_fetch_html.py"""
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


def search_url(item):
    """A Google search for a PDF of the paper: authors and the exact title, filetype:pdf."""
    from urllib.parse import quote_plus
    head = re.sub(r"[`]", "", item.split(" — ")[0])
    m = re.match(r"(.+?)\s*\((\d{4})\),\s*(.+)", head)
    if m:
        authors, title = m.group(1), m.group(3)
    elif "&" in head:                       # "A, B & C, Title" with no year
        cut = head.index(",", head.index("&"))
        authors, title = head[:cut], head[cut + 1:]
    else:                                   # "Author, Title" with no year
        authors, _, title = head.partition(", ")
    # the title ends where the venue (italic), a note, or a series begins
    title = re.split(r",\s*\*|\s\(|\.\s+DOI|,\s*(?:LNCS|WG|ESA|TAMC|COCOON|STACS|SIAM|RSA|DAM|TCS|CUP)\b", title)[0]
    title = re.sub(r"[*]", "", title).strip(" ,.")
    authors = re.sub(r"[*&]", " ", authors)
    authors = re.sub(r"\bet al\.?", "", authors)
    authors = re.sub(r"\s+", " ", authors).strip(" ,")
    if "not the title" in item:            # a description: search its words, unquoted
        q = f"{authors} {title} filetype:pdf"
    else:
        q = f'{authors} "{title}" filetype:pdf' if title else f"{authors} filetype:pdf"
    return "https://www.google.com/search?q=" + quote_plus(q)


def main():
    md = (HERE / "to_fetch.md").read_text()
    out = ["<!doctype html><meta charset=utf-8><title>Paper 3 references to fetch</title>",
           "<style>body{font-family:sans-serif;max-width:62em;margin:2em auto;line-height:1.45}"
           "li{margin:.35em 0}a{word-break:break-all}a.g{word-break:normal;white-space:nowrap;font-weight:bold}</style>"]
    inlist = False
    section = ""
    for line in md.splitlines():
        if line.startswith("- "):
            if not inlist:
                out.append("<ul>")
                inlist = True
            item = inline(line[2:])
            if not section.startswith("Obtained"):
                item += (f' <a class="g" href="{html.escape(search_url(line[2:]), quote=True)}"'
                         ' target="_blank">[Google: PDF]</a>')
            out.append("<li>" + item + "</li>")
            continue
        if line.startswith("## "):
            section = line[3:]
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
