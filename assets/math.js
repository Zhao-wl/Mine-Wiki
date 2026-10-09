/* Row-major storage; all geometric inputs are COLUMN vectors. No epsilon substitution. */
(function (root) {
  'use strict';
  const mul = (a,b) => a.map((row,i)=>b[0].map((_,j)=>row.reduce((s,v,k)=>s+v*b[k][j],0)));
  const apply = (m,p,w=1) => [m[0][0]*p[0]+m[0][1]*p[1]+m[0][2]*w,m[1][0]*p[0]+m[1][1]*p[1]+m[1][2]*w];
  const det = a=>a[0][0]*a[1][1]-a[0][1]*a[1][0];
  const identity = ()=>[[1,0,0],[0,1,0],[0,0,1]];
  const parent = (s,tx=3,ty=2)=>[[0,-1,tx],[s,0,ty],[0,0,1]];
  const translation = (x,y)=>[[1,0,x],[0,1,y],[0,0,1]];
  const maxResidual = (a,b)=>Math.max(...a.flatMap((r,i)=>r.map((v,j)=>Math.abs(v-b[i][j]))));
  function solveVector(a,b) {
    if (![...a.flat(),...b].every(Number.isFinite)) throw new Error('Expected finite numbers');
    const d=det(a);
    if(d!==0) {
      const p=[(a[1][1]*b[0]-a[0][1]*b[1])/d,(a[0][0]*b[1]-a[1][0]*b[0])/d];
      return {status:'unique',particular:p,kernel:[],rank:2};
    }
    const cols=[[a[0][0],a[1][0]],[a[0][1],a[1][1]]];
    if(a.flat().every(v=>v===0)) return b.every(v=>v===0)?{status:'family',particular:[0,0],kernel:[[1,0],[0,1]],rank:0}:{status:'none',rank:0};
    const j=Math.max(...cols[0].map(Math.abs))>=Math.max(...cols[1].map(Math.abs))?0:1;
    const c=cols[j];
    // Exact collinearity for this lesson's controlled numbers. This is not a production rank estimator.
    if(c[0]*b[1]-c[1]*b[0]!==0) return {status:'none',rank:1};
    const i=Math.abs(c[0])>=Math.abs(c[1])?0:1;
    const p=[0,0]; p[j]=b[i]/c[i];
    const row=a[0].some(v=>v!==0)?a[0]:a[1];
    const scale=Math.max(...row.map(Math.abs));
    return {status:'family',particular:p,kernel:[[-row[1]/scale,row[0]/scale]],rank:1};
  }
  function solveAffine(p,w,parameters=[0,0,0]) {
    const a=p.slice(0,2).map(r=>r.slice(0,2));
    const rhs=[[w[0][0],w[1][0]],[w[0][1],w[1][1]],[w[0][2]-p[0][2],w[1][2]-p[1][2]]];
    const solutions=rhs.map(b=>solveVector(a,b));
    if(solutions.some(s=>s.status==='none')) return {status:'none',solutions,position:solutions[2]};
    const cols=solutions.map((s,j)=>s.particular.map((v,i)=>v+(s.kernel[0]?.[i]||0)*parameters[j]));
    const local=[[cols[0][0],cols[1][0],cols[2][0]],[cols[0][1],cols[1][1],cols[2][1]],[0,0,1]];
    const rebuilt=mul(p,local);
    return {status:solutions[0].status,local,rebuilt,residual:maxResidual(rebuilt,w),solutions,position:solutions[2]};
  }
  function reparent(oldP,newP,oldL,mode='world',parameters=[0,0,0]) {
    const oldWorld=mul(oldP,oldL), worldSolution=solveAffine(newP,oldWorld,parameters);
    if(mode==='local') {
      const rebuilt=mul(newP,oldL);
      return {oldWorld,worldSolution,status:'kept-local',local:oldL,rebuilt,residual:maxResidual(rebuilt,oldWorld)};
    }
    return {oldWorld,worldSolution,...worldSolution};
  }
  function metrics(s,uniform=false) {
    return {determinant:uniform?s*s:s,condition:s===0?Infinity:uniform?1:Math.max(Math.abs(s),1)/Math.min(Math.abs(s),1),inverseNorm:s===0?Infinity:uniform?1/Math.abs(s):Math.max(1,1/Math.abs(s))};
  }
  function nearZero(s,delta,uniform=false) {
    const m=metrics(s,uniform);
    if(s===0) return {...m,status:delta===0?'family':'none'};
    const ideal=2+s, observed=ideal+delta;
    const recovered=(observed-2)/s;
    const f=Math.fround, fobserved=f(f(f(2)+f(s))+f(delta));
    const frecovered=f(f(fobserved-f(2))/f(s));
    return {...m,status:'unique',ideal,observed,recovered,frecovered,expectedError:delta/s,actualError:recovered-1,fobserved};
  }
  const api={mul,apply,det,identity,parent,translation,maxResidual,solveVector,solveAffine,reparent,metrics,nearZero};
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
  root.TransformMath=api;
})(typeof globalThis!=='undefined'?globalThis:this);
