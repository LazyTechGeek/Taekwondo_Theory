import json,subprocess,sys
N=[["Sam","Smith","m"],["Sarah","West","f"],["John","Stevenson","m"],["Emily","Clarke","f"],["James","Walker","m"],["Sophie","Turner","f"],["Oliver","Bennett","m"],["Charlotte","Hughes","f"],["Harry","Cooper","m"],["Lucy","Marshall","f"],["Jack","Wilson","m"],["Grace","Morgan","f"],["Thomas","Wright","m"],["Hannah","Baker","f"],["George","Hall","m"],["Amelia","Price","f"],["Daniel","Ward","m"],["Chloe","Fisher","f"],["Ben","Collins","m"],["Megan","Ellis","f"]]
sl=lambda a,b:(a+'-'+b).lower()
kup=[10,9,8,7,6,5,4,3,2]
sets={
 'chunk-13':['gs-name-'+sl(a,b) for a,b,_ in N],
 'chunk-14':['gs-first-'+a.lower() for a,b,_ in N],
 'chunk-15':['gs-pos-%d'%i for i in range(1,11)]+['gs-name-and-grade','gs-line-work','gs-baro','gs-front-row-turn','gs-return-to-marks','gs-moving-on-to-sparring','gs-gear-on','gs-round-1','gs-round-2','gs-round-3','gs-stop'],
 'chunk-16':['gs-ss-3-1-4','gs-ss-3-5-7','gs-ss-3-8-10','gs-ss-2-1-2','gs-ss-2-1-4','gs-ss-2-1-6','gs-ss-2-1-8','gs-ss-1','gs-gear-off-seats','gs-return-to-seats','gs-terminology-forward','gs-terminology-side','gs-correct','gs-end-your-grading','gs-end-grading'],
 'chunk-17':['gs-saw-variety','gs-saw-clean','gs-saw-counters','gs-saw-guard','gs-good-effort','gs-well-done','gs-fix-attack','gs-fix-guard','gs-fix-mix','gs-fix-kicks','gs-fix-moving'],
}
for g,key in (('m','male-1'),('f','female-1')):
    sets[key]=['gs-%s-yes'%g,'gs-%s-thanks'%g,'gs-%s-kihap'%g]+['gs-%s-name-%s'%(g,sl(a,b)) for a,b,x in N if x==g]+['gs-%s-kup-%d'%(g,k) for k in kup]
for k,v in sets.items():
    print('==',k,len(v))
    import os
    env=dict(os.environ); env.update({'chunk-13':{'TH':'32'},'chunk-16':{'AUTO':'8','EXTRA':'[[60.60,61.35],[62.64,63.54],[66.66,67.13],[71.24,71.94],[72.55,73.05],[74.82,75.45]]'},'male-1':{'AUTO':'20','EXTRA':'[[6.26,6.35]]'}}.get(k,{}))
    r=subprocess.run(['python3','/home/claude/split/cut.py','audio-work/batch-7/'+k+'.mp3',json.dumps([x+'.mp3' for x in v]),'/home/claude/split/gs'],capture_output=True,text=True,env=env)
    print(' '.join(l.split()[-1] for l in r.stdout.strip().split('\n')[1:]), r.stderr[-300:])
json.dump(sets,open('audio-work/batch-7.json','w'),indent=1)
