#!/usr/bin/env python3
"""Compatibility entry point; canonical authoring is under content/."""
import runpy,sys
from pathlib import Path
scripts=Path(__file__).resolve().parents[3]/'scripts'
sys.path.insert(0,str(scripts))
runpy.run_path(str(scripts/'build_site.py'),run_name='__main__')
