#!/usr/bin/env python3
"""Build static HTML, Markdown and SVGs from the shared Chinese course. Stdlib only."""
import json, re, html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'course.json').read_text())
E=html.escape
def svg_shell(body,title,w=880,h=340):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{E(title)}"><title>{E(title)}</title><rect width="100%" height="100%" rx="12" fill="#f3f6eb"/><defs><marker id="arr" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="context-stroke"/></marker></defs><g font-family="system-ui, Noto Sans CJK SC, sans-serif" fill="#203d3b">{body}</g></svg>'
def text(x,y,t,size=18,fill='#203d3b'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}">{E(t)}</text>'
def line(x,y,u,v,c='#17685b',width=3,arrow=False):
    return f'<line x1="{x}" y1="{y}" x2="{u}" y2="{v}" stroke="{c}" stroke-width="{width}"'+(' marker-end="url(#arr)"' if arrow else '')+'/>'
def dot(x,y,c='#b4472d'):
    return f'<circle cx="{x}" cy="{y}" r="6" fill="{c}"/>'
def figures():
    b=text(30,38,'01  点随平移走；位移不跟着原点走',22)
    for ox,label in [(70,'平移前'),(510,'平移后 t=(3,2)')]:
        b+=text(ox,82,label,18)+line(ox,250,ox+280,250,'#a4b8ad',1,True)+line(ox,250,ox,95,'#a4b8ad',1,True)
    b+=dot(120,200)+dot(170,200)+line(120,200,170,200,arrow=True)+text(112,232,'P')+text(166,232,'Q')+text(118,173,'d=(1,0)')
    b+=dot(710,100)+dot(760,100)+line(710,100,760,100,arrow=True)+text(687,137,'P+t')+text(751,137,'Q+t')+text(650,182,'同一个 d=(1,0)')
    b+=text(70,278,'P=(1,1)，Q=(2,1)',16)+text(510,278,'P+t=(4,3)，Q+t=(5,3)',16)
    b+=text(32,325,'(Q+t)−(P+t) = Q−P；向量记录方向与长度，点记录位置。',18)
    (ROOT/'assets/points.svg').write_text(svg_shell(b,'点与位移的区别',880,355))
    b=text(30,38,'02  坐标经过每一层：右侧先执行',22)
    boxes=[(30,'子空间','p=(0,0)'),(325,'父空间','Lp=(1,1)'),(620,'世界空间','PLp=(2,4)')]
    for x,a,c in boxes:
        b+=f'<rect x="{x}" y="100" width="230" height="112" rx="12" fill="#e1eadc"/>'+text(x+25,141,a,22)+text(x+25,182,c,20)
    b+=line(262,155,318,155,arrow=True)+text(282,130,'L')+line(557,155,613,155,arrow=True)+text(575,130,'P')
    b+=text(30,264,'L=T(1,1)；P=M₂；世界矩阵 W=P·L',21)+text(30,303,'若还有祖先 G，继续得到 G·P·L。平移列也会受上游影响。',18)
    (ROOT/'assets/hierarchy.svg').write_text(svg_shell(b,'子空间经局部矩阵和父世界矩阵到世界'))
    b=text(30,38,'03  s=0：一整片局部点，只剩一条世界线',22)
    b+=line(60,250,310,250,'#a4b8ad',1,True)+line(80,270,80,90,'#a4b8ad',1,True)+text(289,275,'x')+text(58,100,'y')
    for x in [125,195,265]:
        b+=dot(x,160)+text(x-18,138,{-1:'',125:'−5',195:'0',265:'8'}.get(x,''),15)
    b+=line(110,160,288,160,'#b4472d',2)+text(95,295,'(−5,1)、(0,1)、(8,1)',17)
    b+=line(350,170,455,170,'#17685b',3,True)+text(363,145,'F₀',22)
    b+=line(510,225,835,225,'#355ebe',3)+text(746,254,'v=2',18)+dot(650,225)+text(623,200,'(2,2)',19)
    b+=dot(650,110,'#999')+text(676,114,'(2,4) 不可达',18)+line(650,127,650,206,'#9ba79d',1)
    b+=text(489,301,'x 信息丢失；y=1 仍可确定。',18)
    (ROOT/'assets/collapse.svg').write_text(svg_shell(b,'精确零时可达直线与不可达目标'))
    b=text(28,40,'贯穿算例 · 同一个方块，两种命运',22)
    for ox,s in [(40,2),(470,0)]:
        # map world x,y in [0,5]x[0,6] into each panel
        def pt(x,y): return (ox+48+x*48,286-y*34)
        b+=text(ox+20,84,f's={s}    F(x,y)=(3−y,2+{s}x)',17)
        for k in range(6):
            b+=line(*pt(k,0),*pt(k,5),'#d7e1d4',1)+line(*pt(0,k),*pt(5,k),'#d7e1d4',1)
        b+=line(*pt(0,0),*pt(5.3,0),'#91a89e',1,True)+line(*pt(0,0),*pt(0,5.4),'#91a89e',1,True)
        verts=[(3-y,2+s*x) for x,y in [(0,0),(1,0),(1,1),(0,1)]]
        points=' '.join(f'{pt(x,y)[0]},{pt(x,y)[1]}' for x,y in verts)
        b+=f'<polygon points="{points}" fill="#cee3cb" stroke="#17685b" stroke-width="4"/>'
        b+=dot(*pt(2,2+s))+text(ox+210,164,f'(1,1) → (2,{2+s})',16)
        b+=text(ox+64,325,'面积非零，可唯一反求' if s else '压成 v=2，x 无法恢复',17)
    (ROOT/'assets/overview.svg').write_text(svg_shell(b,'s=2 保留面积，s=0 压成世界直线',880,355))

