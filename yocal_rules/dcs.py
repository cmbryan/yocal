"""GOA Digital Chant Stand secondary key, keys only (no text kept): fetch -> data-key walk -> slot attributes.

URL: https://dcs.goarch.org/goa/dcs/h/s/YYYY/MM/DD/<code>/en/index.html ; `ve` on date D = Vespers served the evening of D.
Only ~2026 is online and pages can vanish, so a missing/empty page is a non-blocking `no key (DCS)`.
"""
from __future__ import annotations

import datetime as dt
import os
import re
import urllib.error
import urllib.request

import yaml

from .rules import DATA

BASE = "https://dcs.goarch.org/goa/dcs/h/s"
UA = {"User-Agent": "yocal-rules/0.1"}
CODES = {"vespers": ["ve"], "matins": ["ma"], "liturgy": ["li", "h91"]}
KV = re.compile(r"<span class='kvp' data-key='([^']*)'>([^<]*)")


def url(date: dt.date, code: str) -> str:
    return f"{BASE}/{date:%Y/%m/%d}/{code}/en/index.html"


def fetch(date: dt.date, code: str, cache: str, offline: bool = False) -> str | None:
    os.makedirs(cache, exist_ok=True)
    fn = os.path.join(cache, f"dcs-{date.isoformat()}-{code}.html")
    if os.path.exists(fn):
        return open(fn, encoding="utf-8").read() or None
    if offline:
        return None
    try:
        html = urllib.request.urlopen(urllib.request.Request(url(date, code), headers=UA), timeout=40).read().decode("utf-8", "replace")
    except urllib.error.HTTPError:
        html = ""
    if html and not KV.search(html):  # empty shell (HTTP 200, no keys)
        html = ""
    open(fn, "w", encoding="utf-8").write(html)
    return html or None


def keys(html: str):
    """-> ordered [(topic, field, has_text)] for non-empty spans; topic has the language/provider suffix removed."""
    out = []
    for k, text in KV.findall(html):
        if not text.strip() or "|" not in k:
            continue
        topic, field = k.split("|", 1)
        out.append((re.sub(r"_[a-z]{2}_[A-Z]{2}_\w+$", "", topic), field))
    return out


def _first(ks, topic_re, field_re=".*"):
    for t, f in ks:
        m = re.match(topic_re, t)
        if m and re.match(field_re, f):
            return m
    return None


def _kmap():
    return yaml.safe_load(open(os.path.join(DATA, "dcs_map.yaml"), encoding="utf-8"))


def _apol(ks):
    r = {}
    m = _first(ks, r"he\.a\.m(\d)", r"heAU\.\w+\.text")
    if m:
        r["res_tone"] = int(m.group(1))
    r["saint"] = _first(ks, r"me\.m\d\d\.d\d\d", r"meVE\.Apolytikion1") is not None
    return r if "res_tone" in r else None


def _chapverse(html: str, topic_re: str):
    m = re.search(r"data-key='(%s)_[a-z]{2}_[A-Z]{2}_\w+\|[^']*chapverse'>([^<]*)" % topic_re, html)
    return m.group(2).strip() if m else None


def parse(service: str, pages: dict):
    """pages: code -> html. -> (key dict slot->attrs, notes)."""
    k, notes = {}, []
    if service == "vespers":
        ks = keys(pages["ve"])
        res = len({f for t, f in ks if re.match(r"oc\.m\d\.d\d$", t) and re.match(r"ocVE\.Stichera\d+\.text", f)})
        if res:
            k["vespers.lihc.stichera"] = dict(res=res)
        a = _apol(ks)
        if a:
            k["vespers.apolytikia"] = a
        if any("prokeimenon.saturday" in f for t, f in ks):
            k["vespers.prokeimenon"] = dict(kind="lord_is_king")
    elif service == "matins":
        ks = keys(pages["ma"])
        m = _first(ks, r"oc\.m(\d)\.d1", r"ocMA\.Kathisma\d+")
        if m:
            k["matins.kathismata"] = dict(tone=int(m.group(1)))
        m = _first(ks, r"eo\.e(\d+)")
        if m:
            k["matins.eothinon_gospel"] = dict(number=int(m.group(1)))
        a = _apol(ks)
        if a:
            k["matins.apolytikia"] = a
        m = _first(ks, r"oc\.m(\d)\.d1", r"ocMA\.Kontakion")
        if m:
            k["matins.kontakion"] = dict(kind="resurrectional", tone=int(m.group(1)))
        lauds = len({(t, f) for t, f in ks if re.match(r"oc\.m\d\.d1$", t) and re.match(r"ocMA\.Lauds\d+\.text", f)})
        if lauds:
            k["matins.praises"] = dict(res=lauds)
    else:
        ks = keys(pages["li"])
        a = _apol(ks)
        if a:
            k["liturgy.apolytikia"] = a
        km = _kmap()["kontakion"]
        for t, f in ks:
            m = re.match(r"ho\.ho\d+$", t)
            kk = re.match(r"(hoTY\.Key\d+)\.text", f)
            if m and kk and kk.group(1) in km:
                k["liturgy.kontakion"] = dict(km[kk.group(1)])
                break
            if m and kk:
                notes.append(f"DCS kontakion key {kk.group(1)} not in dcs_map.yaml")
        ep = _first(ks, r"le\.ep\.(me|mc)", r"le(me|mc)LI\.Epistle\.chapverse")
        ref = _chapverse(pages["li"], r"le\.ep\.(?:me|mc)[\w.]*")
        if ep and ref:
            k["liturgy.epistle"] = dict(owner="saint" if ep.group(1) == "me" else "sunday", ref=ref)
        gref = _chapverse(pages["li"], r"le\.go\.(?:lu|mt|mk|jn|mc)[\w.]*")
        if gref:
            k["liturgy.gospel"] = dict(ref=gref)
        if _first(ks, r"menaion\.verses", r"psLI\.m\d\d\.d\d\d\.prokeimenon"):
            k["liturgy.prokeimenon"] = dict(owner="saint")
        elif _first(ks, r"liturgical\.verses", r"psLI\.sunday\.m\d\.prokeimenon"):
            k["liturgy.prokeimenon"] = dict(owner="sunday")
    return k, notes


def key_for(service: str, date: dt.date, cache: str, offline: bool = False):
    """-> (key, [urls used], notes). Empty key => `no key (DCS)`."""
    pages, used, notes = {}, [], []
    for code in CODES[service]:
        h = fetch(date, code, cache, offline)
        if h:
            pages[code] = h
            used.append(url(date, code))
        elif code == CODES[service][0]:
            return {}, used, [f"DCS page unavailable: {url(date, code)}"]
    if service == "liturgy" and "h91" not in pages:
        notes.append("DCS h91 (readings for the day) unavailable")
    k, n = parse(service, pages)
    return k, used, notes + n
