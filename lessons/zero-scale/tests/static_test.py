#!/usr/bin/env python3
"""No-dependency artifact and local-link checks, also suitable for CI."""
import json,re,subprocess
from pathlib import Path
from urllib.parse import unquote,urlsplit
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id'in d:self.ids.append(d['id'])
        for k in ['href','src','poster']:
            if k in d:self.links.append((tag,d[k]))
for path in [REPO/'index.html',ROOT/'index.html']:
    p=Links();p.feed(path.read_text());assert len(p.ids)==len(set(p.ids)),f'duplicate ids: {path}'
    for tag,link in p.links:
        u=urlsplit(link)
        if u.scheme in ['https','http']:
            assert tag=='a',f'External runtime dependency: {link}';continue
        if not u.path:
            if u.fragment:assert unquote(u.fragment) in p.ids,link
        else:assert (path.parent/unquote(u.path)).exists(),f'Missing file: {link}'
for file in ['course.md','media/lesson-zh.mp4','media/lesson-zh.srt','media/lesson-zh.vtt','media/transcript.md','verification/report.md']:
    assert (ROOT/file).stat().st_size>100,file
assert (ROOT/'media/lesson-zh.mp4').stat().st_size<10*1024**2,'Video exceeds 10 MiB course budget'
assert b'ftyp' in (ROOT/'media/lesson-zh.mp4').read_bytes()[:32]
assert not re.search(r'\b(fetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket)\b',(ROOT/'app.js').read_text())
# Building twice must not drift the generated HTML, Markdown or diagrams.
targets=[ROOT/'index.html',ROOT/'course.md',*sorted((ROOT/'assets').glob('*.svg'))]
before={p:p.read_bytes() for p in targets};subprocess.run(['python3',str(ROOT/'scripts/build_site.py')],check=True)
assert all(p.read_bytes()==content for p,content in before.items()),'Generated artifacts stale; rebuild them'
print('Static links, offline dependencies, media budget and generated artifacts passed')
