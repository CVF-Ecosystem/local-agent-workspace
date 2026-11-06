"""LAW-scoped repair admission. No activation, Office control or permissions are created."""
import hashlib
import argparse
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
REGISTRY = 'docs/milestone-coverage-authority.json'
ROAD = 'roadmap/ROADMAP_VAN_PHONG_NGHIEP_VU.md'
HEADING = '#### 4.4. V4/V7 — Nghiệm thu nội dung và định dạng trong phạm vi công bố'
SECTION_SHA = '6f094ef5ad62915862391d7c2739dcb7af61dac35e74a94d86660cfee3a42d80'
PINS = {
 ROAD:'1a25f170552aece28be7164c43c141e187d54e894b64caa254aac3bdbb7256da',
 'working/excel-workflow-quality-20261029/consumers/Excel-Flow/working/case/REQUEST.md':'46213c4ff01392a983d85eb65e03524911a156133ee5072808a3fbe9a7bc2410',
 'working/excel-workflow-quality-20261029/consumers/Excel-Flow/working/case/RULES.md':'23a59aadaf25ddc13ffd88d34b059490693bb301d6a3172d6555784d6b509ef4',
}
MODULES = {'cvf_milestone_coverage.py':'cd923b842aabce33f352c2ea14c55a3a7c2fa6bb549de62b3897712fc68c0b02',
           'cvf_repair_convergence.py':'227c56680648623eed294b49795e113ac520658276c8503eb6268b925a36fd3c'}
PARENT = ROOT.parent/'CVF_RULE_PACKS/operator-local/source/scripts/lib/downstream_governance'
PARENT_FINGERPRINT = {ROOT.parent/'CVF_RULE_PACKS/operator-local/RULE_PACK_MANIFEST.json':'4e1eeaa1b4c80f502cca9c8fd236db54beacdfe818e4c92c58c269be98f21b45',
 ROOT.parent/'CVF_RULE_PACKS/ACTIVE_RULE_PACK.json':'e56cf61c148029ee28859cfe0b364db10e7b8a95ca8df249d926b7546dd58aaf',
 ROOT.parent/'AGENTS.md':'5b4f57b9172f6f5ad836e0fc145893d48925c9ac813e61da479239b6eef9dc1f',
 ROOT.parent/'Check-CVF-Project-Activation.py':'60f65910d70cde8e9af6af8593f38edbfc9af83128faabb25150d1f07294635b'}
MAX = 1024*1024

class Hold(ValueError): pass

def need(value, reason):
    if not value: raise Hold(reason)

def guard(path):
    p=Path(os.path.abspath(path))
    while True:
        st=os.lstat(p)
        need(not stat.S_ISLNK(st.st_mode) and not getattr(st,'st_file_attributes',0)&0x400,'REPARSE_REFUSED')
        if p.parent==p: break
        p=p.parent

def read(path):
    guard(path); p=Path(path); st=p.stat()
    need(stat.S_ISREG(st.st_mode) and st.st_size<=MAX,'FILE_INVALID_OR_OVERSIZE')
    data=p.read_bytes(); need(len(data)<=MAX,'FILE_INVALID_OR_OVERSIZE'); return data

def sha(data): return hashlib.sha256(data).hexdigest()
def lfsha(data): return sha(data.replace(b'\r\n',b'\n'))
def parse(data):
    def pairs(xs):
        d={}
        for k,v in xs:
            need(k not in d,'DUPLICATE_KEY'); d[k]=v
        return d
    def nonfinite(x): raise Hold('NONFINITE_JSON')
    return json.loads(data.decode('utf-8-sig'),object_pairs_hook=pairs,parse_constant=nonfinite)
def shape(obj, keys): need(isinstance(obj,dict) and set(obj)==set(keys),'PACKET_SHAPE')

def public_relative(rel):
    need(isinstance(rel,str) and rel and '\\' not in rel and ':' not in rel and not rel.startswith('/') and all(x not in ('','.','..') for x in rel.split('/')),'EVIDENCE_PATH_INVALID')
    parts=rel.casefold().split('/');name=parts[-1]
    need('private' not in parts and not ('credentials' in name and name.endswith('.json')) and not name.startswith('.env') and not name.endswith(('.pem','.key','.p12','.pfx')),'PRIVATE_EVIDENCE_REFUSED')

