/* Original visual exercises. No requests, analytics or automatic answer upload. */
(()=>{
  'use strict';
  const $=id=>document.getElementById(id);
  if(!$('lab-aesthetic'))return;
  const key='mine-wiki.aesthetics.observation.v1';
  const fields=[...document.querySelectorAll('[data-aesthetic-field]')];
  const checks=[...document.querySelectorAll('[data-aesthetic-check]')];
  const titles={none:'无标题',solitude:'独处',left:'被落下'};
  let revealed=false,writable=true;
  function stage(show){
    revealed=show;$('aesthetic-variant').hidden=!show;$('aesthetic-analysis').hidden=!show;
    $('aesthetic-comparison').classList.toggle('is-comparing',show);
    $('aesthetic-reveal').setAttribute('aria-expanded',String(show));
    $('aesthetic-reveal').textContent=show?'B 已展开；可返回初看':'写好预测，展开 B';
    $('aesthetic-stage-status').textContent=show?'A 与 B 可直接对照。先核对几何，再检查预测与两种解释；这不是对所有人的心理实验。':'当前只看 A；写下观察与预测后展开 B。返回初看保留文字。';
  }
  function title(){
    const value=$('aesthetic-title').value;
    $('aesthetic-caption').textContent='虚构教学标题：'+titles[value];
    $('aesthetic-title-status').textContent='当前标题：'+titles[value]+'。四个圆的位置、大小与颜色完全没变；标题提供故事可能，不证明身份或关系。';
  }
  function collect(){
    return {version:1,fields:Object.fromEntries(fields.map(el=>[el.dataset.aestheticField,el.value])),checks:Object.fromEntries(checks.map(el=>[el.dataset.aestheticCheck,el.checked])),revealed,title:$('aesthetic-title').value};
  }
  function valid(record){
    const object=v=>v!==null && typeof v==='object' && !Array.isArray(v);
    return object(record)&&record.version===1&&object(record.fields)&&object(record.checks)
      &&Object.keys(record.fields).length===fields.length&&fields.every(el=>typeof record.fields[el.dataset.aestheticField]==='string')
      &&Object.keys(record.checks).length===checks.length&&checks.every(el=>typeof record.checks[el.dataset.aestheticCheck]==='boolean')
      &&typeof record.revealed==='boolean'&&Object.hasOwn(titles,record.title);
  }
  function tell(message){$('aesthetic-storage-status').textContent=message;}
  function reset(){
    fields.forEach(el=>el.value='');checks.forEach(el=>el.checked=false);
    $('aesthetic-title').value='none';title();stage(false);
    $('aesthetic-review-status').textContent='反馈检查遗漏与自查项目，不自动判断解释正确，也不给美丑分数。';
  }
  document.querySelectorAll('[data-aesthetic-action]').forEach(el=>el.disabled=false);
  $('aesthetic-title').disabled=false;
  stage(false);
  try{
    const raw=localStorage.getItem(key);
    if(raw!==null){
      const record=JSON.parse(raw);if(!valid(record))throw Error('Incompatible record');
      fields.forEach(el=>el.value=record.fields[el.dataset.aestheticField]);
      checks.forEach(el=>el.checked=record.checks[el.dataset.aestheticCheck]);
      $('aesthetic-title').value=record.title;title();stage(record.revealed);
      tell('已读取本浏览器保存的练习。继续编辑不会自动保存；请再次点击保存。');
    }else tell('尚无已保存练习。输入暂留本页，点击保存才写入本机；不上传。');
  }catch(e){writable=false;tell('存储不可用或记录格式不兼容；原始内容未覆盖。可以临时编辑与导出。');}
  $('aesthetic-reveal').onclick=()=>{
    for(const id of ['aesthetic-observe','aesthetic-predict']){
      if(!$(id).value.trim()){
        $('aesthetic-stage-status').textContent='先写一条初看观察和一条比较前预测；不评价你选择的审美。';$(id).focus();return;
      }
    }
    stage(true);
  };
  $('aesthetic-back').onclick=()=>stage(false);
  $('aesthetic-title').onchange=title;
  $('aesthetic-review').onclick=()=>{
    const empty=fields.filter(el=>!el.value.trim()).map(el=>el.closest('label').firstChild.textContent.trim());
    const unchecked=checks.filter(el=>!el.checked);
    $('aesthetic-review-status').textContent=(empty.length?'还可补写：'+empty.join('；')+'。':'各记录栏已填写。')
      +(unchecked.length?'请复查 '+unchecked.length+' 项未确认的理由质量。':'四项自查已确认。')
      +' 这只检查完整性；请按证据、替代解释、语境与可检验性自行修订，不意味着内容正确或某种偏好更好。';
  };
  $('aesthetic-save').onclick=()=>{
    if(!writable){tell('未写入本地存储；原记录保留。请导出当前练习。');return;}
    try{
      // Recheck current bytes before writing, including records changed in another tab.
      const raw=localStorage.getItem(key);
      if(raw!==null&&!valid(JSON.parse(raw)))throw Error('Incompatible record');
      localStorage.setItem(key,JSON.stringify(collect()));tell('已保存练习在当前浏览器；不上传。节点页与第一单元共用，其他学习记录未修改。');
    }catch(e){writable=false;tell('未写入本地存储；可能是配额、访问限制或格式不兼容。原记录未覆盖，可导出。');}
  };
  $('aesthetic-export').onclick=()=>{
    const url=URL.createObjectURL(new Blob([JSON.stringify(collect(),null,2)],{type:'application/json'}));
    const a=document.createElement('a');a.href=url;a.download='mine-wiki-aesthetics-observation.json';a.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
    tell('已导出当前页面练习；此操作不写入存储，也不上传。');
  };
  $('aesthetic-reset').onclick=()=>{reset();tell('已重置本页练习与两个实验；已保存的副本保留，刷新会重新读取。若要删除副本，请用删除按钮。');};
  $('aesthetic-delete').onclick=()=>{
    try{localStorage.removeItem(key);writable=true;tell('已删除本浏览器保存的练习；当前页面文字保留，可继续编辑。其他课程记录未改动。');}
    catch(e){tell('浏览器未允许删除；当前页面可继续编辑与导出。');}
  };
  // Never overwrite a different tab silently. The reader chooses whether to reload or save.
  window.addEventListener('storage',e=>{if(e.key===key)tell('另一页面修改了已保存练习。本页文字保留；刷新读取副本，点击保存会用本页覆盖该练习。');});
  window.LessonUI.aesthetic=()=>({revealed,title:$('aesthetic-title').value});
})();
