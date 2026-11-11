"""Service document: only what the service needs (Variable parts as placeholder hymn references). No rules/provenance here."""
from __future__ import annotations

import datetime as dt
import re

TBD = "[to be determined]"


def _short(name: str) -> str:
    return name or "the saint of the day"


_SPLIT = re.compile(r"(?<!\bSt)(?<!\bSS)(?<!\bSts)(?<!\bVen)(?<!\bMt)(?<!\bBl)(?<!\bFr)(?<!\bAbp)(?<!\bBp)\.\s+(?=[A-Z])")


def _items(text: str) -> list:
    """Split a run-on commemoration string into one entry per saint (keeps 'St.'/'SS.' abbreviations intact)."""
    return [x.strip().rstrip(".") for x in _SPLIT.split(text.strip()) if x.strip()]


def _dismissal_saint(f: dict) -> str:
    """The saint named in the dismissal: the principal commemoration, else the first of the other commemorations."""
    if f["principal_name"]:
        return f["principal_name"]
    items = _items(f["other_commem"]) if f["other_commem"] else []
    return items[0] if items else "the saint of the day"


def _tone(t):
    return f"Tone {t}"


def _apol(f, fill, liturgy=False):
    lines = [f"- Apolytikion of the Resurrection — Octoechos {_tone(fill['res_tone'])}"] if fill["res_tone"] else []
    if fill.get("feast"):  # fore/after-feast period (fore_after.yaml): great saint (if any), then the feast's troparion
        if f.get("feast_period_saint"):
            lines.append(f"- Apolytikion of {_short(f['principal_name'])} — Menaion {f['mmdd']}")
        lines.append(f"- Apolytikion of the feast ({f.get('fore_after') or f['principal_name']}) — Menaion {f['mmdd']}")
        if liturgy:
            lines.append("- Apolytikion of the patron saint or feast of the temple")
        elif f.get("feast_period_class") == "saint":  # a saint's feast (Jun 24 p.417, Aug 29 p.466): Theotokion follows
            lines.append("- Theotokion (in the tone of the apolytikion it follows)")
        return lines
    if fill["saint"]:
        lines.append(f"- Apolytikion of {_short(f['principal_name'])} — Menaion {f['mmdd']}")
    if liturgy:
        lines.append("- Apolytikion of the patron saint or feast of the temple")
    else:
        lines.append("- Theotokion (in the tone of the apolytikion it follows)")
    return lines


