#!/usr/bin/env python3
"""Aesthetics catalog contracts, honest map status and generic non-math paths."""
import copy,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from knowledge import load_catalog,validate,reverse_index,anchors,ContentError
from build_site import render_site
NODE='observation-interpretation-preference'
class AestheticsTests(unittest.TestCase):
    def setUp(self):self.c=load_catalog()
    def rejects(self,pattern):
        with self.assertRaisesRegex(ContentError,pattern):validate(self.c)
    def test_map_covers_three_layers_five_stages_and_only_one_ready_unit(self):
        validate(self.c);t=self.c['topics']['aesthetics'];m=t['learning_map']
        self.assertEqual(len(m['layers']),3);self.assertEqual(len(m['stages']),5)
        self.assertEqual([n for n in t['nodes'] if self.c['nodes'][n]['status']=='ready'],[NODE])
        page=render_site(self.c)['topics/aesthetics/index.html']
        self.assertIn('1 / 19 个节点可学习',page);self.assertEqual(page.count('data-status="stub"'),18)
        self.assertNotIn('data-mastery=',page)
        for n in t['nodes']:
            if n!=NODE:
                p=render_site(self.c)['knowledge/'+n+'/index.html']
                self.assertIn('待补充',p);self.assertNotIn('data-mastery=',p)
    def test_map_rejects_unknown_duplicate_and_omitted_nodes(self):
        pristine=copy.deepcopy(self.c)
        for replacement,pattern in [('absent','unknown map node'),(NODE,'duplicate map'),(None,'must cover')]:
            with self.subTest(replacement=replacement):
                self.c=copy.deepcopy(pristine);nodes=self.c['topics']['aesthetics']['learning_map']['layers'][1]['nodes']
                if replacement is None:nodes.pop()
                else:nodes[0]=replacement
                self.rejects(pattern)
    def test_context_is_directed_and_does_not_invent_prerequisites(self):
        self.assertEqual(self.c['nodes'][NODE]['requires'],[])
        self.assertEqual(len(self.c['nodes'][NODE]['context']),2)
        self.c['nodes']['pictorial-arts']['context']=[{'node':NODE,'reason':'Reciprocal context is allowed.'}]
        validate(self.c)
        self.assertEqual(reverse_index(self.c)[NODE]['required_by'],[])
        self.assertNotIn('pictorial-arts',reverse_index(self.c)[NODE]['related'])
        page=render_site(self.c)['knowledge/'+NODE+'/index.html']
        self.assertIn('语境关联 · 不作为必要前置',page)
    def test_context_validates_targets_anchors_and_reasons(self):
        pristine=copy.deepcopy(self.c)
        for value,pattern in [([{'node':'missing','reason':'x'}],'unknown node'),([{'node':'pictorial-arts'}],'context needs a reason'),([{'node':'pictorial-arts','reason':'x','anchor':'formula'}],'missing anchor')]:
            with self.subTest(value=value):
                self.c=copy.deepcopy(pristine);self.c['nodes'][NODE]['context']=value;self.rejects(pattern)
    def test_optional_teaching_fields_and_case_citations_are_validated(self):
        pristine=copy.deepcopy(self.c)
        for field,value,pattern in [('question','','question'),('boundaries',[],'boundaries'),('cases',[],'cases'),('cases',[{'title':'test','paragraphs':['x'],'sources':['mit']}],'case citation')]:
            with self.subTest(field=field):
                self.c=copy.deepcopy(pristine);self.c['nodes'][NODE][field]=value;self.rejects(pattern)
    def test_nonmath_path_has_no_phantom_formula_or_zero_scale_guidance(self):
        validate(self.c);out=render_site(self.c);page=out['lessons/aesthetics-observation/index.html']
        self.assertIn('id="lab-aesthetic"',page);self.assertIn('assets/aesthetics.js',page)
        self.assertNotIn('零缩放策略',page);self.assertNotIn('Unity 链接固定',page);self.assertNotIn('本页算例与坐标约定',page)
        self.assertNotIn('assets/overview.svg',page);self.assertNotIn('aesthetics.js',out['lessons/zero-scale/index.html'])
        self.assertTrue({'boundaries','cases','experiment'}<=anchors(self.c['nodes'][NODE]))
        self.assertNotIn('formula',anchors(self.c['nodes'][NODE]))
    def test_cases_and_boundaries_share_single_source_across_exports(self):
        marker='案例正文的一次修订应出现在两个入口和文字导出。'
        self.c['nodes'][NODE]['cases'][0]['paragraphs'][0]=marker
        out=render_site(self.c)
        for path in ['knowledge/'+NODE+'/index.html','lessons/aesthetics-observation/index.html','lessons/aesthetics-observation/course.md']:
            self.assertIn(marker,out[path])
    def test_nonmath_path_does_not_link_absent_optional_sections(self):
        for field in ['boundaries','cases','lab']:self.c['nodes'][NODE].pop(field)
        validate(self.c);page=render_site(self.c)['lessons/aesthetics-observation/index.html']
        for anchor in ['boundaries','cases','experiment']:
            self.assertNotIn(f'href="#{NODE}--{anchor}"',page)
    def test_existing_prerequisite_graph_and_math_units_are_untouched(self):
        self.assertEqual(validate(self.c)['prerequisite_edges'],10)
        self.assertEqual(len(self.c['paths']['zero-scale']['steps']),9)
        for s in self.c['paths']['zero-scale']['steps']:
            n=self.c['nodes'][s['node']];self.assertEqual(n['status'],'ready');self.assertIn('formula',n)
        node=self.c['nodes'][NODE]
        for field in ['question','intuition','steps','boundaries','lab','cases','exercise','answer','sources']:self.assertTrue(node[field])
if __name__=='__main__':unittest.main(verbosity=2)
