"""PROTOTYPE (throwaway): classical-CV arm.

Templates = connected components of the 1905 Anastasimatarion p.3 (one typeface), labelled once by cluster.
Classify = 1-NN on a size-normalised shape vector. Assembly = geometry only. No per-book templates:
that labelling cost is exactly what this arm would need per typeface.
"""
import os, json, cv2, numpy as np
from common import load, neume_bands, components
from vocab import export, BASES

CLUSTER_LABEL = {}
for ids, lab in [((0,), 'petasti'), ((1, 6, 32, 34, 54, 67), 'apostrophos'), ((2,), 'ison'), ((3,), 'oligon'),
                 ((4,), 'yporroi'), ((5,), 'klasma'), ((9, 52, 39, 40, 51, 28, 61), 'gorgon'),
                 ((10, 42, 55, 16), 'vareia'), ((47, 57), 'ypsili'),
                 ((12, 14, 15, 17, 24, 25, 27, 33, 38, 41, 43, 50, 60, 63, 65), 'kentima'),
                 ((22, 35), 'elaphron'), ((21, 58), 'psifiston'), ((44,), 'digorgon'), ((56, 70), 'm_pa'),
                 ((45,), 'heteron')]:
    for i in ids:
        CLUSTER_LABEL[i] = lab
DOT = 'dot'


