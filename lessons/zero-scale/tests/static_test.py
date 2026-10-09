#!/usr/bin/env python3
"""Compatibility command for the shared content/build/reference checks."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parents[3]/'tests/content_test.py'),run_name='__main__')
