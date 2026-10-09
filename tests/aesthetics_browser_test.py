#!/usr/bin/env python3
"""Actual Chromium checks for visual controls, local-only records and mobile routes."""
import functools,http.server,json,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/aesthetics';OUT.mkdir(parents=True,exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def translate_path(self,path):
        if path.startswith('/Mine-Wiki/'):path=path[len('/Mine-Wiki'):]
        return super().translate_path(path)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
node='knowledge/observation-interpretation-preference/index.html';path='lessons/aesthetics-observation/index.html';map_route='topics/aesthetics/index.html'
key='mine-wiki.aesthetics.observation.v1';oldkey='mine-wiki.learning.v1';checks=[];errors=[];external=[]
def ok(name,condition):
    assert condition,name
    checks.append(name);print('PASS',name,flush=True)
def text_has(page,id,needle):ok(id+': '+needle,needle in page.locator('#'+id).inner_text())
def fill_before(page):
    page.locator('#aesthetic-observe').fill('本图六个等宽同色矩形；我此刻觉得有均匀的重复。')
    page.locator('#aesthetic-predict').fill('间隔重分配后，我可能读成三组；若没有分组感就修订。')
try:
  with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,reduced_motion='reduce')
    context.on('page',lambda p:p.on('pageerror',lambda e:errors.append(str(e))))
    context.on('request',lambda r:external.append(r.url) if not r.url.startswith((base,'blob:','data:')) else None)
    page=context.new_page();page.goto(base+'/index.html')
    ok('homepage exposes map and first-unit path',page.locator('a[href="topics/aesthetics/index.html"]').count()>=1 and page.locator('a[href="lessons/aesthetics-observation/index.html"]').count()==1)
    page.goto(base+'/'+map_route);page.screenshot(path=str(OUT/'map-desktop.png'))
    ok('map declares one ready and eighteen unfinished nodes',page.locator('.map-availability').inner_text().startswith('1 / 19') and page.locator('.node-card[data-status=stub]').count()==18)
    ok('map has three layers and five stages',page.locator('.map-layer').count()==3 and page.locator('.stage-list>li').count()==5)
    page.locator('a[href="../../lessons/aesthetics-observation/index.html"]').click()
    ok('map opens first-unit route',page.url.endswith(path))
    page.screenshot(path=str(OUT/'unit-desktop.png'))
    ok('one shared lab initialized on path',page.evaluate('Object.keys(window.LessonUI)')==['aesthetic'])
    ok('comparison initially concealed',page.locator('#aesthetic-variant').is_hidden() and page.locator('#aesthetic-analysis').is_hidden())
    page.locator('#aesthetic-reveal').click();ok('empty observation returns focus and keeps variant hidden',page.locator('#aesthetic-observe').evaluate('(e)=>e===document.activeElement') and page.locator('#aesthetic-variant').is_hidden())
    page.locator('#aesthetic-observe').fill('六个矩形。');page.locator('#aesthetic-reveal').click()
    ok('prediction required before first comparison',page.locator('#aesthetic-predict').evaluate('(e)=>e===document.activeElement'))
    # Compare invariant geometry before and after opening, including displayed size.
    initial_size=page.locator('#aesthetic-original svg').bounding_box()
    fill_before(page);page.locator('#aesthetic-reveal').focus();page.keyboard.press('Enter')
    ok('keyboard opens comparison',page.locator('#aesthetic-variant').is_visible() and page.locator('#aesthetic-reveal').get_attribute('aria-expanded')=='true')
    after_size=page.locator('#aesthetic-original svg').bounding_box()
    ok('original canvas display size unchanged on reveal',initial_size['width']==after_size['width'] and initial_size['height']==after_size['height'])
    geometry=page.evaluate('''()=>['aesthetic-original','aesthetic-variant'].map(id=>({view:document.querySelector('#'+id+' svg').getAttribute('viewBox'),base:document.querySelector('#'+id+' path').outerHTML,rects:[...document.querySelectorAll('#'+id+' rect')].map(e=>({x:+e.getAttribute('x'),y:+e.getAttribute('y'),w:+e.getAttribute('width'),h:+e.getAttribute('height'),fill:getComputedStyle(e).fill}))}))''')
    a,b=geometry
    def gaps(rects):return [rects[i+1]['x']-rects[i]['x']-rects[i]['w'] for i in range(5)]
    ok('only gap distribution changes',a['view']==b['view'] and a['base']==b['base'] and all({k:v for k,v in x.items() if k!='x'}=={k:v for k,v in y.items() if k!='x'} for x,y in zip(a['rects'],b['rects'])))
    ok('six rectangles endpoints and total gap preserved',len(a['rects'])==len(b['rects'])==6 and a['rects'][0]==b['rects'][0] and a['rects'][-1]==b['rects'][-1] and sum(gaps(a['rects']))==sum(gaps(b['rects']))==160)
    page.locator('#aesthetic-comparison').screenshot(path=str(OUT/'comparison-desktop.png'))
    for _ in range(3):
        page.locator('#aesthetic-back').click();page.locator('#aesthetic-reveal').click()
    ok('repeated return and reveal retain prediction',page.locator('#aesthetic-variant').is_visible() and '修订' in page.locator('#aesthetic-predict').input_value())
    circle_before=page.locator('#aesthetic-circles').evaluate('(e)=>e.outerHTML')
    for title in ['solitude','left','none','left']:
        page.locator('#aesthetic-title').select_option(title)
        ok('title '+title+' leaves scene identical',page.locator('#aesthetic-circles').evaluate('(e)=>e.outerHTML')==circle_before)
    text_has(page,'aesthetic-caption','虚构教学标题：被落下')
    page.locator('#aesthetic-review').click();text_has(page,'aesthetic-review-status','还可补写');text_has(page,'aesthetic-review-status','不意味着内容正确')
    page.locator('[data-aesthetic-field]').evaluate_all("els=>els.forEach(e=>e.value='证据和目的由我复查，另一种解释也成立。')")
    page.locator('[data-aesthetic-check]').evaluate_all('els=>els.forEach(e=>e.checked=true)')
    page.locator('#aesthetic-review').click();text_has(page,'aesthetic-review-status','各记录栏已填写');text_has(page,'aesthetic-review-status','四项自查已确认')
    ok('editing does not autosave',page.evaluate('(k)=>localStorage.getItem(k)',key) is None)
    sentinel=json.dumps({'version':1,'mastery':{},'notes':{'path:zero-scale':'原课程疑问'},'migrations':{}},ensure_ascii=False)
    page.evaluate('([k,v])=>localStorage.setItem(k,v)',[oldkey,sentinel]);page.locator('#aesthetic-save').click()
    ok('save writes only dedicated exercise key',page.evaluate('(k)=>localStorage.getItem(k)',oldkey)==sentinel and page.evaluate('(k)=>JSON.parse(localStorage.getItem(k)).version',key)==1)
    page.goto(base+'/'+node)
    ok('standalone and path reuse the same exercise',page.locator('#aesthetic-title').input_value()=='left' and page.locator('#aesthetic-variant').is_visible() and page.locator('#aesthetic-observe').input_value().startswith('证据'))
    saved=page.evaluate('(k)=>localStorage.getItem(k)',key)
    page.locator('#aesthetic-reset').click()
    ok('reset clears page fields checks title and reveal',page.locator('#aesthetic-observe').input_value()=='' and page.locator('#aesthetic-variant').is_hidden() and page.locator('#aesthetic-title').input_value()=='none' and not page.locator('[data-aesthetic-check]').first.is_checked())
    ok('reset preserves saved copy',page.evaluate('(k)=>localStorage.getItem(k)',key)==saved)
    page.reload();ok('reload restores deliberate saved copy',page.locator('#aesthetic-variant').is_visible())
    # Export is available even if answers are in the hidden comparison section.
    with page.expect_download() as download:page.locator('#aesthetic-export').click()
    payload=json.loads(Path(download.value.path()).read_text())
    ok('export current exercise includes fields and checks',payload['version']==1 and len(payload['fields'])==13 and len(payload['checks'])==4)
    page.locator('#aesthetic-delete').click()
    ok('delete removes exercise key and preserves page plus other records',page.evaluate('(k)=>localStorage.getItem(k)',key) is None and page.locator('#aesthetic-observe').input_value().startswith('证据') and page.evaluate('(k)=>localStorage.getItem(k)',oldkey)==sentinel)
    page.reload();ok('deleted record does not return on reload',page.locator('#aesthetic-observe').input_value()=='' and page.locator('#aesthetic-variant').is_hidden())
    page.goto(base+'/Mine-Wiki/'+map_route)
    page.locator('a[href="../../lessons/aesthetics-observation/index.html"]').click()
    ok('GitHub Pages project prefix preserves links and local scripts',page.url==base+'/Mine-Wiki/'+path and page.evaluate('Object.keys(window.LessonUI)')==['aesthetic'])
    page.locator('#aesthetic-title').focus();page.keyboard.press('Home');page.keyboard.press('ArrowDown');page.keyboard.press('Enter')
    ok('title selector works by keyboard',page.locator('#aesthetic-title').input_value()=='solitude')
    ok('all worksheet fields have explicit labels',page.locator('[data-aesthetic-field]').evaluate_all('els=>els.every(e=>e.labels.length===1)'))
    ok('SVG examples expose accessible descriptions',page.locator('#lab-aesthetic svg').evaluate_all('els=>els.every(e=>e.getAttribute("role")==="img" && e.getAttribute("aria-label"))'))
    for width in [320,390,768]:
      page.set_viewport_size({'width':width,'height':844})
      for route,label in [(map_route,'map'),(node,'node'),(path,'unit'),('knowledge/form-composition/index.html','stub')]:
        page.goto(base+'/'+route);ok(f'{label} fits {width}px',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        if label=='stub':ok(f'unfinished node has no mastery at {width}px',page.locator('[data-mastery]').count()==0)
        if width==390 and label=='map':page.screenshot(path=str(OUT/'map-mobile.png'))
      page.goto(base+'/'+path);fill_before(page);original=page.locator('#aesthetic-original svg').bounding_box();page.locator('#aesthetic-reveal').click()
      ok(f'comparison fits and canvas is stable at {width}px',page.evaluate('document.documentElement.scrollWidth<=innerWidth') and page.locator('#aesthetic-original svg').bounding_box()['width']==original['width'])
      page.locator('#aesthetic-title').select_option('solitude');page.locator('#aesthetic-back').click();page.locator('#aesthetic-reveal').click();page.locator('#aesthetic-reset').click()
      ok(f'narrow return reset and repeated actions at {width}px',page.locator('#aesthetic-variant').is_hidden() and page.locator('#aesthetic-title').input_value()=='none')
      if width==390:
        fill_before(page);page.locator('#aesthetic-reveal').click();page.locator('#lab-aesthetic').scroll_into_view_if_needed();page.screenshot(path=str(OUT/'experiment-mobile.png'));page.locator('#aesthetic-comparison').screenshot(path=str(OUT/'comparison-mobile.png'))
    # No JS remains a readable lesson, with actual comparison and answers.
    nojs=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844});np=nojs.new_page();np.goto(base+'/'+node)
    np.locator('.fallback').first.locator('summary').click();np.locator('#exercise summary').click()
    ok('no-JS static comparison cases and answer',np.locator('.static-rhythm').is_visible() and np.locator('.case-card').count()==2 and np.locator('#exercise details').get_attribute('open') is not None)
    ok('no-JS controls explicitly disabled',np.locator('#aesthetic-save').is_disabled());nojs.close()
    # Storage refusal cannot prevent either visual exercise.
    for raw,label in [('{bad','malformed'),(json.dumps({'version':99}),'future')]:
      bad=browser.new_context(accept_downloads=True);bp=bad.new_page();bp.goto(base+'/index.html');bp.evaluate('([k,v])=>localStorage.setItem(k,v)',[key,raw]);bp.goto(base+'/'+path)
      fill_before(bp);bp.locator('#aesthetic-reveal').click();bp.locator('#aesthetic-save').click()
      ok(label+' record protected and comparison works',bp.evaluate('(k)=>localStorage.getItem(k)',key)==raw and bp.locator('#aesthetic-variant').is_visible())
      text_has(bp,'aesthetic-storage-status','未写入');bad.close()
    for script,label in [("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('blocked','SecurityError')}})",'blocked'),("Storage.prototype.setItem=function(){throw new DOMException('quota','QuotaExceededError')}",'quota')]:
      bad=browser.new_context(accept_downloads=True);bad.add_init_script(script);bp=bad.new_page();bp.goto(base+'/'+path);fill_before(bp);bp.locator('#aesthetic-reveal').click();bp.locator('#aesthetic-title').select_option('left');bp.locator('#aesthetic-save').click()
      text_has(bp,'aesthetic-storage-status','未写入');ok(label+' storage failure preserves interaction',bp.locator('#aesthetic-variant').is_visible())
      with bp.expect_download() as dl:bp.locator('#aesthetic-export').click()
      ok(label+' storage failure still allows export',json.loads(Path(dl.value.path()).read_text())['title']=='left');bad.close()
    mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,reduced_motion='reduce');mp=mobile.new_page();mp.goto(base+'/'+path);fill_before(mp);mp.locator('#aesthetic-reveal').tap()
    ok('mobile touch opens comparison',mp.locator('#aesthetic-variant').is_visible())
    mp.locator('#aesthetic-back').tap();mp.locator('#aesthetic-reveal').tap();mp.locator('#aesthetic-reset').tap()
    ok('mobile touch return repeat and reset',mp.locator('#aesthetic-variant').is_hidden() and mp.locator('#aesthetic-predict').input_value()=='');mobile.close()
    page.goto(base+'/'+path);context.set_offline(True);fill_before(page);page.locator('#aesthetic-reveal').click();page.locator('#aesthetic-title').select_option('left');page.locator('#aesthetic-back').click();page.locator('#aesthetic-reveal').click()
    ok('all exercise actions work offline after local load',page.locator('#aesthetic-variant').is_visible());context.set_offline(False)
    ok('no JavaScript errors',not errors);ok('no remote requests or answer uploads',not external)
    browser.close()
finally:server.shutdown()
(OUT/'browser-results.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'external_requests':external,'limitations':['Automated Chromium and screenshot review; no human participant study, no real assistive-technology session.']},ensure_ascii=False,indent=2)+'\n')
print(len(checks),'aesthetics browser checks passed')
