"""Turn a black-belt figure into a colour-belt figure: collar trim whitened (outline kept), trouser stripe removed,
and a mask of the belt so the game can colour it."""
import glob,os,sys,json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
HINT={'3step-08-counter1-defender':{'xmin':0.60},'3step-09-counter1-defender':{'xmin':0.52}}   # per-figure fixes: name -> dict(stripe_belt=bool ...)
def suit(a,name=''):
    a=a.copy(); r,g,b,al=[a[...,i].astype(int) for i in range(4)]
    solid=al>40
    blk=(r<75)&(g<75)&(b<80)&solid
    core=ndi.binary_erosion(blk,iterations=7)                       # outlines vanish, bands survive
    T=ndi.binary_propagation(ndi.binary_dilation(core,iterations=9),mask=blk)&ndi.binary_dilation(core,iterations=9)
    # belt rows: a long horizontal run of thick black
    lab,k=ndi.label(T)
    belt=np.zeros_like(T); collar=np.zeros_like(T); stripe=np.zeros_like(T)
    H,W=T.shape
    runs=np.zeros(H,int); 
    def longrun(row):
        best=0;c=0
        for v in row:
            c=c+1 if v else 0
            if c>best: best=c
        return best
    comp_has=[]
    ys_fig=np.where(solid.any(1))[0]; fy0,fy1=ys_fig.min(),ys_fig.max(); FH=fy1-fy0
    hairc=(r-b>22)&(r<188)&(g<r)&(g>=b-6)&solid
    xs_fig=np.where(solid.any(0))[0]; fx0,fx1=xs_fig.min(),xs_fig.max()
    xmin=HINT.get(name,{}).get('xmin')
    if xmin is not None:
        cut=int(fx0+xmin*(fx1-fx0)); left=T.copy(); left[:,cut:]=False; stripe|=left; T=T.copy(); T[:,:cut]=False; lab,k=ndi.label(T)
    for i in range(1,k+1):
        m=lab==i; ys=np.where(m.any(1))[0]
        ring=ndi.binary_dilation(m,iterations=5)&~m
        if ring.sum() and (hairc&ring).sum()/ring.sum()>0.3: continue      # a dark patch of hair, not clothing
        lr=np.array([longrun(m[y]) for y in ys])
        rows=ys[lr>=88]
        # the belt sits in the middle of the figure, never at the neck or the shins
        rows=rows[(rows>fy0+0.28*FH)&(rows<fy0+0.72*FH)]
        if len(rows)>=8:
            # one block of rows around the widest row (the crossed lapels can also make a long run higher up)
            lrd=dict(zip(ys,lr)); ymax=max(rows,key=lambda y:lrd[y]); thr=max(88,0.55*lrd[ymax])
            y0=ymax
            while y0-1 in lrd and lrd[y0-1]>=thr: y0-=1
            y1=ymax
            while y1+1 in lrd and lrd[y1+1]>=thr: y1+=1
            rows=np.arange(y0,y1+1)
        if len(rows)>=8:
            top=rows.min()
            below=m.copy(); below[:max(top-3,0)]=False
            above=m.copy(); above[max(top-3,0):]=False
            # bits just above the belt line that do not climb towards the neck stay belt (a tilted belt)
            la,ka=ndi.label(above)
            for j in range(1,ka+1):
                mj=la==j; yj=np.where(mj.any(1))[0]
                if top-yj.min()>55: collar|=mj
                else: below|=mj
            belt|=below
        else:
            cy=ys.mean(); h=ys.max()-ys.min()
            if cy<fy0+0.42*FH: collar|=m
            elif h>110: stripe|=m
            else: collar|=m                # small black panel (jacket vent etc.)
    # stripe that hangs off the belt region: long thin vertical part far below the belt
    cloth=solid&~blk&(r>200)&(g>200)&(b>205)
    col=[int(np.median(x[cloth])) for x in (r,g,b)] if cloth.any() else [238,236,242]
    edge=ndi.binary_dilation(~solid,iterations=6)                   # keep the silhouette outline
    # collar: whiten the inside, keep a rim as the outline
    cin=ndi.binary_erosion(collar,iterations=4)
    # stripe: whiten all of it
    sall=ndi.binary_dilation(stripe,iterations=3)&solid&~edge
    for msk in (cin,sall):
        for i,c in enumerate(col): a[...,i]=np.where(msk,c,a[...,i])
    bmask=ndi.binary_erosion(belt,iterations=4)
    return a,bmask,dict(belt=int(belt.sum()),collar=int(collar.sum()),stripe=int(stripe.sum()))
if __name__=='__main__':
    fs=sorted(glob.glob('in/**/*.png',recursive=True))
    if len(sys.argv)>1: fs=[f for f in fs if any(x in f for x in sys.argv[1:])]
    per=24; C=200
    for s in range(0,len(fs),per):
        S=Image.new('RGB',(C*8,(C+18)*3),(110,150,205))
        from PIL import ImageDraw
        D=ImageDraw.Draw(S)
        for k,f in enumerate(fs[s:s+per]):
            n=os.path.basename(f)[:-4]
            a=np.array(Image.open(f).convert('RGBA'))
            o,bm,info=suit(a,n)
            o[bm]=[250,210,40,255]
            im=Image.fromarray(o); bb=im.getbbox(); im=im.crop(bb); im.thumbnail((C,C))
            x=(k%8)*C; y=(k//8)*(C+18)
            S.paste(im,(x+(C-im.size[0])//2,y+18+C-im.size[1]),im); D.text((x+3,y+3),n[6:],fill='black')
            print(n,info)
        S.save('suit-%d.jpg'%(s//per),quality=85)
