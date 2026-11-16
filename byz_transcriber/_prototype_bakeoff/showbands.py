"""PROTOTYPE: overlay bands for checking."""
import sys, cv2
from common import *
S='/tmp/claude-1000/-home-chris-Documents-yocal/0262b0c0-4464-4091-aaba-8cc212f21630/scratchpad/'
for p in sys.argv[1:]:
    img,bw=load(p); ymin=int(sys.argv[0] and 0)
    bands=neume_bands(bw, 1250 if '003' in p else 0)
    print(p,bands)
    im=cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
    for a,b in bands: cv2.rectangle(im,(5,a),(im.shape[1]-5,b),(0,0,255),4)
    cv2.imwrite(S+'b-'+p.split('/')[-1],cv2.resize(im,None,fx=.35,fy=.35))
