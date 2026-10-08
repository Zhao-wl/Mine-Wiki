#!/usr/bin/env python3
"""Download only pinned official Debian eSpeak packages and extract locally, never install."""
import argparse,hashlib,json,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--destination',type=Path,required=True);args=p.parse_args()
    args.destination.mkdir(parents=True,exist_ok=True);debdir=args.destination/'debs';debdir.mkdir(exist_ok=True);out=args.destination/'root';out.mkdir(exist_ok=True)
    for item in json.loads((ROOT/'tts-provenance.json').read_text()):
        url=item['url'];assert url.startswith('https://deb.debian.org/debian/pool/main/')
        dest=debdir/url.rsplit('/',1)[1]
        data=dest.read_bytes() if dest.exists() else urllib.request.urlopen(url,timeout=30).read()
        if hashlib.sha256(data).hexdigest()!=item['sha256']:raise SystemExit('Package hash mismatch: '+dest.name)
        dest.write_bytes(data);subprocess.run(['dpkg-deb','-x',str(dest),str(out)],check=True);print('Verified and extracted',dest.name)
    print('Local tool root:',out)
if __name__=='__main__':main()
