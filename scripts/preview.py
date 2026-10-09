#!/usr/bin/env python3
"""Serve the static wiki on loopback only; no publishing."""
import argparse,functools,http.server,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'lessons/zero-scale/scripts'))
from preview import RangeHandler
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);args=p.parse_args()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),functools.partial(RangeHandler,directory=str(ROOT)))
    print(f'Local preview: http://127.0.0.1:{args.port}/index.html',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:server.server_close()
