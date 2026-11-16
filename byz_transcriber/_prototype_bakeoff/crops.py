"""PROTOTYPE: write line crops (neume band + lyric context) for viewing/transcription."""
import cv2, json, os
os.makedirs('crops', exist_ok=True)
for k, s in json.load(open('samples.json')).items():
    im = cv2.imread(f'pages/{k}.png', 0)
    for i, (x0, y0, x1, y1) in enumerate(s['lines']):
        h = y1 - y0
        c = im[y0:y1 + int(h * .6), x0:x1]
        f = 1700 / c.shape[1]
        cv2.imwrite(f'crops/{k}-{i}.png', cv2.resize(c, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC))
