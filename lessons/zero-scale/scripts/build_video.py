#!/usr/bin/env python3
"""Offline Chinese narrated diagram video. Requires known local eSpeak NG, Pillow, ffmpeg.
No downloads or credentials. Use --tts-root for the locally extracted Debian tool tree.
"""
import argparse,json,os,re,subprocess,wave,math,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
W,H=1280,720
INK='#eaf1df'; MUTED='#aac3b1'; TEAL='#86d5b2'; CORAL='#f6b18a'; BLUE='#a6bff2'
FONT='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
def ft(n):return ImageFont.truetype(FONT,n)
def display_math(s):
    # Noto CJK has Chinese but not every Unicode superscript/subscript glyph.
    # ASCII exponents avoid tofu boxes while preserving the displayed meaning.
    for a,b in [('10⁻⁶','10^-6'),('10⁻⁴','10^-4'),('10⁶','10^6'),('⁻¹','^(-1)'),('κ₂','κ2'),('₀','_0'),('₁','_1'),('₂','_2')]:s=s.replace(a,b)
    return s
def wrap(s,n):return [s[i:i+n] for i in range(0,len(s),n)]
def cues(text):
    parts=re.findall(r'[^，。！？；：]+[，。！？；：]?',text)
    out=[];pending=''
    for p in parts:
        if len(pending)+len(p)>36 and pending:out.append(pending);pending=''
        while len(p)>36:out.append(p[:36]);p=p[36:]
        pending+=p
        if pending and pending[-1] in '。！？；' and len(pending)>=14:out.append(pending);pending=''
    if pending:out.append(pending)
    return out
def stamp(t,sep=','):
    ms=round(t*1000);sec,ms=divmod(ms,1000);m,s=divmod(sec,60);h,m=divmod(m,60)
    return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'