def feat(crop, band_h):
    h, w = crop.shape; m = max(h, w)
    pad = np.zeros((m, m), np.uint8); pad[(m-h)//2:(m-h)//2+h, (m-w)//2:(m-w)//2+w] = crop
    v = cv2.resize(pad.astype(np.float32), (24, 24), interpolation=cv2.INTER_AREA).ravel()
    v = (v - v.mean()) / (v.std() + 1e-6)
    return np.concatenate([v, [np.log(w / h) * 4, (max(w, h) / band_h) * 20]])


def train():
    """Re-run the same leader clustering as cluster.py on p-003 to recover per-component labels."""
    _, bw = load('pages/p-003.png')
    X, Y, cent = [], [], []
    for b in neume_bands(bw, 1250):
        bh = b[1] - b[0]
        for c in components(bw, b):
            f0 = feat(c['crop'], bh)
            # cluster ids from the original (absolute-size) features, to reuse the labelled montage
            cr = c['crop']; h, w = cr.shape; m = max(h, w)
            pad = np.zeros((m, m), np.uint8); pad[(m-h)//2:(m-h)//2+h, (m-w)//2:(m-w)//2+w] = cr
            v = cv2.resize(pad.astype(np.float32), (24, 24), interpolation=cv2.INTER_AREA).ravel()
            v = (v - v.mean()) / (v.std() + 1e-6)
            fo = np.concatenate([v, [np.log(w / h) * 4, np.log(max(w, h)) * 2]])
            d = [np.linalg.norm(fo - k) for k in cent]
            if d and min(d) < 14:
                k = int(np.argmin(d))
            else:
                cent.append(fo); k = len(cent) - 1
            X.append(f0); Y.append(CLUSTER_LABEL.get(k, DOT if c['area'] < 120 else 'unknown'))
    return np.array(X), Y


def binarise(gray, photo):
    if photo:
        g = cv2.GaussianBlur(gray, (3, 3), 0)
        return (cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 15) > 0).astype(np.uint8)
    return (gray < 128).astype(np.uint8)


def recognise(gray, rect, photo, X, Y):
    x0, y0, x1, y1 = rect
    bw = binarise(gray[y0:y1, x0:x1], photo)
    bh = y1 - y0
    n, lab, st, _ = cv2.connectedComponentsWithStats(bw, 8)
    glyphs = []
    min_area = max(4, int((bh / 130) ** 2 * 12))
    for i in range(1, n):
        x, y, w, h, a = st[i]
        if a < min_area or h > bh * 0.85:
            continue
        crop = (lab[y:y+h, x:x+w] == i).astype(np.uint8)
        f = feat(crop, bh)
        d = np.linalg.norm(X - f, axis=1); j = int(np.argmin(d))
        conf = float(np.exp(-d[j] / 12))
        g = Y[j] if a > min_area * 3 else DOT
        glyphs.append(dict(id=g, x=int(x), y=int(y), w=int(w), h=int(h), conf=round(conf, 3)))
    glyphs.sort(key=lambda g: g['x'])
    return glyphs


MAIN = {'oligon', 'petasti', 'ison'}
STACKABLE = {'apostrophos', 'elaphron', 'yporroi', 'chamili', 'running_elaphron'}


def assemble(glyphs, bh):
    """Geometry-only: main bodies own anything whose x-centre falls in their span; vareia binds rightwards."""
    for g in glyphs:
        g['cx'] = g['x'] + g['w'] / 2; g['cy'] = g['y'] + g['h'] / 2
    mains = [g for g in glyphs if g['id'] in MAIN]
    row = np.median([g['cy'] for g in mains]) if mains else bh / 2
    used = set(); groups = []
    bodies = [g for g in glyphs if g['id'] in MAIN or (g['id'] in BASES and abs(g['cy'] - row) < bh * 0.18)]
    # stackable neumes sitting over a main body are attachments, not bodies
    for g in list(bodies):
        if g['id'] in STACKABLE and any(m['x'] - 3 <= g['cx'] <= m['x'] + m['w'] + 3 and g['cy'] < m['cy'] - 3 for m in mains):
            bodies.remove(g)
    for b in bodies:
        used.add(id(b))
        groups.append(dict(base=b['id'], attach=[], conf=b['conf'], x=b['x'], w=b['w'], cy=b['cy']))
    groups.sort(key=lambda g: g['x'])
    pending_vareia = False
    for g in glyphs:
        if id(g) in used:
            continue
        if not groups:
            continue
        if g['id'] == 'vareia':
            nxt = [G for G in groups if G['x'] >= g['x']]
            if nxt:
                nxt[0]['attach'].append(('vareia', 'left'))
            continue
        if g['id'] in ('m_pa',):
            groups.append(dict(base='martyria', attach=[('m_pa', None)], conf=g['conf'], x=g['x'], w=g['w'], cy=g['cy']))
            continue
        inside = [G for G in groups if G['x'] - 4 <= g['cx'] <= G['x'] + G['w'] + 4]
        G = min(inside or groups, key=lambda G: abs(G['x'] + G['w'] / 2 - g['cx']))
        if not inside:
            G['ambiguous'] = True
        pos = 'above' if g['cy'] < G['cy'] else 'below'
        if g['id'] == 'ypsili':
            pos = 'right' if g['cx'] > G['x'] + G['w'] / 2 else 'left'
        G['attach'].append((g['id'], pos))
        G['conf'] = min(G['conf'], g['conf'])
    for G in groups:  # two kentima above -> kentimata
        ka = [a for a in G['attach'] if a == ('kentima', 'above')]
        if len(ka) >= 2:
            G['attach'] = [a for a in G['attach'] if a != ('kentima', 'above')] + [('kentimata', 'above')]
        G['attach'] = [a for a in G['attach'] if a[0] != 'unknown'] + \
            ([] if all(a[0] != 'unknown' for a in G['attach']) else [])
        if any(a[0] == 'unknown' for a in G['attach']):
            G['conf'] = 0.3
    groups.sort(key=lambda g: g['x'])
    return groups


if __name__ == '__main__':
    X, Y = train()
    print('templates', len(Y), {k: Y.count(k) for k in sorted(set(Y))})
    os.makedirs('out/cv', exist_ok=True)
    samples = json.load(open('samples.json'))
    dump = {}
    for book, s in samples.items():
        gray = cv2.imread(f'pages/{book}.png', 0)
        allg = []
        for i, rect in enumerate(s['lines']):
            gl = recognise(gray, rect, s['tier'] == 'photo', X, Y)
            dump[f'{book}-{i}'] = gl
            if allg:
                allg.append(dict(linebreak=True))
            allg += assemble(gl, rect[3] - rect[1])
        n, f = export(allg, f'out/cv/{book}.byzx', f'CV {book}', thr=0.3)
        print(book, 'groups', n, 'flagged', f)
    json.dump(dump, open('out/cv/glyphs.json', 'w'), indent=0)
