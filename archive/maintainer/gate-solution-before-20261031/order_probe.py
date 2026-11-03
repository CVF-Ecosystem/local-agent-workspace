import os,sys,time,json,subprocess,tempfile,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; JOB=ROOT/'working/gate-runtime-20261031'; SOURCE=ROOT/'working/delta-artifact-20261031/source'
def event(phase,kind,**kw):
 print(json.dumps(dict(phase=phase,event=kind,pid=os.getpid(),elapsed=round(time.monotonic()-START,3),**kw)),flush=True)
START=time.monotonic()
if len(sys.argv)>1:
 import faulthandler,unittest
 faulthandler.dump_traceback_later(110,repeat=False)
 event('import','start');sys.path.insert(0,str(SOURCE/'tests'))
 processes=[]
 original_popen=subprocess.Popen
 class ObservedPopen(original_popen):
  def __init__(self,*a,**kw):
   super().__init__(*a,**kw);processes.append(self);event('process','spawn',child_pid=self.pid)
 subprocess.Popen=ObservedPopen
 import test_panel_intake as intake
 import test_source_response as response
 import test_ui_browser as m
 event('import','end')
 def wrap(obj,name,label):
  old=getattr(obj,name)
  def observed(*a,**k):
   event(label,'start')
   try:return old(*a,**k)
   finally:event(label,'end')
  setattr(obj,name,observed)
 for obj,name,label in [(m,'copy_package','copy_package'),(m.cp,'materialize','materialize'),(m.Panel,'start','Panel.start'),(m.Panel,'stop','Panel.stop'),(m.BrowserCase,'setUp','testsetup'),(m.BrowserCase,'tearDown','teardown')]:wrap(obj,name,label)
 for name in ['setUpClass','tearDownClass']:
  old=getattr(m.LibraryPage,name)
  def observed(cls,_old=old,_name=name):
   event(_name,'start')
   try:return _old()
   finally:event(_name,'end')
  setattr(m.LibraryPage,name,classmethod(observed))
 from playwright.sync_api import Page
 oldeval=Page.evaluate
 def evaluate(self,expression,*a,**kw):
  clipboard='clipboard' in expression
  if clipboard:event('clipboard','start')
  try:return oldeval(self,expression,*a,**kw)
  finally:
   if clipboard:event('clipboard','end')
 Page.evaluate=evaluate
 for name in unittest.defaultTestLoader.getTestCaseNames(m.LibraryPage):wrap(m.LibraryPage,name,'body:'+name)
 wrap(intake.PanelIntake,'setUp','intake_setup')
 baseline_app={k:getattr(intake.app,k) for k in ('ROOT','TOOLS','UI_FILE')}
 import builtins,socket
 baseline_io=(builtins.open,socket.socket)
 class Result(unittest.TextTestResult):
  def startTest(self,test):event('test','start',test=test.id());super().startTest(test)
  def stopTest(self,test):
   event('test','end',test=test.id(),app_patch_restored=all(getattr(intake.app,k)==v for k,v in baseline_app.items()),io_patch_restored=(builtins.open,socket.socket)==baseline_io)
   super().stopTest(test)
 wrap(unittest.TestCase,'doCleanups','cleanup')
 event('discover','start')
 suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(intake),unittest.defaultTestLoader.loadTestsFromModule(response),unittest.defaultTestLoader.loadTestsFromTestCase(m.LibraryPage)])
 event('discover','end',count=suite.countTestCases())
 result=unittest.TextTestRunner(verbosity=2,resultclass=Result).run(suite)
 faulthandler.cancel_dump_traceback_later()
 for proc in processes:
  status=proc.poll();event('process','reconcile',child_pid=proc.pid,exit=status)
  if status is None:
   proc.terminate()
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=5)
   event('process','own_cleanup',child_pid=proc.pid,exit=proc.poll())
 event('run','end',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),skip_reasons=[(t.id(),r) for t,r in result.skipped])
 sys.exit(not result.wasSuccessful())

