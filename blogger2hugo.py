#!/usr/bin/env python3
import os, re, sys, requests, shutil, concurrent.futures
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, NavigableString
from markdownify import markdownify

ATOM_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "blogger": "http://schemas.google.com/blogger/2018"
}

# =====================================================
# Utility
# =====================================================

def safe_mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_text(element, tag, ns=ATOM_NS, default=""):
    el = element.find(tag, ns)
    return el.text.strip() if el is not None and el.text else default

def download_file(url, local_path):
    try:
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
            return True
    except:
        pass
    return False

# =====================================================
# Tables Markdown Conversion
# =====================================================

def has_complex_table(table_tag):
    for cell in table_tag.find_all(["td","th"]):
        if cell.has_attr("colspan") or cell.has_attr("rowspan"):
            return True
    return False

def row_to_text_cells(row_tag):
    cells = []
    for c in row_tag.find_all(["th","td"], recursive=False):
        txt = " ".join([s.strip() for s in c.stripped_strings])
        txt = txt.replace("|", "\\|")
        cells.append(txt)
    return cells

def table_to_markdown(table_tag):
    if has_complex_table(table_tag):
        return None
    rows = []
    for tr in table_tag.find_all("tr"):
        rows.append(row_to_text_cells(tr))
    rows = [r for r in rows if any(cell.strip() for cell in r)]
    if not rows:
        return None
    col_count = max(len(r) for r in rows)
    def norm(r):
        while len(r) < col_count:
            r.append("")
        return r
    rows = [norm(r) for r in rows]
    header = rows[0]
    body = rows[1:]
    md = (
        "\n\n| " + " | ".join(header) + " |\n" +
        "| " + " | ".join("---" for _ in header) + " |\n"
    )
    for r in body:
        md += "| " + " | ".join(r) + " |\n"
    return md + "\n\n"

def convert_tables(soup):
    for table in soup.find_all("table"):
        md = table_to_markdown(table)
        table.replace_with(NavigableString(md if md else "\n\n"+str(table)+"\n\n"))

# =====================================================
# HTML Cleaning + Media + Embed
# =====================================================

def sanitize_filename(filename):
    filename = filename.lower().replace("%20", "-").replace(" ", "-").replace("_", "-")
    filename = re.sub(r"[^a-z0-9\.-]+", "-", filename)
    return re.sub(r"-{2,}", "-", filename).strip("-")

def clean_html(html, image_dir, slug):
    soup = BeautifulSoup(html or "", "html.parser")

    # remove unnecessary attributes
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr not in ["src", "href", "alt", "title"]:
                del tag[attr]

    # === collect images first (faster multi download) ===
    imgJobs = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if not src:
            img.decompose()
            continue
        ext = os.path.splitext(src.split("?")[0])[1][:5] or ".jpg"
        filename = sanitize_filename(f"{slug}-{abs(hash(src))}{ext}")
        local_path = os.path.join(image_dir, filename)
        imgJobs.append((img, src, filename, local_path))

    # always create image dir even if no images will be downloaded
    safe_mkdir(image_dir)

    # parallel download
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(download_file, src, path): (img, filename) 
                   for img, src, filename, path in imgJobs}
        for fut in concurrent.futures.as_completed(futures):
            img, filename = futures[fut]
            if fut.result():
                img.replace_with(NavigableString(f"![{img.get('alt','')}](/posts/{slug}/images/{filename})"))
            else:
                img.replace_with(NavigableString(f"![{img.get('alt','')}]({img.get('src')})"))

    # iframe conversions
    for iframe in list(soup.find_all("iframe")):
        src = iframe.get("src", "")
        if not src:
            iframe.decompose()
            continue
        yt = re.search(r"(?:youtube\.com/embed/|youtu\.be/)([\w-]+)", src)
        if yt:
            iframe.replace_with(NavigableString(f"{{{{< youtube {yt.group(1)} >}}}}"))
            continue
        gd = re.search(r"drive\.google\.com/file/d/([^/]+)", src)
        if gd:
            iframe.replace_with(NavigableString(
                f"[Download PDF](https://drive.google.com/uc?export=download&id={gd.group(1)})"
            ))
            continue
        iframe.replace_with(NavigableString(str(iframe)))

    convert_tables(soup)
    return str(soup)

def html_to_markdown(html):
    try:
        md = markdownify(html, heading_style="ATX", strip=['a'])
        return md if md.strip() else html
    except:
        return html

# =====================================================
# Frontmatter
# =====================================================

def frontmatter(title, date, updated, tags, permalink, draft_flag):
    title = title.replace('"', '\\"')  # escape quotes to prevent YAML break
    aliases = f"aliases:\n  - /{permalink}\n" if permalink else ""
    return (
        "---\n"
        f'title: "{title}"\n'
        f"date: {date}\n"
        f"lastmod: {updated}\n"
        f"tags: {tags}\n"
        f"{aliases}"
        f"draft: {draft_flag}\n"
        "---\n\n"
    )

# =====================================================
# Main
# =====================================================

def convert_atom(atom_file, output_dir):
    tree = ET.parse(atom_file)
    root = tree.getroot()
    base_dir = os.path.join(output_dir, "posts")
    safe_mkdir(base_dir)

    count_posted = 0
    count_draft = 0

    for entry in root.findall("atom:entry", ATOM_NS):
        if extract_text(entry, "blogger:type") != "POST":
            continue

        status = extract_text(entry, "blogger:status")
        draft_flag = "true" if status == "DRAFT" else "false"

        # === Count draft vs posted ===
        if draft_flag == "true":
            count_draft += 1
        else:
            count_posted += 1

        title = extract_text(entry, "atom:title", ATOM_NS, "untitled")
        published = extract_text(entry, "atom:published", ATOM_NS)
        updated = extract_text(entry, "atom:updated", ATOM_NS)
        permalink = extract_text(entry, "blogger:filename", ATOM_NS).strip("/")

        # === Fallback if permalink missing ===
        if not permalink or permalink.strip() == "":
            title_fallback = extract_text(entry, "atom:title", ATOM_NS, "untitled")
            if not title_fallback.strip():
                # fallback to ID if title empty
                title_fallback = extract_text(entry, "atom:id", ATOM_NS).split("-")[-1]
            permalink = sanitize_filename(title_fallback.lower().replace(" ", "-")) + ".html"
        
        slug = sanitize_filename(permalink.replace(".html",""))


        post_dir = os.path.join(base_dir, slug)
        image_dir = os.path.join(post_dir, "images")

        # Create both dirs upfront to avoid misplacement bugs
        safe_mkdir(post_dir)
        safe_mkdir(image_dir)

        html = extract_text(entry, "atom:content", ATOM_NS, "")
        cleaned = clean_html(html, image_dir, slug)
        markdown = html_to_markdown(cleaned)

        tags = [t.attrib.get("term") for t in entry.findall("atom:category", ATOM_NS) if t.attrib.get("term")]
        tags = str(tags)

        with open(os.path.join(post_dir, "index.md"), "w", encoding="utf-8") as f:
            f.write(frontmatter(title, published, updated, tags, permalink, draft_flag))
            f.write(markdown)

        print(f"[OK] /posts/{slug}/index.md | draft={draft_flag}")

    # === Final summary ===
    print(f"\n🎉 Completed extract {count_posted} posted article(s) and {count_draft} draft article(s)!\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python blogger2hugo.py [file.atom] [output_dir]")
        sys.exit(1)
    convert_atom(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "content")