def trusted_modules(root=ROOT, here=HERE):
    guard(root);guard(here)
    need(Path(here).resolve().is_relative_to(Path(root).resolve()),'MODULE_DIR_OUTSIDE_ROOT')
    for p,pin in PARENT_FINGERPRINT.items(): need(sha(read(p))==pin,'PARENT_FINGERPRINT_CHANGED')
    for n,pin in MODULES.items():
        need(sha(read(Path(here)/n))==pin,'MODULE_PIN_MISMATCH')
        need(sha(read(PARENT/n))==pin,'SOURCE_PIN_MISMATCH')
    allowed=set(MODULES)|{'law_repair_adapter.py','activation.json','integration-lock.json','assessment.json','history'}
    for p in Path(here).iterdir():
        guard(p)
        need(p.name in allowed and (p.is_dir() if p.name=='history' else p.is_file()),'UNEXPECTED_MODULE')
    spec=importlib.util.spec_from_file_location('law_cvf13_coverage',Path(here)/'cvf_milestone_coverage.py')
    need(spec is not None and spec.loader is not None,'COVERAGE_IMPORT_REFUSED')
    module=importlib.util.module_from_spec(spec);sys.dont_write_bytecode=True;spec.loader.exec_module(module)
    return module

def check_authority(root, cov):
    for rel,pin in PINS.items(): need(sha(read(Path(root)/rel))==pin,'SOURCE_PIN_MISMATCH')
    data=read(Path(root)/ROAD).decode('utf-8-sig')
    need(cov.digest(cov.section(data,HEADING).encode('utf-8'))==SECTION_SHA,'AUTHORITY_SECTION_CHANGED')

