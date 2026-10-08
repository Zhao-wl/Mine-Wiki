#!/usr/bin/env python3
"""Loopback-only static preview with byte ranges, so MP4 seeking works before full download."""
import argparse,http.server,functools,re
from pathlib import Path
class RangeHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path=Path(self.translate_path(self.path));self.remaining=None
        if not path.is_file():return super().send_head()
        size=path.stat().st_size;start,end=0,size-1;header=self.headers.get('Range');partial=False
        if header:
            m=re.fullmatch(r'bytes=(\d*)-(\d*)',header)
            if not m or not any(m.groups()):self.send_error(416);return None
            a,b=m.groups()
            if a:start=int(a);end=min(int(b),size-1) if b else size-1
            else:start=max(0,size-int(b))
            if start>end or start>=size:self.send_error(416);return None
            partial=True
        f=path.open('rb');f.seek(start);self.remaining=end-start+1
        self.send_response(206 if partial else 200);self.send_header('Content-Type',self.guess_type(str(path)));self.send_header('Accept-Ranges','bytes');self.send_header('Content-Length',str(self.remaining));self.send_header('Last-Modified',self.date_time_string(path.stat().st_mtime))
        if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers();return f
    def copyfile(self,source,outputfile):
        if self.remaining is None:return super().copyfile(source,outputfile)
        try:
            while self.remaining>0:
                block=source.read(min(64*1024,self.remaining))
                if not block:break
                outputfile.write(block);self.remaining-=len(block)
        except (BrokenPipeError,ConnectionResetError):pass
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);a=p.parse_args()
    root=Path(__file__).resolve().parents[3]
    server=http.server.ThreadingHTTPServer(('127.0.0.1',a.port),functools.partial(RangeHandler,directory=str(root)))
    print(f'Local only: http://127.0.0.1:{a.port}/lessons/zero-scale/',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
