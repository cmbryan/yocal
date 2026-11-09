"""PROTOTYPE (throwaway): parse Sunday ORTHROS/READ ANCA files into per-slot keys; compare with Rule predictions
(#6 Typikon, #19 Basil, #21/#22 prokeimenon, #25 kontakion windows, #27 Matins kontakion). Untracked outputs in ../sun_*.csv."""
import csv, re, subprocess, sqlite3, datetime as dt, collections, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "pdfs_sun"
DB = ROOT.parent.parent / "db/yocal/YOCal_Master.db"
W = {w: i for i, w in enumerate("ZERO ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN".split())}
ORD = {w: i + 1 for i, w in enumerate("FIRST SECOND THIRD FOURTH FIFTH SIXTH SEVENTH EIGHTH NINTH TENTH ELEVENTH".split())}
HEAD = re.compile(r"^\s*([A-Z][A-Z0-9 ,.:()’'/*+&-]{5,})$")

def text(p):
    return subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True).stdout

def tone(h):
    m = re.search(r"IN TONE (\w+)", h)
    if not m: return None
    w = m.group(1); return W.get(w) or (int(w) if w.isdigit() else None)

def heads(t):
    out = []
    for ln in t.splitlines():
        m = HEAD.match(ln)
        if m and not re.match(r"^\s*(PSALM \d+|THE (LITTLE|GREAT) LITANY|LITANY)$", ln.strip()):
            h = re.sub(r"\s*\((CHANT|CHORAL|KAZAN|KARAM|EL MASSIH)\)", "", m.group(1)).strip()
            out.append(h)
    return out

def parse_read(t):
    k = {}
    k["rite"] = "basil" if re.search(r"Divine Liturgy of St\.? Basil", t, re.I) else ("chrys" if re.search(r"Chrysostom", t) else "unspec")
    hs = heads(t)
    k["heads"] = hs
    kon = [h for h in hs if "KONTAKION" in h and "KOINONIKON" not in h]
    k["kontakion"] = kon[0] if kon else ""
    k["kon_tone"] = tone(kon[0]) if kon else None
    k["apolytikia"] = [h for h in hs if "APOLYTIKION" in h]
    k["eisodikon"] = next((h for h in hs if "EISODIKON" in h), "")
    k["antiphons"] = sum("ANTIPHON" in h and "ANTI-TRISAGION" not in h for h in hs)
    k["trisagion_sub"] = next((h for h in hs if "TRISAGION" in h), "")
    k["megalynarion"] = next((h for h in hs if "MEGALYNARION" in h), "")
    k["koinonikon"] = next((h for h in hs if "KOINONIKON" in h), "")
    m = re.search(r"Epistle[^\n]*\n?[^\n]*\((\d+:\d+[-–\d:,; a-z]*)\)", t)
    k["epistle_ref"] = m.group(1).strip() if m else ""
    m = re.search(r"Holy Gospel according to St\.? \w+\.?\s*\(([^)]+)\)", t)
    k["gospel_ref"] = m.group(1).strip() if m else ""
    m = re.search(r"THE EPISTLE\s*\n\s*\(For ([^)]+)\)", t)
    k["epistle_for"] = m.group(1) if m else ""
    m = re.search(r"THE EPISTLE\s*\n(?:\s*\(For[^\n]*\n)?\s*(\S[^\n]*)\n", t)
    k["prokeimenon_text"] = m.group(1).strip()[:70] if m else ""
    k["has_alleluia"] = bool(re.search(r"Alleluia", t.split("THE EPISTLE")[-1][:1500])) if "THE EPISTLE" in t else False
    return k

def parse_orth(t):
    k = {}
    hs = heads(t); k["heads"] = hs
    k["eothinon"] = next((ORD.get(re.search(r"THE (\w+) EOTHINON GOSPEL", h).group(1)) for h in hs if re.search(r"THE \w+ EOTHINON GOSPEL", h)), None)
    k["kathismata"] = bool(re.search(r"KATHISMATA", t))
    m = re.search(r"KATHISMATA[^\n]*", t); k["kathismata_head"] = m.group(0).strip() if m else ""
    pk = [h for h in hs if "PROKEIMENON" in h]
    k["prokeimenon"] = pk[0] if pk else ""
    k["prok_tone"] = tone(pk[0]) if pk else None
    k["ainoi_tone"] = next((tone(h) for h in hs if "AINOI" in h), None)
    k["doxology_tone"] = next((tone(h) for h in hs if "GREAT DOXOLOGY" in h), None)
    k["final_troparion"] = next((h for h in hs[::-1] if h.startswith(("TROPARION", "APOLYTIKION", "RESURRECTIONAL APOLYTIKION")) ), "")
    kon = [h for h in hs if "KONTAKION" in h]
    k["kontakion"] = kon[0] if kon else ""
    k["canon"] = [h for h in hs if "CANON" in h or "KATAVASIA" in h]
    k["exapost"] = [h for h in hs if "EXAPOSTEILARION" in h or "PHOTAGOGIKON" in h]
    k["apolyt"] = [h for h in hs if "APOLYTIKION" in h]
    k["theotokion"] = [h for h in hs if "THEOTOKION" in h]
    k["doxasticon"] = [h for h in hs if "DOXASTICON" in h]
    k["psalm50_trop"] = next((h for h in hs if "AFTER PSALM 50" in h), "")
    return k

def main():
    db = sqlite3.connect(DB)
    rows = []
    for rf in sorted(PDF.glob("*-READ.pdf")):
        d = rf.name[:10]
        of = PDF / f"{d}-ORTHROS.pdf"
        r = parse_read(text(rf)); o = parse_orth(text(of)) if of.exists() else {}
        rows.append(dict(date=d, **{"L_" + a: (";".join(map(str, b)) if isinstance(b, list) else b) for a, b in r.items() if a != "heads"},
                         **{"M_" + a: (";".join(map(str, b)) if isinstance(b, list) else b) for a, b in o.items() if a != "heads"}))
    keys = sorted({k for r in rows for k in r})
    with open(ROOT / "sun_keys.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date"] + [k for k in keys if k != "date"], restval=""); w.writeheader(); w.writerows(rows)
    print(len(rows), "dates parsed")

if __name__ == "__main__":
    main()
