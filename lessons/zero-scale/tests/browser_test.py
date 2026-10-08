#!/usr/bin/env python3
"""Compatibility command for node/path interaction and record-migration checks."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[3]/'tests/browser_test.py'),run_name='__main__')
