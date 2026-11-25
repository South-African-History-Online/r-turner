#!/usr/bin/env python3
"""Rebuild hugo-site/content and static files from legacy-site.

Sources: legacy-site/wayback holds the archived pages of the old Rick Turner
subsite (Wayback Machine captures of the Drupal 7 site and the 2008 static
site); legacy-site/files holds its images, graphics and PDFs. This script is
the single record of how each legacy page maps to the new site.
"""
import html
import json
import os
import re
import shutil
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "legacy-site"
WAYBACK = LEGACY / "wayback"
FILES = LEGACY / "files"
CONTENT = ROOT / "hugo-site" / "content"
STATIC = ROOT / "hugo-site" / "static"
IMAGES = STATIC / "images"


def read(name):
    return (WAYBACK / name).read_text(encoding="utf-8", errors="replace")


BLOCK = {"p", "div", "td", "tr", "table", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol"}
NOISE = re.compile(
    r"^(\*\*)?\s*(HISTORY|GALLERY|RESOURCES|NEWS|BOOKS / CATALOGUES|Biographies|Timeline|"
    r"Newspaper articles|enlarge|BACK TO TOP|<\s*BACK|<\s*EXHIBITIONS|BACK|EXHIBITIONS:?|view photos from the exhibition|"
    r"< PREVIOUS PAGE|NEXT PAGE >)\s*(\*\*)?$",
    re.I,
)


def slug(name):
    stem, ext = os.path.splitext(name)
    stem = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return stem + ext.lower()


class Markdown(HTMLParser):
    def __init__(self, base, links, images):
        super().__init__(convert_charrefs=True)
        self.base, self.links, self.images = base, links, images
        self.out, self.skip, self.href, self.list = [], 0, [], []

    def emit(self, text):
        if not self.skip:
            self.out.append(text)

    def resolve(self, target):
        target = urllib.parse.unquote(target.split("#")[0].split("?")[0])
        target = re.sub(r"^https?://(www\.)?sahistory\.org\.za", "", target)
        return target

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "head"):
            self.skip += 1
        elif tag in BLOCK:
            self.emit("\n\n")
            if tag in ("ul", "ol"):
                self.list.append(tag)
        elif tag == "br":
            self.emit("  \n")
        elif tag in ("strong", "b"):
            self.emit("\x01")
        elif tag in ("em", "i"):
            self.emit("\x02")
        elif tag == "li":
            self.emit("\n- ")
        elif tag == "sup":
            self.emit("<sup>")
        elif tag == "a":
            href = a.get("href", "")
            url = None
            if self.resolve(href) in self.links:
                url = self.links[self.resolve(href)]
            elif href.startswith("http"):
                url = href
            elif href and not href.startswith(("javascript", "#", "mailto")):
                url = self.links.get(self.resolve(href))
            self.href.append(url)
            if url:
                self.emit("[")
        elif tag == "img":
            src = self.resolve(a.get("src", ""))
            if src in self.images:
                self.emit(f"\n\n![]({self.images[src]})\n\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head"):
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK:
            self.emit("\n\n")
            if tag in ("ul", "ol") and self.list:
                self.list.pop()
        elif tag in ("strong", "b"):
            self.emit("\x01")
        elif tag in ("em", "i"):
            self.emit("\x02")
        elif tag == "sup":
            self.emit("</sup>")
        elif tag == "a" and self.href:
            url = self.href.pop()
            if url:
                self.emit(f"]({url})")

    def handle_data(self, data):
        self.emit(re.sub(r"\s+", " ", data))


def emphasis(text, mark, md):
    def wrap(match):
        inner = match.group(1)
        if not inner.strip():
            return inner
        lead = inner[: len(inner) - len(inner.lstrip())]
        trail = inner[len(inner.rstrip()):]
        return f"{lead}{md}{inner.strip()}{md}{trail}"

    text = re.sub(mark + "([^" + mark + "\n]*)" + mark, wrap, text)
    return text.replace(mark, "")


