/* Offline enhancement only. Course and fallback examples already exist in HTML. */
(()=>{
  'use strict';
  const M=window.TransformMath,$=id=>document.getElementById(id),num=id=>Number($(id).value);
  const fmt=n=>!Number.isFinite(n)?(n===Infinity?'∞':'—'):Object.is(n,-0)?'0':Math.abs(n)<1e-5&&n!==0?n.toExponential(4):Number(n.toPrecision(8)).toString();
  const vec=p=>'('+p.map(fmt).join(', ')+')';
  const matrix=a=>a.map(r=>'[ '+r.map(fmt).join('   ')+' ]').join('\n');
  const colors={teal:'#17685b',orange:'#b4472d',blue:'#355ebe',grid:'#d6dfd2'};
  function frame(id,points=[],fixed=false){
    const svg=$(id),max=Math.max(4,...points.flat().map(Math.abs));
    const scale=fixed?48:Math.min(42,135/max),ox=210,oy=210;
    const xy=p=>[ox+p[0]*scale,oy-p[1]*scale];
    let b=''; const step=max>8?Math.ceil(max/5):1;
    for(let v=-Math.ceil(ox/scale);v<=(440-ox)/scale;v+=step){const x=xy([v,0])[0];b+=`<line x1="${x}" y1="20" x2="${x}" y2="337" stroke="${colors.grid}"/>`;if(v!==0)b+=`<text x="${x+3}" y="${oy+17}">${v}</text>`;}
    for(let v=-Math.ceil((360-oy)/scale);v<=(oy-20)/scale;v+=step){const y=xy([0,v])[1];b+=`<line x1="20" y1="${y}" x2="421" y2="${y}" stroke="${colors.grid}"/>`;if(v!==0)b+=`<text x="${ox+5}" y="${y-4}">${v}</text>`;}
    b+=`<path d="M20 ${oy} H425 M${ox} 338 V17" fill="none" stroke="#879f94"/><text x="414" y="${oy+20}">x →</text><text x="${ox+9}" y="25">y ↑</text><text x="${ox+5}" y="${oy+17}">0</text>`;
    const segment=(a,c,color,width=3,dash='')=>{let [x,y]=xy(a),[u,v]=xy(c);return `<line x1="${x}" y1="${y}" x2="${u}" y2="${v}" stroke="${color}" stroke-width="${width}" ${dash?'stroke-dasharray="'+dash+'"':''}/>`;};
    const arrow=(a,c,color)=>{let [x,y]=xy(a),[u,v]=xy(c);if(x===u&&y===v)return `<circle cx="${u}" cy="${v}" r="4" fill="${color}"/>`;let ang=Math.atan2(v-y,u-x),z=8;return segment(a,c,color)+`<path d="M${u-z*Math.cos(ang-.5)} ${v-z*Math.sin(ang-.5)} L${u} ${v} L${u-z*Math.cos(ang+.5)} ${v-z*Math.sin(ang+.5)}" fill="none" stroke="${color}" stroke-width="3"/>`;};
    const point=(p,label,color,hollow=false)=>{let[x,y]=xy(p);let tx=Math.max(10,Math.min(346,x+9)),ty=Math.max(18,Math.min(342,y-10));return `<circle cx="${x}" cy="${y}" r="${hollow?8:5}" fill="${hollow?'#fffef9':color}" stroke="${color}" stroke-width="2"/>`+(label?`<text x="${tx}" y="${ty}" style="fill:${color}">${label}</text>`:'');};
    return {svg,xy,scale,ox,oy,b,segment,arrow,point};
  }
  function input(ids,fn){ids.forEach(id=>$(id).addEventListener('input',fn));}
  function set(values){for(const[k,v]of Object.entries(values))$(k).value=v;}
  window.LessonUI={};
  function initBasis(){
  // Basis handles persist across redraws so keyboard focus and pointer capture are retained.
  const basisSvg=$('basis-plot');basisSvg.innerHTML='<g id="basis-drawing"></g><circle id="handle-1" class="handle" tabindex="0" role="button" r="11" fill="#17685b"/><circle id="handle-2" class="handle" tabindex="0" role="button" r="11" fill="#355ebe"/>';
  let basisFrame;
  function basis(){
    const a=[num('b1x'),num('b1y')],b=[num('b2x'),num('b2y')],s=[a[0]+b[0],a[1]+b[1]],d=a[0]*b[1]-a[1]*b[0];
    const f=frame('basis-plot',[a,b,s]);basisFrame=f;
    $('basis-drawing').innerHTML=f.b+f.segment(a,s,colors.blue,2,'4 4')+f.segment(b,s,colors.teal,2,'4 4')+f.arrow([0,0],a,colors.teal)+f.arrow([0,0],b,colors.blue)+f.point(s,'(1,1) 的组合',colors.orange);
    [a,b].forEach((v,i)=>{let[x,y]=f.xy(v),h=$('handle-'+(i+1));h.setAttribute('cx',x);h.setAttribute('cy',y);h.setAttribute('aria-label',`b${i+1} 端点 ${vec(v)}，方向键调整`);});
    $('basis-output').textContent=`b₁=${vec(a)}；b₂=${vec(b)}\n组合=${vec(s)}\ndet=${fmt(d)}\n${d===0?'两列不构成平面的基：缺少独立方向。':'两列独立：每个平面向量都有唯一配方。'}`;
  }
  input(['b1x','b1y','b2x','b2y'],basis);
  $('basis-reset').onclick=()=>{set({b1x:0,b1y:2,b2x:-1,b2y:0});basis();};
  $('basis-zero').onclick=()=>{set({b1x:0,b1y:0});basis();};
  $('basis-collinear').onclick=()=>{set({b1x:1,b1y:1,b2x:2,b2y:2});basis();};
  let dragging=null;
  [1,2].forEach(i=>{
    const h=$('handle-'+i);
    h.addEventListener('pointerdown',e=>{dragging=i;basisSvg.setPointerCapture(e.pointerId);e.preventDefault();});
    h.addEventListener('keydown',e=>{const v={ArrowLeft:['x',-.25],ArrowRight:['x',.25],ArrowUp:['y',.25],ArrowDown:['y',-.25]}[e.key];if(v){e.preventDefault();let id='b'+i+v[0];$(id).value=Math.max(-3,Math.min(3,num(id)+v[1]));basis();}});
  });
  basisSvg.addEventListener('pointermove',e=>{if(!dragging)return;const pt=basisSvg.createSVGPoint();pt.x=e.clientX;pt.y=e.clientY;const p=pt.matrixTransform(basisSvg.getScreenCTM().inverse());const clamp=n=>Math.max(-3,Math.min(3,Math.round(n*4)/4));$('b'+dragging+'x').value=clamp((p.x-basisFrame.ox)/basisFrame.scale);$('b'+dragging+'y').value=clamp((basisFrame.oy-p.y)/basisFrame.scale);basis();});
  basisSvg.addEventListener('pointerup',()=>dragging=null);basisSvg.addEventListener('pointercancel',()=>dragging=null);
    window.LessonUI.basis=basis;basis();
  }
  function initOrder(){
  function order(){
    const s=num('order-s'),step=num('order-step'),rs=[[1,1],[s,1],[-1,s],[2,2+s]],sr=[[1,1],[-1,1],[-s,1],[3-s,3]];
    const f=frame('order-plot',[...rs,...sr]);let b=f.b;
    for(let i=1;i<=step;i++){b+=f.segment(rs[i-1],rs[i],colors.teal,3)+f.segment(sr[i-1],sr[i],colors.orange,2,'6 4');}
    b+=f.arrow([0,0],rs[step],colors.teal)+f.arrow([0,0],sr[step],colors.orange)+f.point(rs[step],'RS',colors.teal)+f.point(sr[step],'SR',colors.orange,true);f.svg.innerHTML=b;
    $('order-s-label').textContent=fmt(s);
    $('order-output').textContent=`当前第 ${step} 步\nRS：${rs.slice(0,step+1).map(vec).join(' → ')}\nSR：${sr.slice(0,step+1).map(vec).join(' → ')}\n${s===1?'s=1，两个顺序恰好相同。':'两种顺序通常不同；追踪中间结果。'}`;
  }
  input(['order-s','order-step'],order);$('order-next').onclick=()=>{$('order-step').value=(num('order-step')+1)%4;order();};$('order-zero').onclick=()=>{$('order-s').value=0;order();};$('order-reset').onclick=()=>{set({'order-s':2,'order-step':3});order();};
    window.LessonUI.order=order;order();
  }
  function initPrecision(){
  function precision(){
    const s=num('precision-s'),delta=num('precision-noise'),uniform=$('precision-kind').value==='uniform',r=M.nearZero(s,delta,uniform);
    let msg=`s=${fmt(s)}；det=${fmt(r.determinant)}\nκ₂=${fmt(r.condition)}；逆范数=${fmt(r.inverseNorm)}\n`;
    if(s===0){msg+=uniform?(delta===0?'精确零：仅平移点可达；局部 x、y 均任意。':'精确零：目标偏离平移点，无解。'):(delta===0?'精确零：v=2 可达，x 任意。':'精确零：v≠2，无解。');msg+='\n未执行除零，也未替换 epsilon。';}
    else msg+=`世界理想分量：${fmt(r.ideal)}\n加噪后：${fmt(r.observed)}\n反求 x（双精度）：${fmt(r.recovered)}\n理论 δ/s：${fmt(r.expectedError)}\n实际 x−1：${fmt(r.actualError)}\nfloat32 世界分量：${fmt(r.fobserved)}\nfloat32 反求 x：${fmt(r.frecovered)}\n${uniform?'κ₂=1 仍会放大绝对误差。':'方向缩放悬殊会放大最坏相对误差。'}`;
    $('precision-output').textContent=msg;$('precision-meter').style.width=(s===0?0:Math.min(100,Math.log10(1+Math.abs(r.expectedError))*20))+'%';
  }
  input(['precision-s','precision-kind','precision-noise'],precision);$('precision-reset').onclick=()=>{set({'precision-s':.000001,'precision-kind':'axis','precision-noise':.0001});precision();};
    window.LessonUI.precision=precision;precision();
  }
  function initReparent(){
  const names={unique:'唯一解',family:'无穷多解',none:'无解'};
  function reparent(){
    const oldP=M.parent(num('old-s')),newP=M.parent(num('new-s'),3,num('new-ty')),oldL=M.translation(num('local-x'),num('local-y')),mode=$('keep-mode').value,params=['free-a','free-b','free-t'].map(num);
    const r=M.reparent(oldP,newP,oldL,mode,params),sol=r.worldSolution;
    $('family-controls').disabled=mode!=='world'||sol.status!=='family';
    const oldPts=[[0,0],[1,0],[0,1]].map(p=>M.apply(r.oldWorld,p)),newPts=r.rebuilt?[[0,0],[1,0],[0,1]].map(p=>M.apply(r.rebuilt,p)):[];
    const f=frame('reparent-plot',[...oldPts,...newPts]);let b=f.b;
    if(num('new-s')===0)b+=f.segment([-4,num('new-ty')],[5,num('new-ty')],colors.blue,2,'5 4');
    [[oldPts,colors.orange,true],[newPts,colors.teal,false]].forEach(([pts,col,hollow])=>{
      if(!pts.length)return;
      b+=f.segment(pts[0],pts[1],col,hollow?6:3,hollow?'5 4':'')+f.segment(pts[0],pts[2],col,hollow?6:3,hollow?'5 4':'');
      const groups=new Map();pts.forEach((p,i)=>{let k=p.join(',');if(!groups.has(k))groups.set(k,{p,n:[]});groups.get(k).n.push(['O','X','Y'][i]);});
      groups.forEach(({p,n},k)=>{const sameNew=hollow&&newPts.some(q=>q.join(',')===k);b+=f.point(p,sameNew?'':n.join('=')+(hollow?'旧':'新'),col,hollow);});
    });f.svg.innerHTML=b;
    let msg=`旧局部位置=${vec([num('local-x'),num('local-y')])}\n旧世界原点=${vec(oldPts[0])}\n只保持原点：${names[sol.position.status]}\n保持完整矩阵：${names[sol.status]}\n`;
    if(mode==='local')msg+=`当前 keep-local：仅正向乘法\n新世界原点=${vec(newPts[0])}\n世界差异 max|ΔW|=${fmt(r.residual)}`;
    else if(r.local)msg+=`当前 keep-world：${names[r.status]}\n回代 max|P_new L_new−W_old|=${fmt(r.residual)}`;
    else msg+='当前 keep-world 无法精确满足；未伪造局部矩阵。';
    $('reparent-summary').textContent=msg;
    const solText=sol.solutions.map((v,i)=>`${['线性第一列','线性第二列','平移列'][i]}：${names[v.status]}${v.particular?'；特解 '+vec(v.particular):''}${v.kernel?.length?'；核方向 '+v.kernel.map(vec).join('、'):''}`).join('\n');
    $('reparent-matrices').textContent=`P_old\n${matrix(oldP)}\n\nP_new（完整父世界矩阵）\n${matrix(newP)}\n\nW_old\n${matrix(r.oldWorld)}\n\n${solText}\n\n${r.local?'当前 L_new\n'+matrix(r.local)+'\n\n回代世界\n'+matrix(r.rebuilt):'不满足精确方程；没有可展示的完整解。'}\n\n多解表示：每列 = 特解 + 对应自由参数 × 核方向。残差使用最大元素绝对差，未把阈值用于修改缩放。`;
  }
  const defaultReparent={'old-s':0,'new-s':2,'local-x':1,'local-y':1,'new-ty':2,'keep-mode':'world','free-a':0,'free-b':0,'free-t':0};
  input(Object.keys(defaultReparent),reparent);$('reparent-reset').onclick=()=>{set(defaultReparent);reparent();};
  document.querySelectorAll('[data-preset]').forEach(b=>b.onclick=()=>{set(defaultReparent);let p=b.dataset.preset;set(p==='old-zero'?{}:p==='unreachable'?{'old-s':2,'new-s':0}:p==='position-only'?{'old-s':2,'new-s':0,'local-x':0}:{'old-s':0,'new-s':0});reparent();});
    window.LessonUI.reparent=reparent;reparent();
  }
  if($('lab-basis'))initBasis();
  if($('lab-order'))initOrder();
  if($('lab-precision'))initPrecision();
  if($('lab-reparent'))initReparent();

  // One browser-local record per stable node; question notes stay with their page.
  const scope=document.body.dataset.recordScope;
  if(scope && $('notes-input')) {
    const key='mine-wiki.learning.v1';
    const config=JSON.parse($('learning-config')?.textContent||'{"legacy":[]}');
    const fresh=()=>({version:1,mastery:{},notes:{},migrations:{}});
    const object=v=>v && typeof v==='object' && !Array.isArray(v);
    const valid=v=>object(v)&&v.version===1&&object(v.mastery)&&object(v.notes)&&object(v.migrations)
      &&Object.values(v.mastery).every(x=>typeof x==='boolean')&&Object.values(v.notes).every(x=>typeof x==='string');
    let saved=fresh(),writable=true,notice='',dirty=false;
    const visible=[...document.querySelectorAll('[data-mastery]')];
    function tell(text){$('notes-status').textContent=text;}
    try {
      const raw=localStorage.getItem(key);
      if(raw!==null){const parsed=JSON.parse(raw);if(!valid(parsed))throw Error('Unrecognized records');saved=parsed;}
      let changed=false;
      for(const migration of config.legacy||[]) {
        if(saved.migrations[migration.key])continue;
        const rawOld=localStorage.getItem(migration.key);
        if(rawOld===null)continue;
        let previous;
        try{previous=JSON.parse(rawOld);if(!object(previous)||!object(previous.mastery)||typeof previous.notes!=='string')throw Error('Invalid legacy records');}
        catch(e){notice='旧记录格式异常，原始数据保留，未自动导入。';continue;}
        for(const [oldId,newId] of Object.entries(migration.mastery_map)) {
          if(typeof previous.mastery[oldId]==='boolean'&&!Object.hasOwn(saved.mastery,newId))saved.mastery[newId]=previous.mastery[oldId];
        }
        const noteScope='path:'+migration.path;
        if(!Object.hasOwn(saved.notes,noteScope))saved.notes[noteScope]=previous.notes;
        saved.migrations[migration.key]=true;changed=true;
      }
      if(changed){localStorage.setItem(key,JSON.stringify(saved));notice='已迁移旧课程记录；原始记录仍保留作为备份。';}
    }catch(e){writable=false;notice='本地存储不可用或现有记录格式不兼容；原始记录未覆盖，当前修改仅留在本页，可导出。';}
    function progress(){
      const count=visible.filter(c=>c.checked).length;
      if($('progress')){$('progress').max=visible.length;$('progress').value=count;}
      if($('progress-label'))$('progress-label').textContent=count+' / '+visible.length;
    }
    function sync(){visible.forEach(c=>c.checked=saved.mastery[c.dataset.mastery]===true);progress();}
    function persist(message){
      if(!writable){tell('未写入本地存储；当前修改仅在本页，请导出留底。');return;}
      try{localStorage.setItem(key,JSON.stringify(saved));tell(message);}
      catch(e){writable=false;tell('浏览器未允许本地存储；当前修改仅在本页，请导出留底。');}
    }
    function save(){saved.notes[scope]=$('notes-input').value;dirty=false;persist('已保存在当前浏览器，不上传。');}
    // Read the latest valid record before each edit, keeping changes from other pages.
    function refresh(){
      if(!writable)return;
      try{const raw=localStorage.getItem(key);if(raw!==null){const next=JSON.parse(raw);if(!valid(next))throw Error('Invalid records');saved=next;}}
      catch(e){writable=false;tell('现有记录无法读取，未覆盖原始内容；可导出本页记录。');}
    }
    visible.forEach(c=>c.onchange=()=>{refresh();saved.mastery[c.dataset.mastery]=c.checked;progress();save();});
    $('notes-input').value=saved.notes[scope]||'';
    $('notes-input').addEventListener('input',()=>{dirty=true;});
    $('save-notes').onclick=()=>{refresh();save();};
    $('clear-notes').onclick=()=>{
      refresh();visible.forEach(c=>saved.mastery[c.dataset.mastery]=false);saved.notes[scope]='';
      $('notes-input').value='';dirty=false;sync();persist('已清除此页疑问及所含节点的共享自评；其他疑问和迁移前备份保留。');
    };
    $('export-notes').onclick=()=>{
      refresh();saved.notes[scope]=$('notes-input').value;
      const u=URL.createObjectURL(new Blob([JSON.stringify(saved,null,2)],{type:'application/json'}));
      const a=document.createElement('a');a.href=u;a.download='mine-wiki-learning-records.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);
    };
    window.addEventListener('storage',e=>{
      if(e.key!==key||!e.newValue)return;
      try{const next=JSON.parse(e.newValue);if(valid(next)){saved=next;sync();if(!dirty)$('notes-input').value=saved.notes[scope]||'';}}catch(err){}
    });
    sync();tell(notice||'本地记录已就绪。节点自评共享，疑问按页面保存。');
  }
  if('IntersectionObserver'in window){
    const observer=new IntersectionObserver(entries=>{
      entries.filter(e=>e.isIntersecting).forEach(e=>document.querySelectorAll('.rail a').forEach(a=>a.classList.toggle('active',a.hash==='#'+e.target.id)));
    },{rootMargin:'-5% 0px -70% 0px'});
    document.querySelectorAll('.chapter,.appendix').forEach(s=>observer.observe(s));
  }
})();
