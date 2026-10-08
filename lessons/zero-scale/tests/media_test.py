#!/usr/bin/env python3
"""Validate actual encoded A/V, cue timing and representative rendered subtitle frames."""
import argparse,json,subprocess,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification';VIDEO=ROOT/'media/lesson-zh.mp4'
p=argparse.ArgumentParser();p.add_argument('--render-work',type=Path,default=Path('/workspace/scratch/zero-scale-video'));args=p.parse_args()
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(VIDEO)]))
streams={s['codec_type']:s for s in probe['streams']};v,a=streams['video'],streams['audio'];assert v['codec_name']=='h264' and a['codec_name']=='aac';assert (v['width'],v['height'])==(1280,720);assert 'subtitle' in streams
timing=json.loads((ROOT/'media/timing.json').read_text());cues=timing['cues'];assert abs(float(v['duration'])-float(a['duration']))<=1/12+.01
assert abs(float(a['duration'])-timing['duration'])<.02
for i,c in enumerate(cues):
    assert c['end']>c['start'] and len(c['text'])<=36
    if i:assert abs(c['start']-cues[i-1]['end'])<1e-6
    assert c['text'] in (ROOT/'media/lesson-zh.srt').read_text()
    assert c['text'] in (ROOT/'media/lesson-zh.vtt').read_text()
subprocess.run(['ffmpeg','-v','error','-i',str(VIDEO),'-map','0:v','-map','0:a','-f','null','-'],check=True)
pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(VIDEO),'-map','0:a','-f','f32le','-ac','1','-ar','22050','-'])
samples=np.frombuffer(pcm,dtype='<f4');rms=[]
for c in cues:
    s=samples[round(c['start']*22050):round(c['end']*22050)];rms.append(float(np.sqrt(np.mean(s*s))))
assert min(rms)>.005,'Silent narration cue';clipped=float(np.mean(np.abs(samples)>=.999));assert clipped<.001
frames=[];errors=[]
for scene_idx in [0,3,7,8,10,11,12]:
    selected=[c for c in cues if c['scene']==scene_idx];c=selected[len(selected)//2];t=(c['start']+c['end'])/2
    out=OUT/f'video-scene-{scene_idx+1:02}.jpg'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(VIDEO),'-frames:v','1','-q:v','2',str(out)],check=True)
    actual=Image.open(out).convert('RGB');ci=selected.index(c);expected_path=args.render_work/f'{scene_idx:02d}-{ci:02d}.png'
    if expected_path.exists():
        expected=Image.open(expected_path).convert('RGB');err=float(np.mean(np.abs(np.asarray(actual.crop((42,551,1238,670)),dtype=float)-np.asarray(expected.crop((42,551,1238,670)),dtype=float))));assert err<3,('Subtitle/frame mismatch',scene_idx,err);errors.append(err)
    frames.append(actual.resize((384,216)))
sheet=Image.new('RGB',(384*2,216*4),'#f6f4eb')
for i,im in enumerate(frames):sheet.paste(im,((i%2)*384,(i//2)*216))
sheet.save(OUT/'video-contact-sheet.jpg',quality=88)
result={'status':'passed','duration_seconds':float(probe['format']['duration']),'video_duration':float(v['duration']),'audio_duration':float(a['duration']),'size_bytes':VIDEO.stat().st_size,'sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),'video':'H.264 1280x720 12fps','audio':'AAC mono 22050Hz 64kbps','cue_count':len(cues),'scene_count':len(timing['scenes']),'min_cue_rms':min(rms),'max_cue_rms':max(rms),'clipped_sample_ratio':clipped,'sampled_frame_count':len(frames),'max_subtitle_image_mean_abs_error':max(errors) if errors else None,'subjective_listening':'Not performed by a human; synthetic Mandarin voice is mechanical. Numeric checks do not certify pronunciation quality.'}
(OUT/'media-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
