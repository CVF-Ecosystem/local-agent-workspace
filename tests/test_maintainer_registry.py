import os, sys, tempfile, unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import check_package as cp
import upgrade_package as up

class RegistryBoundary(unittest.TestCase):
 def test_projection_and_py38(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)/'src';root.mkdir(); out=Path(tmp)/'out'
   files={'docs/milestone-coverage-authority.json':b'PRIVATE', 'en/docs/milestone-coverage-authority.json':b'PRIVATE EN', '.cvf/maintainer/cvf13/future.py':b'x.is_relative_to(y)\n', 'en/.cvf/maintainer/future.py':b'x.is_relative_to(y)\n','docs/milestone-coverage-authority-notes.json':b'PUBLIC','docs/public.py':b'x=1\n'}
   for name,data in files.items(): p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
   with mock.patch.object(cp,'ROOT',str(root)),mock.patch.object(cp,'source_state',return_value='maintainer'),mock.patch.object(cp,'_check_user_file_mapping'),mock.patch.object(cp,'CVF_CLOSURE',()),mock.patch.object(cp,'TEMPLATE_OVERLAYS',{}),mock.patch.object(cp,'delivery_problems',return_value=[]),mock.patch.object(cp,'_ep') as ep:
    ep.return_value.clean_profile_bytes.return_value=b'{}\n'
    selection=cp.delivery_selection(branding=False)
    for name in list(files)[:4]: self.assertNotIn(name,selection)
    self.assertIn('docs/milestone-coverage-authority-notes.json',selection)
    self.assertFalse(cp.check_py38())
    manifest=cp.delivery_manifest(selection,branding=False).decode();self.assertNotIn('docs/milestone-coverage-authority.json',manifest)
    cp.materialize(str(out),branding=False)
    self.assertFalse((out/'docs/milestone-coverage-authority.json').exists());self.assertTrue((out/'docs/milestone-coverage-authority-notes.json').exists())
    for path in ('docs/MILESTONE-COVERAGE-AUTHORITY.json','en\\docs\\.\\milestone-coverage-authority.json','.cvf/maintainer/cvf13/future.py','en/.CVF/MAINTAINER/future.py'):
     self.assertTrue(cp.user_owned(path));self.assertFalse(cp.in_manifest(path))
     with self.assertRaises(cp.ProjectionError):cp.delivery_bytes(path)
    self.assertFalse(cp.maintainer_namespace('.cvf/maintainer-notes/file.py'))
 def test_contaminated_source_and_old_verify_never_open_reserved(self):
  import builtins, hashlib
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); names=['docs/milestone-coverage-authority.json','en/docs/milestone-coverage-authority.json','.cvf/maintainer/cvf13/file.py','en/.cvf/maintainer/cvf13/file.py'];public='docs/ordinary.md'
   for rel in names+[public]:
    p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'original')
   lines=['%s  %s'%(hashlib.sha256(b'original').hexdigest(),rel) for rel in names+[public]]
   (root/'MANIFEST.sha256').write_text('\n'.join(lines)+'\n',encoding='utf-8')
   original=builtins.open; attempts=[]
   def observed(path,*args,**kwargs):
    if any(os.path.normcase(os.path.normpath(str(path)))==os.path.normcase(os.path.normpath(str(root/n))) for n in names): attempts.append(str(path));raise AssertionError('reserved open')
    return original(path,*args,**kwargs)
   with mock.patch('builtins.open',side_effect=observed),mock.patch.object(cp,'ROOT',str(root)),mock.patch('builtins.print'):
    problems=cp.source_package_problems(str(root));self.assertIn('SOURCE_MANIFEST_USER_DATA',[x[0] for x in problems]);self.assertEqual(cp.verify(),0)
    (root/public).write_bytes(b'changed');self.assertEqual(cp.verify(),1)
   self.assertEqual(attempts,[])
 def test_old_and_new_manifest_cannot_acquire(self):
  with tempfile.TemporaryDirectory() as tmp:
   base=Path(tmp);project=base/'project';source=base/'source';project.mkdir();source.mkdir()
   reg='docs/milestone-coverage-authority.json'; maint='.cvf/maintainer/cvf13/file.py'; public='docs/normal.md'
   for rel,data in [(reg,b'own'),(maint,b'local')]: p=project/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
   old={reg:'0'*64,maint:'0'*64,public:'0'*64};new={reg:'1'*64,maint:'1'*64,public:'1'*64}
   with mock.patch.object(up,'read_manifest',side_effect=[old,new]),mock.patch.object(up,'branding_files',return_value=[]): plan=up.plan(str(project),str(source),'vi')
   for key in ('add','update','conflict','obsolete','kept','user_missing','user_changed'):
    self.assertNotIn(reg,str(plan[key]));self.assertNotIn(maint,str(plan[key]))
   self.assertEqual((project/reg).read_bytes(),b'own');self.assertEqual((project/maint).read_bytes(),b'local')
   with mock.patch.object(up,'read_manifest',side_effect=[old,{public:'1'*64}]),mock.patch.object(up,'branding_files',return_value=[]): plan=up.plan(str(project),str(source),'vi')
   self.assertNotIn(reg,plan['obsolete']);self.assertNotIn(maint,plan['obsolete'])

if __name__=='__main__':unittest.main()
