"""PROTOTYPE: grid overlay for picking line crops (coords in native px)."""
import sys, cv2
im = cv2.cvtColor(cv2.imread(sys.argv[1], 0), cv2.COLOR_GRAY2BGR)
step = int(sys.argv[3]) if len(sys.argv) > 3 else 100
for y in range(0, im.shape[0], step):
    cv2.line(im, (0, y), (im.shape[1], y), (0, 0, 255), 1); cv2.putText(im, str(y), (2, y + 14), 0, .5, (0, 0, 255), 1)
for x in range(0, im.shape[1], step):
    cv2.line(im, (x, 0), (x, im.shape[0]), (255, 0, 0), 1); cv2.putText(im, str(x), (x + 2, 28), 0, .5, (255, 0, 0), 1)
cv2.imwrite(sys.argv[2], im)
