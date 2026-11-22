# Read the All Theory workbook and turn it into the JSON the app embeds. Prints any problems it finds.
import sys,json,re
from openpyxl import load_workbook
wb=load_workbook(sys.argv[1],data_only=True);probs=[]
GR=['10th_Kup','9th_Kup','8th_Kup','7th_Kup','6th_Kup','5th_Kup','4th_Kup','3rd_Kup','2nd_Kup','1st_Kup','1st_Dan','2nd_Dan','3rd_Dan','4th_Dan','5th_Dan']
def rows(t):
    ws=wb[t];h=[str(c.value or '').strip() for c in ws[1]]
    need={'Terminology':['ID','Grade','Belt','English','Korean','Pronounced','MP3'],'Patterns':['ID','Grade','Belt','Pattern','Moves','Meaning','Pronounced','MP3'],'Belt meanings':['ID','Belt','First grade','Meaning','Pronounced','MP3']}.get(t,[])
    for n in need:
        if n not in h:probs.append(f'{t}: header "{n}" is missing (headers are {h})')
    for r in ws.iter_rows(min_row=2,values_only=True):
        if not any(v not in (None,'') for v in r):continue
        yield {h[i]:(str(v).strip() if v is not None else '') for i,v in enumerate(r) if i<len(h)}
def col(d,name):
    for k in d:
        if k.lower().startswith(name.lower()):return d[k]
    return ''
def secs(v,where):
    v=str(v).strip()
    if not v:return None
    if re.fullmatch(r'\d+(\.\d+)?',v):
        f=float(v)
        if 0<f<1:return round(f*86400)          # Excel turned 0:21 into a time of day
        return int(f)
    m=re.fullmatch(r'(?:(\d+):)?(\d{1,2}):(\d{2})(?::00)?',v)
    if m:
        h=int(m.group(1) or 0);a=int(m.group(2));b=int(m.group(3))
        return h*3600+a*60+b
    probs.append(f'{where}: time "{v}" not understood');return None
def vid(u,where):
    if not u:return None
    m=re.search(r'(?:[?&]v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})',u)
    if not m:probs.append(f'{where}: link "{u}" has no single video in it');return None
    return m.group(1)
out={'terms':[],'patterns':[],'belts':[]};seen=set()
def chk_id(i,where):
    if not i:probs.append(f'{where}: missing ID')
    elif i in seen:probs.append(f'{where}: ID {i} used twice')
    seen.add(i)
# Audio status: blank / New / Redo / OK (only OK, or blank with an MP3 from before 3.86, plays for everyone)
def ast(d):
    v=(d.get('Audio status','') or '').strip()
    if v and v not in ('New','Redo','OK'):probs.append(f"{d.get('ID')}: Audio status must be New, Redo or OK (is \"{v}\")")
    if v in ('New','OK') and not d.get('MP3'):probs.append(f"{d.get('ID')}: Audio status {v} but no MP3")
    return v
def qa(d,w):  # Question / Answer audio status on the Questions tab
    v=(col(d,w+' audio status') or '').strip()
    if v and v not in ('New','Redo','OK'):probs.append(f"{d.get('ID')}: {w} audio status must be New, Redo or OK")
    return v
for d in rows('Terminology'):
    w=f"Terminology {d.get('ID')}";chk_id(d.get('ID'),w)
    if d['Grade'] not in GR:probs.append(f'{w}: unknown grade "{d["Grade"]}"')
    if not d['English'] or not d['Korean']:probs.append(f'{w}: English or Korean is empty')
    out['terms'].append({'id':d['ID'],'g':d['Grade'],'en':d['English'],'kr':d['Korean'],'say':d.get('Pronounced',''),'mp3':d.get('MP3',''),'ast':ast(d)})
for d in rows('Patterns'):
    w=f"Patterns {d.get('ID')} ({d.get('Pattern')})";chk_id(d.get('ID'),w)
    if d['Grade'] not in GR:probs.append(f'{w}: unknown grade "{d["Grade"]}"')
    v=vid(col(d,'Video link'),w);s=secs(col(d,'Video start'),w);e=secs(col(d,'Video end'),w)
    if v and s is not None and e is not None and e<=s:probs.append(f'{w}: video end {col(d,"Video end")} is not after start {col(d,"Video start")}')
    if not v and (s or e):probs.append(f'{w}: has times but no link')
    out['patterns'].append({'id':d['ID'],'g':d['Grade'],'name':d['Pattern'],'moves':int(float(d['Moves'])) if d['Moves'] else None,'meaning':d['Meaning'],
        'say':d.get('Pronounced',''),'mp3':d.get('MP3',''),'ast':ast(d),'video':{'id':v,'start':s or 0,'end':e} if v else None})