def main():
    figures()
    labraw=(ROOT/'labs.html').read_text()
    chunks=re.split(r'<!-- lab:(\w+) -->',labraw)
    labs=dict(zip(chunks[1::2],chunks[2::2]))
    sources={s['id']:s for s in DATA['sources']}
    def citation(sid):
        s=sources[sid]; return f'<a href="{s["url"]}" target="_blank" rel="noreferrer">{E(s["title"])}</a>'
    nav=''.join(f'<li><a href="#{c["id"]}">{i:02d} · {E(c["title"].split("：")[0])}</a></li>' for i,c in enumerate(DATA['chapters'],1))
    chapters=[]
    md=[f'# {DATA["title"]}',DATA['subtitle'],DATA['conventions'],'预计精读约 90 分钟，可分三次完成。先预测、再操作、最后手算。所有内容可离线使用。','## 统一算例','F_s(x,y)=(3−y,2+s·x)，A_s=[[0,−1],[s,0]]。先 x 缩放 s，再逆时针 90°，最后平移 (3,2)。s=2 时 (1,1)→(2,4)。']
    for i,c in enumerate(DATA['chapters'],1):
        paras=''.join(f'<p>{E(p)}</p>' for p in c['intuition'])
        steps=''.join(f'<li>{E(p)}</li>' for p in c['steps'])
        fig=f'<figure class="diagram"><a href="assets/{c["figure"]}" aria-label="单独查看放大图"><img src="assets/{c["figure"]}" alt="{E(c["title"])}"></a><figcaption>原创图解 · 点击可单独放大查看 · 与正文共用坐标约定和算例</figcaption></figure>' if 'figure' in c else ''
        cite='<p class="source">延伸依据：'+citation('numpy-cond' if c['id']=='precision' else 'numpy-pinv')+'。</p>' if c['id'] in ['inverse','precision'] else ''
        chapters.append(f'''<section class="chapter" id="{c['id']}"><div class="chapter-head"><span class="number">{i:02d}</span><span class="duration">约 {c['minutes']} 分钟 · 先理解，再动手</span></div><h2>{E(c['title'])}</h2><h3>先有直觉</h3>{paras}<pre class="formula">{E(c['formula'])}</pre>{fig}<h3>一步一步算</h3><ol class="steps">{steps}</ol>{labs.get(c.get('lab',''),'')}<div class="exercise"><span class="tag">停一下 · 自己算</span><p>{E(c['exercise'])}</p><details><summary>展开答案与理由</summary><p>{E(c['answer'])}</p></details></div>{cite}<p class="bridge">下一步 · {E(c['bridge'])}</p><label class="mastery"><input type="checkbox" data-mastery="{c['id']}">我能不用看答案解释这一节</label></section>''')
        md.extend([f'## {i:02d} {c["title"]}','### 直觉',*c['intuition'],'```text\n'+c['formula']+'\n```'])
        if 'figure' in c: md.append(f'![{c["title"]}](assets/{c["figure"]})')
        md+=['### 逐步算例','\n'.join(f'{n}. {t}' for n,t in enumerate(c['steps'],1)),'### 小练习',c['exercise'],'### 答案与理由',c['answer'],c['bridge']]
        if c['id'] in ['inverse','precision']:
            s=sources['numpy-cond' if c['id']=='precision' else 'numpy-pinv'];md.append(f'延伸依据：[{s["title"]}]({s["url"]})。')
    api=''.join(f'<h3>{E(a["title"])}</h3><p>{E(a["text"])}'+(f' {citation(a["source"])}。' if 'source' in a else '')+'</p>' for a in DATA['api'])
    src=''.join(f'<li id="source-{s["id"]}">{citation(s["id"])}<span>{E(s["note"])}</span></li>' for s in DATA['sources'])
    advanced='''<details><summary>进阶：等秩为什么仍不够？零旧父与 TRS 又如何分开？</summary><p>rank(B)≤rank(A) 只是必要条件。例如 A=diag(0,1)，B=diag(1,0)，两者秩都为 1，但 B 的第一列 (1,0) 不在 A 的竖直列空间中，AC=B 无解。必须看每列落在哪个子空间。</p><p>再取旧父 diag(0,1)，子旋转 45°，新父 I。唯一的新局部线性矩阵是 [[0,0],[1/√2,1/√2]]。两列非零且共线；单个 R·diag(sx,sy) 的非零列必须正交，所以这个矩阵无法写成该形式。它作为仿射矩阵有解，却无法无损表示成单个无剪切 TRS。</p><p>另一个快速反例：新父 F(x,y)=(10,y)。位置 (10,2) 的解是 (任意 x,2)，(11,2) 无解；即使原点能到 (10,2)，B=I 的完整物体也无法保持，因为新父不能产生水平位移。不要把 lossyScale 逐轴相除当成通用换父算法。</p></details>'''
    media='''<section class="appendix" id="video"><div class="eyebrow" style="color:var(--teal)">WATCH & REVISIT</div><h2>带着图，再走一遍</h2><p>中文离线合成配音导读，覆盖九节的因果链。视频用于复习，完整逐步算例与小练习仍在上文。音色偏机械；字幕已烧录进画面，无需联网字幕服务。</p><video class="video" controls preload="metadata" playsinline poster="media/poster.jpg"><source src="media/lesson-zh.mp4" type="video/mp4"><track kind="subtitles" srclang="zh" label="中文" src="media/lesson-zh.vtt">浏览器无法播放时，请下载 MP4。</video><div class="chips"><a href="media/lesson-zh.mp4" download>下载视频 MP4</a><a href="media/lesson-zh.srt" download>字幕 SRT</a><a href="media/transcript.md">完整讲稿与时间码</a></div></section>'''
    body=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="以零缩放换父节点为线索，从点和向量开始重学线性代数。离线中文课程、四个交互实验、图解和讲解视频。"><title>{E(DATA['title'])} · Mine-Wiki</title><link rel="stylesheet" href="styles.css"><script src="math.js" defer></script><script src="app.js" defer></script></head><body><a class="skip" href="#course-start">跳到课程正文</a><header class="topbar"><a href="../../index.html" class="brand">MINE / WIKI</a><span class="pill">学习案例 001 · 坐标变换</span></header><section class="hero"><div><div class="eyebrow">A SMALL CASE, A DEEP UNDERSTANDING</div><h1>缩放为零之后，<br>坐标去了哪里？</h1><p>{E(DATA['subtitle'])}。不急着背逆矩阵公式，先看见一个方向如何消失。</p><a class="button" href="#points">从一支箭头开始 ↗</a><div class="meta">9 节循序课程 / 4 个实验 / 中文讲解视频<br>静态离线 · 无账号 · 学习记录只在当前浏览器</div></div><figure>{(ROOT/'assets/overview.svg').read_text()}</figure></section><div class="layout"><nav class="rail" aria-label="课程目录"><div class="label">LEARNING PATH / 学习路径</div><ol>{nav}<li><a href="#api">10 · 数学与 Unity API 边界</a></li><li><a href="#video">11 · 视频与讲稿</a></li><li><a href="#references">12 · 引用与继续学习</a></li></ol><div class="progress"><label for="progress">掌握度 <span id="progress-label">0 / 9</span></label><progress id="progress" max="9" value="0"></progress><p class="small">勾选表示自评，不是考试成绩。</p></div><a href="course.md">纯文字 Markdown ↗</a></nav><main id="course-start"><section class="intro"><h2>先约定同一张地图</h2><p>{E(DATA['conventions'])}</p><div class="callout"><p>学习目标：独立判断换父时在求什么、何时有解、为何丢信息，以及数学和引擎 API 之间还隔着哪些条件。这里不替项目选择零缩放处理策略。</p></div><p>建议分三次读：01–03 建立坐标直觉，04–06 串起变换，07–09 回答零缩放。每节先预测，再算例，再做小练习。预计精读约 90 分钟。</p><pre class="formula">F_s(x,y) = (3−y, 2+s·x)\n先 x 缩放 s → 逆时针 90° → 平移 (3,2)\ns=2 时，(1,1) → (2,4)</pre><noscript><p class="callout">JavaScript 已关闭。正文、图解、小练习答案和实验静态后备仍可阅读；交互与本地记录不可用。</p></noscript></section>{''.join(chapters)}<section class="appendix" id="api"><h2>数学结论 ≠ 未实测的引擎行为</h2>{api}{advanced}<h3>迁移到真实项目时，先问这些问题</h3><ol><li>目标是保持局部、仅世界位置，还是完整世界矩阵？</li><li>使用的父矩阵是否包括祖先和挂点？新父是否奇异？</li><li>目标平移与各列是否可达？回代残差是多少？</li><li>可解矩阵能否由该 API 的 TRS 表示？是否出现剪切？</li><li>浮点精度与可接受误差是什么？引擎版本和实测结果是什么？</li></ol></section>{media}<section class="appendix feedback" id="notes"><h2>留一个还没想通的问题</h2><p>记录仅保存在当前浏览器的 localStorage，不上传。私密浏览或直接打开文件时，浏览器可能禁用存储；页面会明确显示状态。可导出 JSON 留底。</p><label for="notes-input">我的疑问 / 我想再算一遍的例子</label><textarea id="notes-input" placeholder="例如：为什么位置可达，完整矩阵却不一定可达？"></textarea><div class="lab-buttons"><button id="save-notes" class="primary">保存在本机</button><button id="export-notes">导出记录</button><button id="clear-notes">清除本课记录</button></div><p class="feedback-status" id="notes-status" aria-live="polite">尚未保存。</p></section><section class="appendix" id="references"><h2>引用与继续学习</h2><p class="small">官方来源核查日期：2026-10-08。Unity 链接固定在 6.0（6000.0）。正文的数值、图形与推导为原创教学算例；本环境没有执行 Unity 实测。</p><ol class="source">{src}</ol><div class="chips"><a href="verification/report.md">查看验证报告</a><a href="README.md">文件与复现说明</a></div></section></main></div><footer>Mine-Wiki / 案例 001 · 数学模型使用一般仿射矩阵。课程无远程脚本、无统计、无自动上传。外部参考链接仅在主动打开时联网。</footer></body></html>'''
    (ROOT/'index.html').write_text(body)
    md+=['## 数学与 API 边界']
    for a in DATA['api']:
        md += ['### '+a['title'],a['text']]
        if 'source' in a:
            s=sources[a['source']]; md +=[f'来源：[{s["title"]}]({s["url"]})。']
    md+=['## 进阶辨析',re.sub('<[^>]+>','',advanced),'## 引用资料（核查日期 2026-10-08）']
    md += [f'- [{s["title"]}]({s["url"]})：{s["note"]}' for s in DATA['sources']]
    md+=['## 其他形式','[交互 HTML](index.html) · [图解总览](assets/overview.svg) · [中文视频](media/lesson-zh.mp4) · [讲稿](media/transcript.md) · [字幕](media/lesson-zh.srt)']
    (ROOT/'course.md').write_text('\n\n'.join(md)+'\n')
    print('Built index.html, course.md and 4 SVG diagrams')
if __name__=='__main__': main()
