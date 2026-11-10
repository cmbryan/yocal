#!/usr/bin/env python3
"""Emit CSV: date_key, role, name, has_vespers_glory (+ glory_en, name_gr) from ALWB Menaion day files.
Usage: python3 -I extract.py <cog_menaion_dir> <dedes_menaion_dir> > menaion_commems.csv
Glory flag = non-empty <prefix>meVE.SticGlory.text in Greek (cog). glory_en = same in en-US dedes.
Name = English first_short/full/first_name/meLE (leading 'Memory of ' stripped), else Greek equivalent (name_lang=gr). Text is never emitted beyond names."""
import csv, re, sys
from pathlib import Path

LINE = re.compile(r'^((?:alt\d+\.)?)(\S+)\s*=\s*"(.*?)"\s*(?://.*)?$')
FNAME = re.compile(r'^me\.m(\d\d)\.d(\w\w)_')

def parse(path):
    d = {}
    for ln in path.read_text(encoding='utf-8').splitlines():
        m = LINE.match(ln)
        if m:
            d[(m.group(1).rstrip('.') or 'main', m.group(2))] = m.group(3)
    return d

def blocks(d):
    return sorted({r for r, _ in d}, key=lambda r: (r != 'main', r))

def name(d, r):
    for k in ('meDA.commemoration.first_short', 'meDA.commemoration.full', 'meDA.commemoration.first_name', 'meLE.commemoration1'):
        v = d.get((r, k), '').strip()
        if v:
            return re.sub(r'^(Memory of|Μνήμη) (the |τοῦ |τῆς |τῶν )?', '', v)
    return ''

def main(cog, en):
    w = csv.writer(sys.stdout)
    w.writerow(['date_key', 'role', 'name', 'has_vespers_glory', 'glory_en', 'name_lang'])
    for p in sorted(Path(cog).glob('m*/me.m*.ares')):
        m = FNAME.match(p.name)
        key = f'{m.group(1)}-{m.group(2)}' if m else p.name
        gr = parse(p)
        ep = Path(en) / p.parent.name / p.name.replace('gr_GR_cog', 'en_US_dedes')
        ed = parse(ep) if ep.exists() else {}
        roles = sorted(set(blocks(gr)) | set(blocks(ed)), key=lambda r: (r != 'main', r))
        for r in roles:
            if not any(k[0] == r and k[1].startswith('me') for k in list(gr) + list(ed)):
                continue
            g = int(bool(gr.get((r, 'meVE.SticGlory.text'), '').strip()))
            ge = int(bool(ed.get((r, 'meVE.SticGlory.text'), '').strip()))
            n, lang = name(ed, r), 'en'
            if not n:
                n, lang = name(gr, r), 'gr'
            w.writerow([key, r, n, g, ge, lang if n else ''])

if __name__ == '__main__':
    main(*sys.argv[1:3])
