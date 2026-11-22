import glob,os,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage as ndi
h3=json.load(open('head3.json'))
G=0.55; HEADW=198*G
OVR={'3step-10-counter1-defender':1.03}
os.makedirs('fig',exist_ok=True); os.makedirs('pairs',exist_ok=True)
FIG={}
def fig(n):
    if n in FIG: return FIG[n]
    f=glob.glob('in/**/'+n+'.png',recursive=True)[0]
    a=np.array(Image.open(f).convert('RGBA')); m=a[...,3]>40
    lab,k=ndi.label(m); sz=ndi.sum(m,lab,range(1,k+1))
    keep=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>0.004*sz.max()]); a[~keep,3]=0
    ys,xs=np.where(keep); a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
    s=OVR.get(n,min(1.1,max(0.92,((180/h3[n]['sq'])*(198/min(h3[n]['w'],215)))**0.5)))*G
    im=Image.fromarray(a).resize((round(a.shape[1]*s),round(a.shape[0]*s)),Image.LANCZOS)
    im.save('fig/'+n+'.png'); FIG[n]=im; return im
def edges(im):
    m=np.array(im)[...,3]>40; H=m.shape[0]
    def right(y0,y1):
        r=m[int(H*y0):int(H*y1)]; return np.where(r.any(0))[0].max()
    def left(y0,y1):
        r=m[int(H*y0):int(H*y1)]; return np.where(r.any(0))[0].min()
    return m,right,left
OPT={'3step-01-move1':{'front':'a'},'3step-04-move2':{'front':'a'},'3step-02-counter1':{'neck':1},'3step-03-move1':{'front':'a'},'3step-03-move2':{'shift':-0.15},'3step-03-counter1':{'front':'a','shift':-0.3},'3step-05-move1':{'front':'a'},'3step-05-counter1':{'front':'a','shift':-0.2},'3step-06-move1':{'front':'a'},'3step-06-counter1':{'front':'a','shift':-0.25},'3step-07-move3':{'shift':2.2},'3step-08-move3':{'shift':2.2},'3step-08-counter2':{'neck':1,'shift':0.12,'lift':0.33},'3step-10-counter1':{'shift':4.0},'3step-09-move2':{'front':'a','lift':-0.14},'3step-09-move1':{'lift':0.17},'3step-09-counter3':{'neck':1,'lift':-0.19,'shift':0.1},'3step-10-counter3':{'neck':1,'lift':-0.32,'shift':0.1},'3step-02b-counter1':{'neck':1,'shift':-0.2,'front':'a'}}
BL={}
def black(im,key):
    if key in BL: return BL[key]
    a=np.array(im).astype(int); r,g,b,al=a[...,0],a[...,1],a[...,2],a[...,3]
    H=a.shape[0]
    hair=(r-b>22)&(r<188)&(g<r)&(g>=b-6)&(al>40)
    # head only: the hair blob that touches the top of the figure
    lab,k=ndi.label(ndi.binary_dilation(hair,iterations=3))
    ys,xs=np.where(hair); top=lab[ys.min(),xs[ys.argmin()]]
    hm=hair&(lab==top)
    lum=(0.3*r+0.59*g+0.11*b)
    gr=np.clip(lum*0.40+6,0,255)
    for i,add in ((0,0),(1,0),(2,7)): a[...,i]=np.where(hm,np.clip(gr+add,0,255),a[...,i])
    out=Image.fromarray(a.astype('uint8')); BL[key]=out; return out
