#!/usr/bin/env python3
"""Independent NumPy oracle for the JS solver and condition-number teaching claims."""
import json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];rng=np.random.default_rng(20261008)
cases=[]
for i in range(120):
    while True:
        a=rng.integers(-6,7,size=(2,2))
        if round(np.linalg.det(a))!=0:break
    p=np.eye(3);p[:2,:2]=a;p[:2,2]=rng.integers(-6,7,size=2)
    w=np.eye(3);w[:2,:]=rng.integers(-6,7,size=(2,3))
    cases.append({'p':p.tolist(),'w':w.tolist()})
for i in range(60):
    c=rng.integers(-4,5,size=2)
    if not np.any(c):c[0]=1
    row=rng.integers(-4,5,size=2)
    if not np.any(row):row[0]=1
    p=np.eye(3);p[:2,:2]=np.outer(c,row);p[:2,2]=rng.integers(-3,4,size=2)
    l=np.eye(3);l[:2,:]=rng.integers(-4,5,size=(2,3));w=p@l
    cases.append({'p':p.tolist(),'w':w.tolist()})
    # Force the target first column outside the one-dimensional image.
    wbad=w.copy();wbad[:2,0]=[-c[1],c[0]]
    cases.append({'p':p.tolist(),'w':wbad.tolist()})
js="const fs=require('fs'),M=require('./math.js');console.log(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8')).map(c=>M.solveAffine(c.p,c.w))));"
r=subprocess.run(['node','-e',js],input=json.dumps(cases),text=True,capture_output=True,cwd=ROOT,check=True)
outputs=json.loads(r.stdout);worst=0;unique=family=none=0
for case,out in zip(cases,outputs):
    p,w=np.array(case['p']),np.array(case['w']);a=p[:2,:2];rhs=w[:2,:].copy();rhs[:,2]-=p[:2,2]
    if np.linalg.matrix_rank(a)==2:
        expected=np.linalg.solve(a,rhs);assert out['status']=='unique';np.testing.assert_allclose(np.array(out['local'])[:2,:],expected,atol=1e-11);unique+=1
    else:
        fit=np.linalg.lstsq(a,rhs,rcond=None)[0];res=np.max(np.abs(a@fit-rhs))
        if res>1e-9:assert out['status']=='none';none+=1;continue
        assert out['status']=='family';family+=1
    residual=float(np.max(np.abs(p@np.array(out['local'])-w)));worst=max(worst,residual);assert residual<1e-11
for s in [1e-8,1e-6,.01,1,2,-2]:
    np.testing.assert_allclose(np.linalg.cond(s*np.eye(2)),1)
    np.testing.assert_allclose(np.linalg.cond([[0,-1],[s,0]]),max(1,abs(s))/min(1,abs(s)))
a=np.array([[0,-1],[0,0.]])
np.testing.assert_allclose(np.linalg.pinv(a)@[-1,2],[0,1]);np.testing.assert_allclose(a@np.linalg.pinv(a)@[-1,2],[-1,0])
report={'cases':len(cases),'unique':unique,'family':family,'none':none,'worst_reconstruction_residual':worst,'numpy_version':np.__version__,'status':'passed'}
(ROOT/'verification/numpy-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
