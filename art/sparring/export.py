import json,os,sys
from PIL import Image,ImageOps
import pair as P
REPO='/home/claude/taekwondo_theory'; OUT=REPO+'/img/sparring'; K=0.8
man=json.load(open('manifest.json'))
# both men in parallel ready stance (left brown, right black)
D=P.fig('3step-ready-lowblock-defender'); L=ImageOps.mirror(D); R=P.black(D,'ready-def')
gap=int(1.5*P.HEADW); W=L.size[0]+gap+R.size[0]+20; H=max(L.size[1],R.size[1])+10
C=Image.new('RGBA',(W,H),(0,0,0,0)); C.alpha_composite(L,(10,H-L.size[1]-5)); C.alpha_composite(R,(10+L.size[0]+gap,H-R.size[1]-5)); C.save('final/ready.png')
mk=P.MASK['3step-ready-lowblock-defender']; M=Image.new('L',(W,H),0); M.paste(ImageOps.mirror(mk),(10,H-L.size[1]-5)); M.paste(mk,(10+L.size[0]+gap,H-R.size[1]-5)); M.save('final/ready-belt.png')
used={'ready.png'}
for k,v in man.items():
    for lab,fn,mir in v: used.add(fn)
sizes={}
for fn in sorted(used):
    im=Image.open('final/'+fn); bb=im.getchannel('A').point(lambda v:255 if v>8 else 0).getbbox()
    # keep the bottom edge (the floor line) but trim the other sides
    box=(max(bb[0]-4,0),max(bb[1]-4,0),min(bb[2]+4,im.size[0]),im.size[1])
    im=im.crop(box); mk=Image.open('final/'+fn[:-4]+'-belt.png').convert('L').crop(box)
    im=im.resize((round(im.size[0]*K),round(im.size[1]*K)),Image.LANCZOS); mk=mk.resize(im.size,Image.LANCZOS)
    out='s3-'+fn[:-4]+'.webp'; im.save(OUT+'/'+out,'WEBP',quality=86,method=4)
    wm=Image.new('RGBA',im.size,(255,255,255,0)); wm.putalpha(mk); wm.save(OUT+'/'+out[:-5]+'-belt.webp','WEBP',lossless=True,method=4)
    sizes[out]={'w':im.size[0],'h':im.size[1],'head':round(P.HEADW*K),'fixed':True}
json.dump(sizes,open('sizes_new.json','w'),indent=1)
print(len(sizes),sum(os.path.getsize(OUT+'/'+f) for f in sizes)//1024,'KB')