def pair(stem,kind,front='d',opt=None,hair=('brown','black')):
    o=opt if opt is not None else OPT.get(stem,{}); front=o.get('front',front)
    A=fig(stem+'-attacker'); D=fig(stem+'-defender')
    if hair[0]=='black': A=black(A,stem+'-attacker')
    if hair[1]=='black': D=black(D,stem+'-defender')
    mA,rA,lA=edges(A); mD,rD,lD=edges(D)
    fist=rA(0.05,0.45)                    # attacker's leading hand
    if kind=='ready': dx=A.size[0]+int(1.3*HEADW)-lD(0,1)
    elif kind=='move': dx=fist-int(0.75*HEADW)-lD(0.0,0.45)      # block meets the wrist
    else:                                  # counter: defender's strike reaches the attacker's body
        body=rA(0.47,0.56)
        dx=body+int(0.30*HEADW)-lD(0.0,0.62)
    if o.get('neck'):
        top=mA[:int(mA.shape[0]*0.12)]; hc=int(np.where(top.any(0))[0].mean())
        dx=hc-int(0.18*HEADW)-lD(0.0,0.30)
    dx+=int(o.get('shift',0)*HEADW)
    lift=int(o.get('lift',0)*HEADW)
    W=max(A.size[0],dx+D.size[0])+20; la=max(0,-lift); lift=max(0,lift); Ht=max(A.size[1]+la,D.size[1]+lift)+10
    C=Image.new('RGBA',(W,Ht),(0,0,0,0))
    pa=(10,Ht-A.size[1]-5-la); pd=(10+dx,Ht-D.size[1]-5-lift)
    for who in (('a','d') if front=='d' else ('d','a')):
        if who=='a': C.alpha_composite(A,pa)
        else: C.alpha_composite(D,pd)
    return C
if __name__=='__main__':
    SEQ={ 1:['01-move1','01-move2','01-move1','04-counter2'],
      2:['04-move1','04-move2','04-move1','02-counter1'],
      3:['03-move1','03-move2','03-move1','03-counter1'],
      4:['04-move1','04-move2','04-move1','04-counter1','04-counter2'],
      5:['05-move1','05-move2','05-move1','05-counter1'],
      6:['06-move1','06-move2','?06-move3','06-counter1'],
      7:['05-move1','05-move2','07-move3','07-counter1','07-counter2','07-counter3'],
      8:['06-move1','06-move2','08-move3','08-counter1','08-counter2'],
      9:['09-move1','09-move2','09-move1','09-counter1','09-counter3'],
      10:['06-move1','06-move2','06-move1@far','10-counter1','08-counter1','10-counter3']}
    F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
    F2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    CW,CH=470,400
    for part,nums in enumerate([[1,2,3,4,5],[6,7,8,9,10]]):
        S=Image.new('RGB',(90+CW*6,CH*len(nums)),(110,150,205)); Dr=ImageDraw.Draw(S)
        for ri,nn in enumerate(nums):
            y=ri*CH; Dr.text((8,y+CH//2-12),'No. %d'%nn,font=F,fill='white')
            mi=0;ci=0
            for k,st in enumerate(SEQ[nn]):
                x=90+k*CW; iscounter='counter' in st
                if iscounter: ci+=1; lab='Counter %d'%ci
                else: mi+=1; lab='Move %d'%mi
                Dr.rectangle((x,y,x+CW-1,y+CH-1),outline='white')
                Dr.text((x+8,y+6),lab,font=F,fill='black')
                if st.startswith('?'):
                    Dr.text((x+8,y+36),'no picture: 3step-'+st[1:],font=F2,fill=(150,0,0)); continue
                Dr.text((x+8,y+34),'3step-'+st,font=F2,fill=(40,40,40))
                base=st.split('@')[0]
                if '@' in st: OPT['3step-'+base+'@']=dict(OPT.get('3step-'+base,{}),shift=2.0)
                P=pair('3step-'+base,'counter' if iscounter else 'move',opt=OPT.get('3step-'+base+'@') if '@' in st else None)
                P.save('pairs/3step-'+st.replace('@','-')+'.png')
                k=min(0.46,(CW-16)/P.size[0],(CH-66)/P.size[1]); P2=P.resize((int(P.size[0]*k),int(P.size[1]*k)))
                S.paste(P2,(x+(CW-P2.size[0])//2,y+CH-6-P2.size[1]),P2)
        S.save('check-%d.jpg'%(part+1),quality=85); print(S.size)
    pair('3step-ready-lowblock','ready').save('pairs/3step-ready-lowblock.png')