def describe(slot: str, res, f: dict):
    """-> list of markdown lines for one slot."""
    fl = res.fill
    if res.status == "missing":
        return [f"- {TBD}"]
    if fl.get("parts") and slot != "liturgy.dismissal":  # Rules for proper days (e.g. pentecostarion.yaml) spell out their parts
        return [f"- {re.sub(r'{(tone|desig|mmdd|sunday|epistle_ref|gospel_ref|feast_matins_gospel_ref|liturgy_author)}', lambda m: str((f.get('desig_g') or f.get('desig')) if m.group(1) == 'sunday' else f.get(m.group(1)) or ''), p)}" for p in fl["parts"]]  # {tone} etc. for movable days
    if slot == "vespers.lihc.stichera":
        out = [f"- {fl['res']} resurrectional stichera — Octoechos {_tone(f['tone'])}"]
        if fl.get("of"):  # labelled blocks (fore_after.yaml)
            lab = {"feast": f"the feast ({f.get('fore_after') or f['principal_name']})", "forefeast": f"the forefeast ({f.get('fore_after')})",
                   "saint": _short(f["principal_name"]), "sunday": f"the Sunday ({f['desig']})"}
            return out + [f"- {n} stichera of {lab.get(o, o)} — Menaion {f['mmdd']}" for n, o in zip(fl["other"], fl["of"])]
        if len(fl["other"]) == 1:
            out.append(f"- {fl['other'][0]} stichera of {_short(f['principal_name'])} — Menaion {f['mmdd']}")
        else:
            out.append(f"- {fl['other'][0]} stichera of {_short(f['principal_name'])} — Menaion {f['mmdd']}")
            out += [f"- {n} stichera of the second commemoration — Menaion {f['mmdd']}" for n in fl["other"][1:]]
        return out
    if slot == "vespers.prokeimenon":
        if fl.get("kind") == "great":
            return [f"- Great prokeimenon of the feast — {_tone(fl['tone'])}"]
        return [f"- Saturday-evening prokeimenon (“The Lord is King”) — {_tone(fl['tone'])}"]
    if slot.endswith(".apolytikia"):
        return _apol(f, fl, liturgy=slot.startswith("liturgy"))
    if slot == "matins.kathismata":
        return [f"- Resurrectional kathismata hymns — Octoechos {_tone(fl['tone'])}"]
    if slot == "matins.prokeimenon":
        return [f"- Resurrectional prokeimenon — {_tone(fl['tone'])}"]
    if slot == "matins.eothinon_gospel":
        return [f"- Eothinon Gospel no. {fl['number']}"]
    if slot == "matins.praises":
        res = fl.get("res", fl["total"])
        if fl.get("other"):
            oth = " + ".join(str(n) for n in fl["other"])
            whom = "the feast" if f.get("feast_period") else "the saint / commemoration"
            return [f"- {fl['total']} stichera: {res} resurrectional — Octoechos {_tone(f['tone'])}; {oth} for {whom}"]
        return [f"- {fl['total']} resurrectional stichera — Octoechos {_tone(f['tone'])}"]
    if slot == "liturgy.kontakion":
        if fl["kind"] == "ordinary_theotokos":
            return [f"- Ordinary kontakion of the Theotokos — {_tone(fl['tone'])}"]
        return [f"- Kontakion ({fl['kind']}) — {_tone(fl['tone'])}"]
    if slot == "liturgy.prokeimenon":
        if fl["owner"] == "saint":
            return [f"- Prokeimenon of {_short(f['principal_name'])} — Menaion {f['mmdd']}"]
        return [f"- Prokeimenon of the Sunday — Octoechos {_tone(f['tone'])}"]
    if slot == "liturgy.epistle":
        who = _short(f["principal_name"]) if fl["owner"] == "saint" else f"the Sunday, {f['desig']}"
        return [f"- {fl['ref']} — for {who}"]
    if slot == "liturgy.alleluia":
        return [f"- Alleluia — {_tone(fl['tone'])}, with the verses of the day"]
    if slot == "liturgy.gospel":
        return [f"- {fl['ref']} ({f['desig_g'] or f['desig']})"]
    if slot == "liturgy.author":
        return [f"- Liturgy of St. {fl['author']}"]
    if slot == "liturgy.dismissal":
        if fl.get("parts"):
            names = "; ".join([fl["author"]] + fl["parts"])
        elif fl.get("named_as", "").startswith("the Archangel"):
            names = f"{fl['author']}; {_short(f['principal_name'])} (in the bodiless-powers clause)"
        elif fl.get("named_as", "").startswith("the Sunday"):
            names = f"{fl['author']}; {f['desig_g'] or f['desig']} (the Sunday's own commemoration)"
        else:
            names = f"{fl['author']}" + (f"; {_dismissal_saint(f)}" if fl["saint_named"] else "")
        out = [f"- Great Dismissal naming: {names}"]
        if f["uk_commem"]:
            out.append("- Local (UK) commemorations:")
            out += [f"  - {x}" for x in _items(f["uk_commem"])]
        return out
    if slot == "liturgy.dismissal_phrase":
        ph = {"resurrection": "“May He who rose from the dead …”",
              "feast_and_resurrection": f"the characteristic phrase of the feast ({f.get('fore_after') or f['principal_name']}), then “and rose from the dead …”",
              "feast": "the characteristic phrase of the feast"}.get(fl.get("phrase"), str(fl.get("phrase")))
        cl = {"theotokos": "; the feast named in the Theotokos clause", "cross": "; the Elevation named in the Cross clause",
              "forerunner": "; the feast named in the Forerunner clause"}.get(fl.get("clause"), "")
        return [f"- Opening: {ph}{cl}"]
    return [f"- {fl}"]


TITLES = {"vespers": "Great Vespers", "matins": "Matins", "liturgy": "Divine Liturgy", "agape": "Agape Vespers"}


def service_document(r) -> str:
    f, sd = r.facts, r.service_date
    ld = dt.date.fromisoformat(f["date"])
    head = f"# {TITLES[r.service]} — {sd:%A %-d %B %Y}"
    if r.service == "vespers":
        head += f" (eve of {ld:%A %-d %B})"
        if f["pascha_days"] == 0:
            head = f"# Vesperal Liturgy of Holy Saturday — {sd:%A %-d %B %Y} (eve of Pascha)"
    L = [head, ""]
    tbd = []
    day = " · ".join(x for x in [f"{f['desig']}" if f["desig"] else "", f"Tone {f['tone']}" if f["tone"] else "",
                                 f"Eothinon {f['eothinon']}" if f["eothinon"] else "", f["desig_g"] or ""] if x)
    if day:
        L += [f"**{day}**", ""]
    author = next(((m, x) for sl, m, x in r.slots if sl == "liturgy.author"), None)
    if author:  # the Liturgy's author is stated under the date/tone line, not in a section of its own
        m, x = author
        if x.status == "missing":
            L += [f"**Liturgy: {TBD}**", ""]
            tbd.append(m["label"])
        else:
            L += [f"**Liturgy of St. {x.fill['author']}**", ""]
    if f["principal_name"]:
        L += [f"Commemoration: {f['principal_name']}", ""]
    if f["other_commem"]:
        L.append("Also commemorated:")
        L += [f"- {x}" for x in _items(f["other_commem"])]
        L.append("")
    if not f["in_slice"]:
        L += [f"> **Incomplete:** this date is outside the implemented Rules ({'; '.join(f['slice_reasons'])}). "
              f"Parts marked {TBD} need Rules not yet written.", ""]
    for slot, meta, res in r.slots:
        if slot == "liturgy.author":
            continue
        L += [f"## {meta['label']}", ""]
        L += describe(slot, res, f)
        L.append("")
        if res.status == "missing":
            tbd.append(meta["label"])
    L.append("---")
    L.append(f"*Slots marked {TBD}: {', '.join(tbd)}.*" if tbd else "*All Variable parts determined.*")
    return "\n".join(L).rstrip() + "\n"
