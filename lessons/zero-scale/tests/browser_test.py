#!/usr/bin/env python3
"""End-to-end checks using installed Chromium/Playwright; local server only."""
import json,sys,threading,http.server,functools
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'verification'
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
    context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True)
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
    page.locator('[data-mastery="points"]').check();contains(page,'progress-label','1 / 9')
    page.locator('#notes-input').fill('测试疑问：位置可达与完整矩阵可达。');page.locator('#save-notes').click();page.reload();ok('local note persistence',page.locator('#notes-input').input_value().startswith('测试疑问'));ok('mastery persistence',page.locator('[data-mastery="points"]').is_checked())
    with page.expect_download() as dl:page.locator('#export-notes').click()
    d=dl.value;payload=json.loads(Path(d.path()).read_text());ok('export JSON',payload['course']=='zero-scale' and payload['mastery']['points'])
    page.locator('#clear-notes').click();page.reload();ok('clear local notes',page.locator('#notes-input').input_value()=='');contains(page,'progress-label','0 / 9')
    # Same final video must actually decode and advance, not just have a source tag.
    page.locator('video').scroll_into_view_if_needed();page.locator('video').evaluate('(v)=>{v.muted=true;v.play().catch(()=>{});}');page.wait_for_function('document.querySelector("video").currentTime>0.4',timeout=15000);page.locator('video').evaluate('(v)=>v.pause()')
    duration=page.locator('video').evaluate('(v)=>v.duration');ok('video playable with finite duration',480<duration<540)
    page.locator('video').evaluate('(v)=>v.currentTime=300');page.wait_for_function('Math.abs(document.querySelector("video").currentTime-300)<1 && document.querySelector("video").readyState>=2');page.locator('video').screenshot(path=str(OUT/'video-browser.png'));ok('video seek to 5 minutes')
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
    blocked=browser.new_context();blocked.add_init_script("Object.defineProperty(window, 'localStorage', {get(){throw new DOMException('Blocked','SecurityError')}})");bp=blocked.new_page();bp.goto(url);bp.locator('#notes-input').fill('不可持久化');bp.locator('#save-notes').click();contains(bp,'notes-status','未允许本地存储');bp.locator('#basis-zero').click();contains(bp,'basis-output','det=0');blocked.close()
    # Exercise the pointer path with touch input at a mobile viewport.
    mobile=browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True);mp=mobile.new_page();mp.goto(url);mp.locator('#basis-reset').click();mp.locator('#handle-1').scroll_into_view_if_needed();box=mp.locator('#handle-1').bounding_box();x=box['x']+box['width']/2;y=box['y']+box['height']/2;cdp=mobile.new_cdp_session(mp)
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+40,'y':y}]});cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});ok('mobile touch drag',float(mp.locator('#b1x').input_value())>0);mobile.close()
    browser.close()
server.shutdown()
(OUT/'browser-results.json').write_text(json.dumps({'passed':len(checks),'checks':checks,'errors':errors,'external_requests':external,'video_duration':duration,'limitations':limitations},ensure_ascii=False,indent=2)+'\n')
print(f'{len(checks)} browser checks passed')