for d in rows('Belt meanings'):
    w=f"Belt meanings {d.get('ID')}";chk_id(d.get('ID'),w)
    out['belts'].append({'id':d['ID'],'belt':d['Belt'],'g':d['First grade'],'meaning':d['Meaning'],'say':d.get('Pronounced',''),'mp3':d.get('MP3',''),'ast':ast(d)})
# Questions tab (optional): Grade is All or a grade; answers and wrong answers separated by |
out['questions']=[]
if 'Questions' in wb.sheetnames:
    split=lambda v:[x.strip() for x in str(v or '').split('|') if x.strip()]
    for d in rows('Questions'):
        w=f"Questions {d.get('ID')}";chk_id(d.get('ID'),w)
        g=d.get('Grade','')
        if g!='All' and g not in GR:probs.append(f'{w}: unknown grade "{g}"')
        i=d.get('ID','');exp='Q_All_' if g=='All' else 'Q_'+g.replace('_','-')+'_'
        if i and not i.startswith(exp):probs.append(f'{w}: ID does not match its grade (expected {exp}..)')
        if not d.get('Question') or not split(d.get('Answer')):probs.append(f'{w}: Question or Answer is empty');continue
        ans=split(d.get('Answer'));wr=[x for x in split(d.get('Wrong answers')) if x.lower() not in [a.lower() for a in ans]]
        out['questions'].append({'id':i,'g':g,'q':d['Question'],'a':ans,'w':wr,
            'qsay':col(d,'Question pronounced') or d.get('Pronounced',''),'qmp3':col(d,'Question MP3') or d.get('MP3',''),
            'asay':col(d,'Answer pronounced'),'amp3':col(d,'Answer MP3'),'qast':qa(d,'Question'),'aast':qa(d,'Answer')})
        # Appears in games: blank / Yes = normal; No = Study Guide only (long answers that cannot be multiple choice)
        ag=(col(d,'Appears in games') or '').strip().lower()
        if ag not in ('','yes','no'):probs.append(f'{w}: Appears in games must be Yes or No')
        if ag=='no':out['questions'][-1]['ng']=1
# Body parts tab (optional): labels from the four body charts; Grade is All or a grade
out['body']=[]
if 'Body parts' in wb.sheetnames:
    for d in rows('Body parts'):
        w=f"Body parts {d.get('ID')}";chk_id(d.get('ID'),w)
        g=d.get('Grade','') or 'All'
        if g!='All' and g not in GR:probs.append(f'{w}: unknown grade "{g}"')
        if not d.get('English') or not d.get('Korean'):probs.append(f'{w}: English or Korean is empty')
        if not d.get('Chart'):probs.append(f'{w}: Chart is empty')
        out['body'].append({'id':d.get('ID',''),'g':g,'chart':d.get('Chart',''),'sec':d.get('Section',''),'en':d.get('English',''),'kr':d.get('Korean',''),
            'say':d.get('Pronounced',''),'mp3':d.get('MP3',''),'ast':ast(d),'note':d.get('Note','')})
# Grading Simulator tabs (optional): Line Work, Step Sparring, Grading Order, Grading by Grade
import re as _re
def num(v,w,what,blank=None):
    if v in ('',None):return blank
    try:return int(float(v))
    except Exception:probs.append(f'{w}: {what} must be a number (is "{v}")');return blank
ANIMS={'press-ups','punch','kick','jump kick','block','low block','rising block','knife hand','guard','strike','twin','random'}
out['linework']=[]
if 'Line Work' in wb.sheetnames:
    for d in rows('Line Work'):
        w=f"Line Work {d.get('ID')}";chk_id(d.get('ID'),w)
        if d.get('Grade') not in GR:probs.append(f'{w}: unknown grade "{d.get("Grade")}"')
        if d.get('Direction','') not in ('','Stationary','Forwards','Backwards'):probs.append(f'{w}: Direction must be Stationary, Forwards or Backwards')
        if not d.get('Line work'):probs.append(f'{w}: Line work is empty')
        an=[x.strip().lower() for x in d.get('Animation','').split(',') if x.strip()]
        for x in an:
            if x not in ANIMS:probs.append(f'{w}: Animation "{x}" is not one of {sorted(ANIMS)}')
        out['linework'].append({'id':d.get('ID',''),'g':d.get('Grade',''),'no':num(d.get('No.'),w,'No.',0),'dir':d.get('Direction',''),'text':d.get('Line work',''),
            'stance':d.get('Stance',''),'qty':num(d.get('Quantity'),w,'Quantity',4),'steps':num(d.get('Steps'),w,'Steps',1),'anim':an,
            'tts':d.get('Text to speech',''),'mp3':d.get('MP3',''),'note':d.get('Notes','')})
