#!/usr/bin/env python3
"""Generate offline node pages, topics and continuous paths from one content source."""
import argparse,html,json,posixpath,re
from pathlib import Path
from knowledge import ROOT,load_catalog,validate,reverse_index,anchors,ContentError
E=html.escape
LABEL={'stub':'待补充','draft':'整理中','ready':'可学习'}

def node_url(key):return f'knowledge/{key}/index.html'
def path_url(key):return f'lessons/{key}/index.html'
def topic_url(key):return f'topics/{key}/index.html'
def relative(page,target):
    file,sep,fragment=target.partition('#')
    result=posixpath.relpath(file,posixpath.dirname(page) or '.') if file else ''
    return result+(sep+fragment if sep else '')

def render_site(c):
    reverse=reverse_index(c);out={};raw=(ROOT/'assets/labs.html').read_text();chunks=re.split(r'<!-- lab:(\w+) -->',raw);labs=dict(zip(chunks[1::2],chunks[2::2]))
    config={'version':1,'legacy':[{'path':key,**p['legacy_storage']} for key,p in c['paths'].items() if 'legacy_storage'in p]}
    def link(page,target,label,cls=''):
        return f'<a href="{E(relative(page,target))}"'+(f' class="{cls}"' if cls else '')+f'>{E(label)}</a>'
    def node_link(page,ref,within=None):
        key=ref['node'];anchor=ref.get('anchor');target=node_url(key)+(('#'+anchor) if anchor else '')
        if within and key in within and anchor not in {'connections','notes','references'}:
            target='#'+within[key]+(('--'+anchor) if anchor and anchor!='overview' else '')
        href=target if target.startswith('#') else relative(page,target)
        return f'<a href="{E(href)}">{E(c["nodes"][key]["title"].split("：")[0])}</a>'
    def sources(page,ids,prefix=''):
        items=''.join(f'<li id="{prefix}source-{sid}"><a href="{E(c["sources"][sid]["url"])}" target="_blank" rel="noreferrer">{E(c["sources"][sid]["title"])}</a><span>{E(c["sources"][sid]["note"])}</span></li>' for sid in dict.fromkeys(ids))
        return f'<ol class="source">{items}</ol>'
    def example(key):
        ex=c['examples'][key]
        return f'<details class="example-context"><summary>本页算例与坐标约定</summary><p>{E(ex["conventions"])}</p><pre class="formula">{E(ex["formula"])}</pre></details>'
    def note_box():
        return '''<section class="appendix feedback" id="notes"><h2>留一个还没想通的问题</h2><p>疑问按当前节点或问题路径分别保存；掌握度在使用同一节点的页面间共享。记录只在当前浏览器，不上传。</p><label for="notes-input">我的疑问 / 想再算一遍的例子</label><textarea id="notes-input" placeholder="先记下卡住的一步，之后可以从这里继续。"></textarea><div class="lab-buttons"><button id="save-notes" class="primary">保存在本机</button><button id="export-notes">导出全部学习记录</button><button id="clear-notes">清除此页记录</button></div><p class="small">清除会重置此页所含节点的共享自评及此页疑问；不会清除其他疑问，也不会删除迁移前的备份。</p><p id="notes-status" class="feedback-status" aria-live="polite">启用 JavaScript 后可保存本地记录。</p></section>'''
    def progress(count):
        return f'<div class="progress"><label for="progress">本页自评 <span id="progress-label">0 / {count}</span></label><progress id="progress" max="{count}" value="0"></progress><p class="small">掌握度属于知识节点，可在其他路径继续使用。</p></div>'
    def shell(page,title,hero,body,rail='',scope='',count=0):
        nav=''.join(link(page,topic_url(k),t['title']) for k,t in c['topics'].items())
        cfg=json.dumps(config,ensure_ascii=False).replace('<','\\u003c')
        return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Mine-Wiki：关联前置知识，从问题出发逐步理解。静态离线交互学习。"><title>{E(title)} · Mine-Wiki</title><link rel="stylesheet" href="{relative(page,'assets/styles.css')}"><script src="{relative(page,'assets/math.js')}" defer></script><script src="{relative(page,'assets/app.js')}" defer></script></head>
