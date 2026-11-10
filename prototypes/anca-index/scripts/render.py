"""Render antiochian.org/liturgicday/<id> in headless Chrome; cache rendered DOM HTML.
Usage: render.py ID [ID...]   -> prints id<TAB>heading<TAB>n_servicetext_links
Throttled; cache in raw/<id>.html (untracked)."""
import re, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

RAW = Path(__file__).resolve().parent.parent / "raw"
DELAY = 1.0

def fetch(page, i, force=False):
    f = RAW / f"{i}.html"
    if f.exists() and not force:
        return f.read_text()
    for attempt in range(3):
        try:
            page.goto(f"https://www.antiochian.org/liturgicday/{i}", wait_until="domcontentloaded", timeout=30000)
            break
        except Exception:
            time.sleep(5)
    try:
        page.wait_for_function("document.body.innerText.match(/(SUNDAY|MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY), /i)", timeout=7000)
    except Exception:
        pass
    try:
        page.wait_for_selector('a[href*="servicetexts"]', timeout=3500)
    except Exception:
        pass
    page.wait_for_timeout(500)
    html = page.content()
    f.write_text(html)
    time.sleep(DELAY)
    return html

def heading(html):
    m = re.search(r"((?:SUNDAY|MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY),\s*[A-Z]+\s+\d+,\s*\d{4})", html, re.I)
    return m.group(1) if m else ""

if __name__ == "__main__":
    RAW.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        page = b.new_page()
        for i in sys.argv[1:]:
            h = fetch(page, i)
            print(i, heading(h), len(re.findall(r"servicetexts/", h)), sep="\t", flush=True)
        b.close()
