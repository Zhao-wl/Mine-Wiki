'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const M=require('../math.js'),course=require('../course.json');
function close(a,b,tol=1e-10){assert.ok(Math.abs(a-b)<=tol,`${a} ≠ ${b}`);}
function matrixClose(a,b,tol=1e-10){assert.ok(M.maxResidual(a,b)<=tol,`${JSON.stringify(a)} ≠ ${JSON.stringify(b)}`);}
test('shared canonical example: F₂(1,1)=(2,4), point vs vector',()=>{
 const f=course.facts;assert.deepEqual(M.apply(M.parent(f.s),f.point),f.world);
 assert.deepEqual(M.apply(M.parent(2),[1,1],0),[-1,2]);
});
test('matrix columns, RS vs SR and rightmost first',()=>{
 const R=[[0,-1,0],[1,0,0],[0,0,1]],S=[[2,0,0],[0,1,0],[0,0,1]];
 assert.deepEqual(M.apply(M.mul(R,S),[1,1]),[-1,2]);
 assert.deepEqual(M.apply(M.mul(S,R),[1,1]),[-2,1]);
 assert.deepEqual(M.apply(M.parent(2),[1,0],0),[0,2]);
});
test('hierarchy includes ancestors and transforms the child translation',()=>{
 const W=M.mul(M.parent(2),M.translation(1,1));assert.deepEqual(W,[[0,-1,2],[2,0,4],[0,0,1]]);
 assert.deepEqual(M.apply(M.mul(M.translation(10,0),W),[0,0]),[12,4]);
 const ancestor=[[0,0,0],[0,1,0],[0,0,1]],parentWorld=M.mul(ancestor,M.parent(2));
 assert.equal(M.det(parentWorld),0);assert.equal(M.solveAffine(parentWorld,M.identity()).status,'none');
});
test('exact zero inverse problem: unreachable vs whole affine family',()=>{
 const p=M.parent(0);
 assert.equal(M.solveVector([[0,-1],[0,0]],[-1,2]).status,'none');
 const s=M.solveVector([[0,-1],[0,0]],[-1,0]);assert.equal(s.status,'family');
 for(const x of [-1e6,-5,0,8,1e6])assert.deepEqual(M.apply(p,[x,1]),[2,2]);
});
test('old singular / new invertible: complete matrix is uniquely recoverable',()=>{
 const r=M.reparent(M.parent(0),M.parent(2),M.translation(1,1));
 assert.equal(r.status,'unique');matrixClose(r.local,[[0,0,0],[0,1,1],[0,0,1]]);close(r.residual,0);
});
test('new singular / old invertible: position unreachable',()=>{
 const r=M.reparent(M.parent(2),M.parent(0),M.translation(1,1));assert.equal(r.status,'none');assert.equal(r.position.status,'none');assert.equal(r.local,undefined);
});
test('position reachable but complete matrix impossible',()=>{
 const r=M.reparent(M.parent(2),M.parent(0),M.translation(0,1));assert.equal(r.position.status,'family');assert.equal(r.status,'none');assert.equal(r.solutions[0].status,'none');
});
test('both singular with matching image: independent column and position freedoms',()=>{
 for(const parameters of [[0,0,0],[1,2,3],[-2,.5,-4]]){
  const r=M.reparent(M.parent(0),M.parent(0),M.translation(1,1),'world',parameters);
  assert.equal(r.status,'family');close(r.residual,0);matrixClose(r.rebuilt,r.oldWorld);
  r.local[1].forEach((v,i)=>close(v,[0,1,1][i]));
 }
});
test('both singular but displaced images: no solution',()=>{
 const r=M.reparent(M.parent(0),M.parent(0,3,3),M.translation(1,1));assert.equal(r.status,'none');assert.equal(r.position.status,'none');
});
test('keep-local remains a finite forward product with either/both zero parents',()=>{
 for(const a of [0,2])for(const b of [0,2]){
  const L=M.translation(1,1),r=M.reparent(M.parent(a),M.parent(b),L,'local');
  assert.deepEqual(r.local,L);assert.ok(r.rebuilt.flat().every(Number.isFinite));matrixClose(r.rebuilt,M.mul(M.parent(b),L));
 }
});
test('equal rank is insufficient when column spaces differ',()=>{
 const P=[[0,0,0],[0,1,0],[0,0,1]],W=[[1,0,0],[0,0,0],[0,0,1]];
 const r=M.solveAffine(P,W);assert.equal(r.status,'none');assert.equal(r.position.status,'family');
});
test('F(x,y)=(10,y): position family vs no solution, full I impossible',()=>{
 const P=[[0,0,10],[0,1,0],[0,0,1]];
 assert.equal(M.solveAffine(P,M.translation(10,2)).position.status,'family');
 assert.equal(M.solveAffine(P,M.translation(11,2)).position.status,'none');
 assert.equal(M.solveAffine(P,M.translation(10,2)).status,'none');
});
test('rank zero: only translation point reachable',()=>{
 const P=[[0,0,3],[0,0,2],[0,0,1]],W=[[0,0,3],[0,0,2],[0,0,1]];
 const r=M.solveAffine(P,W);assert.equal(r.status,'family');close(r.residual,0);
 assert.equal(M.solveVector([[0,0],[0,0]],[0,0]).kernel.length,2);
 assert.equal(M.solveVector([[0,0],[0,0]],[0,1]).status,'none');
});
test('unique affine solution does not imply single no-shear TRS representation',()=>{
 const c=Math.SQRT1_2,R=[[c,-c,0],[c,c,0],[0,0,1]],old=[[0,0,0],[0,1,0],[0,0,1]];
 const r=M.reparent(old,M.identity(),R);assert.equal(r.status,'unique');close(r.residual,0);
 // R diag(s) has perpendicular nonzero columns; these have nonzero dot product.
 close(r.local[0][0]*r.local[0][1]+r.local[1][0]*r.local[1][1],.5);
 const invScale=[[.5,0,0],[0,1,0],[0,0,1]],C=M.mul(invScale,R);
 close(C[0][0]*C[0][1]+C[1][0]*C[1][1],3/8);
});
test('near zero is never silently clamped to zero',()=>{
 const r=M.solveVector([[0,-1],[1e-12,0]],[-1,1e-12]);assert.equal(r.status,'unique');assert.deepEqual(r.particular,[1,1]);
 assert.equal(M.nearZero(0,0).status,'family');assert.equal(M.nearZero(0,1e-4).status,'none');
});
test('condition number versus absolute amplification, including negative s',()=>{
 for(const s of [1e-8,1e-6,.01,1,2,-2]){
  const u=M.metrics(s,true),a=M.metrics(s,false);close(u.condition,1);close(u.determinant,s*s);close(u.inverseNorm,1/Math.abs(s));
  close(a.condition,Math.max(Math.abs(s),1)/Math.min(Math.abs(s),1));
 }
 close(M.nearZero(1e-6,1e-4).expectedError,100);close(M.nearZero(1e-6,1e-4,true).expectedError,100);
});
test('float32 can erase increment before inverse, independent of injected noise',()=>{
 const r=M.nearZero(1e-8,0);assert.equal(r.fobserved,2);assert.equal(r.frecovered,0);close(r.recovered,1,1e-7);
});
test('pseudoinverse example selects a solution but cannot recover lost x',()=>{
 const pinv=[[0,0],[-1,0]],local=[0,1];assert.deepEqual(M.apply(M.parent(0),local),[2,2]);
 assert.deepEqual([pinv[0][0]*(-1)+pinv[0][1]*2,pinv[1][0]*(-1)+pinv[1][1]*2],[0,1]);
 assert.deepEqual(M.apply(M.parent(0),[8,1]),M.apply(M.parent(0),local));
});
test('all controlled old/new branches reconstruct exactly when a solution exists',()=>{
 let checked=0;
 for(const a of [-2,0,2])for(const b of [-2,0,2])for(const x of [-2,0,1])for(const y of [-1,1])for(const ty of [2,3]){
  const r=M.reparent(M.parent(a),M.parent(b,3,ty),M.translation(x,y));
  if(r.local){matrixClose(M.mul(M.parent(b,3,ty),r.local),r.oldWorld);assert.ok(r.local.flat().every(Number.isFinite));checked++;}
 }
 // 72 invertible-new cases plus 6 matching singular/singular cases, out of 108.
 assert.equal(checked,78);
});
test('course has all nine prerequisite stages with nonempty examples and answers',()=>{
 assert.deepEqual(course.chapters.map(c=>c.id),['points','basis','columns','order','affine','hierarchy','inverse','precision','reparent']);
 for(const c of course.chapters){assert.ok(c.intuition.length>=3);assert.ok(c.steps.length>=3);assert.ok(c.exercise.length>15);assert.ok(c.answer.length>40);}
});