<body data-record-scope="{E(scope)}"><script type="application/json" id="learning-config">{cfg}</script><a class="skip" href="#course-start">跳到正文</a><header class="topbar">{link(page,'index.html','MINE / WIKI','brand')}<nav class="top-links" aria-label="主题">{nav}</nav></header>
{hero}<div class="layout{' catalog-layout' if not rail else ''}">{('<nav class="rail" aria-label="本页导航">'+rail+progress(count)+'</nav>') if rail else ''}<main id="course-start">{body}<noscript><p class="callout">JavaScript 已关闭。正文、图解、练习答案和实验静态后备仍可阅读；交互与本地记录不可用。</p></noscript></main></div><footer>Mine-Wiki · 从问题出发，持续修订理解。内容可离线阅读；学习记录保存在本机。外部资料只在主动打开链接时访问。</footer></body></html>\n'''
    def hero(label,title,summary,extra='',art=False):
        figure=f'<figure>{(ROOT/"lessons/zero-scale/assets/overview.svg").read_text()}</figure>' if art else ''
        return f'<section class="hero{ " compact-hero" if not art else ""}"><div><div class="eyebrow">{E(label)}</div><h1>{E(title)}</h1><p>{E(summary)}</p>{extra}</div>{figure}</section>'
    def relation_list(page,refs,within=None,reasons=False):
        return '<ul>'+''.join('<li>'+node_link(page,r,within)+(f'：{E(r["reason"])}' if reasons and r.get('reason') else '')+'</li>' for r in refs)+'</ul>'
    def connections(page,key):
        back=reverse[key];parts=[]
        if back['required_by']:parts.append('<h3>哪些知识以此为前提</h3>'+relation_list(page,back['required_by'],reasons=True))
        if back['related']:
            explicit={r['node']:r for r in c['nodes'][key]['related']}
            parts.append('<h3>相关延伸 · 可按需阅读</h3>'+relation_list(page,[explicit.get(n,{'node':n}) for n in back['related']]))
        if back['paths']:parts.append('<h3>在问题中使用</h3><ul>'+''.join('<li>'+link(page,path_url(p)+'#'+key,c['paths'][p]['title'])+'</li>' for p in back['paths'])+'</ul>')
        if back['topics']:parts.append('<p>所属主题：'+' · '.join(link(page,topic_url(t),c['topics'][t]['title']) for t in back['topics'])+'</p>')
        return ''.join(parts)
    def content(page,n,section_id,standalone=False,number=None,within=None):
        def aid(name):return name if standalone else section_id+'--'+name
        alias=f'<span class="anchor-alias" id="{n["id"]}"></span>' if n['id']!=section_id and not standalone else ''
        req='<h3>先理解这些</h3>'+relation_list(page,n['requires'],within,True) if n['requires'] else '<p class="small">本单元不要求先阅读其他知识节点。</p>'
        head=(f'<span class="number">{number:02}</span>' if number else '')+f'<span class="duration">约 {n.get("minutes",0)} 分钟 · {LABEL[n["status"]]}</span>'
        body=''
        if n['status']!='ready':body+=f'<p class="callout">{LABEL[n["status"]]}：{E(n["summary"])}。尚不作为已完成的前置知识。</p>'
        missing=[r for r in n['requires'] if c['nodes'][r['node']]['status']!='ready']
        if missing:body+='<p class="callout">前置待补齐：'+', '.join(E(c['nodes'][r['node']]['title']) for r in missing)+'</p>'
        if n.get('intuition'):body+=f'<h3 id="{aid("intuition")}">先有直觉</h3>'+''.join(f'<p>{E(t)}</p>' for t in n['intuition'])
        if n.get('formula'):body+=f'<pre class="formula" id="{aid("formula")}">{E(n["formula"])}</pre>'
        if n.get('figure'):body+=f'<figure class="diagram"><a href="{relative(page,n["figure"])}"><img src="{relative(page,n["figure"])}" alt="{E(n["title"])}"></a><figcaption>原创图解 · 点击可单独放大查看</figcaption></figure>'
        if n.get('steps'):body+=f'<h3 id="{aid("example")}">{"一步一步算" if n.get("formula") else "逐步理解与例证"}</h3><ol class="steps">'+''.join(f'<li>{E(t)}</li>' for t in n['steps'])+'</ol>'
        if n.get('lab'):body+=f'<div id="{aid("experiment")}">'+labs[n['lab']]+'</div>'
        if n.get('exercise'):body+=f'<div class="exercise" id="{aid("exercise")}"><span class="tag">停一下 · {"自己算" if n.get("formula") else "检查理解"}</span><p>{E(n["exercise"])}</p>'+ (f'<details><summary>展开答案与理由</summary><p>{E(n["answer"])}</p></details>' if n.get('answer') else '<p>答案整理中。</p>')+'</div>'
        if n.get('sources'):body+='<p class="source">依据与延伸：'+' · '.join(f'<a href="{E(c["sources"][sid]["url"])}" target="_blank" rel="noreferrer">{E(c["sources"][sid]["title"])}</a>' for sid in n['sources'])+'</p>'
        if n['status']=='ready':body+=f'<label class="mastery"><input type="checkbox" data-mastery="{n["id"]}">我能不用看答案解释这一单元</label>'
        return f'<section class="chapter" id="{section_id}" data-node-id="{n["id"]}">{alias}<div class="chapter-head">{head}</div><h2>{E(n["title"])}</h2>{req}{body}</section>'
    def card(page,key):
        n=c['nodes'][key];return f'<article class="node-card"><span class="status-chip">{LABEL[n["status"]]} · {n.get("minutes",0)} 分钟</span><h3>{link(page,node_url(key),n["title"].split("：")[0])}</h3><p>{E(n["summary"])}</p><p class="small">{len(n["requires"])} 项必要前置 · {len(reverse[key]["paths"])} 条问题路径使用</p></article>'
    def path_card(page,key):
        p=c['paths'][key];return f'<article class="path-card"><span class="eyebrow">问题学习路径 · {LABEL[p["status"]]}</span><h3>{link(page,path_url(key),p["title"])}</h3><p>{E(p["summary"])}</p><p class="small">{len(p["steps"])} 个完整学习单元 · 可连续阅读，也可从熟悉的节点进入</p></article>'
    page='index.html'
    topic_cards=''.join(f'<article class="node-card"><h3>{link(page,topic_url(k),t["title"])}</h3><p>{E(t["summary"])}</p><p class="small">{len(t["nodes"])} 个知识节点</p></article>' for k,t in c['topics'].items())
    body='<section class="intro"><h2>沿主题找知识</h2><p>同一节点可以出现在多个主题和问题里。解释、算例与自评随节点复用。</p><div class="card-grid">'+topic_cards+'</div></section><section class="appendix"><h2>带着一个问题开始</h2>'+''.join(path_card(page,k) for k in c['paths'])+'</section>'
    out[page]=shell(page,'相互连接的学习笔记',hero('LEARN · CONNECT · REVISIT','从一个问题，走向相互连接的理解。','把前提弄清，把过程算明白。每次学习都能复用已有知识，并留下下一次追问的入口。'),body)
    for key,t in c['topics'].items():
        page=topic_url(key);body='<section class="intro"><h2>知识节点</h2><p>需要补哪一段，就从哪一段开始。节点页会列出必要前置和继续使用它的地方。</p><div class="card-grid">'+''.join(card(page,n) for n in t['nodes'])+'</div></section><section class="appendix"><h2>相关问题路径</h2>'+''.join(path_card(page,p) for p in t['paths'])+'</section>'
        out[page]=shell(page,t['title'],hero('主题导航',t['title'],t['summary']),body)
    for key,n in c['nodes'].items():
        page=node_url(key);body='<section class="intro">'+(example(n['example']) if n.get('example') else '')+'</section>'+content(page,n,'overview',True)+'<section class="appendix" id="connections"><h2>把这段理解接到别处</h2>'+connections(page,key)+'</section>'+note_box()+f'<section class="appendix" id="references"><h2>引用资料</h2>{sources(page,n.get("sources",[]))}</section>'
        rail='<div class="label">一个完整学习单元</div><ol>'+''.join(f'<li><a href="#{a}">{title}</a></li>' for a,title in [('overview','从这里开始'),('intuition','直觉'),('example','逐步算例' if n.get('formula') else '例证与推演'),('experiment','交互实验'),('exercise','练习与答案'),('connections','前后关联'),('notes','我的疑问')] if a in anchors(n))+'</ol>'
        out[page]=shell(page,n['title'],hero('知识节点 · '+LABEL[n['status']],n['title'],n['summary']),body,rail,'node:'+key,1 if n['status']=='ready' else 0)
    for key,p in c['paths'].items():
        page=path_url(key);within={s['node']:s.get('legacy_anchor',s['node']) for s in p['steps']}
        rail='<div class="label">按问题串起知识</div><ol>'+''.join(f'<li><a href="#{within[s["node"]]}">{i:02d} · {E(c["nodes"][s["node"]]["title"].split("：")[0])}</a></li>' for i,s in enumerate(p['steps'],1))+'<li><a href="#api">应用与引擎边界</a></li><li><a href="#references">引用资料</a></li></ol>'
        goals=''.join(f'<li>{E(g)}</li>' for g in p.get('goals',[]))
        body=f'<section class="intro" id="overview"><h2>带着什么问题往下读</h2><p>{E(p["summary"])}</p><ul>{goals}</ul><p>完整阅读约 {sum(c["nodes"][s["node"]].get("minutes",0) for s in p["steps"])} 分钟，可分段完成。每节均可单独打开；这里保留同一算例和过渡，帮助连贯理解。课程提供判断依据，不替项目选择零缩放策略。</p>{example(p["example"])}</section>'
        if p['status']!='ready':body+='<p class="callout">这条路径仍在整理，包含的待补充节点会明确标出。</p>'
        for i,s in enumerate(p['steps'],1):
            n=c['nodes'][s['node']];body+=content(page,n,within[n['id']],number=i,within=within)
            body+='<div class="step-bridge"><p>'+link(page,node_url(n['id']),'单独学习此节点与查看关联 ↗')+'</p><p class="bridge">'+E(s.get('bridge',''))+'</p></div>'
        api=''.join(f'<h3>{E(a["title"])}</h3><p>{E(a["text"])}'+(f' <a href="{E(c["sources"][a["source"]]["url"])}" target="_blank" rel="noreferrer">官方依据</a>。' if a.get('source') else '')+'</p>' for a in p.get('api',[]))
        advanced=p.get('advanced');api+=(f'<details><summary>{E(advanced["title"])}</summary>'+''.join(f'<p>{E(t)}</p>' for t in advanced['paragraphs'])+'</details>') if advanced else ''
        api+='<h3>迁移到真实项目时，先问这些问题</h3><ol>'+''.join(f'<li>{E(t)}</li>' for t in p.get('checklist',[]))+'</ol>'
        body+='<section class="appendix" id="api"><h2>数学结论与引擎行为的边界</h2>'+api+'</section>'+note_box()
        body+=f'<section class="appendix" id="references"><h2>引用与继续学习</h2><p class="small">资料核查日期：{E(c["checked_at"])}。Unity 链接固定在 6.0；本环境未执行 Unity 实测。</p>{sources(page,p.get("sources",[]))}</section>'
        if p.get('historical_media'):
            history=f'lessons/{key}/history.html'
            body+='<section class="appendix historical" id="video"><details><summary>历史辅助资料 · 按需查看</summary><p>早期视频、字幕和文字导出保留供回看。当前学习以交互网页为主，历史视频不随节点持续修订。</p><div class="chips">'+link(page,history,'历史视频与字幕')+link(page,f'lessons/{key}/course.md','本次路径的文字导出')+'</div></details></section>'
            media=p['historical_media'];hbody='<section class="intro"><h2>历史辅助资料</h2><p>此视频对应初版九节课程，配音为 eSpeak NG 中文合成音。保留作历史回看，不保证跟随当前知识节点的修订。学习请以交互网页为准。</p>'+link(history,page,'返回当前问题学习路径')+f'<video class="video" controls preload="none" playsinline poster="{relative(history,media["poster"])}"><source src="{relative(history,media["video"])}" type="video/mp4"><track kind="subtitles" srclang="zh" label="中文" src="{relative(history,media["captions"])}"></video><div class="chips">'+link(history,media['video'],'原视频 MP4')+link(history,media['srt'],'字幕 SRT')+link(history,media['transcript'],'原始逐字稿')+'</div></section>'
            out[history]=shell(history,'历史辅助资料',hero('历史存档','视频与原始讲稿','早期导读保留，交互网页是持续维护的学习入口。'),hbody)
        out[page]=shell(page,p['title'],hero('问题学习路径 · '+LABEL[p['status']],p['title'],p['subtitle'],f'<a class="button" href="#{within[p["steps"][0]["node"]]}">沿路径开始学习 ↗</a>',True),body,rail,'path:'+key,sum(c['nodes'][s['node']]['status']=='ready' for s in p['steps']))
        # Legacy exports remain derived products, never a second authoring source.
        ex=c['examples'][p['example']];chapters=[];md=[f'# {p["title"]}','本文件由知识节点与问题路径生成。交互网页是主要学习入口。',ex['conventions'],ex['formula']]
        for i,s in enumerate(p['steps'],1):
            n=c['nodes'][s['node']];legacy={k:n[k] for k in ['title','minutes','intuition','formula','steps','exercise','answer','lab'] if k in n};legacy.update(id=s.get('legacy_anchor',n['id']),bridge=s.get('bridge',''))
            if n.get('figure'):legacy['figure']=Path(n['figure']).name
            chapters.append(legacy);md+=[f'## {i:02d} {n["title"]}','### 直觉',*n.get('intuition',[]),'```text\n'+n.get('formula','')+'\n```','### 逐步算例',*[f'{j}. {t}' for j,t in enumerate(n.get('steps',[]),1)],'### 小练习',n.get('exercise',''),'### 答案与理由',n.get('answer',''),s.get('bridge','')]
            if n.get('figure'):md.append(f'![{n["title"]}]({relative(f"lessons/{key}/course.md",n["figure"])})')
        md+=['## 应用与引擎边界',*[a['title']+'：'+a['text'] for a in p.get('api',[])],'## 引用资料',*[f'- [{c["sources"][sid]["title"]}]({c["sources"][sid]["url"]})' for sid in p.get('sources',[])]]
        out[f'lessons/{key}/course.md']='\n\n'.join(md)+'\n'
        out[f'lessons/{key}/course.json']=json.dumps({'_generated':'Do not edit; generated from content/nodes and content/paths.','title':p['title'],'subtitle':p['subtitle'],'conventions':ex['conventions'],'facts':ex['facts'],'chapters':chapters,'api':p.get('api',[]),'sources':[c['sources'][sid] for sid in p.get('sources',[])]},ensure_ascii=False,indent=2)+'\n'
    # Keep old asset URLs functional. Canonical shared code lives under assets/.
    for name in ['math.js','app.js','styles.css','labs.html']:out['lessons/zero-scale/'+name]=(ROOT/'assets'/name).read_text()
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true',help='Validate and compare generated files without writing');args=p.parse_args()
    try:
        catalog=load_catalog();counts=validate(catalog);outputs=render_site(catalog)
        if args.check:
            stale=[name for name,data in outputs.items() if not (ROOT/name).exists() or (ROOT/name).read_text()!=data]
            if stale:raise ContentError('Stale generated files: '+', '.join(stale))
        else:
            for name,data in outputs.items():
                dest=ROOT/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(data)
        print(json.dumps({**counts,'generated_files':len(outputs),'mode':'check' if args.check else 'build'},ensure_ascii=False))
    except (ContentError,KeyError,TypeError) as e:raise SystemExit(str(e))
if __name__=='__main__':main()
