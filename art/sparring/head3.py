import glob,os,json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
res={}
for f in sorted(glob.glob('in/**/*.png',recursive=True)):
    n=os.path.basename(f)[:-4]
    a=np.array(Image.open(f).convert('RGBA')); m=a[...,3]>40
    ys,xs=np.where(m); y0=ys.min(); H=ys.max()-y0
    r,g,b=[a[...,i].astype(int) for i in range(3)]
    col=(r-b>28)&(r>55)&(g<=r+5)&(g>=b-5)&m      # brown hair or skin, not white/grey/black
    col[y0+int(H*0.33):]=False
    col=ndi.binary_closing(col,structure=np.ones((3,3)),iterations=7)
    lab,k=ndi.label(col)
    # component containing topmost coloured pixel
    yy,xx=np.where(col); t=lab[yy.min(),xx[yy.argmin()]]
    sz=ndi.sum(col,lab,range(1,k+1)); big=sz.argmax()+1
    sl=ndi.find_objects(lab)[big-1]
    res[n]=dict(area=float(sz.max()),sq=round(float(np.sqrt(sz.max())),1),top=bool(t==big),w=sl[1].stop-sl[1].start,h=sl[0].stop-sl[0].start)
    print(n,res[n])
json.dump(res,open('head3.json','w'))