def to_markdown(rel, links, images):
    parser = Markdown(rel, links, images)
    parser.feed(rel if "<" in rel else read(rel))
    text = "".join(parser.out).replace("\xa0", " ")
    text = text.replace("\u201d\u00a6", "\u2026").replace("\u201d\u009d", "\u201d")
    text = re.sub(r"[\u0080-\u009f\ufffd]", "", text)
    text = re.sub(r"\u201c[ \t]+", "\u201c", text)
    text = re.sub(r"(?<=\w)[ \t]+([,;])", r"\1", text)
    text = re.sub(r"(?<=[a-z])[ \t]+\.(?=[ \t\n]|$)", ".", text)
    text = emphasis(text, "\x01", "**")
    text = emphasis(text, "\x02", "*")
    paragraphs = []
    for block in re.split(r"\n\s*\n", text):
        lines = [re.sub(r"[ \t]+", " ", l).strip() for l in block.split("\n")]
        lines = [l + "  " if raw.endswith("  ") else l for l, raw in zip(lines, block.split("\n"))]
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        block = "\n".join(lines).strip()
        block = re.sub(r"^(\s*\n)+", "", block)
        plain = re.sub(r"[*<>|\s]", "", block)
        unlinked = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", block).replace("\n", " ").strip()
        if not plain or NOISE.match(unlinked):
            continue
        paragraphs.append(block)
    return paragraphs


def headings(paragraphs):
    out = []
    for p in paragraphs:
        m = re.fullmatch(r"\*\*([^*\n]{3,110})\*\*:?", p.strip())
        out.append(f"## {m.group(1).strip().rstrip(':')}" if m else p)
    return out




def write(path, front, body=""):
    target = CONTENT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(front, indent=2, ensure_ascii=False) + "\n\n" + body.strip() + "\n", encoding="utf-8")


def copy_file(src, dest_rel):
    dest = STATIC / dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return "/" + dest_rel


def region(name):
    """The node body of an archived Drupal page, without theme chrome."""
    raw = read(name)
    start = raw.find('<div class="region region-content">')
    end = raw.find("<footer>", start)
    if end == -1:
        end = raw.find("<!-- /.block -->", start)
    return raw[start:end]


def full_size(name):
    """Prefer the full image over the thumbnail the old page embedded."""
    folder = FILES / "images" / os.path.dirname(name)
    base = os.path.basename(name)
    stem = re.sub(r"(-thumb-?|-thu|-small)$", "", os.path.splitext(base)[0], flags=re.I)
    if stem == os.path.splitext(base)[0]:
        return name
    norm = lambda text: re.sub(r"[^a-z0-9]", "", text.lower())
    pool = [c for c in sorted(folder.iterdir()) if c.is_file() and not re.search(r"thumb|-thu\.|small", c.name, re.I)]
    prefixed = [c for c in pool if norm(c.stem).startswith(norm(stem))]
    containing = [c for c in pool if norm(stem) in norm(c.stem)]
    if prefixed:
        best = max(prefixed, key=lambda c: c.stat().st_size)
    elif containing:
        best = min(containing, key=lambda c: len(c.name))
    else:
        return name
    return os.path.join(os.path.dirname(name), best.name)


def gallery(fragment, dest):
    works = []
    for cell in re.findall(r"(?is)<td[^>]*>(.*?)</td>", fragment):
        img = re.search(r'(?i)<img[^>]+src="[^"]*/r-turner/images/([^"]+)"', cell)
        if not img:
            continue
        name = full_size(urllib.parse.unquote(img.group(1)))
        source = FILES / "images" / name
        if not source.exists():
            continue
        caption = re.sub(r"(?i)<br\s*/?>", " ", cell)
        caption = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", caption)).replace("\xa0", " ")).strip()
        work = {"image": copy_file(source, f"images/{dest}/{slug(os.path.basename(name))}")}
        if caption:
            work["title"] = caption
        works.append(work)
    return works


LINKS = {
    "/r-turner/biography": "/life/biography/",
    "/r-turner/chronology": "/life/chronology/",
    "/r-turner/his-writings": "/writings/",
    "/r-turner/gallery": "/gallery/family-and-funeral/",
    "/r-turner/Thirty_Years_On": "/remembering/thirty-years-on/",
    "/r-turner/Who_Shot_My_Dad": "/remembering/who-shot-my-dad/",
    "/library-resources/online books/eye-needle/eye-index.htm": "https://sahistory.org.za/archive/eye-needle-rick-turner",
}
for pdf in sorted((FILES / "pdfs").glob("*.pdf")):
    LINKS[f"/r-turner/pdfs/{pdf.name}"] = f"/pdfs/{slug(pdf.name)}"


def essay(name, path, title, weight, extra=None):
    paragraphs = headings(to_markdown(region(name), LINKS, {}))
    paragraphs = [p for p in paragraphs if not p.startswith(("Error message", "Deprecated function"))]
    front = {"title": title, "weight": weight, "legacy_path": name}
    front.update(extra or {})
    write(path, front, "\n\n".join(paragraphs))