old=json.loads((ROOT/'working/delta-artifact-20261031/BUILD.json').read_text(encoding='utf8'))
for pin in old['binary_bindings']:assert hashlib.sha256(Path(pin['path']).read_bytes()).hexdigest()==pin['sha256']
source_paths=subprocess.check_output(['git','-C',str(SOURCE),'ls-files','-z']).decode().split('\0')
source_pins={p:hashlib.sha256((SOURCE/p).read_bytes()).hexdigest() for p in source_paths if p}
assert subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD']).decode().strip()=='4ca8489f86ac7b3da01b45a34dad0e3690183b7c'
runtime=Path(tempfile.mkdtemp(prefix='law-gate-order-DATAMOCK-'))
for p in ['home','roaming','local','temp','hooks']:(runtime/p).mkdir()
env={k:v for k,v in os.environ.items() if k.upper() in ['SYSTEMROOT','WINDIR','COMSPEC','PATHEXT','PROCESSOR_ARCHITECTURE','NUMBER_OF_PROCESSORS']}
env.update(PATH=os.pathsep.join(dict.fromkeys(str(Path(p['path']).parent) for p in old['binary_bindings'])),PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONUNBUFFERED='1',USERNAME='law-fixture-user-probe',USERPROFILE=str(runtime/'home'),HOME=str(runtime/'home'),APPDATA=str(runtime/'roaming'),LOCALAPPDATA=str(runtime/'local'),TEMP=str(runtime/'temp'),TMP=str(runtime/'temp'),GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_TERMINAL_PROMPT='0',GIT_OPTIONAL_LOCKS='0',GIT_CONFIG_COUNT='3',GIT_CONFIG_KEY_0='core.hooksPath',GIT_CONFIG_VALUE_0=str(runtime/'hooks'),GIT_CONFIG_KEY_1='core.longpaths',GIT_CONFIG_VALUE_1='true',GIT_CONFIG_KEY_2='core.fsmonitor',GIT_CONFIG_VALUE_2='false',PIP_NO_INDEX='1',PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1',PLAYWRIGHT_BROWSERS_PATH=str(Path(next(p['path'] for p in old['binary_bindings'] if p['path'].endswith('chrome.exe'))).parents[2]))
receipt=dict(requested_worker='gpt-6.1-sol/medium',actual_backend='UNKNOWN',scope='one order composite; no product writes',whole_cause='UNKNOWN',status='STARTING',parent_pid=os.getpid(),runtime=str(runtime),binary_bindings=old['binary_bindings'],environment_sha256=hashlib.sha256(json.dumps(env,sort_keys=True).encode()).hexdigest(),started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_commit=old['source_commit'],source_pins=source_pins)
path=JOB/'SOLUTION.json';assert not path.exists()
def save():path.write_text(json.dumps(receipt,indent=2),encoding='utf8')
save();event('before_spawn','start')
with (JOB/'order-stdout.log').open('xb') as out,(JOB/'order-stderr.log').open('xb') as err:
 child=subprocess.Popen([sys.executable,'-X','utf8','-B',__file__,'child'],cwd=str(SOURCE),env=env,stdout=out,stderr=err)
 receipt.update(status='RUNNING',pid=child.pid);save();event('spawn','end',child_pid=child.pid)
 try:receipt.update(exit=child.wait(timeout=120),status='EXITED')
 except subprocess.TimeoutExpired:
  killed=subprocess.run([str(Path(env['SYSTEMROOT'])/'System32/taskkill.exe'),'/PID',str(child.pid),'/T','/F'],capture_output=True,timeout=10)
  receipt.update(status='TIMEOUT',termination_exit=killed.returncode,exit=child.wait(timeout=10))
receipt.update(process_tree_state='UNKNOWN beyond observed Popen handles; no OS-wide absence claim',fullsuite=0,builder=0,retry=0,elapsed_seconds=round(time.monotonic()-START,3),exact_child_poll=child.poll(),source_pins_unchanged=all(hashlib.sha256((SOURCE/p).read_bytes()).hexdigest()==h for p,h in source_pins.items()));save();print(json.dumps(receipt),flush=True)
