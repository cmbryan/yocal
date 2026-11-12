"""Parse a GOA Digital Chant Stand service page into ordered rows: titles, texts and music links."""
from __future__ import annotations

import html as _html
import re

from bs4 import BeautifulSoup

DCS_ORIGIN = "https://dcs.goarch.org"  # media live at the site root (the page <base> is only for the viewer)
_SUFFIX = re.compile(r"_[a-z]{2}_[A-Z]{2}_\w+$")
_FILE = re.compile(r"file=(/media/[^'\"&]+\.(?:pdf|mp3))")


def _txt(el) -> str:
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()


def parse(page: str) -> list:
    """-> ordered rows: {kind: heading|designation|text|media, ...}.

    heading: {text, key}; designation: {text}; text: {topic, field, text};
    media: {title, section, assets: [{url, label, form}]} where form is 'byzantine'|'western'|'audio'.
    """
    soup = BeautifulSoup(page, "html.parser")
    rows, section, last_title = [], "", ""
    for tr in soup.find_all("tr"):
        media = tr.find("div", class_="media-group")
        if media:
            assets = []
            for a in media.find_all("a", href=_FILE):
                url = DCS_ORIGIN + _FILE.search(a["href"]).group(1)
                people = a.find("span", class_="mediaMenuItemPeople")
                form = "audio" if url.endswith(".mp3") else ("byzantine" if "/b/" in url else "western")
                assets.append({"url": url, "label": _txt(people) if people else "", "form": form})
            for a in media.find_all("a", href=re.compile(r"^(?!.*file=).*\.(pdf|mp3)$")):
                url = a["href"] if a["href"].startswith("http") else f"{DCS_ORIGIN}/{a['href'].lstrip('/')}"
                assets.append({"url": url, "label": _txt(a), "form": "audio" if url.endswith(".mp3") else "western"})
            if assets:
                rows.append({"kind": "media", "title": last_title, "section": section, "assets": assets})
            continue
        des = tr.find("p", class_="designation")
        if des:
            last_title = _txt(des)
            rows.append({"kind": "designation", "text": last_title})
            continue
        for span in tr.find_all("span", class_="kvp"):
            key = span.get("data-key", "")
            if "|" not in key or not _txt(span):
                continue
            topic, field = key.split("|", 1)
            topic = _SUFFIX.sub("", topic)
            if field.endswith(".title") and topic.startswith("eu."):
                section = _txt(span)
                rows.append({"kind": "heading", "text": section, "key": field})
                last_title = section
            elif field.endswith(".title"):
                last_title = _txt(span)
                rows.append({"kind": "designation", "text": last_title})
            else:
                rows.append({"kind": "text", "topic": topic, "field": field, "text": _txt(span)})
    return rows
