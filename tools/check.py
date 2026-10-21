"""Quick health check for index.html: JS syntax (node --check) and a Playwright smoke test at
phone sizes 390x844 and 360x640 — loads the page, opens every menu item, reports page errors
and any screen wider than the phone. Usage: python3 tools/check.py [index.html]"""
import sys,os,re,subprocess,tempfile
html=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
src=open(html,encoding='utf-8').read();js=re.findall(r'<script>(.*?)</script>',src,re.S)[-1]
f=os.path.join(tempfile.mkdtemp(),'main.js');open(f,'w').write(js)
r=subprocess.run(['node','--check',f],capture_output=True,text=True);print('syntax:',r.stderr.strip() or 'ok')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
  b=p.chromium.launch()
  for W,H in [(390,844),(360,640)]:
    pg=b.new_page(viewport={'width':W,'height':H});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file://'+html);pg.wait_for_timeout(600)
    print(W,'x',H,'version',pg.evaluate('APP_VERSION'))
    for m in pg.evaluate("[...document.querySelectorAll('.mode')].map(b=>b.dataset.mode)"):
      pg.evaluate("goHome()");pg.evaluate(f"document.querySelector('.mode[data-mode=\"{m}\"]').click()");pg.wait_for_timeout(250)
      w=pg.evaluate('document.documentElement.scrollWidth')
      if w>W:print('  too wide:',m,w)
    print('  errors:',errs or 'none');pg.close()
  b.close()
