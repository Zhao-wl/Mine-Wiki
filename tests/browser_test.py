#!/usr/bin/env python3
"""End-to-end checks using installed Chromium/Playwright; local server only."""
import json,sys,threading,http.server,functools
from pathlib import Path
from playwright.sync_api import sync_playwright
REPO=Path(__file__).resolve().parents[1];ROOT=REPO/'lessons/zero-scale';OUT=REPO/'verification';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts'))
from preview import RangeHandler
class QuietHandler(RangeHandler):
    def log_message(self,*args):pass
handler=functools.partial(QuietHandler,directory=str(REPO))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/lessons/zero-scale/index.html'
checks=[];limitations=[]
def ok(name,cond=True):
    assert cond,name
    checks.append(name);print('PASS',name,flush=True)
def contains(page,id,expected):ok(id+': '+expected,expected in page.locator('#'+id).inner_text())
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,reduced_motion='reduce')
    page=context.new_page();errors=[];external=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:external.append(r.url) if not r.url.startswith(('http://127.0.0.1:','blob:','data:')) else None)
    page.goto(url);page.screenshot(path=str(OUT/'desktop.png'))
    ok('nine static chapters',page.locator('.chapter').count()==9)
    ok('four experiments',page.locator('.lab').count()==4)
    page.locator('#basis-zero').click();contains(page,'basis-output','不构成平面的基')
    page.locator('#basis-reset').click();h=page.locator('#handle-1');h.focus();page.keyboard.press('ArrowRight');ok('basis keyboard handle',page.locator('#b1x').input_value()=='0.25')
    page.locator('#basis-reset').click();box=h.bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down();page.mouse.move(box['x']+box['width']/2+42,box['y']+box['height']/2,steps=8);page.mouse.up();ok('basis pointer drag',float(page.locator('#b1x').input_value())>0)
    page.locator('#basis-collinear').click();contains(page,'basis-output','det=0');page.locator('#basis-reset').click()
    page.locator('#order-reset').click();contains(page,'order-output','(2, 4)');contains(page,'order-output','(1, 3)')
    page.locator('#order-zero').click();contains(page,'order-output','(2, 2)');contains(page,'order-output','(3, 3)')
    page.locator('#order-next').click();contains(page,'order-output','第 0 步');page.locator('#order-reset').click()
    page.locator('#precision-kind').select_option('uniform');contains(page,'precision-output','κ₂=1；');contains(page,'precision-output','理论 δ/s：100')
    page.locator('#precision-s').select_option('0');contains(page,'precision-output','无解');page.locator('#precision-noise').select_option('0');contains(page,'precision-output','均任意')
    page.locator('#precision-s').select_option('0.00000001');contains(page,'precision-output','float32 反求 x：0');page.locator('#precision-reset').click()
    page.locator('[data-preset="old-zero"]').click();contains(page,'reparent-summary','保持完整矩阵：唯一解');contains(page,'reparent-summary','|=0')
    page.locator('[data-preset="unreachable"]').click();contains(page,'reparent-summary','只保持原点：无解')
    page.locator('[data-preset="position-only"]').click();contains(page,'reparent-summary','只保持原点：无穷多解');contains(page,'reparent-summary','保持完整矩阵：无解')
    page.locator('[data-preset="family"]').click();contains(page,'reparent-summary','保持完整矩阵：无穷多解');ok('free parameters enabled',page.locator('#free-a').is_enabled())
    for key,val in [('free-a','1'),('free-b','-1'),('free-t','2')]:page.locator('#'+key).fill(val)
    contains(page,'reparent-summary','|=0')
    page.locator('#new-ty').select_option('3');contains(page,'reparent-summary','保持完整矩阵：无解')
    page.locator('#keep-mode').select_option('local');contains(page,'reparent-summary','仅正向乘法');ok('free parameters disabled',not page.locator('#free-a').is_enabled())
    page.locator('#reparent-reset').click();page.locator('#lab-reparent').screenshot(path=str(OUT/'reparent-desktop.png'))
    page.locator('[data-mastery="point-vector"]').check();contains(page,'progress-label','1 / 9')
    page.locator('#notes-input').fill('测试疑问：位置可达与完整矩阵可达。');page.locator('#save-notes').click();page.reload();ok('local note persistence',page.locator('#notes-input').input_value().startswith('测试疑问'));ok('mastery persistence',page.locator('[data-mastery="point-vector"]').is_checked())
    with page.expect_download() as dl:page.locator('#export-notes').click()
    d=dl.value;payload=json.loads(Path(d.path()).read_text());ok('export JSON',payload['version']==1 and payload['mastery']['point-vector'] and payload['notes']['path:zero-scale'])
    page.locator('#clear-notes').click();page.reload();ok('clear local notes',page.locator('#notes-input').input_value()=='');contains(page,'progress-label','0 / 9')
    ok('video is optional history, not part of learning page',page.locator('video').count()==0)
    page.locator('#video summary').click();ok('legacy video anchor links to history',page.locator('#video a[href="history.html"]').count()==1)
    for width in [320,390,768]:
        page.set_viewport_size({'width':width,'height':844});page.goto(url)
        ok(f'no horizontal overflow at {width}px',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
        if width==390:
            page.screenshot(path=str(OUT/'mobile.png'));page.locator('#lab-reparent').screenshot(path=str(OUT/'reparent-mobile.png'));page.locator('#lab-basis').screenshot(path=str(OUT/'basis-mobile.png'))
    ok('no JavaScript errors',not errors);ok('no remote subresource requests',not external)
    # No-JS static fallback + native disclosure answers.
    nj=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844});np=nj.new_page();np.goto(url);ok('no-JS full content',np.locator('.chapter').count()==9 and np.locator('.fallback').count()==4);np.locator('#points details summary').click();ok('no-JS answer disclosure',np.locator('#points details').get_attribute('open') is not None);nj.close()
    # Managed browser policy may prohibit file://; record that boundary without bypassing it.
    off=browser.new_context(viewport={'width':390,'height':844});fp=off.new_page()
    try:
        fp.goto((ROOT/'index.html').as_uri());off.set_offline(True);fp.locator('[data-preset="position-only"]').click();contains(fp,'reparent-summary','保持完整矩阵：无解');ok('file:// offline interaction')
    except Exception as exc:
        if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(exc):raise
        limitations.append('Managed Chromium blocks file:// with ERR_BLOCKED_BY_ADMINISTRATOR; direct file opening not verified. No policy bypass attempted.')
        fp.close();fp=off.new_page();fp.goto(url);off.set_offline(True);fp.locator('[data-preset="position-only"]').click();contains(fp,'reparent-summary','保持完整矩阵：无解');fp.locator('#basis-zero').click();contains(fp,'basis-output','det=0');ok('offline interaction after loading exclusively from loopback')
    off.close()
    # Private-mode-like storage failure is surfaced, not fatal.
    blocked=browser.new_context();blocked.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new DOMException('Blocked','SecurityError')}})");bp=blocked.new_page();bp.goto(url);bp.locator('#notes-input').fill('不可持久化');bp.locator('#save-notes').click();contains(bp,'notes-status','未写入本地存储');bp.locator('#basis-zero').click();contains(bp,'basis-output','det=0');blocked.close()
    # Exercise the pointer path with touch input at a mobile viewport.
    mobile=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True);mp=mobile.new_page();mp.goto(url);mp.locator('#basis-reset').click();mp.locator('#handle-1').scroll_into_view_if_needed();box=mp.locator('#handle-1').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2;cdp=mobile.new_cdp_session(mp)
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+40,'y':y}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});ok('mobile touch drag',float(mp.locator('#b1x').input_value())>0);mobile.close()
    # Additional node, navigation and storage migration checks.
    page.set_viewport_size({'width':1440,'height':1000})
    catalog=json.loads((REPO/'content/paths/zero-scale.json').read_text());nodes=[s['node'] for s in catalog['steps']]
    base=url.split('/lessons/')[0]
    page.goto(base+'/index.html');page.screenshot(path=str(OUT/'home-desktop.png'))
    ok('home has two topic entries',page.locator('.card-grid .node-card').count()==2)
    for topic in ['linear-algebra','graphics-transforms']:
        page.goto(base+'/topics/'+topic+'/index.html');ok(topic+' has reusable nodes and path',page.locator('.node-card').count()>=7 and page.locator('.path-card').count()==1)
    for node in nodes:
        page.goto(base+'/knowledge/'+node+'/index.html')
        ok(node+' standalone unit',page.locator('.chapter').count()==1 and page.locator('.exercise').count()==1)
        ok(node+' only initializes present labs',page.evaluate('Object.keys(window.LessonUI).length')==page.locator('.lab').count())
        ok(node+' reverse path link',page.locator('#connections a[href*="lessons/zero-scale/index.html#"]').count()==1)
    page.goto(base+'/knowledge/basis-coordinates/index.html');page.locator('#basis-zero').click();contains(page,'basis-output','不构成平面的基');page.locator('#basis-reset').click()
    page.locator('#handle-1').focus();page.keyboard.press('ArrowRight');ok('standalone basis keyboard interaction',page.locator('#b1x').input_value()=='0.25')
    page.locator('#basis-reset').click();page.screenshot(path=str(OUT/'node-desktop.png'))
    page.locator('#connections').screenshot(path=str(OUT/'node-connections.png'))
    single_text=page.locator('.chapter .steps').inner_text()
    page.goto(url);ok('node and path share identical worked example',page.locator('#basis .steps').inner_text()==single_text)
    for step in catalog['steps']:
        page.goto(url+'#'+step['legacy_anchor']);ok('old anchor '+step['legacy_anchor'],page.locator('#'+step['legacy_anchor']).get_attribute('data-node-id')==step['node'])
    for width in [320,390,768]:
        page.set_viewport_size({'width':width,'height':844})
        for route,label in [('index.html','home'),('topics/linear-algebra/index.html','topic'),('knowledge/basis-coordinates/index.html','node'),('knowledge/invertibility-information/index.html','inverse'),('lessons/zero-scale/index.html','path')]:
            page.goto(base+'/'+route);ok(f'{label} no overflow at {width}px',page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
            if width==390:page.screenshot(path=str(OUT/(label+'-mobile.png')))
    ok('all visited learning pages have no JS errors',not errors);ok('all learning resources local',not external)
    # No-JS standalone node has its example, answer and prerequisite links.
    nj=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844});np=nj.new_page();np.goto(base+'/knowledge/basis-coordinates/index.html')
    np.locator('#exercise summary').click();ok('standalone node without JavaScript',np.locator('#exercise details').get_attribute('open') is not None and np.locator('.fallback').count()==1);nj.close()
    # Old records migrate even when the first entry is a standalone node.
    oldkey='mine-wiki.zero-scale.v1';newkey='mine-wiki.learning.v1'
    legacy={'mastery':{s['legacy_anchor']:i%2==1 for i,s in enumerate(catalog['steps'])},'notes':'旧课程疑问：可达位置与完整矩阵。'}
    legacy_raw=json.dumps(legacy,ensure_ascii=False)
    mc=browser.new_context(accept_downloads=True);mp=mc.new_page();mp.goto(base+'/index.html')
    mp.evaluate('([k,v])=>localStorage.setItem(k,v)',[oldkey,legacy_raw]);mp.goto(base+'/knowledge/basis-coordinates/index.html')
    ok('old mastery imported into stable node',mp.locator('[data-mastery="basis-coordinates"]').is_checked())
    ok('old path notes not misassigned to node',mp.locator('#notes-input').input_value()=='')
    saved=mp.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',newkey)
    ok('all nine old mastery keys mapped',all(saved['mastery'][s['node']]==legacy['mastery'][s['legacy_anchor']] for s in catalog['steps']))
    ok('legacy note preserved on path',saved['notes']['path:zero-scale']==legacy['notes'])
    ok('legacy source untouched',mp.evaluate('(k)=>localStorage.getItem(k)',oldkey)==legacy_raw)
    mp.locator('[data-mastery="basis-coordinates"]').uncheck();mp.reload();ok('migration only once, false remains false',not mp.locator('[data-mastery="basis-coordinates"]').is_checked())
    mp.locator('#notes-input').fill('节点自己的疑问');mp.locator('#save-notes').click();mp.goto(url)
    ok('path shows migrated note',mp.locator('#notes-input').input_value()==legacy['notes'])
    ok('path reflects shared node self-assessment',not mp.locator('[data-mastery="basis-coordinates"]').is_checked())
    second=mc.new_page();second.goto(base+'/knowledge/basis-coordinates/index.html');mp.locator('[data-mastery="basis-coordinates"]').check()
    second.wait_for_function('document.querySelector("[data-mastery]").checked');ok('cross-tab shared mastery updates',second.locator('[data-mastery]').is_checked())
    mp.locator('#clear-notes').click();mp.reload();ok('clear does not resurrect legacy mastery',not mp.locator('[data-mastery="basis-coordinates"]').is_checked())
    ok('clear does not resurrect legacy note',mp.locator('#notes-input').input_value()=='')
    ok('clear preserves old backup',mp.evaluate('(k)=>localStorage.getItem(k)',oldkey)==legacy_raw)
    saved=mp.evaluate('(k)=>JSON.parse(localStorage.getItem(k))',newkey);ok('clear preserves other page notes',saved['notes']['node:basis-coordinates']=='节点自己的疑问')
    with mp.expect_download() as dl:mp.locator('#export-notes').click()
    payload=json.loads(Path(dl.value.path()).read_text());ok('export retains all scopes and migration marker',payload['notes']['node:basis-coordinates']=='节点自己的疑问' and payload['migrations'][oldkey]);mc.close()
    # A newer explicit answer beats older migrated data.
    ec=browser.new_context();ep=ec.new_page();ep.goto(base+'/index.html')
    newer={'version':1,'mastery':{'basis-coordinates':False},'notes':{'path:zero-scale':'新疑问'},'migrations':{}}
    ep.evaluate('([a,b,c,d])=>{localStorage.setItem(a,b);localStorage.setItem(c,d)}',[oldkey,legacy_raw,newkey,json.dumps(newer,ensure_ascii=False)]);ep.goto(url)
    ok('migration preserves newer explicit false and notes',not ep.locator('[data-mastery="basis-coordinates"]').is_checked() and ep.locator('#notes-input').input_value()=='新疑问');ec.close()
    # Malformed or future records remain byte-for-byte untouched.
    for raw,label in [('{bad json','malformed'),(json.dumps({'version':99,'mastery':{},'notes':{},'migrations':{}}),'future version')]:
        bad=browser.new_context();bp=bad.new_page();bp.goto(base+'/index.html');bp.evaluate('([k,v])=>localStorage.setItem(k,v)',[newkey,raw]);bp.goto(base+'/knowledge/point-vector/index.html')
        bp.locator('[data-mastery]').check();bp.locator('#notes-input').fill('临时疑问');bp.locator('#save-notes').click()
        ok(label+' records never overwritten',bp.evaluate('(k)=>localStorage.getItem(k)',newkey)==raw);contains(bp,'notes-status','未写入');bad.close()
    bad=browser.new_context();bp=bad.new_page();bp.goto(base+'/index.html');bp.evaluate('(k)=>localStorage.setItem(k,"bad legacy")',oldkey);bp.goto(url)
    contains(bp,'notes-status','旧记录格式异常');ok('malformed legacy preserved',bp.evaluate('(k)=>localStorage.getItem(k)',oldkey)=='bad legacy');bad.close()
    quota=browser.new_context();quota.add_init_script("Storage.prototype.setItem=function(){throw new DOMException('Quota','QuotaExceededError')}");qp=quota.new_page();qp.goto(base+'/knowledge/basis-coordinates/index.html');qp.locator('#notes-input').fill('配额不足也可暂存');qp.locator('#save-notes').click();contains(qp,'notes-status','未允许本地存储');qp.locator('#basis-zero').click();contains(qp,'basis-output','不构成平面的基');quota.close()

    browser.close()
server.shutdown()
(OUT/'browser-results.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'external_requests':external,'limitations':limitations},ensure_ascii=False,indent=2)+'\n')
print(f'{len(checks)} browser checks passed')
