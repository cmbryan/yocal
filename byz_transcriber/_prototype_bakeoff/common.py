"""PROTOTYPE (throwaway): shared page -> neume-line bands + components. Both arms use the same bands."""
import cv2, numpy as np

def load(path):
    img = cv2.imread(path, 0)
    return img, (img < 128).astype(np.uint8)

def lyric_baselines(bw, ymin=0):
    n, _, st, _ = cv2.connectedComponentsWithStats(bw, 8)
    H = np.zeros(bw.shape[0])
    for x, y, w, h, a in st[1:]:
        if 12 <= h <= 45 and 8 <= w <= 50 and y > ymin:
            H[y + h] += 1
    H = np.convolve(H, np.ones(9), 'same')
    peaks = []
    for y in range(5, len(H) - 5):
        if H[y] >= 12 and H[y] == H[y-5:y+6].max() and (not peaks or y - peaks[-1] > 60):
            peaks.append(y)
    return peaks

def neume_bands(bw, ymin=0):
    bl = lyric_baselines(bw, ymin)
    bands = []
    for i, b in enumerate(bl):
        top = bl[i-1] + 15 if i else b - 170
        bands.append((top, b - 38))
    return [b for b in bands if b[1] - b[0] > 80]

def components(bw, band):
    a, b = band
    sub = bw[a:b].copy()
    n, lab, st, _ = cv2.connectedComponentsWithStats(sub, 8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = st[i]
        if area < 12 or h > 110 or (x < 140 and h > 55):  # specks; drop-cap initial
            continue
        crop = (lab[y:y+h, x:x+w] == i).astype(np.uint8)
        out.append(dict(x=int(x), y=int(y + a), w=int(w), h=int(h), area=int(area), crop=crop))
    out.sort(key=lambda c: c['x'])
    return out