def chronology():
    rows = re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", region("chronology.html"))
    out = []
    for row in rows:
        cells = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c)).replace("\xa0", " ")).strip() for c in re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)]
        cells = [c for c in cells if c]
        if len(cells) >= 2:
            out.append(f"## {cells[0]}\n\n{' '.join(cells[1:])}")
    if not out:
        out = to_markdown(region("chronology.html"), LINKS, {})
        out = [f"## {p}" if re.fullmatch(r"(c\. ?)?(19|20)\d\d(\s?-\s?\d{2,4})?", p.strip()) else p for p in out]
    return "\n\n".join(out)


def quotes():
    raw = read("static-notable-quotes_turner.htm")
    raw = raw[[m.start() for m in re.finditer(r"(?i)notable quotes", raw)][-1]:]
    out = []
    for p in to_markdown("<div>" + raw + "</div>", LINKS, {})[1:]:
        text = re.sub(r"^\*+|\*+$", "", p.strip()).strip()
        if "copyright" in text.lower() or re.match(r"^(home|top|back)\b", text, re.I):
            continue
        if text.startswith(("\u201c", '"')):
            out.append("> " + text.replace("\n", "\n> "))
        elif len(text) < 60:
            out.append("## " + text.rstrip(":"))
        else:
            out.append(text)
    return "\n\n".join(out)


PDF_NODES = [
    (23, "What is political philosophy?", "Richard Turner", "What is political philosophy.pdf", "writings"),
    (24, "Sartre and Ryle on the imagination", "Richard Turner", "Sartre and Ryle on the imagination.pdf", "writings"),
    (25, "Letter to parliament", "Richard Turner", "South African Outlook June 1978.pdf", "writings"),
    (26, "Human models and economic systems", "Richard Turner", "Human models and economic systems.pdf", "writings"),
    (27, "The East London strikes", "Richard Turner", "The East London strikes.pdf", "writings"),
    (28, "Dialectical Reason", "Richard Turner", "Dialectical reason.pdf", "writings"),
    (None, "Memorandum to the Schlebusch Commission", "Richard Turner", "Memorandum to Schlebusch Commission.pdf", "writings"),
    (21, "Biographical introduction to The Eye of the Needle", "Tony Morphet", "Tony Morphet The Eye of the Needle Ravan 1980.pdf", "remembering"),
    (30, "The Moment of Western Marxism in South Africa", "Andrew Nash", "Turner by Nash.pdf", "remembering"),
    (31, "Re-reading Rick Turner in the New South Africa", "Tony Fluxman and Peter Vale", "Turner by Fluxman and Vale.pdf", "remembering"),
    (20, "Is the continuation of the present a possible future?", "Mark Heywood, Daily Maverick, 4 August 2014", "Heywood - Is the continuation of the present a possible future.pdf", "remembering"),
]


