"""Small, standard-library content catalog and relation validator."""
import json,re
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
STATUSES={'stub','draft','ready'}
ID=re.compile(r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$')
class ContentError(ValueError):pass

def require(ok,message):
    if not ok:raise ContentError(message)

def unique(items,kind):
    result={}
    for item in items:
        key=item.get('id')
        require(isinstance(key,str) and bool(ID.fullmatch(key)),f'{kind}: invalid ID {key!r}')
        require(key not in result,f'{kind}: duplicate ID {key}')
        result[key]=item
    return result

def load_catalog(root=ROOT):
    def read(p):return json.loads((root/p).read_text())
    def records(folder):
        items=[]
        for p in sorted((root/folder).glob('*.json')):
            item=json.loads(p.read_text());require(p.stem==item.get('id'),f'{p}: filename must match stable ID');items.append(item)
        return items
    return {'nodes':unique(records('content/nodes'),'node'),
            'paths':unique(records('content/paths'),'path'),
            'examples':unique(records('content/examples'),'example'),
            'topics':unique(read('content/topics.json')['items'],'topic'),
            'sources':unique(read('content/sources.json')['items'],'source'),
            'checked_at':read('content/sources.json')['checked_at']}

def anchors(node):
    result={'overview','connections','notes','references'}
    for key,anchor in [('intuition','intuition'),('formula','formula'),('steps','example'),('exercise','exercise'),('boundaries','boundaries'),('cases','cases')]:
        if node.get(key):result.add(anchor)
    if node.get('lab'):result.add('experiment')
    return result

def validate(catalog,root=ROOT):
    nodes,paths,examples,topics,sources=(catalog[k] for k in ['nodes','paths','examples','topics','sources'])
    def strings(v,label,nonempty=False):
        require(isinstance(v,list) and all(isinstance(x,str) and x.strip() for x in v),label+' must contain nonempty strings')
        if nonempty:require(bool(v),label+' cannot be empty')
    def file(name):
        require(isinstance(name,str) and not Path(name).is_absolute() and '..' not in Path(name).parts,f'Unsafe asset path {name!r}')
        require((root/name).is_file(),f'Missing asset {name}')
    def ref(r,where):
        require(isinstance(r,dict) and r.get('node') in nodes,f'{where}: unknown node reference {r}')
        require(set(r)<= {'node','reason','anchor'},f'{where}: unsupported reference fields')
        if 'anchor'in r:require(r['anchor'] in anchors(nodes[r['node']]),f'{where}: missing anchor {r["node"]}#{r["anchor"]}')
    labs=re.findall(r'<!-- lab:(\w+) -->',(root/'assets/labs.html').read_text())
    require(len(labs)==len(set(labs)),'Duplicate lab template')
    for sid,s in sources.items():
        u=urlsplit(s.get('url',''));require(u.scheme in {'https','http'} and bool(u.netloc),f'{sid}: invalid citation URL')
        require(bool(s.get('title')),f'{sid}: missing source title')
    for key,example in examples.items():
        require(all(example.get(k) for k in ['title','conventions','formula','facts']),f'{key}: incomplete example')
    for key,n in nodes.items():
        require(n.get('status') in STATUSES,f'{key}: invalid status')
        require(all(isinstance(n.get(f),str) and n[f].strip() for f in ['title','summary']),f'{key}: title and summary required even for stub')
        for relation in ['requires','related','context']:
            require(isinstance(n.get(relation,[]),list),f'{key}: {relation} must be a list')
            if relation!='context':require(relation in n,f'{key}: {relation} must be a list')
            seen=set()
            for r in n.get(relation,[]):
                ref(r,key);target=r['node'];require(target!=key,f'{key}: self reference')
                require(target not in seen,f'{key}: duplicate {relation} {target}');seen.add(target)
                if relation in {'requires','context'}:require(isinstance(r.get('reason'),str) and bool(r['reason'].strip()),f'{key}: {"prerequisite" if relation=="requires" else "context"} needs a reason')
        if 'question' in n:require(isinstance(n['question'],str) and bool(n['question'].strip()),f'{key}: question must be nonempty')
        if 'boundaries' in n:strings(n['boundaries'],f'{key}: boundaries',True)
        if 'cases' in n:
            require(isinstance(n['cases'],list) and bool(n['cases']),f'{key}: cases must be a nonempty list')
            for case in n['cases']:
                require(isinstance(case,dict) and isinstance(case.get('title'),str) and bool(case['title'].strip()),f'{key}: case needs a title')
                strings(case.get('paragraphs'),f'{key}: case paragraphs',True)
                strings(case.get('sources'),f'{key}: case sources',True)
                for sid in case['sources']:require(sid in sources and sid in n.get('sources',[]),f'{key}: case citation must be registered in node sources')
        if n['status']=='ready':
            for field in ['intuition','steps']:strings(n.get(field),key+': '+field,True)
            require(all(isinstance(n.get(f),str) and n[f].strip() for f in ['exercise','answer']),f'{key}: ready content incomplete')
            require(isinstance(n.get('minutes'),int) and n['minutes']>0,f'{key}: invalid reading time')
        if 'formula'in n:require(isinstance(n['formula'],str) and bool(n['formula'].strip()),f'{key}: formula must be nonempty when provided')
        if 'example'in n:require(n['example'] in examples,f'{key}: unknown example')
        if 'lab'in n:require(n['lab'] in labs,f'{key}: unknown lab')
        if 'figure'in n:file(n['figure'])
        require(isinstance(n.get('sources',[]),list),f'{key}: sources must be a list')
        for sid in n.get('sources',[]):require(sid in sources,f'{key}: unknown citation {sid}')
    done=set();visiting=[]
    def visit(key):
        require(key not in visiting,'Prerequisite cycle: '+' → '.join(visiting+[key]))
        if key in done:return
        visiting.append(key)
        for r in nodes[key]['requires']:visit(r['node'])
        visiting.pop();done.add(key)
    for key in nodes:visit(key)
    reserved={'course-start','api','video','notes','references','overview'}
    for key,p in paths.items():
        require(p.get('status') in STATUSES,f'{key}: invalid path status')
        require(p.get('title') and p.get('summary'),f'{key}: incomplete path metadata')
        if 'example' in p:require(p['example'] in examples,f'{key}: unknown path example')
        require(isinstance(p.get('steps'),list) and bool(p['steps']),f'{key}: path has no steps')
        seen=set();old_anchors=set();used_labs=set()
        for step in p['steps']:
            node=step.get('node');require(node in nodes,f'{key}: unknown step {node}')
            require(node not in seen,f'{key}: repeated step {node}')
            if p['status']=='ready':
                require(nodes[node]['status']=='ready',f'{key}: required node {node} is not ready')
                for r in nodes[node]['requires']:require(r['node'] in seen,f'{key}: missing or out-of-order prerequisite {r["node"]} before {node}')
            seen.add(node)
            legacy=step.get('legacy_anchor')
            if legacy:
                require(bool(ID.fullmatch(legacy)) and legacy not in old_anchors|reserved,f'{key}: conflicting legacy anchor {legacy}')
                require(legacy not in nodes or legacy==node,f'{key}: legacy anchor conflicts with a stable node ID')
                old_anchors.add(legacy)
            lab=nodes[node].get('lab')
            if lab:
                require(lab not in used_labs,f'{key}: repeated lab DOM; use one shared learning unit for {lab}')
                used_labs.add(lab)
        for sid in p.get('sources',[]):require(sid in sources,f'{key}: unknown citation {sid}')
        for entry in p.get('api',[]):
            if 'source'in entry:require(entry['source'] in sources,f'{key}: unknown API citation')
        for name in p.get('historical_media',{}).values():file(name)
        legacy=p.get('legacy_storage')
        if legacy:
            require(bool(legacy.get('key')) and isinstance(legacy.get('mastery_map'),dict),f'{key}: invalid storage migration map')
            require(set(legacy['mastery_map'])==old_anchors,f'{key}: storage migration must cover legacy anchors')
            require(set(legacy['mastery_map'].values())==seen,f'{key}: storage migration targets must match path nodes')
    for key,t in topics.items():
        require(t.get('title') and t.get('summary'),f'{key}: incomplete topic')
        for field,targets in [('nodes',nodes),('paths',paths)]:
            values=t.get(field,[]);strings(values,f'{key}: {field}')
            require(len(values)==len(set(values)),f'{key}: duplicate {field} member')
            require(all(v in targets for v in values),f'{key}: unknown {field} member')
        if 'learning_map' in t:
            m=t['learning_map'];require(isinstance(m,dict),f'{key}: invalid learning map')
            require(isinstance(m.get('orientation'),str) and bool(m['orientation'].strip()),f'{key}: map orientation required')
            strings(m.get('history_questions'),f'{key}: history questions',True)
            for field in ['layers','stages']:
                groups=m.get(field);require(isinstance(groups,list) and bool(groups),f'{key}: map {field} required')
                unique(groups,f'{key}: map {field}');seen=set()
                for group in groups:
                    require(all(isinstance(group.get(f),str) and group[f].strip() for f in ['title','summary']),f'{key}: incomplete map group')
                    strings(group.get('nodes'),f'{key}: map nodes',True)
                    for target in group['nodes']:
                        require(target in t['nodes'],f'{key}: unknown map node {target}')
                        require(target not in seen,f'{key}: duplicate map {field} node {target}');seen.add(target)
                    if field=='stages':require(isinstance(group.get('practice'),str) and bool(group['practice'].strip()),f'{key}: map practice required')
                require(seen==set(t['nodes']),f'{key}: map {field} must cover topic nodes')
    return {'nodes':len(nodes),'paths':len(paths),'topics':len(topics),'prerequisite_edges':sum(len(n['requires']) for n in nodes.values())}

def reverse_index(c):
    result={key:{'required_by':[],'related':set(),'paths':[],'topics':[]} for key in c['nodes']}
    for key,n in c['nodes'].items():
        for r in n['requires']:result[r['node']]['required_by'].append({'node':key,'reason':r['reason']})
        for r in n['related']:
            result[key]['related'].add(r['node']);result[r['node']]['related'].add(key)
    for key,p in c['paths'].items():
        for step in p['steps']:result[step['node']]['paths'].append(key)
    for key,t in c['topics'].items():
        for node in t['nodes']:result[node]['topics'].append(key)
    for values in result.values():values['related']=sorted(values['related'])
    return result