out['stepspar']=[]
if 'Step Sparring' in wb.sheetnames:
    for d in rows('Step Sparring'):
        w=f"Step Sparring {d.get('ID')}";chk_id(d.get('ID'),w)
        t=num(d.get('Type'),w,'Type')
        if t not in (1,2,3):probs.append(f'{w}: Type must be 1, 2 or 3')
        out['stepspar'].append({'id':d.get('ID',''),'type':t,'no':num(d.get('No.'),w,'No.',0),'start':d.get('Start image',''),
            'moves':[d.get(f'Image {i}','') for i in (1,2,3)][:t or 3],'counters':[x for x in (d.get(f'Counter {i}','') for i in (1,2,3)) if x],'note':d.get('Notes','')})
STAGES=['Line-up','Name and grade','Line work','Patterns','Step sparring','Free sparring','Questions']
out['gorder']=[];out['gsay']={}
if 'Grading Order' in wb.sheetnames:
    for d in sorted(rows('Grading Order'),key=lambda d:float(d.get('Order') or 99)):
        if d.get('Stage') not in STAGES:probs.append(f'Grading Order: unknown stage "{d.get("Stage")}" (stages are {STAGES})')
        else:
            out['gorder'].append(d['Stage'])
            if d.get('Examiner says'):out['gsay'][d['Stage']]=d['Examiner says']
    for s in STAGES:
        if s not in out['gorder']:probs.append(f'Grading Order: stage "{s}" is missing')
out['gplan']=[]
if 'Grading by Grade' in wb.sheetnames:
    for d in rows('Grading by Grade'):
        w=f"Grading by Grade {d.get('Grade')} / {d.get('Stage')}"
        if d.get('Grade') not in GR:probs.append(f'{w}: unknown grade')
        if d.get('Stage') not in STAGES:probs.append(f'{w}: unknown stage');continue
        if d.get('Done?','') not in ('Yes','No'):probs.append(f'{w}: Done? must be Yes or No')
        e={'g':d.get('Grade',''),'stage':d['Stage'],'done':d.get('Done?')!='No','detail':d.get('Detail','')}
        det=e['detail']
        if d['Stage']=='Step sparring' and e['done']:
            sets=[]
            for part in det.split(';'):
                m=_re.match(r'^\s*([123])-step(?:\s+(\d+)-(\d+))?(?:\s*\(top marks (\d+)-(\d+)\))?\s*$',part)
                if not m:probs.append(f'{w}: cannot read "{part.strip()}" (write e.g. "3-step 1-4" or "2-step 1-2 (top marks 1-4); 1-step")');continue
                sets.append({'type':int(m.group(1)),'from':int(m.group(2) or 0),'to':int(m.group(3) or 0),'top':int(m.group(5) or 0)})
            e['sets']=sets
        if d['Stage']=='Questions' and e['done']:
            m=_re.match(r'^\s*(\d+) questions?,\s*(side|top) table\s*$',det)
            if not m:probs.append(f'{w}: cannot read "{det}" (write e.g. "2 questions, side table")')
            else:e['n']=int(m.group(1));e['where']=m.group(2)
        out['gplan'].append(e)
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
print(len(out['linework']),'line work,',len(out['stepspar']),'step sparring,',len(out['gplan']),'grading plan rows,',len(out.get('questions',[])),'questions,',len(out['body']),'body parts,',len(out['terms']),'terms,',len(out['patterns']),'patterns,',len(out['belts']),'belts,',sum(1 for p in out['patterns'] if p['video']),'videos')
print('PROBLEMS:' if probs else 'No problems found.');[print(' -',p) for p in probs]
print('No video:',[p['name'] for p in out['patterns'] if not p['video']])
