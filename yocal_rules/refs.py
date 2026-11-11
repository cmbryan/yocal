"""Scripture reference normaliser: '12:27-13:8' == '12:27 – 31; 13:1 – 8' == '1 Corinthians 12:27-13:8'."""
import re


def _segments(s: str):
    m = re.search(r"\d+\s*:\s*\d+", s or "")
    if not m:
        return []
    s = re.sub(r"(?<=\d)[a-z]\b", "", s[m.start():].lower())  # drop verse letters
    s = re.sub(r"[()\[\]]", "", s).replace("–", "-").replace("—", "-").replace("‑", "-")
    s = re.sub(r"\s+", "", s)
    segs, chap = [], None
    for tok in re.split(r"[;,]", s):
        if not tok:
            continue
        m = re.fullmatch(r"(?:(\d+):)?(\d+)(?:-(?:(\d+):)?(\d+))?", tok)
        if not m:
            continue
        c1, v1, c2, v2 = m.groups()
        c1 = int(c1) if c1 else chap
        if c1 is None:
            continue
        v1 = int(v1)
        c2 = int(c2) if c2 else c1
        v2 = int(v2) if v2 else v1
        segs.append([c1, v1, c2, v2])
        chap = c2
    # a lone single-verse '8:8' alongside other segments is the optional Luke 8:8 acclamation ANCA prints only sometimes
    if len(segs) > 1:
        segs = [x for x in segs if x != [8, 8, 8, 8]]
    # union overlapping/adjacent verse intervals inside one chapter ('8:5-8a,9-15,8b' == '8:5-15')
    segs.sort(key=lambda x: (x[0], x[1]))
    uni = []
    for sg in segs:
        if uni and sg[0] == sg[2] and uni[-1][0] == uni[-1][2] == sg[0] and sg[1] <= uni[-1][3] + 1:
            uni[-1][3] = max(uni[-1][3], sg[3])
        else:
            uni.append(sg)
    segs = uni
    # merge 'c:a-c:z' + '(c+1):1-...' into one continuous span
    out = []
    for sg in segs:
        if out and sg[0] == out[-1][2] + 1 and sg[1] == 1:
            out[-1][2], out[-1][3] = sg[2], sg[3]
        else:
            out.append(sg)
    return out


def norm_ref(s: str) -> str:
    return ";".join(f"{c1}:{v1}-{c2}:{v2}" for c1, v1, c2, v2 in _segments(s))
