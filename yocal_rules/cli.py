"""python -m yocal_rules DATE SERVICE  ->  service document + supplement (Markdown)."""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

from . import assemble, calfacts, render, report

DEFAULT_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "yocal_rules")


def _common(ap):
    ap.add_argument("--out", default="build/service", help="output directory (default build/service)")
    ap.add_argument("--db", default=calfacts.DEFAULT_DB, help="YOCal master DB")
    ap.add_argument("--cache", default=DEFAULT_CACHE, help="download cache for ANCA/DCS files (never committed)")
    ap.add_argument("--offline", action="store_true", help="use cached ANCA/DCS files only")
    ap.add_argument("--no-compare", action="store_true", help="skip both comparisons")
    ap.add_argument("--no-dcs", action="store_true")
    ap.add_argument("--no-anca", action="store_true")
    ap.add_argument("--strip-uk", action="store_true", help="omit UK-origin commemorations from the document")
    ap.add_argument("--fail-on-diff", action="store_true", help="exit 2 if there is an unexplained ANCA diff")


def _run(a, service, date):
    """Build one service; write its document and supplement. -> (result, doc, base path)."""
    r = assemble.build(service, date, a.db, a.strip_uk)
    if not a.no_compare:
        assemble.compare_keys(r, a.cache, a.offline, dcs_on=not a.no_dcs, anca_on=not a.no_anca)
    os.makedirs(a.out, exist_ok=True)
    base = os.path.join(a.out, f"{date.isoformat()}-{service}")
    doc = render.service_document(r)
    open(base + ".md", "w", encoding="utf-8").write(doc)
    open(base + "-supplement.md", "w", encoding="utf-8").write(report.supplement(r))
    return r, doc, base


def weekend(argv) -> int:
    """python -m yocal_rules weekend DATE: Saturday Great Vespers + Sunday Matins + Sunday Liturgy (+ Agape Vespers when the Sunday is Pascha)."""
    ap = argparse.ArgumentParser(prog="yocal_rules weekend", description="Build the whole weekend (Sat Great Vespers, Sun Matins, Sun Liturgy) and a combined Markdown file.")
    ap.add_argument("date", type=dt.date.fromisoformat, help="the Saturday, or any date in that weekend (Mon-Fri resolve to the coming Saturday)")
    _common(ap)
    a = ap.parse_args(argv)
    sat = a.date + dt.timedelta(days=(5 - a.date.weekday()) % 7) if a.date.weekday() != 6 else a.date - dt.timedelta(days=1)
    sun = sat + dt.timedelta(days=1)
    plan = [("vespers", sat), ("matins", sun), ("liturgy", sun)]
    if sun == calfacts.pascha(sun.year):  # Pascha weekend: Holy Saturday Vesperal Liturgy, Paschal Matins, Liturgy, and Agape Vespers that evening
        plan.append(("agape", sun))
    parts, paths, blocked = [], [], False
    try:
        for service, d in plan:
            r, doc, base = _run(a, service, d)
            parts.append(doc.rstrip() + "\n")
            paths += [base + ".md", base + "-supplement.md"]
            print(f"{service}: {report.summary_line(r)}", file=sys.stderr)
            blocked = blocked or bool(report.gate(r))
    except (assemble.OutOfScope, LookupError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    combined = os.path.join(a.out, f"{sat.isoformat()}-weekend.md")
    # demote each document's headings one level so the weekend has a single H1
    body = "\n\n".join("\n".join(("#" + ln) if ln.startswith("#") else ln for ln in p.splitlines()) + "\n" for p in parts)
    open(combined, "w", encoding="utf-8").write(f"# Weekend of {sat:%-d %B %Y}\n\n" + body)
    print("\n".join([combined] + paths))
    return 2 if (a.fail_on_diff and blocked) else 0


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if argv and argv[0] == "weekend":
        return weekend(argv[1:])
    ap = argparse.ArgumentParser(prog="yocal_rules", description="Generate the Variable parts of a service and review them against ANCA and the Digital Chant Stand. "
                                 "Also: 'yocal_rules weekend DATE' builds Sat Vespers + Sun Matins + Sun Liturgy.")
    ap.add_argument("date", type=dt.date.fromisoformat, help="service date YYYY-MM-DD (Great Vespers: the Saturday evening)")
    ap.add_argument("service", choices=assemble.SERVICES)
    _common(ap)
    ap.add_argument("--print", dest="show", action="store_true", help="print the service document to stdout")
    a = ap.parse_args(argv)
    try:
        r, doc, base = _run(a, a.service, a.date)
    except (assemble.OutOfScope, LookupError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if a.show:
        print(doc)
    print(report.summary_line(r), file=sys.stderr)
    print(f"{base}.md\n{base}-supplement.md")
    return 2 if (a.fail_on_diff and report.gate(r)) else 0
