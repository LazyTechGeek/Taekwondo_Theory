import os,json
from PIL import Image,ImageDraw,ImageFont,ImageOps
import pair as P
SEQ={1:['01-move1','01-move2','01-move1','04-counter2'],
 2:['04-move1','04-move2','04-move1','02-counter1'],
 3:['03-move1','03-move2','03-move1','03-counter1'],
 4:['04-move1','04-move2','04-move1','04-counter1','04-counter2'],
 5:['05-move1','05-move2','05-move1','05-counter1'],
 6:['06-move1','06-move2','06-move1@far','06-counter1'],
 7:['05-move1','05-move2','07-move3','07-counter1','07-counter3','07-counter2'],
 8:['06-move1','06-move2','08-move3','08-counter1','08-counter2'],
 9:['09-move1','09-move2','09-move1','09-counter1','09-counter3'],
 10:['06-move1','06-move2','06-move1@far','10-counter1','08-counter1','10-counter3']}
def get(st,ret):
    base=st.split('@')[0]; kind='ready' if 'ready' in st else ('counter' if 'counter' in st else 'move')
    o=None
    if '@far' in st: o=dict(P.OPT.get('3step-'+base,{}),shift=2.0)
    if '@hit' in st: o={'neck':1,'shift':0.5}
    if '@close' in st: o=dict(P.OPT.get('3step-'+base,{})); o['shift']=o.get('shift',0)-0.5
    hair=('black','brown') if ret else ('brown','black')
    im=P.pair('3step-'+base,kind,opt=o,hair=hair)
    mk=P.pair.mask
    get.mask=ImageOps.mirror(mk) if ret else mk
    return ImageOps.mirror(im) if ret else im
def retseq(n):
    f=SEQ[n]; m=f[:3]; c=f[3:]
    if m[2]==m[0]: r=[(m[1],0),(m[0],0),(m[1],0)]
    elif '@far' in m[2]: r=[(m[1],0),(m[0],0),(m[1]+'@far',0)]
    else: r=[(m[1],0),(m[0],0),(m[2],1)]
    if n==2: return r+[('02b-counter1',0)]
    if n==1: return r+[('04-counter1',0)]
    if n==3: return r+[('03-move2@hit',0)]
    if n==4: return r+[('04-counter2',0),('04-counter1',0),('04-counter2',0)]
    return r+[(x,1) for x in c]
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',22)
F2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
CW,CH=470,400
os.makedirs('final',exist_ok=True); man={}
for ret in (0,1):
    for part,nums in enumerate([[1,2,3,4,5],[6,7,8,9,10]]):
        S=Image.new('RGB',(90+CW*7,CH*len(nums)+50),(110,150,205)); Dr=ImageDraw.Draw(S)
        Dr.text((10,12),('WAY BACK: right man attacks' if ret else 'WAY THERE: left man attacks')+'   numbers %d to %d'%(nums[0],nums[-1]),font=F,fill='white')
        for ri,nn in enumerate(nums):
            y=50+ri*CH; Dr.text((8,y+CH//2-12),'No. %d'%nn,font=F,fill='white')
            cells=[('ready-lowblock',1 if ret else 0)]+(retseq(nn) if ret else [(x,0) for x in SEQ[nn]])
            mi=ci=0; names=[]
            for k,(st,mir) in enumerate(cells):
                x=90+k*CW
                if k==0: lab='Start'
                elif 'counter' in st or k>3: ci+=1; lab='Counter %d'%ci
                else: mi+=1; lab='Move %d'%mi
                Dr.rectangle((x,y,x+CW-1,y+CH-1),outline='white')
                Dr.text((x+8,y+6),lab,font=F,fill='black')
                Dr.text((x+8,y+34),st+(' (flipped)' if ret else ''),font=F2,fill=(40,40,40))
                if mir: Dr.text((x+CW-110,y+8),'MIRRORED',font=F2,fill=(170,0,0))
                im=get(st,ret)
                fn=('back-' if ret else '')+st.replace('@','-')+'.png'; im.save('final/'+fn); get.mask.save('final/'+fn[:-4]+'-belt.png'); names.append((lab,fn,mir))
                yb=Image.new('RGBA',im.size,(242,194,0,255)); im=im.copy(); im.paste(yb,(0,0),get.mask)
                kf=min(0.46,(CW-16)/im.size[0],(CH-66)/im.size[1]); t=im.resize((int(im.size[0]*kf),int(im.size[1]*kf)))
                S.paste(t,(x+(CW-t.size[0])//2,y+CH-6-t.size[1]),t)
            man[('back' if ret else 'fwd')+str(nn)]=names
        S.resize((1940,int(S.size[1]*1940/S.size[0]))).save('%s-%d.jpg'%('way-back' if ret else 'way-there',part+1),quality=86)
json.dump(man,open('manifest.json','w'),indent=1)
print('ok')
