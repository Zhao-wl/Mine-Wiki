#!/usr/bin/env python3
"""Create an allowlisted offline reader ZIP; no upload, credentials or deployment."""
import argparse,hashlib,json,posixpath,subprocess,zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
from knowledge import ROOT,load_catalog,validate
from build_site import render_site,node_url,topic_url,path_url

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:self.ids.add(a['id'])
        for key in ('href','src','poster'):
            if key in a:self.links.append(a[key])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    output=args.output.resolve()
    if output.is_relative_to(ROOT):raise SystemExit('Put the reader ZIP outside the repository.')
    c=load_catalog();validate(c)
    for name,text in render_site(c).items():
        if not (ROOT/name).is_file() or (ROOT/name).read_text()!=text:raise SystemExit('Rebuild stale generated file: '+name)
    names={'index.html','assets/app.js','assets/math.js','assets/styles.css'}
    names.update(node_url(key) for key in c['nodes']);names.update(topic_url(key) for key in c['topics'])
    names.update(n['figure'] for n in c['nodes'].values() if n.get('figure'))
    for key,path in c['paths'].items():
        names.update([path_url(key),f'lessons/{key}/course.md'])
        if path.get('historical_media'):
            names.add(f'lessons/{key}/history.html');names.update(path['historical_media'].values())
    contents={}
    for name in sorted(names):
        source=ROOT/name
        if source.is_symlink() or not source.resolve().is_relative_to(ROOT):raise SystemExit('Unsupported file path: '+name)
        if source.suffix not in {'.html','.js','.css','.svg','.png','.jpg','.jpeg','.webp','.mp4','.srt','.vtt','.md'}:raise SystemExit('Unexpected asset type: '+name)
        contents[name]=source.read_bytes()
    parsed={}
    for name,data in contents.items():
        if name.endswith('.html'):q=Links();q.feed(data.decode());parsed[name]=q
    for name,page in parsed.items():
        for link in page.links:
            url=urlsplit(link)
            if url.scheme in {'https','http'}:continue
            if url.scheme or url.netloc:raise SystemExit('Unexpected URL scheme: '+link)
            target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(url.path))) if url.path else name
            if target not in contents:raise SystemExit(f'Reader missing local target: {name} -> {link}')
            if url.fragment and (target not in parsed or unquote(url.fragment) not in parsed[target].ids):raise SystemExit(f'Reader missing anchor: {name} -> {link}')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip())
    contents['README.txt']=(f'''Mine-Wiki 离线读者包

打开 index.html，从主题、知识节点或零缩放问题路径开始。
本包是离线文件交付，不是上线部署。来源提交：{commit}
打包时工作区：{'含未提交更改' if dirty else '与提交一致'}。

若浏览器禁止直接打开本地文件，可在解压后的 mine-wiki-reader 文件夹内运行：
python3 -m http.server 8765 --bind 127.0.0.1
然后打开 http://127.0.0.1:8765/index.html
该命令只在本机提供文件，不会部署网站。停止时按 Ctrl+C。

正文、练习答案与静态图解无需 JavaScript；实验和本地记录需要它。
记录只保存在当前浏览器来源，更换浏览器、域名或端口不会自动迁移。
外部引用只在主动点击时联网，网页没有远程运行依赖。

早期视频保留在 lessons/zero-scale/history.html，属于可选历史辅助，
不随当前知识节点维护。当前学习内容以交互网页为准。
本包不包含模型、凭据、Git 元数据、构建依赖或临时文件。
''').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(contents.items()):
            info=zipfile.ZipInfo('mine-wiki-reader/'+name,date_time=(2026,10,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,data)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert all(not i.flag_bits&1 and '..' not in Path(i.filename).parts and not i.is_dir() for i in z.infolist())
    print(json.dumps({'file':str(output),'files':len(contents),'html_pages':len(parsed),'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'source_commit':commit,'working_tree_dirty':dirty,'crc':'passed','local_links_and_fragments':'passed'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