def render(scene,index,count,subtitle,progress,out):
    im=Image.new('RGB',(W,H),'#123a34');d=ImageDraw.Draw(im)
    d.text((48,28),'MINE / WIKI     001 · 线性代数与坐标变换',font=ft(17),fill=MUTED)
    d.text((48,74),scene['title'],font=ft(36),fill=INK)
    d.text((1130,32),f'{index+1:02}/{count:02}',font=ft(20),fill=MUTED)
    d.rounded_rectangle((42,151,688,528),radius=18,fill='#1e4b40')
    y=178
    for k,s in enumerate(scene['board']):
        s=display_math(s)
        d.text((65,y),f'0{k+1}',font=ft(16),fill=TEAL);y+=30
        font=ft(26 if len(s)<33 else 22)
        for row in wrap(s,39):d.text((65,y),row,font=font,fill=INK);y+=40
        y+=18
    # Original coordinate diagrams, no private screenshots and no external assets.
    ox,oy,unit=934,443,39
    def xy(p):return (ox+p[0]*unit,oy-p[1]*unit)
    def ln(a,b,col,width=3):d.line([xy(a),xy(b)],fill=col,width=width)
    def arrow(a,b,col):
        ln(a,b,col,4);x,y=xy(b);u,v=xy(a);ang=math.atan2(y-v,x-u)
        for off in [-.55,.55]:d.line([(x,y),(x-12*math.cos(ang+off),y-12*math.sin(ang+off))],fill=col,width=4)
    def dot(p,label,col=CORAL):
        x,y=xy(p);d.ellipse((x-6,y-6,x+6,y+6),fill=col);d.text((x+9,y-26),label,font=ft(19),fill=col)
    for k in range(-4,7):
        if 733<=ox+k*unit<=1225:d.line((ox+k*unit,170,ox+k*unit,520),fill='#2b584b')
        if 170<=oy-k*unit<=520:d.line((730,oy-k*unit,1230,oy-k*unit),fill='#2b584b')
    d.line((730,oy,1230,oy),fill=MUTED);d.line((ox,520,ox,166),fill=MUTED)
    d.text((1207,oy+3),'x',font=ft(18),fill=MUTED);d.text((ox+8,165),'y',font=ft(18),fill=MUTED)
    kind=scene['visual']
    if kind=='points':
        dot([1,1],'P');dot([2,1],'Q');arrow([1,1],[2,1],TEAL)
        dot([4,3],'');dot([5,3],'Q+t');arrow([4,3],[5,3],TEAL)
        d.text((1080,300),'P+t',font=ft(19),fill=CORAL)
        d.text((746,187),'平移 t=(3,2)，位移不变',font=ft(21),fill=INK)
    elif kind=='basis':
        arrow([0,0],[0,2],TEAL);arrow([0,0],[-1,0],BLUE);arrow([0,0],[-1,2],CORAL);dot([-1,2],'(−1,2)')
    elif kind=='precision':
        arrow([0,0],[0,.12],TEAL);arrow([0,0],[-2,0],BLUE);d.text((743,188),'一个方向的刻度变短',font=ft(22),fill=TEAL)
        d.text((760,244),'δv / s = δx',font=ft(28),fill=CORAL);d.text((760,302),'10^-4 / 10^-6 = 100',font=ft(23),fill=INK)
        d.text((760,485),'箭头长度示意，未按比例',font=ft(17),fill=MUTED)
    elif kind=='api':
        arrow([0,0],[2,1],TEAL);arrow([0,0],[1,2],BLUE);ln([2,1],[3,3],BLUE);ln([1,2],[3,3],TEAL);dot([3,3],'剪切',CORAL)
        d.text((749,185),'仿射矩阵 → TRS → API',font=ft(21),fill=INK)
    else:
        scale=0 if kind in ['collapse','oldzero','full'] else 2
        t=json.loads((ROOT/'course.json').read_text())['facts']['translation']
        verts=[(t[0]-y,t[1]+scale*x) for x,y in [(0,0),(1,0),(1,1),(0,1)]]
        if kind=='oldzero':verts=[(2-y,2) for x,y in [(0,0),(1,0),(1,1),(0,1)]]
        if kind=='full':verts=[(2-y,2+2*x) for x,y in [(0,0),(1,0),(1,1),(0,1)]]
        d.polygon([xy(p) for p in verts],fill='#2d6756',outline=TEAL,width=4)
        for a,b in zip(verts,verts[1:]+verts[:1]):ln(a,b,TEAL,4)
        dot([2,2+scale],f'(2,{2+scale})')
        if scale==0:
            ln([-4,2],[6,2],BLUE,2);d.text((757,oy-2*unit-31),'v=2',font=ft(21),fill=BLUE)
            if kind=='collapse':dot([2,4],'不可达',MUTED)
            if kind=='full':dot([2,4],'旧 X 点到不了',CORAL)
        if kind=='order':dot([1,3],'SR (1,3)',BLUE)
        if kind=='hierarchy':dot([1,1],'父空间 (1,1)',BLUE)
    d.rounded_rectangle((42,551,1238,670),radius=14,fill='#0c2925')
    lines=wrap(subtitle,36)
    for n,line in enumerate(lines):
        bbox=d.textbbox((0,0),line,font=ft(29));x=(W-(bbox[2]-bbox[0]))/2
        d.text((x,583+n*39 if len(lines)==1 else 561+n*41),line,font=ft(29),fill='#fffdf1')
    d.text((48,684),'中文离线合成配音 · 可暂停手算 · 列向量 / x右y上 / 右侧先执行',font=ft(15),fill=MUTED)
    d.rectangle((0,713,W,719),fill='#28554a');d.rectangle((0,713,int(W*progress),719),fill=TEAL)
    im.save(out)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tts-root',type=Path,default=Path('/workspace/scratch/mine-wiki-tools/root'));p.add_argument('--work',type=Path,default=Path('/workspace/scratch/zero-scale-video'));args=p.parse_args()
    config=json.loads((ROOT/'video.json').read_text());scenes=config['scenes'];work=args.work;work.mkdir(parents=True,exist_ok=True);media=ROOT/'media';media.mkdir(exist_ok=True)
    exe=args.tts_root/'usr/bin/espeak-ng';env=os.environ.copy();env['LD_LIBRARY_PATH']=str(args.tts_root/'usr/lib/x86_64-linux-gnu');env['ESPEAK_DATA_PATH']=str(args.tts_root/'usr/lib/x86_64-linux-gnu/espeak-ng-data')
    if not exe.exists():raise SystemExit('Local eSpeak NG not found; provide --tts-root. No automatic installation.')
    items=[];audio=[];time=0;sr=None;transcript=['# 中文讲解视频逐字稿','配音：eSpeak NG cmn，离线合成；画面为原创图解卡片。视频覆盖完整知识链，详细练习见文字课。','全片采用列向量、x右y上、右侧先执行。字幕时间码来自实际合成音频。'];scene_times=[]
    for si,scene in enumerate(scenes):
        start=time;transcript += [f'## {si+1:02d} {scene["title"]}',f'开始：{stamp(time,".")}','画面：'+' / '.join(scene['board'])]
        for ci,cue in enumerate(cues(scene['speech'])):
            name=f'{si:02d}-{ci:02d}';wav=work/(name+'.wav')
            subprocess.run([str(exe),'-v',config['voice'],'-s',str(config['speed']),'-w',str(wav),cue],env=env,check=True,stdout=subprocess.DEVNULL)
            with wave.open(str(wav),'rb') as w:
                assert w.getnchannels()==1 and w.getsampwidth()==2
                if sr is None:sr=w.getframerate()
                assert sr==w.getframerate();frames=w.readframes(w.getnframes())
            # Align cue durations to video frames and add a short readable pause.
            total_samples=math.ceil((len(frames)/2/sr+.22)*12)/12*sr
            silence=max(0,round(total_samples)-len(frames)//2)
            block=frames+b'\0\0'*silence;dur=len(block)/2/sr;audio.append(block)
            image=work/(name+'.png');render(scene,si,len(scenes),cue,(si+(ci+1)/len(cues(scene['speech'])))/len(scenes),image)
            items.append({'start':time,'end':time+dur,'text':cue,'image':str(image),'scene':si,'audio_samples':len(block)//2});transcript+=[f'{stamp(time,".")} → {stamp(time+dur,".")}  {cue}'];time+=dur
        scene_times.append({'title':scene['title'],'start':start,'end':time});print(f'Scene {si+1}/{len(scenes)}: {time-start:.1f}s',flush=True)
    joined=work/'narration.wav'
    with wave.open(str(joined),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(b''.join(audio))
    srt='\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(items,1))+'\n'
    vtt='WEBVTT\n\n'+'\n\n'.join(f'{stamp(c["start"],".")} --> {stamp(c["end"],".")}\n{c["text"]}' for c in items)+'\n'
    (media/'lesson-zh.srt').write_text(srt);(media/'lesson-zh.vtt').write_text(vtt);(media/'transcript.md').write_text('\n\n'.join(transcript)+'\n')
    (media/'timing.json').write_text(json.dumps({'duration':time,'sample_rate':sr,'scenes':scene_times,'cues':[{k:v for k,v in c.items() if k!='image'} for c in items]},ensure_ascii=False,indent=2))
    concat=work/'frames.txt';concat.write_text(''.join(f"file '{i['image']}'\noption framerate 12\nduration {i['end']-i['start']:.9f}\n" for i in items)+f"file '{items[-1]['image']}'\noption framerate 12\n")
    Image.open(items[0]['image']).save(media/'poster.jpg',quality=88)
    cmd=['ffmpeg','-hide_banner','-loglevel','warning','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(joined),'-i',str(media/'lesson-zh.srt'),'-map','0:v','-map','1:a','-map','2:s','-vf','fps=12,tpad=stop_mode=clone:stop_duration=1','-c:v','libx264','-preset','fast','-tune','stillimage','-crf','28','-pix_fmt','yuv420p','-c:a','aac','-b:a','64k','-c:s','mov_text','-metadata:s:a:0','language=zho','-metadata:s:s:0','language=zho','-t',str(time),'-movflags','+faststart',str(media/'lesson-zh.mp4')]
    subprocess.run(cmd,check=True)
    print(f'Video complete: {time:.2f}s, {(media/"lesson-zh.mp4").stat().st_size/1024**2:.2f} MiB',flush=True)
if __name__=='__main__':main()