def evaluate(root,registry,seal,packet,cov,run_transition=False,packet_path=None,packet_text=None):
    """Pure composition entry for bounded fixture tests; caller owns trusted module loading."""
    root=Path(root)
    shape(seal,('schema','milestone','authority','affected','history_prefix'))
    need(seal['schema']=='law.cvf13.seal/1' and seal['milestone']=='V4','SEAL_INVALID')
    expected={'path':ROAD,'heading':HEADING}
    need(seal['authority']==expected and seal['affected']==['V4'],'SEAL_AUTHORITY_MISMATCH')
    api=cov._repair_api(packet_path,packet_text)
    # Preserve parent read budgets while adding LAW's no-reparse/private boundary.
    parent_read,parent_evidence=api.read_file,api.evidence
    def safe_path(base,rel):
        public_relative(rel)
        need(rel.startswith(('.cvf/maintainer/cvf13/','working/excel-workflow-quality-20261029/','working/cvf-profile13-adoption-20261105/')) or rel in PINS or rel==REGISTRY,'EVIDENCE_SCOPE_REFUSED')
        guard(Path(base)/rel)
    def bounded_read(base,rel):
        safe_path(base,rel);return parent_read(base,rel)
    def bounded_evidence(base,refs,required=False):
        need(isinstance(refs,list) and len(refs)<=100,'EVIDENCE_LIST_INVALID')
        for ref in refs:
            shape(ref,('path','sha256'));safe_path(base,ref['path'])
        return parent_evidence(base,refs,required)
    api.read_file=bounded_read;api.evidence=bounded_evidence
    repair=cov._repair()
    rows=repair.controls(registry,api)
    need(registry.get('schemaVersion')=='cvf.milestoneAuthority@1.1.0' and registry.get('milestones',{}).get('V4')==expected and 'V4' in rows,'V4_ENROLLMENT_REQUIRED')
    row=rows['V4']; shape(row,('history','affectedCriteria','audit'))
    need(row['affectedCriteria']==['V4'] and isinstance(row['history'],list) and isinstance(seal['history_prefix'],list) and bool(seal['history_prefix']) and row['history'][:len(seal['history_prefix'])]==seal['history_prefix'],'HISTORY_PREFIX_MISMATCH')
    shape(packet,('milestone','action','rows','conclusions'))
    shape(packet['milestone'],('id',));need(packet['milestone']['id']=='V4','MILESTONE_REFUSED')
    need(isinstance(packet['action'],dict),'ACTION_INVALID')
    extra=('question','sourceBoundary') if packet['action'].get('kind')=='VERIFY' else ()
    shape(packet['action'],('kind','selected','owner','output','budgetMinutes')+extra)
    action=packet['action'];need(action['kind'] in ('PLAN','REVIEW','IMPLEMENT','VERIFY'),'ACTION_REFUSED')
    need(action['selected']==['V4'],'SELECTION_REFUSED')
    need(isinstance(action['owner'],str) and bool(action['owner'].strip()) and isinstance(action['output'],str) and bool(action['output'].strip()) and type(action['budgetMinutes']) is int and action['budgetMinutes']>0,'ACTION_INVALID')
    for key in extra: cov.text(action[key])
    need(packet['rows']==[{'id':'V4','state':'BLOCKED'}],'ROWS_REFUSED')
    shape(packet['conclusions'],('product',));need(packet['conclusions']['product']=='BLOCKED','PRODUCT_NOT_BLOCKED')
    affected,audit=repair.inspect_control(root,'V4',row,api)
    need(affected=={'V4'} and audit is not None,'ASSESSMENT_REQUIRED')
    if action['kind'] in ('IMPLEMENT','VERIFY'):
        need(packet_path is not None and packet_text is not None,'PACKET_BINDING_REQUIRED')
    repair.validate(root,packet,registry,api)
    if run_transition: repair.transition(root,None,api)
    return 'VALID_'+audit['disposition']+'_NO_EFFECT_AUTHORITY'

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('inspect','admit'),nargs='?',default='inspect')
    parser.add_argument('--packet')
    args=parser.parse_args(argv)
    try:
        need((args.command=='admit')==bool(args.packet),'PACKET_ARGUMENT_REQUIRED')
        activation=parse(read(HERE/'activation.json'));shape(activation,('schema','seal_sha256','adapter_sha256','registry_sha256','review_evidence'))
        need(activation['schema']=='law.cvf13.activation/2' and activation['adapter_sha256']==sha(read(HERE/'law_repair_adapter.py')),'ACTIVATION_INVALID')
        seal_data=read(HERE/'integration-lock.json');need(lfsha(seal_data)==activation['seal_sha256'],'SEAL_PIN_MISMATCH')
        evidence=activation['review_evidence'];shape(evidence,('path','sha256'))
        rel=evidence['path'];public_relative(rel)
        need(rel.startswith('working/cvf-profile13-adoption-20261105/'),'REVIEW_PATH_INVALID')
        need(lfsha(read(ROOT/rel))==evidence['sha256'],'REVIEW_PIN_MISMATCH')
        cov=trusted_modules();check_authority(ROOT,cov)
        cov.evidence(ROOT,[evidence],True)
        registry_data=read(ROOT/REGISTRY);need(lfsha(registry_data)==activation['registry_sha256'],'REGISTRY_PIN_MISMATCH')
        registry=parse(registry_data);seal=parse(seal_data)
        packet_path=packet_text=None
        if args.command=='admit':
            packet_path=args.packet
            public_relative(packet_path)
            need(packet_path.startswith('working/cvf-profile13-adoption-20261105/') and '\\' not in packet_path and ':' not in packet_path and all(x not in ('','.','..') for x in packet_path.split('/')),'PACKET_PATH_INVALID')
            packet_text=read(ROOT/packet_path).decode('utf-8-sig');packet=parse(packet_text.encode('utf-8'))
            need(isinstance(packet,dict) and isinstance(packet.get('action'),dict) and packet['action'].get('kind') in ('IMPLEMENT','VERIFY'),'ADMISSION_ACTION_REQUIRED')
        else:
            packet={'milestone':{'id':'V4'},'action':{'kind':'PLAN','selected':['V4'],'owner':'Main','output':'inspection','budgetMinutes':1},'rows':[{'id':'V4','state':'BLOCKED'}],'conclusions':{'product':'BLOCKED'}}
        print(evaluate(ROOT,registry,seal,packet,cov,run_transition=True,packet_path=packet_path,packet_text=packet_text));return 0
    except Exception as exc:
        print('HOLD: '+str(exc));return 1

if __name__=='__main__': sys.exit(main())
