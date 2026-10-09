#!/usr/bin/env python3
"""Graph, state, single-source generation and offline-link regression checks."""
import copy,json,sys,unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from knowledge import load_catalog,validate,reverse_index,ContentError,unique
from build_site import render_site

class Links(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:self.ids.append(a['id'])
        for k in ['href','src','poster']:
            if k in a:self.links.append((tag,a[k]))

class ContentTests(unittest.TestCase):
    def setUp(self):self.c=load_catalog()
    def nonformula_fixture(self):
        node={'id':'fixture-observation','title':'观察与推断（仅测试夹具）','status':'ready',
              'summary':'能区分直接记录与解释，并检查解释是否充分。','minutes':3,
              'requires':[],'related':[],'sources':[],
              'intuition':['观察记录看到的情况；推断为情况提出解释。'],
              'steps':['看到房间的灯亮着，这是观察。','认为房间里有人，是一种仍需验证的推断。'],
              'exercise':'仅凭灯亮着，能断定房间里有人吗？',
              'answer':'不能；无人时灯也可能亮着，需要更多证据。'}
        self.c['nodes'][node['id']]=node
        return node
    def reject(self,text):
        with self.assertRaisesRegex(ContentError,text):validate(self.c)
    def test_current_catalog(self):
        counts=validate(self.c)
        self.assertGreaterEqual(counts['nodes'],9)
        self.assertIn('zero-scale',self.c['paths'])
        self.assertTrue({'linear-algebra','graphics-transforms'}<=set(self.c['topics']))
    def test_duplicate_stable_id(self):
        with self.assertRaisesRegex(ContentError,'duplicate ID'):unique([{'id':'same'},{'id':'same'}],'node')
    def test_unknown_reference(self):
        self.c['nodes']['point-vector']['related']=[{'node':'missing'}];self.reject('unknown node')
    def test_bad_anchor(self):
        self.c['nodes']['point-vector']['related']=[{'node':'basis-coordinates','anchor':'absent'}];self.reject('missing anchor')
    def test_valid_section_reference(self):
        self.c['nodes']['point-vector']['related']=[{'node':'basis-coordinates','anchor':'example'}];validate(self.c)
        self.assertIn('../basis-coordinates/index.html#example',render_site(self.c)['knowledge/point-vector/index.html'])
    def test_prerequisite_page_anchor_keeps_canonical_link(self):
        self.c['nodes']['basis-coordinates']['requires'][0]['anchor']='connections';validate(self.c)
        page=render_site(self.c)['lessons/zero-scale/index.html']
        self.assertIn('../../knowledge/point-vector/index.html#connections',page)
        self.assertNotIn('#points--connections',page)
    def test_prerequisite_reason_required(self):
        self.c['nodes']['basis-coordinates']['requires'][0]['reason']='';self.reject('needs a reason')
    def test_prerequisite_cycle(self):
        self.c['nodes']['point-vector']['requires']=[{'node':'matrix-linear-map','reason':'cycle fixture'}];self.reject('cycle')
    def test_related_cycles_are_not_prerequisites(self):
        self.c['nodes']['affine-homogeneous']['related'].append({'node':'point-vector'});validate(self.c)
    def test_unknown_citation(self):
        self.c['nodes']['point-vector']['sources']=['absent'];self.reject('unknown citation')
    def test_ready_requires_complete_teaching_unit(self):
        self.c['nodes']['basis-coordinates']['answer']='';self.reject('ready content incomplete')
    def test_ready_nonformula_unit_builds_without_numeric_assets(self):
        node=self.nonformula_fixture();validate(self.c)
        page=render_site(self.c)['knowledge/'+node['id']+'/index.html']
        self.assertIn(node['intuition'][0],page);self.assertIn(node['answer'],page)
        self.assertIn('逐步理解与例证',page);self.assertIn('检查理解',page)
        self.assertIn('data-mastery="'+node['id']+'"',page)
        p=Links();p.feed(page)
        self.assertIn('example',p.ids);self.assertNotIn('formula',p.ids);self.assertNotIn('experiment',p.ids)
        self.assertNotIn('本页算例与坐标约定',page);self.assertNotIn('位置与位移的直觉',page)
        for _,href in p.links:
            u=urlsplit(href)
            if u.fragment and not u.path:self.assertIn(u.fragment,p.ids)
    def test_reference_to_absent_formula_anchor_fails(self):
        node=self.nonformula_fixture()
        self.c['nodes']['point-vector']['related']=[{'node':node['id'],'anchor':'formula'}]
        self.reject('missing anchor .*#formula')
    def test_nonformula_ready_still_needs_explanation_example_and_check(self):
        for field,value in [('intuition',[]),('steps',[]),('exercise',''),('answer',''),('summary','')]:
            with self.subTest(field=field):
                node=self.nonformula_fixture();node[field]=value
                with self.assertRaises(ContentError):validate(self.c)
    def test_optional_fields_are_checked_when_provided(self):
        for field,value,message in [('example','missing','unknown example'),('lab','missing','unknown lab'),('formula',[],'formula must be nonempty')]:
            with self.subTest(field=field):
                node=self.nonformula_fixture();node[field]=value
                self.reject(message)
    def test_ready_path_requires_ready_steps(self):
        self.c['nodes']['basis-coordinates']['status']='draft';self.reject('not ready')
    def test_ready_path_checks_prerequisite_order(self):
        p=self.c['paths']['zero-scale'];p['steps'][0],p['steps'][1]=p['steps'][1],p['steps'][0];self.reject('out-of-order prerequisite')
    def test_missing_prerequisite_is_not_silently_skipped(self):
        p=self.c['paths']['zero-scale'];p.pop('legacy_storage');p['steps']=p['steps'][1:];self.reject('missing or out-of-order')
    def test_stub_is_explicit_and_linkable(self):
        stub={'id':'future-unit','title':'后续待补单元','status':'stub','summary':'补齐这个学习目标','requires':[],'related':[]}
        self.c['nodes'][stub['id']]=stub;self.c['nodes']['point-vector']['related'].append({'node':stub['id']});validate(self.c)
        page=render_site(self.c)['knowledge/future-unit/index.html'];self.assertIn('待补充',page);self.assertNotIn('data-mastery=',page)
    def test_draft_path_discloses_missing_content(self):
        self.c['paths']['zero-scale']['status']='draft';self.c['nodes']['basis-coordinates']['status']='stub';validate(self.c)
        page=render_site(self.c)['lessons/zero-scale/index.html'];self.assertIn('前置待补齐',page);self.assertIn('这条路径仍在整理',page)
    def test_unknown_lab(self):
        self.c['nodes']['basis-coordinates']['lab']='absent';self.reject('unknown lab')
    def test_legacy_map_cannot_drop_old_records(self):
        del self.c['paths']['zero-scale']['legacy_storage']['mastery_map']['points'];self.reject('cover legacy anchors')
    def test_reverse_usage_is_derived(self):
        r=reverse_index(self.c)
        self.assertIn({'node':'basis-coordinates','reason':self.c['nodes']['basis-coordinates']['requires'][0]['reason']},r['point-vector']['required_by'])
        self.assertIn('zero-scale',r['basis-coordinates']['paths'])
        self.assertTrue({'linear-algebra','graphics-transforms'}<=set(r['basis-coordinates']['topics']))
        self.assertIn('point-vector',r['affine-homogeneous']['related'])
    def test_same_source_updates_node_and_continuous_path(self):
        marker='一次修订，应在两个阅读入口同时出现。';self.c['nodes']['basis-coordinates']['intuition'][0]=marker
        out=render_site(self.c)
        for file in ['knowledge/basis-coordinates/index.html','lessons/zero-scale/index.html','lessons/zero-scale/course.md']:self.assertIn(marker,out[file])
        self.assertNotIn(self.c['paths']['zero-scale']['steps'][1]['bridge'],out['knowledge/basis-coordinates/index.html'])
    def test_webpages_do_not_require_video(self):
        out=render_site(self.c)
        for path,text in out.items():
            if path.endswith('.html') and not path.endswith('/history.html'):self.assertNotIn('<video',text)
        self.assertIn('<video',out['lessons/zero-scale/history.html'])
    def test_all_generated_links_and_fragments(self):
        outputs=render_site(self.c);parsed={}
        for name,text in outputs.items():
            if name.endswith('.html'):
                p=Links();p.feed(text);self.assertEqual(len(p.ids),len(set(p.ids)),name+' duplicate IDs');parsed[name]=p
        for name,p in parsed.items():
            for tag,href in p.links:
                u=urlsplit(href)
                if u.scheme:
                    self.assertIn(u.scheme,['https','http']);self.assertEqual(tag,'a');continue
                target=(ROOT/name).parent/unquote(u.path) if u.path else ROOT/name
                target=target.resolve();self.assertTrue(target.is_relative_to(ROOT),'escaped repository')
                key=target.relative_to(ROOT).as_posix();self.assertTrue(key in outputs or target.is_file(),name+' → '+href)
                if u.fragment:
                    q=parsed.get(key)
                    if q is None:q=Links();q.feed(target.read_text())
                    self.assertIn(unquote(u.fragment),q.ids,name+' → '+href)
        for key in self.c['nodes']:self.assertIn(f'knowledge/{key}/index.html',parsed)
        for key in self.c['topics']:self.assertIn(f'topics/{key}/index.html',parsed)
        for key in self.c['paths']:self.assertIn(f'lessons/{key}/index.html',parsed)
    def test_build_outputs_current_and_deterministic(self):
        a=render_site(self.c);self.assertEqual(a,render_site(self.c))
        for name,data in a.items():self.assertEqual((ROOT/name).read_text(),data,name+' stale')
    def test_old_urls_and_section_anchors_remain(self):
        out=render_site(self.c);p=Links();p.feed(out['lessons/zero-scale/index.html'])
        for name in ['points','basis','columns','order','affine','hierarchy','inverse','precision','reparent','api','video','notes','references','lab-basis','lab-order','lab-precision','lab-reparent']:
            self.assertIn(name,p.ids)
        self.assertEqual(out['lessons/zero-scale/math.js'],(ROOT/'assets/math.js').read_text())

if __name__=='__main__':unittest.main(verbosity=2)