def main():
    for d in (CONTENT, IMAGES, STATIC / "pdfs"):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    for pdf in sorted((FILES / "pdfs").glob("*.pdf")):
        copy_file(pdf, f"pdfs/{slug(pdf.name)}")

    portrait = copy_file(FILES / "images/R-Turner.jpg", "images/site/rick-turner.jpg")
    banner = copy_file(FILES / "graphics/turner-banner-aeriel.jpg", "images/site/banner.jpg")
    cover = copy_file(FILES / "graphics/eye-needle-book.jpg", "images/site/eye-of-the-needle.jpg")
    lecture = copy_file(FILES / "images/turner-speaking-university.jpg", "images/site/turner-speaking.jpg")
    copy_file(FILES / "graphics/saho-logo.gif", "images/site/saho-logo.gif")

    bio = [p for p in to_markdown(region("biography.html"), LINKS, {})]
    write("_index.md", {
        "title": "Richard Albert David Turner",
        "tagline": "South African political philosopher, 1941 - 1978",
        "strapline": "A visionary academic and philosopher who inspired a generation of young activists.",
        "portrait": portrait,
        "cover": cover,
        "quote": "Unless we can see our society in the light of other possible societies we cannot even understand how and why it works as it does, let alone judge it.",
        "quote_source": "The Eye of the Needle, 1972",
        "legacy_path": "home.html",
    }, "\n\n".join(bio[:2]))

    write("life/_index.md", {"title": "Life", "weight": 10, "summary": "A biography and a brief chronology, from Cape Town in 1941 to Durban in 1978.", "cover": lecture})
    essay("biography.html", "life/biography.md", "A biography of Richard Albert David Turner", 10, {"menu_title": "Biography"})
    write("life/chronology.md", {"title": "A brief chronology", "weight": 20, "layout": "chronology", "legacy_path": "chronology.html"}, chronology())

    listing = [p for p in headings(to_markdown(region("his-writings.html"), LINKS, {})) if p.strip() != "His writings"]
    # The old page ran a list of typescripts together and ended with a stray
    # attachment block that the document pages below now replace.
    listing = [p for p in listing if "sites/default/files" not in p and p.strip() != "Dialectical Reason by Richard Turner"]
    listing = [re.sub(r"\.?\s*Typescript(?=[A-Z\[0-9])", ". Typescript\n\n", p).replace("attended??", "attended?") for p in listing]
    write("writings/_index.md", {"title": "His writings", "menu_title": "Writings", "weight": 20, "summary": "A bibliography of published and unpublished work, with scanned articles.", "cover": cover, "legacy_path": "his-writings.html"}, "\n\n".join(listing))
    write("writings/notable-quotes.md", {"title": "Notable quotes from The Eye of the Needle", "weight": 5, "summary": "On society, education, work and change.", "layout": "quotes", "legacy_path": "static-notable-quotes_turner.htm"}, quotes())

    write("remembering/_index.md", {"title": "Remembering", "weight": 30, "summary": "Articles by his daughter Jann Turner, a poem by Peter Sacks, and essays re-reading his work.", "legacy_path": "article-landing-page.html"})
    essay("node-33.html", "remembering/thirty-years-on.md", "Rick Turner: Thirty Years On", 10, {"author": "Jann Turner"})
    essay("node-32.html", "remembering/who-shot-my-dad.md", "Who Shot My Dad?", 20, {"author": "Jann Turner", "year": "1997"})
    poem = to_markdown(region("node-36.html"), LINKS, {})
    poem = [p for p in poem if not p.startswith(("Error message", "Deprecated function"))]
    write("remembering/for-richard-turner.md", {"title": "For Richard Turner", "weight": 30, "author": "Peter Sacks", "layout": "poem", "legacy_path": "node-36.html"}, "  \n".join(poem))

    for weight, (nid, title, author, pdf, section) in enumerate(PDF_NODES):
        url = f"/pdfs/{slug(pdf)}"
        write(f"{section}/{slug(title + '.x')[:-2]}.md", {"title": title, "weight": 40 + weight, "author": author, "document": url, "summary": "Scanned document (PDF).", "legacy_path": f"node-{nid}.html" if nid else f"pdfs/{pdf}"},
              f"[Read the scanned document (PDF)]({url})")

    write("gallery/_index.md", {"title": "Gallery", "weight": 40, "summary": "Portraits, family photographs, the funeral, press headlines and letters."})
    for weight, (name, path, title, dest, variant) in enumerate([
        ("node-16.html", "portraits", "Portraits", "portraits", None),
        ("gallery.html", "family-and-funeral", "Family and the funeral", "family", None),
        ("node-17.html", "press", "Newspaper headlines", "press", "scans"),
        ("node-18.html", "letters", "Letters", "letters", "scans"),
    ]):
        works = gallery(region(name), dest)
        front = {"title": title, "type": "gallery", "weight": 10 + weight, "summary": f"{len(works)} images.", "cover": works[0]["image"] if works else "", "works": works, "legacy_path": name}
        if variant:
            front["variant"] = variant
        write(f"gallery/{path}.md", front)

    suspicious = re.compile(r"[\u0080-\u009f\ufffd\u00a6]|\u00e2\u20ac|\u00c3.|\u00c2[^a-zA-Z]|&[a-z]+;|&#\d+;")
    broken = [f"{page.relative_to(CONTENT)}: {m.group(0)!r}" for page in CONTENT.rglob("*.md") for m in suspicious.finditer(page.read_text(encoding="utf-8"))]
    if broken:
        raise SystemExit("broken characters in migrated content:\n" + "\n".join(broken[:40]))

    pages = sum(1 for _ in CONTENT.rglob("*.md"))
    images = sum(1 for p in IMAGES.rglob("*") if p.is_file())
    print(f"wrote {pages} pages, {images} images, {len(list((STATIC / 'pdfs').glob('*.pdf')))} pdfs")


if __name__ == "__main__":
    main()
