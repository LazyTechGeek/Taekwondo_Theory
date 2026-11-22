"""Measure how big the people are drawn in each step-sparring picture, so the game can show them all at one size.
Usage: python3 tools/sparring_sizes.py      (run after adding pictures to img/sparring/)
Writes img/sparring/sizes.json: {"file.webp": {"w": picture width, "h": height, "head": width of the bald defender's head in pixels}}.
The head is found as the biggest skin-coloured patch in the top third of the picture. If a picture comes out the wrong
size in the game, set its "head" by hand here and add "fixed": true so this script leaves it alone."""
import json,os,glob
import numpy as np
from PIL import Image
from scipy import ndimage
here=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','img','sparring');out=os.path.join(here,'sizes.json')
old=json.load(open(out)) if os.path.exists(out) else {}
res={}
for f in sorted(glob.glob(os.path.join(here,'*.webp'))):
    n=os.path.basename(f)
    if old.get(n,{}).get('fixed'):res[n]=old[n];continue
    im=np.array(Image.open(f).convert('RGBA')).astype(int);r,g,b,a=[im[...,i] for i in range(4)]
    skin=(a>200)&(r>200)&(g>140)&(g<215)&(b>90)&(b<175)&(r-b>50)
    lab,_=ndimage.label(skin);best=None
    for i,sl in enumerate(ndimage.find_objects(lab),1):
        area=int((lab[sl]==i).sum())
        if area>=1500 and sl[0].start<im.shape[0]*0.35 and (best is None or area>best[0]):best=(area,sl[1].stop-sl[1].start)
    res[n]={'w':im.shape[1],'h':im.shape[0],'head':int(best[1]) if best else None}
    print(n,res[n])
json.dump(res,open(out,'w'),indent=1)
