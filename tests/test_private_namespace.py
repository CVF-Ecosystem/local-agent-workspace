"""Private namespace boundary; tiny DATAMOCK fixtures, never project ROOT materialization."""
import builtins,io,os,sys,tempfile,unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'tools'))
import check_package as cp
import upgrade_package as up
PRIVATE=('.agent/private/README.md','.agent/private/nested/config.json','.agent/private/file.unknown','.agent/private/credentials.example.json','en/.agent/private/demo.example')
PUBLIC=('.agent/private-notes.md','.agent/private.example','tools/public_credentials.example.json')
ALIASES=('.agent/private','.agent/private/a.md','.AGENT\\PRIVATE\\x.json','en/.Agent/private/a.example','en\\.agent\\foo\\..\\PRIVATE\\x')
class Boundary(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(prefix='law-private-namespace-'); self.addCleanup(self.t.cleanup); self.base=Path(self.t.name); self.source=self.base/'source'; self.source.mkdir()
  for rel in PRIVATE+PUBLIC:
   p=self.source/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(('DATAMOCK '+rel+'\n').encode())
 def spy(self):
  opened=[]; a=builtins.open; b=io.open
  def intercept(original):
   def call(path,*args,**kw):
    if isinstance(path,(str,bytes,os.PathLike)):
     s=os.fsdecode(path).replace('\\','/').casefold()
     if '/.agent/private/' in s: opened.append(s); raise AssertionError('private content attempted: '+s)
    return original(path,*args,**kw)
   return call
  return opened,mock.patch('builtins.open',intercept(a)),mock.patch('io.open',intercept(b))
 def test_alias_classification_and_delivery_refusal_before_open(self):
  for rel in ALIASES:
   with self.subTest(rel=rel):
    self.assertTrue(cp.user_owned(rel)); self.assertFalse(cp.in_manifest(rel))
    opened,p1,p2=self.spy()
    with mock.patch.object(cp,'ROOT',str(self.source)),p1,p2:
     with self.assertRaises(cp.ProjectionError) as e: cp.delivery_bytes(rel)
     self.assertEqual(e.exception.code,'EXCLUDED_FILE')
  for rel in PUBLIC:
   self.assertTrue(cp.in_manifest(rel)); self.assertFalse(cp.user_owned(rel))
 def test_selection_manifest_and_materialization_without_private_reads_or_walk(self):
  opened,p1,p2=self.spy(); real_walk=os.walk; visited=[]
  def walk(*args,**kw):
   for d,dirs,files in real_walk(*args,**kw): visited.append(str(d).replace('\\','/').casefold()); yield d,dirs,files
  dest=self.base/'delivery'
  with mock.patch.object(cp,'ROOT',str(self.source)),mock.patch.object(cp,'source_state',return_value='maintainer'),mock.patch.object(cp,'delivery_problems',return_value=[]),mock.patch.object(cp,'TEMPLATE_OVERLAYS',{}),mock.patch.object(cp,'_check_user_file_mapping',return_value=None),mock.patch.object(cp,'CVF_CLOSURE',()),mock.patch.object(cp.os,'walk',walk),p1,p2:
   self.assertFalse(cp.private_files(self.source))
   self.assertFalse(any(cp.private_namespace(r) for r in cp._walk(self.source,skip_private=False)))
   selected=cp.delivery_selection(branding=False)
   manifest=cp.delivery_manifest(selected,branding=False)
   cp.materialize(str(dest),branding=False)
  self.assertFalse(opened); self.assertFalse(any('/.agent/private' in d for d in visited))
  for rel in PRIVATE: self.assertNotIn(rel,selected); self.assertNotIn(rel.encode(),manifest); self.assertFalse((dest/rel).exists())
  for rel in PUBLIC: self.assertIn(rel,selected); self.assertTrue((dest/rel).is_file()); self.assertIn(rel.encode(),manifest)
 def test_namespace_root_file_is_not_enumerated(self):
  isolated=self.base/'root-file'; isolated.mkdir()
  for rel in ('.agent/private','en/.AGENT/PRIVATE'):
   path=isolated/rel; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(b'DATAMOCK private root file')
  self.assertEqual(cp._walk(isolated),[])
  self.assertEqual(cp._walk(isolated,skip_private=False),[])
  self.assertEqual(cp.private_files(isolated),[])
 def test_delivered_tree_private_presence_metadata_only(self):
  # Deliberately no manifest entry: release-tree detection must still refuse.
  isolated=self.base/'delivered'; isolated.mkdir()
  for rel in ('.AGENT/PRIVATE/canary.json','EN/.agent/private/nested/canary.example'):
   path=isolated/rel; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(b'DATAMOCK')
  opened,p1,p2=self.spy(); original=os.scandir; visited=[]
  def scan(path):
   text=str(path).replace('\\','/').casefold(); visited.append(text)
   if text.endswith('/private') or '/private/' in text: raise AssertionError('entered private namespace')
   return original(path)
  with mock.patch.object(cp,'ROOT',str(isolated)),mock.patch.object(cp.os,'scandir',scan),p1,p2:
   problems=cp.tree_problems()
  self.assertFalse(opened)
  self.assertEqual(len([v for v in problems if 'có namespace private' in v]),2)
  self.assertFalse(any(v.endswith('/private') or '/private/' in v for v in visited))
 def test_old_target_manifest_does_not_reclassify_or_read_private(self):
  target=self.base/'target'; new=self.base/'new'; target.mkdir(); new.mkdir()
  target_private=target/'.agent/private/settings.json'; target_private.parent.mkdir(parents=True); target_private.write_bytes(b'DATAMOCK USER CHOICE')
  before=target_private.read_bytes(); line='0'*64+'  .agent/private/settings.json\n'
  (target/'MANIFEST.sha256').write_text(line,encoding='utf8'); (new/'MANIFEST.sha256').write_text('',encoding='utf8')
  opened,p1,p2=self.spy()
  with p1,p2: plan=up.plan(str(target),str(new),'vi')
  self.assertFalse(opened); self.assertNotIn('.agent/private/settings.json',plan['obsolete']); self.assertEqual(target_private.read_bytes(),before)
  (new/'MANIFEST.sha256').write_text(line,encoding='utf8')
  with p1,p2: new_plan=up.plan(str(target),str(new),'vi')
  self.assertFalse(opened)
  for key in ('add','update','conflict','obsolete','kept','user_missing','user_changed'): self.assertEqual(new_plan[key],[],key)
  self.assertEqual(new_plan['snapshot'],{})
  self.assertEqual(target_private.read_bytes(),before)
 def test_contaminated_source_manifest_refuses_before_private_read(self):
  rel=PRIVATE[0]; (self.source/'MANIFEST.sha256').write_text('0'*64+'  '+rel+'\n',encoding='utf8')
  opened,p1,p2=self.spy()
  with p1,p2: problems=cp.source_package_problems(str(self.source))
  self.assertFalse(opened); self.assertIn('SOURCE_MANIFEST_USER_DATA',[code for code,_ in problems])
if __name__=='__main__': unittest.main(verbosity=2)
