"""Prokeimenon and Alleluia verses for each Sunday tone, from the GOA Digital Chant Stand Liturgy readings pages (`li2`).

The page for any Sunday carries `psLI.sunday.mN.{prokeimenon,alleluia}.vK` for that Sunday's tone N; crawling the published window (about
eight months, so every tone) gives a tone table. Third-party text: kept in git-ignored local/dcs_tones.json with the source page of each tone.

    python -m yocal_service.dcs_tones [DAYS]
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from . import dcs_page, music

LOCAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local")
PATH = os.path.join(LOCAL, "dcs_tones.json")
FIELD = re.compile(r"^psLI\.sunday\.m(\d)\.(prokeimenon|alleluia)\.v(\d)\.text$")


def build(days: int = 300):
    from yocal_rules import dcs as rules_dcs
    start = dt.date.today()
    start += dt.timedelta(days=(6 - start.weekday()) % 7)
    sundays = [start + dt.timedelta(weeks=i) for i in range(days // 7)]

    def one(d):
        try:
            return d, rules_dcs.fetch(d, "li2", music.CACHE, False)
        except Exception:
            return d, None
    table = {}
    with ThreadPoolExecutor(8) as ex:
        for d, html in ex.map(one, sundays):
            if not html:
                continue
            for r in dcs_page.parse(html):
                m = r["kind"] == "text" and FIELD.match(r["field"])
                if m:
                    e = table.setdefault(m.group(1), {"source": f"GOA Digital Chant Stand, Divine Liturgy readings page, {d.isoformat()} ({rules_dcs.url(d, 'li2')})"})
                    e.setdefault(m.group(2), {})[f"v{m.group(3)}"] = r["text"].strip()
    os.makedirs(LOCAL, exist_ok=True)
    json.dump(table, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("tones with verses:", sorted(table), "->", PATH)


def get(tone) -> dict:
    if not tone or not os.path.exists(PATH):
        return {}
    return json.load(open(PATH, encoding="utf-8")).get(str(tone), {})


if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
