"""PROTOTYPE: cluster p-003 components by shape; write montage for hand labelling."""
import cv2, numpy as np, json
from common import *
S='/tmp/claude-1000/-home-chris-Documents-yocal/0262b0c0-4464-4091-aaba-8cc212f21630/scratchpad/'
def feat(c):
    cr=c['crop']; h,w=cr.shape; m=max(h,w)
    pad=np.zeros((m,m),np.uint8); pad[(m-h)//2:(m-h)//2+h,(m-w)//2:(m-w)//2+w]=cr
    v=cv2.resize(pad.astype(np.float32),(24,24),interpolation=cv2.INTER_AREA).ravel()
    v=(v-v.mean())/(v.std()+1e-6)
    return np.concatenate([v, [np.log(w/h)*4, np.log(max(w,h))*2]])
comps=[]
for p in ['pages/p-003.png']:
    img,bw=load(p)
    for bi,b in enumerate(neume_bands(bw,1250)):
        for c in components(bw,b): c['band']=bi; comps.append(c)
F=np.array([feat(c) for c in comps])
# greedy leader clustering
cent=[];lab=[]
for f in F:
    d=[np.linalg.norm(f-c) for c in cent]
    if d and min(d)<14: lab.append(int(np.argmin(d)))
    else: cent.append(f); lab.append(len(cent)-1)
print(len(comps),'comps',len(cent),'clusters')
# montage: each cluster row: id + up to 8 examples
rows=[]
for k in range(len(cent)):
    ex=[c for c,l in zip(comps,lab) if l==k][:8]
    tiles=[]
    for c in ex:
        t=np.full((90,140),255,np.uint8); cr=(1-c['crop'])*255
        h,w=cr.shape; s=min(1,80/h,130/w); cr=cv2.resize(cr,(max(1,int(w*s)),max(1,int(h*s))))
        t[5:5+cr.shape[0],5:5+cr.shape[1]]=cr; tiles.append(t)
    lbl=np.full((90,110),255,np.uint8); cv2.putText(lbl,f'{k}:{lab.count(k)}',(3,50),0,0.9,0,2)
    rows.append(np.hstack([lbl]+tiles+[np.full((90,140),255,np.uint8)]*(8-len(tiles))))
for i in range(0,len(rows),18):
    cv2.imwrite(S+f'clusters{i//18}.png',np.vstack(rows[i:i+18]))
json.dump(dict(labels=lab),open(S+'clusters.json','w'))
np.save(S+'cent.npy',np.array(cent))
