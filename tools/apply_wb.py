"""Embed the All Theory workbook into index.html.
Usage: python3 tools/apply_wb.py all-theory.xlsx [index.html]
Runs wb2json (validates and prints problems), replaces the <script id="allTheory"> JSON block,
and embeds the workbook itself (base64, <script id="wbTemplate">) for developer-mode Export."""
import sys,json,subprocess,base64,os,tempfile
here=os.path.dirname(os.path.abspath(__file__))
xlsx=sys.argv[1];html=sys.argv[2] if len(sys.argv)>2 else os.path.join(here,'..','index.html')
tmp=os.path.join(tempfile.mkdtemp(),'at.json')
r=subprocess.run([sys.executable,os.path.join(here,'wb2json.py'),xlsx,tmp],capture_output=True,text=True);print(r.stdout+r.stderr)
if r.returncode or 'PROBLEMS' in r.stdout:sys.exit('Fix the problems above first (or edit this script if they are expected).')
s=open(html,encoding='utf-8').read();data=json.load(open(tmp))
js=json.dumps(data,ensure_ascii=False,indent=0).replace('</','<\\/')
i=s.index('<!-- ALL THEORY:');j=s.index('</script>',s.index('id="allTheory"'))+9
s=s[:i]+'<!-- ALL THEORY: copied from Dave\'s "All Theory" workbook (Terminology, Patterns, Belt meanings, Questions tabs). Rebuild with tools/apply_wb.py. -->\n<script type="application/json" id="allTheory">\n'+js+'\n</script>'+s[j:]
b=base64.b64encode(open(xlsx,'rb').read()).decode()
blk='<!-- WORKBOOK TEMPLATE: Dave\'s All Theory workbook, used only by developer-mode Export. Rebuilt with the data. -->\n<script type="text/plain" id="wbTemplate">'+b+'</script>'
i=s.index('<!-- WORKBOOK TEMPLATE:');j=s.index('</script>',s.index('id="wbTemplate"'))+9;s=s[:i]+blk+s[j:]
open(html,'w',encoding='utf-8').write(s);print('Embedded data and workbook template into',html)
