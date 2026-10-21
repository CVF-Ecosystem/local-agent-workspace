"""A-09 checks: execution profile, authority owner, explicit migration and profile lifecycle (new / init / adopt / upgrade / delivery).

Everything runs on fake data in temporary folders. Grants and evidence below are structurally valid FAKE claims; nothing here activates a policy,
registers a role, calls a host, a model, the network or CVF, and no real maintainer profile is created or migrated. Faults use the transaction
module's own test hook. The repository tree is only ever read.
"""
import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_package as cp  # noqa: E402
import execution_profile as ep  # noqa: E402
import result_schema  # noqa: E402
import transaction as tx  # noqa: E402

HAVE_JSONSCHEMA = importlib.util.find_spec('jsonschema') is not None
NEED = unittest.skipUnless(HAVE_JSONSCHEMA, 'structure checks need jsonschema (>=4.18)')
PROFILE = ep.PROFILE_REL
LEGACY_VI = 'Trong phiên bảo trì, Main được gọi Reviewer độc lập cho việc đọc và bản nháp.'
LEGACY_EN = 'Main may call an independent Reviewer for reading and drafts.'


def tree(root):
    """Every file and folder with bytes (runtime data included): proof that a refusal or a preview changed nothing."""
    return {p.relative_to(root).as_posix(): (p.read_bytes() if p.is_file() else None) for p in sorted(Path(root).rglob('*'))
            if '__pycache__' not in p.parts}


def run(base, script, *args, env=None):
    e = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    e.update(env or {})
    return subprocess.run([sys.executable, str(Path(base) / 'tools' / script), *map(str, args)], cwd=str(base), env=e,
                          capture_output=True, encoding='utf-8', timeout=300)


def project_text(value, label=ep.PROJECT_LABELS[0], extra=''):
    return ('# NGỮ CẢNH\n\n## Thông tin dự án\n\n- Tên dự án: Demo\n- %s: %s\n- Ngoại lệ thư mục nguồn cũ: Không có\n%s' % (label, value, extra))


def profile_doc(owner='PROJECT', **over):
    doc = ep.default_profile(owner)
    doc.update(over)
    return doc


def fake_grant(gid='fake-grant-1', callees=('worker',), **over):
    g = {
        'schema_version': 'law.cvf.control/3', 'record_type': 'grant', 'evaluation_basis': 'COOPERATIVE_WORKFLOW',
        'grant_id': gid, 'grant_revision': 1,
        'issuer': {'actor_id': 'fake-user', 'role': 'user'},
        'issuer_ref': {'ref_id': gid, 'kind': 'grant', 'locator': 'PROJECT.md#pham-vi', 'digest': 'sha256:' + '0' * 64,
                       'attribution': {'source_class': 'USER_CONFIRMATION', 'channel': 'USER_MESSAGE', 'evidence_locator': 'host:msg/0007',
                                       'recorded_by': {'actor_id': 'main', 'role': 'main'}}},
        'subject': {'roles': ['main']},
        'scope': {'delegate_callees': [{'role_class': 'core', 'role_name': c} for c in callees], 'task_classes': ['doc-draft'],
                  'operations': ['read', 'create_new'], 'paths': ['working/']},
        'status': 'ACTIVE',
    }
    g.update(over)
    return g


def write_exact_text(path, text):
    """Keep fixture bytes unchanged on Python 3.8 and across newline conventions."""
    with open(str(path), 'w', encoding='utf-8', newline='') as stream:
        return stream.write(text)


def make_project(parent, name='proj', line=LEGACY_VI, label=ep.PROJECT_LABELS[0], profile='default', roles=True, text=None):
    """A minimal project folder. profile: 'default' (owner PROJECT, no grants) | None (absent) | dict | bytes."""
    root = Path(parent) / name
    (root / '.agent').mkdir(parents=True)
    write_exact_text(root / 'PROJECT.md', text if text is not None else project_text(line, label))
    if profile == 'default':
        profile = profile_doc('PROJECT')
    if isinstance(profile, dict):
        (root / PROFILE).write_bytes(ep.serialize(profile))
    elif isinstance(profile, bytes):
        (root / PROFILE).write_bytes(profile)
    if roles:
        for r in ep.CORE_ROLES:
            (root / 'roles' / r).mkdir(parents=True)
            shutil.copyfile(str(ROOT / 'roles' / r / 'config.json'), str(root / 'roles' / r / 'config.json'))
    return root


class Base(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='law-a09-'))
        self.addCleanup(shutil.rmtree, str(self.work), True)
        ep.LANG = 'vi'
        self.addCleanup(setattr, ep, 'LANG', 'vi')

    def project(self, **kw):
        return make_project(self.work, **kw)

    def assertUnchanged(self, root, before):
        self.assertEqual(tree(root), before)


@NEED
class SchemaAndStatus(Base):
    def test_package_schema_and_defaults_validate(self):
        self.assertEqual(ep.schema_problems(), [])
        for owner in ep.OWNERS:
            self.assertEqual(ep.evaluate_doc(profile_doc(owner))[0], 'OK')
        self.assertEqual(ep.clean_profile_bytes(), (ROOT / 'release_templates' / PROFILE).read_bytes().replace(b'\r\n', b'\n'))

    def test_null_requested_fallback_and_limit_fixtures(self):
        doc = profile_doc('PROFILE', host='claude-code')
        doc['roles']['worker'].update(model='claude-sonnet-5-5', effort='high')
        doc['roles']['reviewer'].update(tier='large', effort='xhigh')
        doc['fallback'].update(allowed=True, tier='small')
        doc['requested_limits'].update(max_concurrency=2, max_depth=1)
        self.assertEqual(ep.evaluate_doc(doc)[0], 'OK')
        both = copy.deepcopy(doc)
        both['roles']['worker']['tier'] = 'large'  # model OR tier, never both
        self.assertEqual(ep.evaluate_doc(both)[0], 'INVALID')
        silent = profile_doc('PROFILE')
        silent['fallback']['model'] = 'm'  # a fallback nobody allowed
        self.assertEqual(ep.evaluate_doc(silent)[0], 'INVALID')
        silent['fallback'].update(allowed=True)
        self.assertEqual(ep.evaluate_doc(silent)[0], 'OK')
        for bad in ({'max_concurrency': 0, 'max_depth': None}, {'max_concurrency': None, 'max_depth': 99}, {'max_concurrency': None}):
            d = profile_doc('PROFILE', requested_limits=bad)
            self.assertEqual(ep.evaluate_doc(d)[0], 'INVALID', bad)

    def test_wrong_shapes_future_unknown_role_and_credentials_keep_bytes(self):
        base = profile_doc('PROJECT')
        cases = {}
        d = copy.deepcopy(base); del d['fallback']; cases['missing_field'] = (d, 'INVALID')
        d = copy.deepcopy(base); d['roles']['worker']['effort'] = 'raw10'; cases['bad_effort'] = (d, 'INVALID')
        d = copy.deepcopy(base); d['roles']['boss'] = d['roles']['worker']; cases['unknown_role'] = (d, 'INVALID')
        d = copy.deepcopy(base); d['roles']['worker']['api_key'] = 'x'; cases['credential_field'] = (d, 'INVALID')
        d = copy.deepcopy(base); d['account'] = {'session': 'x'}; cases['account_session'] = (d, 'INVALID')
        d = copy.deepcopy(base); d['observed'] = {'applied': True}; cases['observed_runtime'] = (d, 'INVALID')
        d = copy.deepcopy(base); d['host'] = 'sk-' + 'a1b2c3d4e5f6a7b8c9d0'; cases['secret_value'] = (d, 'INVALID')
        d = copy.deepcopy(base); d['schema_version'] = 'law.execution-profile/2'; cases['future'] = (d, 'UNSUPPORTED')
        d = copy.deepcopy(base); d['schema_version'] = 'something/else'; cases['foreign_version'] = (d, 'UNSUPPORTED')
        d = copy.deepcopy(base); del d['schema_version']; cases['no_version'] = (d, 'INVALID')
        d = copy.deepcopy(base); d['$schema'] = 'http://example.invalid/s.json'; d['$ref'] = 'http://example.invalid/r'; cases['schema_override'] = (d, 'INVALID')
        for name, (doc, want) in cases.items():
            with self.subTest(name):
                root = self.project(name=name, profile=ep.serialize(doc))
                before = tree(root)
                with mock.patch('socket.socket', side_effect=AssertionError('network is not used')):
                    rep = ep.inspect(root)
                self.assertEqual(rep['profile']['status'], want)
                self.assertFalse(rep['authority_usable'])
                self.assertIn(rep['state'], ('INVALID', 'UNSUPPORTED'))
                self.assertUnchanged(root, before)  # reading never normalises, repairs or creates anything
        for name, raw in {'not_json': b'{not json', 'duplicate_keys': b'{"schema_version":"a","schema_version":"b"}', 'nan': b'{"x": NaN}',
                          'not_utf8': b'\xff\xfe\x00', 'array': b'[]'}.items():
            with self.subTest(name):
                root = self.project(name=name, profile=raw)
                before = tree(root)
                self.assertEqual(ep.inspect(root)['profile']['status'], 'INVALID')
                self.assertUnchanged(root, before)

    def test_missing_validator_reports_unchecked_and_refuses_mutation(self):
        root = self.project(profile=profile_doc('PROJECT'))
        before = tree(root)
        with mock.patch.object(ep, '_jsonschema_ok', return_value=None):
            rep = ep.inspect(root)
            self.assertEqual((rep['profile']['status'], rep['state']), ('UNVALIDATED', 'UNVALIDATED'))
            self.assertIn('VALIDATOR_UNAVAILABLE', rep['reasons'])
            self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'REFUSED')
            self.assertEqual(ep.apply_migration(root, [fake_grant()], 'x')['status'], 'REFUSED')
        self.assertUnchanged(root, before)

    def test_roles_report_requested_not_applied_registered_or_permitted(self):
        trial = json.loads((ROOT / 'roles' / 'worker' / 'config.json').read_text(encoding='utf-8'))
        self.assertTrue(trial['implementation_trial'] and trial['host_presets'])  # the LAW trial exists; the only product-side presets are CANDIDATE ones (A-10)
        self.assertTrue(all(p['status'] == 'CANDIDATE' for p in trial['host_presets'].values()))
        root = self.project(profile=profile_doc('PROJECT'), line='[Không có / loại việc]')
        rep = ep.inspect(root)
        self.assertEqual(rep['state'], 'OK')
        for role in ep.CORE_ROLES:
            info = rep['roles'][role]
            self.assertEqual((info['config'], info['applied'], info['registration'], info['permission']),
                             ('NOT_CONFIGURED', 'NOT_INSPECTED', 'NOT_INSPECTED', 'NO_GRANT'))
            self.assertEqual(info['catalog_status'], 'PENDING_R4')
            self.assertFalse(info['product_presets'])  # a candidate is not a qualified product preset ...
            self.assertTrue(info['candidate_presets'])  # ... but it is reported as a candidate
        self.assertNotIn('APPLIED', json.dumps(rep))  # host state is never denied (NOT_APPLIED) nor claimed (APPLIED): it is NOT_INSPECTED
        gone = self.project(name='nofile', profile=None)
        rep = ep.inspect(gone)
        self.assertEqual(rep['state'], 'PROFILE_ABSENT')
        self.assertTrue(all(i['permission'] == 'BLOCKED' and i['config'] == 'UNAVAILABLE' for i in rep['roles'].values()))
        self.assertTrue(rep['migration_required'])  # legacy prose present, no profile yet
        empty = self.project(name='noroles', roles=False)
        self.assertEqual({i['catalog'] for i in ep.inspect(empty)['roles'].values()}, {'MISSING'})

    def test_grant_claim_shows_only_for_profile_owner_with_pointer(self):
        doc = profile_doc('PROFILE', grants=[fake_grant(callees=('worker',))])
        root = self.project(profile=doc, line=ep.POINTERS['vi'])
        rep = ep.inspect(root)
        self.assertEqual(rep['state'], 'OK')
        self.assertFalse(rep['authority_usable'])
        self.assertEqual(rep['roles']['worker']['permission'], 'GRANT_CLAIMED')
        self.assertEqual(rep['roles']['scout']['permission'], 'NO_GRANT')
        self.assertIn('grant_authenticity', rep['unchecked'])
        revoked = profile_doc('PROFILE', grants=[fake_grant(status='REVOKED')])
        rep = ep.inspect(self.project(name='rev', profile=revoked, line=ep.POINTERS['en'], label=ep.PROJECT_LABELS[1]))
        self.assertEqual(rep['roles']['worker']['permission'], 'NO_GRANT')
        self.assertFalse(rep['authority_usable'])
        for name, grant in (('expired', fake_grant(status='EXPIRED')),
                            ('past-expiry', fake_grant(limits={'expires_at': '2020-01-01T00:00:00Z'}))):
            with self.subTest(name):
                expired = profile_doc('PROFILE', grants=[grant])
                report = ep.inspect(self.project(name=name, profile=expired, line=ep.POINTERS['vi']))
                self.assertEqual(report['profile']['status'], 'OK')
                self.assertFalse(report['authority_usable'])
        bad = profile_doc('PROFILE', grants=[fake_grant(schema_version='law.cvf.control/2')])
        self.assertEqual(ep.inspect(self.project(name='v2', profile=bad, line=ep.POINTERS['vi']))['profile']['status'], 'INVALID')

    def test_cli_status_envelope_and_exit_code(self):
        good = self.project(profile=profile_doc('PROFILE'), line=ep.POINTERS['vi'], name='good')
        r = run(ROOT, 'execution_profile.py', 'status', '--project', good, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(result_schema.split_output(r.stdout)[1]['status'], 'success')
        legacy = self.project(name='leg')
        r = run(ROOT, 'execution_profile.py', 'status', '--project', legacy, '--result-json')
        env = result_schema.split_output(r.stdout)[1]
        self.assertEqual((r.returncode, env['status'], env['message']), (1, 'issues', 'LEGACY'))


class Bootstrap(Base):
    def test_clear_lines_bootstrap_and_prose_is_never_parsed(self):
        for value in ('', '[Không có / loại việc, vai được gọi]', 'Không có', 'None.'):
            plan = ep.bootstrap_plan(project_text(value))
            self.assertEqual(plan['state'], 'OK', value)
            self.assertEqual(json.loads(plan['bytes'])['authority_owner'], 'PROJECT')
            self.assertEqual(json.loads(plan['bytes'])['grants'], [])
        plan = ep.bootstrap_plan(project_text(LEGACY_VI))
        self.assertEqual((plan['state'], plan['reasons']), ('LEGACY', ['LEGACY_MIGRATION_REQUIRED']))
        doc = json.loads(plan['bytes'])
        self.assertEqual((doc['authority_owner'], doc['grants']), ('PROJECT', []))
        self.assertNotIn('Reviewer', plan['bytes'].decode('utf-8'))  # no sentence, operation or status was copied out of the prose
        en = ep.bootstrap_plan(project_text(LEGACY_EN, label=ep.PROJECT_LABELS[1]))
        self.assertEqual(en['state'], 'LEGACY')

    def test_missing_ambiguous_and_pointer_lines_write_nothing(self):
        self.assertEqual(ep.bootstrap_plan('# x\n- Tên dự án: A\n')['state'], 'PROJECT_LINE_MISSING')
        twice = project_text(LEGACY_VI, extra='- %s: %s\n' % (ep.PROJECT_LABELS[1], LEGACY_EN))
        self.assertEqual(ep.bootstrap_plan(twice)['state'], 'PROJECT_LINE_AMBIGUOUS')
        same_label = project_text(LEGACY_VI, extra='- %s: [x]\n' % ep.PROJECT_LABELS[0])
        self.assertEqual(ep.bootstrap_plan(same_label)['state'], 'PROJECT_LINE_AMBIGUOUS')
        for text in (project_text(ep.POINTERS['vi']), project_text(ep.POINTERS['en'], label=ep.PROJECT_LABELS[1])):
            plan = ep.bootstrap_plan(text)
            self.assertEqual((plan['bytes'], plan['state']), (None, 'POINTER_PROFILE_MISSING'))

    @NEED
    def test_owner_conflicts_use_neither_source(self):
        cases = {
            'project_owner_but_pointer': (profile_doc('PROJECT'), ep.POINTERS['vi']),
            'profile_owner_but_prose': (profile_doc('PROFILE'), LEGACY_VI),
            'profile_owner_but_placeholder': (profile_doc('PROFILE'), '[Không có]'),
            'project_owner_with_grants': (profile_doc('PROJECT', grants=[fake_grant()]), LEGACY_VI),
        }
        for name, (doc, line) in cases.items():
            with self.subTest(name):
                root = self.project(name=name, profile=doc, line=line)
                before = tree(root)
                rep = ep.inspect(root)
                self.assertEqual(rep['state'], 'OWNER_CONFLICT')
                self.assertFalse(rep['authority_usable'])
                self.assertEqual(rep['grant_claims'], 0)
                self.assertTrue(all(i['permission'] == 'BLOCKED' for i in rep['roles'].values()))
                self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'REFUSED')
                self.assertEqual(ep.plan_migration(root, [fake_grant()])['status'], 'REFUSED')
                self.assertUnchanged(root, before)

    @NEED
    def test_missing_or_ambiguous_project_line_blocks_instead_of_guessing(self):
        for name, text in (('missing', '# x\n- Tên dự án: A\n'), ('twice', project_text(LEGACY_VI, extra='- %s: y\n' % ep.PROJECT_LABELS[1]))):
            root = self.project(name=name, text=text, profile=profile_doc('PROJECT'))
            before = tree(root)
            rep = ep.inspect(root)
            self.assertEqual(rep['state'], 'PROJECT_LINE_MISSING' if name == 'missing' else 'PROJECT_LINE_AMBIGUOUS')
            self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'REFUSED')
            self.assertUnchanged(root, before)

    @NEED
    def test_legacy_state_keeps_prose_unmigrated_and_not_granted(self):
        root = self.project()
        rep = ep.inspect(root)
        self.assertEqual((rep['state'], rep['migration_required']), ('LEGACY', True))
        self.assertFalse(rep['authority_usable'])
        self.assertEqual({i['permission'] for i in rep['roles'].values()}, {'LEGACY_UNMIGRATED'})


@NEED
class ConfigLane(Base):
    def test_edit_choices_only_and_keep_grants_owner_contract_and_main_files(self):
        doc = profile_doc('PROFILE', grants=[fake_grant()])
        root = self.project(profile=doc, line=ep.POINTERS['vi'])
        roles_before = {p: (root / p).read_bytes() for p in ('roles/worker/config.json', 'roles/scout/config.json', 'roles/reviewer/config.json')}
        project_before = (root / 'PROJECT.md').read_bytes()
        choices = {'host': 'claude-code', 'roles': {'worker': {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': 'high'}},
                   'fallback': {'allowed': True, 'model': None, 'tier': 'small', 'effort': None},
                   'requested_limits': {'max_concurrency': 2, 'max_depth': 1}}
        preview = ep.plan_config(root, choices)
        self.assertEqual(preview['status'], 'PREVIEW')
        self.assertEqual(preview['plan']['host_application'], 'NOT_INSPECTED')
        self.assertFalse(preview['plan']['grants_changed'])
        self.assertEqual(json.loads((root / PROFILE).read_bytes())['host'], None)  # a preview writes nothing
        res = ep.apply_config(root, choices, preview['plan']['plan_sha256'])
        self.assertEqual(res['status'], 'WRITTEN', res)
        new = json.loads((root / PROFILE).read_bytes())
        self.assertEqual((new['authority_owner'], new['grants']), ('PROFILE', doc['grants']))
        self.assertEqual((new['host'], new['roles']['worker']['model'], new['roles']['scout']['model']), ('claude-code', 'claude-sonnet-5-5', None))
        self.assertEqual(new['requested_limits'], {'max_concurrency': 2, 'max_depth': 1})
        self.assertEqual({p: (root / p).read_bytes() for p in roles_before}, roles_before)  # a model change never touches agent.md/checks.md/config.json
        self.assertEqual((root / 'PROJECT.md').read_bytes(), project_before)
        self.assertEqual(ep.inspect(root)['state'], 'OK')
        self.assertEqual(ep.apply_config(root, choices)['status'], 'UNCHANGED')  # repeating changes nothing

    def test_grants_owner_version_and_extra_fields_are_refused_before_any_write(self):
        root = self.project(profile=profile_doc('PROJECT'))
        before = tree(root)
        for bad in ({'grants': [fake_grant()]}, {'authority_owner': 'PROFILE'}, {'schema_version': 'law.execution-profile/2'},
                    {'host': 'a', 'allow_delegation': True}, {'$schema': 'http://example.invalid/x'}):
            res = ep.apply_config(root, bad)
            self.assertEqual((res['status'], res['reasons']), ('REFUSED', ['CONFIG_FORBIDDEN_FIELD']), bad)
        self.assertEqual(ep.apply_config(root, {})['reasons'], ['CONFIG_EMPTY'])
        self.assertEqual(ep.apply_config(root, ['host'])['reasons'], ['CONFIG_NOT_OBJECT'])
        for bad in ({'roles': {'boss': {'model': 'm', 'tier': None, 'effort': None}}}, {'roles': {'worker': {'model': 'm', 'tier': 't', 'effort': None}}},
                    {'requested_limits': {'max_concurrency': 0, 'max_depth': None}}, {'host': 'has space'}):
            self.assertEqual(ep.apply_config(root, bad)['reasons'], ['CONFIG_INVALID'], bad)
        self.assertEqual(ep.apply_config(root, {'roles': {'worker': {'model': 'm', 'tier': None, 'effort': None, 'api_key': 'k'}}})['status'], 'REFUSED')
        self.assertIn('CREDENTIAL_VALUE', ep.apply_config(root, {'host': 'sk-' + 'a1b2c3d4e5f6a7b8c9d0'})['reasons'])
        self.assertUnchanged(root, before)

    def test_invalid_future_and_unfinished_states_are_preserved(self):
        raw = ep.serialize(dict(profile_doc('PROJECT'), schema_version='law.execution-profile/9'))
        for name, profile in (('future', raw), ('invalid', b'{"schema_version": "law.execution-profile/1"}'), ('absent', None)):
            root = self.project(name=name, profile=profile)
            before = tree(root)
            res = ep.apply_config(root, {'host': 'claude-code'})
            self.assertEqual((res['status'], res['reasons'][0]), ('REFUSED', 'CONFIG_BLOCKED_STATE'), name)
            self.assertUnchanged(root, before)
        root = self.project(name='pending')
        txdir = root / '.agent' / 'runtime' / 'transactions' / '20260101-000000-abcd1234'
        txdir.mkdir(parents=True)
        (txdir / 'journal.json').write_text(json.dumps({'schema': tx.SCHEMA, 'id': txdir.name, 'status': 'committing', 'ops': []}), encoding='utf-8')
        before = tree(root)
        self.assertEqual(ep.inspect(root)['state'], 'TRANSACTION_UNFINISHED')
        self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'REFUSED')
        (txdir / 'journal.json').write_text('{broken', encoding='utf-8')
        before = tree(root)
        self.assertEqual(ep.inspect(root)['state'], 'TRANSACTION_UNKNOWN')
        self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'REFUSED')
        self.assertUnchanged(root, before)  # an unreadable journal is never deleted to get going

    def test_stale_plan_and_user_edit_between_preview_and_apply(self):
        root = self.project()
        choices = {'host': 'claude-code'}
        plan = ep.plan_config(root, choices)['plan']['plan_sha256']
        data = json.loads((root / PROFILE).read_bytes())
        data['roles']['scout']['effort'] = 'low'  # the user edits the profile after previewing
        (root / PROFILE).write_bytes(ep.serialize(data))
        before = tree(root)
        res = ep.apply_config(root, choices, plan)
        self.assertEqual((res['status'], res['reasons']), ('CONFLICT', ['PLAN_CHANGED']))
        self.assertUnchanged(root, before)

    def test_link_targets_and_runtime_are_refused(self):
        root = self.project()
        real = self.work / 'elsewhere.json'
        real.write_bytes(ep.serialize(profile_doc('PROJECT')))
        (root / PROFILE).unlink()
        try:
            os.symlink(str(real), str(root / PROFILE))
        except (OSError, NotImplementedError):
            self.skipTest('file symlinks unavailable here (WinError 1314 or non-admin); link handling not measured')
        before = real.read_bytes()
        rep = ep.inspect(root)
        self.assertEqual(rep['reasons'][0], 'PROFILE_NOT_REGULAR_FILE')
        self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'REFUSED')
        self.assertEqual(real.read_bytes(), before)


    @unittest.skipUnless(os.name == 'nt', 'junctions are measured on Windows only')
    def test_runtime_junction_blocks_every_write(self):
        root = self.project()
        target = self.work / 'outside-runtime'
        target.mkdir()
        (root / '.agent' / 'runtime').parent.mkdir(exist_ok=True)
        r = subprocess.run(['cmd', '/c', 'mklink', '/J', str(root / '.agent' / 'runtime'), str(target)], capture_output=True, encoding='utf-8', errors='replace')
        if r.returncode != 0:
            self.skipTest('junction could not be created here: ' + r.stdout[-120:])
        before = tree(target), (root / PROFILE).read_bytes()
        self.assertEqual(ep.inspect(root)['state'], 'TRANSACTION_UNKNOWN')  # an unreadable runtime is not "no unfinished work"
        res = ep.apply_config(root, {'host': 'claude-code'})
        self.assertEqual(res['status'], 'REFUSED')
        self.assertEqual((tree(target), (root / PROFILE).read_bytes()), before)  # nothing leaked through the junction, nothing written


@NEED
class MigrationLane(Base):
    def legacy(self, **kw):
        return self.project(**kw)

    def test_full_claim_migrates_with_snapshots_and_second_run_is_refused(self):
        root = self.legacy()
        grants = [fake_grant('fake-grant-1', callees=('worker', 'reviewer')), fake_grant('fake-grant-2', callees=('scout',))]
        files_before = tree(root)
        preview = ep.plan_migration(root, grants)
        self.assertEqual(preview['status'], 'PREVIEW', preview)
        plan = preview['plan']
        self.assertEqual(plan['host_application'], 'NOT_INSPECTED')
        self.assertEqual(plan['evidence'], 'CLAIM_ONLY')
        self.assertEqual((plan['owner_before'], plan['owner_after']), ('PROJECT', 'PROFILE'))
        self.assertEqual(plan['project_line']['before'], LEGACY_VI)
        self.assertEqual(plan['project_line']['after'], ep.POINTERS['vi'])
        self.assertEqual([g['grant_id'] for g in plan['grants']], ['fake-grant-1', 'fake-grant-2'])
        self.assertUnchanged(root, files_before)  # preview writes nothing
        self.assertEqual(ep.apply_migration(root, grants)['reasons'], ['PREVIEW_REQUIRED'])
        res = ep.apply_migration(root, grants, plan['plan_sha256'])
        self.assertEqual(res['status'], 'WRITTEN', res)
        doc = json.loads((root / PROFILE).read_bytes())
        self.assertEqual((doc['authority_owner'], doc['grants']), ('PROFILE', grants))
        self.assertEqual(ep.project_line((root / 'PROJECT.md').read_text(encoding='utf-8'))[0], 'POINTER')
        baks = sorted(p.name for p in root.rglob('*.bak-*'))
        self.assertEqual(len(baks), 2)
        self.assertEqual((root / (PROFILE + '.bak-' + baks[0].rsplit('.bak-', 1)[1])).read_bytes(), files_before[PROFILE])
        self.assertIn(LEGACY_VI.encode('utf-8'), (root / ('PROJECT.md.bak-' + baks[0].rsplit('.bak-', 1)[1])).read_bytes())
        rep = ep.inspect(root)
        self.assertEqual((rep['state'], rep['grant_claims'], rep['roles']['worker']['permission'], rep['roles']['scout']['permission']),
                         ('OK', 2, 'GRANT_CLAIMED', 'GRANT_CLAIMED'))
        self.assertEqual({p: (root / p).read_bytes() for p, b in files_before.items() if b is not None and p.startswith('roles/')},
                         {p: b for p, b in files_before.items() if b is not None and p.startswith('roles/')})  # roles and the rest untouched
        after = tree(root)
        again = ep.apply_migration(root, grants, plan['plan_sha256'])
        self.assertEqual((again['status'], again['reasons'][0]), ('REFUSED', 'MIGRATION_BLOCKED_STATE'))
        self.assertEqual(tree(root), after)

    def test_english_project_migrates_to_the_english_pointer(self):
        root = self.legacy(line=LEGACY_EN, label=ep.PROJECT_LABELS[1])
        plan = ep.plan_migration(root, [fake_grant()])['plan']
        self.assertEqual(plan['project_line']['after'], ep.POINTERS['en'])
        self.assertEqual(ep.apply_migration(root, [fake_grant()], plan['plan_sha256'])['status'], 'WRITTEN')
        text = (root / 'PROJECT.md').read_text(encoding='utf-8')
        self.assertIn('- %s: %s' % (ep.PROJECT_LABELS[1], ep.POINTERS['en']), text)
        self.assertNotIn(LEGACY_EN, text)

    def test_crlf_project_keeps_its_line_endings(self):
        text = project_text(LEGACY_VI).replace('\n', '\r\n')
        root = self.legacy(text=text)
        plan = ep.plan_migration(root, [fake_grant()])['plan']
        self.assertEqual(ep.apply_migration(root, [fake_grant()], plan['plan_sha256'])['status'], 'WRITTEN')
        raw = (root / 'PROJECT.md').read_bytes()
        self.assertEqual(raw.count(b'\r\n'), raw.count(b'\n'))

    def test_refusals_happen_before_any_mutation(self):
        ok = fake_grant()
        user = {'source_class': 'USER_CONFIRMATION', 'channel': 'USER_MESSAGE', 'evidence_locator': 'host:msg/1',
                'recorded_by': {'actor_id': 'main', 'role': 'main'}}

        def with_att(**over):
            g = fake_grant()
            g['issuer_ref']['attribution'] = dict(user, **over)
            return g
        no_evidence = fake_grant()
        del no_evidence['issuer_ref']['attribution']['evidence_locator']
        no_attribution = fake_grant()
        del no_attribution['issuer_ref']['attribution']
        example = fake_grant(example_only=True, status='EXAMPLE_INACTIVE')
        cases = {
            'no_evidence_locator': ([no_evidence], 'GRANT_INVALID'),
            'no_attribution': ([no_attribution], 'GRANT_INVALID'),
            'role_report_source': ([with_att(source_class='ROLE_REPORT', channel='ROLE_OUTPUT', observed_by={'actor_id': 'w', 'role': 'worker'})], 'GRANT_ATTRIBUTION_MISSING'),
            'main_proposal_source': ([with_att(source_class='MAIN_PROPOSAL', channel='MAIN_AUTHORED')], 'GRANT_ATTRIBUTION_MISSING'),
            'unverified_source': ([with_att(source_class='UNVERIFIED', channel='NONE')], 'GRANT_ATTRIBUTION_MISSING'),
            'example_inactive': ([example], 'GRANT_EXAMPLE_OR_INACTIVE'),
            'revoked': ([fake_grant(status='REVOKED')], 'GRANT_EXAMPLE_OR_INACTIVE'),
            'expired_status': ([fake_grant(status='EXPIRED')], 'GRANT_EXAMPLE_OR_INACTIVE'),
            'v2_record': ([fake_grant(schema_version='law.cvf.control/2')], 'GRANT_NOT_V3'),
            'v1_record': ([fake_grant(schema_version='law.cvf.control/1')], 'GRANT_NOT_V3'),
            'no_version': ([{k: v for k, v in ok.items() if k != 'schema_version'}], 'GRANT_NOT_V3'),
            'not_a_grant': ([fake_grant(record_type='task')], 'GRANT_NOT_GRANT_RECORD'),
            'missing_scope': ([{k: v for k, v in ok.items() if k != 'scope'}], 'GRANT_INVALID'),
            'extra_field': ([dict(ok, allow_all=True)], 'GRANT_INVALID'),
            'duplicate_ids': ([ok, copy.deepcopy(ok)], 'GRANT_DUPLICATE_ID'),
            'prose_text': (LEGACY_VI, 'MIGRATION_INPUT_NOT_GRANTS'),
            'prose_items': ([LEGACY_VI], 'MIGRATION_INPUT_NOT_GRANTS'),
            'empty': ([], 'MIGRATION_NO_GRANTS'),
        }
        for name, (grants, code) in cases.items():
            with self.subTest(name):
                root = self.legacy(name=name)
                before = tree(root)
                res = ep.plan_migration(root, grants)
                self.assertEqual(res['status'], 'REFUSED', res)
                self.assertIn(code, res['reasons'])
                res = ep.apply_migration(root, grants, 'x' * 64)
                self.assertEqual(res['status'], 'REFUSED')
                self.assertUnchanged(root, before)  # no journal, no backup, no runtime folder

    def test_wrong_owner_or_line_state_is_refused(self):
        cases = {
            'already_profile_owner': dict(profile=profile_doc('PROFILE'), line=ep.POINTERS['vi']),
            'conflict': dict(profile=profile_doc('PROFILE'), line=LEGACY_VI),
            'absent_profile': dict(profile=None),
            'ambiguous_line': dict(text=project_text(LEGACY_VI, extra='- %s: z\n' % ep.PROJECT_LABELS[1])),
            'missing_line': dict(text='# x\n'),
        }
        for name, kw in cases.items():
            with self.subTest(name):
                root = self.legacy(name=name, **kw)
                before = tree(root)
                res = ep.plan_migration(root, [fake_grant()])
                self.assertEqual((res['status'], res['reasons'][0]), ('REFUSED', 'MIGRATION_BLOCKED_STATE'))
                self.assertUnchanged(root, before)

    def test_clear_placeholder_line_may_receive_explicit_grants(self):
        root = self.legacy(line='[Không có / loại việc, vai được gọi]')
        plan = ep.plan_migration(root, [fake_grant()])
        self.assertEqual(plan['status'], 'PREVIEW')
        self.assertEqual(plan['plan']['project_line']['kind_before'], 'PLACEHOLDER')

    def test_user_edit_between_preview_and_apply_blocks_and_keeps_bytes(self):
        root = self.legacy()
        grants = [fake_grant()]
        plan = ep.plan_migration(root, grants)['plan']['plan_sha256']
        write_exact_text(root / 'PROJECT.md', project_text(LEGACY_VI + ' (đã sửa tay)'))
        before = tree(root)
        res = ep.apply_migration(root, grants, plan)
        self.assertEqual((res['status'], res['reasons']), ('CONFLICT', ['PLAN_CHANGED']))
        self.assertUnchanged(root, before)
        # the plan was recomputed but a hook swaps the file after planning: the transaction's own hash guard refuses, user bytes survive
        plan2 = ep.plan_migration(root, grants)['plan']['plan_sha256']

        def edit(point, info):
            write_exact_text(root / 'PROJECT.md', project_text('sửa lần hai'))
        before_profile = (root / PROFILE).read_bytes()
        with mock.patch.object(ep, '_HOOK', edit):
            res = ep.apply_migration(root, grants, plan2)
        self.assertEqual(res['status'], 'CONFLICT', res)
        self.assertIn('sửa lần hai', (root / 'PROJECT.md').read_text(encoding='utf-8'))
        self.assertEqual((root / PROFILE).read_bytes(), before_profile)
        self.assertFalse(list(root.rglob('*.bak-*')))

    def test_existing_backup_blocks_without_overwriting(self):
        root = self.legacy()
        plan = ep.plan_migration(root, [fake_grant()])['plan']['plan_sha256']
        import datetime
        stamp = datetime.date.today().strftime('%Y%m%d')
        (root / ('PROJECT.md.bak-' + stamp)).write_text('older backup', encoding='utf-8')
        before = tree(root)
        res = ep.apply_migration(root, [fake_grant()], plan)
        self.assertEqual((res['status'], res['reasons']), ('REFUSED', ['BACKUP_EXISTS']))
        self.assertUnchanged(root, before)

    def interrupted(self, root, grants):
        plan = ep.plan_migration(root, grants)['plan']['plan_sha256']
        with mock.patch.dict(os.environ, {tx.FAULT_ENV: 'commit:3'}):  # two backups and the profile land; PROJECT.md does not
            res = ep.apply_migration(root, grants, plan)
        return res

    def test_interrupt_between_the_two_writes_blocks_then_rollback_restores(self):
        root = self.legacy()
        grants = [fake_grant()]
        original = {p: (root / p).read_bytes() for p in (PROFILE, 'PROJECT.md')}
        res = self.interrupted(root, grants)
        self.assertEqual((res['status'], res['reasons']), ('PARTIAL', ['PARTIAL_WRITE']))
        self.assertEqual({f['path']: f['action'] for f in res['files']}, {PROFILE: 'written', 'PROJECT.md': 'not_written'})
        self.assertTrue(res['txid'])
        rep = ep.inspect(root)  # profile says PROFILE, PROJECT.md still holds prose: nothing may be read as authority
        self.assertEqual(rep['state'], 'TRANSACTION_UNFINISHED')
        self.assertFalse(rep['authority_usable'])
        self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'REFUSED')
        out = tx.rollback(root, res['txid'])
        self.assertEqual(out['status'], 'success', out)
        self.assertEqual({p: (root / p).read_bytes() for p in original}, original)
        self.assertEqual(ep.inspect(root)['state'], 'LEGACY')

    def test_user_edit_during_the_commit_is_partial_and_keeps_their_bytes(self):
        root = self.legacy()
        grants = [fake_grant()]
        plan = ep.plan_migration(root, grants)['plan']['plan_sha256']

        def edit_before_project_commit(point, path):  # the transaction's own test hook: fires once the folders are held, before the hash check
            if point == 'commit' and os.path.basename(path) == 'PROJECT.md':
                write_exact_text(Path(path), project_text('người dùng sửa đúng lúc ghi'))
        with mock.patch.object(tx, '_HOOK', edit_before_project_commit):
            res = ep.apply_migration(root, grants, plan)
        self.assertEqual((res['status'], res['reasons'][0]), ('PARTIAL', 'PARTIAL_WRITE'), res)
        self.assertEqual({f['path']: f['action'] for f in res['files']}, {PROFILE: 'written', 'PROJECT.md': 'changed_by_other'})
        self.assertIn('người dùng sửa đúng lúc ghi', (root / 'PROJECT.md').read_text(encoding='utf-8'))
        self.assertTrue(any('rollback' in a for a in res['next_actions']))
        rep = ep.inspect(root)
        self.assertEqual(rep['state'], 'TRANSACTION_UNFINISHED')
        self.assertFalse(rep['authority_usable'])

    def test_interrupt_then_resume_completes_the_group(self):
        root = self.legacy()
        grants = [fake_grant()]
        res = self.interrupted(root, grants)
        out = tx.resume(root, res['txid'])
        self.assertEqual(out['status'], 'success', out)
        rep = ep.inspect(root)
        self.assertEqual((rep['state'], rep['grant_claims']), ('OK', 1))

    def test_interrupt_then_user_edit_conflict_keeps_user_bytes_and_stays_blocked(self):
        root = self.legacy()
        res = self.interrupted(root, [fake_grant()])
        write_exact_text(root / 'PROJECT.md', project_text('người dùng sửa tay sau khi gián đoạn'))
        mine = (root / 'PROJECT.md').read_bytes()
        profile_now = (root / PROFILE).read_bytes()
        out = tx.resume(root, res['txid'])
        self.assertNotEqual(out['status'], 'success')
        self.assertEqual((root / 'PROJECT.md').read_bytes(), mine)  # user bytes survive recovery
        self.assertEqual((root / PROFILE).read_bytes(), profile_now)  # the profile is not reset to get past the block
        self.assertTrue((root / '.agent' / 'runtime' / 'transactions' / res['txid'] / 'journal.json').is_file())  # the journal is not deleted
        self.assertEqual(ep.inspect(root)['state'], 'TRANSACTION_UNFINISHED')

    def test_cli_preview_then_apply_with_plan_hash(self):
        root = self.legacy()
        gfile = self.work / 'grants.json'
        gfile.write_text(json.dumps([fake_grant()]), encoding='utf-8')
        r = run(ROOT, 'execution_profile.py', 'preview-migration', '--project', root, '--grants', gfile, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(result_schema.split_output(r.stdout)[1]['status'], 'preview')
        digest = result_schema.split_output(r.stdout)[1]['outcome']['plan']['plan_sha256']
        r = run(ROOT, 'execution_profile.py', 'apply-migration', '--project', root, '--grants', gfile)
        self.assertEqual(r.returncode, 1)  # --expect-plan is required
        r = run(ROOT, 'execution_profile.py', 'apply-migration', '--project', root, '--grants', gfile, '--expect-plan', digest, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(ep.inspect(root)['state'], 'OK')
        bad = self.work / 'bad.json'
        bad.write_text('{"not": "an array"', encoding='utf-8')
        self.assertEqual(run(ROOT, 'execution_profile.py', 'preview-migration', '--project', root, '--grants', bad).returncode, 1)


@NEED
class SameSnapshot(Base):
    """Corrective: owner/state is validated on the very bytes the plan, hashes, backups and expected-before are built from.

    The interleaving is CONTROLLED, not a kernel race: right after the first read of the profile (the capture) a mutation swaps the files on disk.
    Run twice against the pre-fix helper: the same seam exists there, so the same tests show red on the reread gap and green on the fix.
    """
    GRANTS = [fake_grant('fake-grant-snap')]

    def mutations(self):
        future = ep.serialize(dict(profile_doc('PROJECT'), schema_version='law.execution-profile/2'))
        pointer = project_text(ep.POINTERS['vi'])
        return {
            'owner_profile_and_pointer': lambda r: ((r / PROFILE).write_bytes(ep.serialize(profile_doc('PROFILE', grants=[fake_grant('user-new')]))),
                                                    write_exact_text(r / 'PROJECT.md', pointer)),
            'profile_owner_only': lambda r: (r / PROFILE).write_bytes(ep.serialize(profile_doc('PROFILE', grants=[fake_grant('user-new')]))),
            'profile_future': lambda r: (r / PROFILE).write_bytes(future),
            'profile_broken_json': lambda r: (r / PROFILE).write_bytes(b'{broken'),
            'project_pointer_only': lambda r: write_exact_text(r / 'PROJECT.md', pointer),
            'project_line_edited': lambda r: write_exact_text(r / 'PROJECT.md', project_text(LEGACY_VI + ' (sửa tay)')),
            'project_line_ambiguous': lambda r: write_exact_text(r / 'PROJECT.md', project_text(LEGACY_VI, extra='- %s: z\n' % ep.PROJECT_LABELS[1])),
        }

    def after_capture(self, root, mutate):
        """Patch read_plain: once, right after the profile is first read, run mutate(root)."""
        real, fired = ep.read_plain, []

        def spy(path):
            out = real(path)
            if not fired and os.path.basename(path) == 'EXECUTION_PROFILE.json':
                fired.append(True)
                mutate(root)
            return out
        return mock.patch.object(ep, 'read_plain', spy)

    def test_migration_preview_describes_the_captured_bytes_for_every_change_after_capture(self):
        for name, mutate in self.mutations().items():
            with self.subTest(name):
                root = self.project(name=name)
                profile0, project0 = (root / PROFILE).read_bytes(), (root / 'PROJECT.md').read_bytes()
                with self.after_capture(root, mutate):
                    res = ep.plan_migration(root, self.GRANTS)
                changed = tree(root)
                self.assertNotEqual((changed[PROFILE], changed['PROJECT.md']), (profile0, project0))  # the seam did fire
                if res['status'] == 'PREVIEW':  # honest preview of the OLD snapshot: owner, line, hashes and backups all from the same bytes
                    plan = res['plan']
                    self.assertEqual((plan['owner_before'], plan['project_line']['kind_before']), ('PROJECT', 'LEGACY'))
                    self.assertEqual((plan['profile_before_sha256'], plan['project_before_sha256']), (ep.sha256(profile0), ep.sha256(project0)))
                    self.assertEqual(res['_backups'], (profile0, project0))
                    self.assertEqual(res['_before'], (ep.sha256(profile0), ep.sha256(project0)))
                    self.assertEqual(plan['project_line']['before'], LEGACY_VI)
                    # applying that preview must not overwrite what is on disk now
                    out = ep.apply_migration(root, self.GRANTS, plan['plan_sha256'])
                    self.assertIn(out['status'], ('CONFLICT', 'REFUSED'), out)
                else:
                    self.assertEqual(res['status'], 'REFUSED', res)
                self.assertUnchanged(root, changed)  # neither the preview nor the refused apply touched the user's newer bytes

    def test_apply_migration_refuses_when_files_change_after_capture(self):
        for name, mutate in self.mutations().items():
            with self.subTest(name):
                root = self.project(name=name)
                plan = ep.plan_migration(root, self.GRANTS)['plan']['plan_sha256']
                with self.after_capture(root, mutate):
                    out = ep.apply_migration(root, self.GRANTS, plan)
                self.assertIn(out['status'], ('CONFLICT', 'REFUSED'), out)
                changed = tree(root)
                self.assertFalse(any('.bak-' in p for p in changed), changed.keys())  # no backup for a refused write
                self.assertNotIn('fake-grant-snap', changed[PROFILE].decode('utf-8', 'replace'))  # the migrated grant never landed on the newer bytes
    def test_the_reviewer_probe_owner_changed_after_validation_is_not_previewed_as_owner_project(self):
        root = self.project()
        new = ep.serialize(profile_doc('PROFILE', grants=[fake_grant('user-new')]))
        profile0 = (root / PROFILE).read_bytes()

        def mutate(r):
            (r / PROFILE).write_bytes(new)
            write_exact_text(r / 'PROJECT.md', project_text(ep.POINTERS['vi']))
        with self.after_capture(root, mutate):
            res = ep.plan_migration(root, [fake_grant('migration-input')])
        self.assertEqual(res['status'], 'PREVIEW', res)
        self.assertEqual((res['plan']['owner_before'], res['plan']['profile_before_sha256']), ('PROJECT', ep.sha256(profile0)))  # not the mixed view
        self.assertNotEqual(res['plan']['profile_before_sha256'], ep.sha256(new))
        self.assertEqual(ep.inspect(root)['owner'], 'PROFILE')
        out = ep.apply_migration(root, [fake_grant('migration-input')], res['plan']['plan_sha256'])
        self.assertEqual(out['status'], 'REFUSED', out)  # the live state is no longer migratable; user grants survive
        self.assertEqual((root / PROFILE).read_bytes(), new)

    def test_config_preview_and_apply_use_the_captured_bytes(self):
        choices = {'host': 'claude-code'}
        for name in ('owner_profile_and_pointer', 'profile_owner_only', 'profile_future', 'profile_broken_json'):
            with self.subTest(name):
                root = self.project(name=name)
                profile0 = (root / PROFILE).read_bytes()
                with self.after_capture(root, self.mutations()[name]):
                    res = ep.plan_config(root, choices)
                changed = tree(root)
                self.assertEqual(res['status'], 'PREVIEW', res)
                self.assertEqual(res['plan']['profile_before_sha256'], ep.sha256(profile0))  # not the bytes that arrived after the check
                self.assertEqual(res['_before'], ep.sha256(profile0))
                self.assertEqual(res['plan']['changes'], [{'path': 'host', 'before': None, 'after': 'claude-code'}])
                self.assertEqual(tree(root), changed)  # a preview writes nothing
                out = ep.apply_config(root, choices, res['plan']['plan_sha256'])
                self.assertIn(out['status'], ('CONFLICT', 'REFUSED'), out)
                self.assertUnchanged(root, changed)
        for name in ('owner_profile_and_pointer', 'profile_owner_only', 'profile_future', 'profile_broken_json'):
            with self.subTest('apply_' + name):  # without a preview the capture is still the only truth: the newer bytes survive, grants included
                root = self.project(name='a' + name)
                with self.after_capture(root, self.mutations()[name]):
                    out = ep.apply_config(root, choices)
                changed = tree(root)
                self.assertEqual(out['status'], 'CONFLICT', out)
                self.assertEqual(out['reasons'], ['EXPECTED_BEFORE_MISMATCH'])
                self.assertNotIn('claude-code', changed[PROFILE].decode('utf-8'))  # the config never landed on the newer bytes

    def test_config_reads_project_as_a_precondition_and_never_writes_it(self):
        root = self.project()
        project0 = (root / 'PROJECT.md').read_bytes()
        choices = {'host': 'claude-code'}
        edited = project_text(ep.POINTERS['vi'])  # PROJECT.md changes owner meaning after the capture
        with self.after_capture(root, lambda r: write_exact_text(r / 'PROJECT.md', edited)):
            out = ep.apply_config(root, choices)
        self.assertEqual((out['status'], out['reasons']), ('CONFLICT', ['EXPECTED_BEFORE_MISMATCH']), out)
        self.assertEqual((root / 'PROJECT.md').read_bytes(), edited.encode('utf-8'))  # user bytes kept
        self.assertIsNone(json.loads((root / PROFILE).read_bytes())['host'])  # the profile was not written
        self.assertEqual(ep.plan_config(self.project(name='bound'), choices)['plan']['project_before_sha256'], ep.sha256(project0))  # PROJECT.md is bound in the plan
        root2 = self.project(name='plan_bound')  # an optional expect-plan from the preview also binds PROJECT.md
        digest = ep.plan_config(root2, choices)['plan']['plan_sha256']
        write_exact_text(root2 / 'PROJECT.md', project_text(LEGACY_VI + ' (sửa tay)'))
        before = tree(root2)
        self.assertEqual(ep.apply_config(root2, choices, digest)['reasons'], ['PLAN_CHANGED'])
        self.assertUnchanged(root2, before)

    def test_valid_flows_and_status_leak_nothing_from_the_capture(self):
        root = self.project()
        rep = ep.inspect(root)
        self.assertEqual([k for k in rep if k.startswith('_')], [])  # no private/raw snapshot keys in the status
        self.assertFalse(rep['authority_usable'])
        blob = json.dumps(rep, ensure_ascii=False)
        self.assertNotIn(LEGACY_VI, blob)
        plan = ep.plan_migration(root, self.GRANTS)
        self.assertEqual(ep.apply_migration(root, self.GRANTS, plan['plan']['plan_sha256'])['status'], 'WRITTEN')
        self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'WRITTEN')
        self.assertEqual(json.loads((root / PROFILE).read_bytes())['grants'], self.GRANTS)
        self.assertEqual(ep.inspect(root)['state'], 'OK')


class SourceTree(unittest.TestCase):
    """One copy of the source tree (read-only original) so a live maintainer profile can be planted without touching the repository."""
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-a09-src-')
        cls.src = Path(cls.tmp.name) / 'src'
        shutil.copytree(str(ROOT), str(cls.src), ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__', 'runtime', 'node_modules'))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='law-a09-w-'))
        self.addCleanup(shutil.rmtree, str(self.work), True)

    def new(self, src, name, lang='vi'):
        r = run(src, 'new_project.py', '--name', name, '--dest', self.work, '--lang', lang, '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return self.work / name


class Delivery(SourceTree):
    def test_selection_ownership_and_bytes_without_a_source_profile(self):
        self.assertFalse((ROOT / PROFILE).exists(), 'the repository must not hold a live profile (maintainer profile is out of scope)')
        self.assertIn(PROFILE, cp.delivery_selection())
        self.assertEqual(cp.delivery_bytes(PROFILE), ep.clean_profile_bytes())
        self.assertEqual(cp.PROFILE_REL, ep.PROFILE_REL)  # one constant in two modules (check_package imports lazily so --verify stays standalone)
        self.assertEqual(cp.PROFILE_REL, ep.PROFILE_REL)  # one constant in two modules (check_package imports lazily so --verify stays standalone)
        self.assertFalse(cp.in_manifest(PROFILE))
        self.assertTrue(cp.user_owned(PROFILE))
        self.assertTrue(cp.in_manifest(ep.SCHEMA_REL) and not cp.user_owned(ep.SCHEMA_REL))
        self.assertTrue(cp.in_manifest('tools/execution_profile.py'))
        self.assertEqual(cp.delivery_problems(), [])
        dest = self.work / 'pkg'
        rels = cp.materialize(str(dest))
        self.assertIn(PROFILE, rels)
        manifest = (dest / 'MANIFEST.sha256').read_text(encoding='utf-8')
        self.assertNotIn(PROFILE, manifest)
        self.assertIn(ep.SCHEMA_REL, manifest)
        self.assertIn('tools/execution_profile.py', manifest)
        self.assertEqual((dest / PROFILE).read_bytes(), ep.clean_profile_bytes())

    def test_live_choices_and_grants_in_the_source_never_ship(self):
        src = self.work / 'live-src'
        shutil.copytree(str(self.src), str(src))
        live = profile_doc('PROFILE', host='claude-code', grants=[fake_grant()])
        live['roles']['worker'].update(model='claude-sonnet-5-5', effort='high')
        (src / PROFILE).write_bytes(ep.serialize(live))
        proj = self.new(src, 'LiveSrc')
        self.assertEqual((proj / PROFILE).read_bytes(), ep.clean_profile_bytes())
        self.assertNotIn(b'fake-grant-1', (proj / PROFILE).read_bytes())
        self.assertNotIn('fake-grant-1', (proj / 'MANIFEST.sha256').read_text(encoding='utf-8'))
        self.assertFalse(list(proj.rglob('*.new')))

    def test_template_checks_detect_a_dirty_or_missing_clean_profile(self):
        base = self.work / 'tpl'
        (base / 'release_templates' / '.agent').mkdir(parents=True)
        self.assertEqual(cp.profile_template_problems(str(base)), ['Thiếu mẫu profile sạch %s.' % cp.PROFILE_TEMPLATE])
        (base / cp.PROFILE_TEMPLATE).write_bytes(ep.serialize(profile_doc('PROFILE', host='claude-code')))
        self.assertEqual(len(cp.profile_template_problems(str(base))), 1)
        (base / cp.PROFILE_TEMPLATE).write_bytes(ep.clean_profile_bytes().replace(b'\n', b'\r\n'))
        self.assertEqual(cp.profile_template_problems(str(base)), [])
        tree_root = self.work / 'rel'
        cp.materialize(str(tree_root))
        (tree_root / PROFILE).write_bytes(ep.serialize(profile_doc('PROFILE', host='claude-code')))
        shutil.rmtree(str(tree_root / 'release_templates'), ignore_errors=True)
        with mock.patch.object(cp, 'ROOT', str(tree_root)):
            self.assertTrue(any('profile không sạch' in p for p in cp.tree_problems()))
            (tree_root / PROFILE).unlink()
            self.assertTrue(any('thiếu' in p.lower() and 'EXECUTION_PROFILE' in p for p in cp.tree_problems()))

    def test_new_project_vi_en_ships_clean_profile_pointer_and_idempotent_init(self):
        for lang, label, pointer in (('vi', ep.PROJECT_LABELS[0], ep.POINTERS['vi']), ('en', ep.PROJECT_LABELS[1], ep.POINTERS['en'])):
            proj = self.new(ROOT, 'New-' + lang, lang)
            self.assertEqual((proj / PROFILE).read_bytes(), ep.clean_profile_bytes())
            self.assertEqual(ep.project_line((proj / 'PROJECT.md').read_text(encoding='utf-8'))[:2], ('POINTER', pointer))
            self.assertFalse((proj / 'en' / '.agent' / 'EXECUTION_PROFILE.json').exists())  # one language-neutral profile, no EN copy
            self.assertTrue((proj / ep.SCHEMA_REL).is_file() and (proj / 'tools' / 'execution_profile.py').is_file())
            self.assertNotIn(PROFILE, (proj / 'MANIFEST.sha256').read_text(encoding='utf-8'))
            rep = ep.inspect(proj)
            self.assertEqual(rep['state'], 'OK', rep['reasons'])
            self.assertEqual(run(proj, 'check_package.py', '--verify').returncode, 0)
            # the user chooses something, then init runs again: nothing resets
            self.assertEqual(ep.apply_config(proj, {'host': 'claude-code'})['status'], 'WRITTEN')
            chosen = (proj / PROFILE).read_bytes()
            for _ in range(2):
                r = run(proj, 'init_project.py', '--name', 'Again', '--lang', lang, '--force')
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual((proj / PROFILE).read_bytes(), chosen)

    def test_init_keeps_invalid_and_future_profiles_byte_for_byte(self):
        proj = self.new(ROOT, 'Keep')
        for raw in (b'{"schema_version": "law.execution-profile/1"}', ep.serialize(dict(profile_doc('PROFILE'), schema_version='law.execution-profile/7')), b'\xff\xfe junk'):
            (proj / PROFILE).write_bytes(raw)
            before = {p: (proj / p).read_bytes() for p in ('PROJECT.md', 'MANIFEST.sha256')}
            for _ in range(2):
                r = run(proj, 'init_project.py', '--name', 'Keep', '--force')
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual((proj / PROFILE).read_bytes(), raw)
            self.assertEqual(sorted(p.name for p in (proj / '.agent').glob('EXECUTION_PROFILE*')), ['EXECUTION_PROFILE.json', 'EXECUTION_PROFILE.schema.json'])
            self.assertEqual({p: (proj / p).read_bytes() for p in before}, before)
        # the package check reports a damaged or future profile as a warning (user data, never repaired) and never as "fine"
        (proj / PROFILE).write_bytes(ep.serialize(dict(profile_doc('PROFILE'), schema_version='law.execution-profile/7')))
        r = run(proj, 'check_package.py')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('Profile project (UNSUPPORTED)', r.stdout)
        (proj / PROFILE).write_bytes(ep.clean_profile_bytes())
        self.assertNotIn('Profile project', run(proj, 'check_package.py').stdout)

    def test_init_bootstraps_a_missing_profile_only_from_a_clear_line(self):
        for name, text, state in (('legacy', project_text(LEGACY_VI), 'LEGACY'), ('placeholder', project_text('[Không có / loại việc]'), 'OK'),
                                  ('missing', '# x\n- Tên dự án: [Tên]\n', None),
                                  ('twice', project_text('a', extra='- %s: b\n' % ep.PROJECT_LABELS[1]), None),
                                  ('pointer', project_text(ep.POINTERS['vi']), None)):
            with self.subTest(name):
                proj = self.new(ROOT, 'Boot-' + name)
                (proj / PROFILE).unlink()
                write_exact_text(proj / 'PROJECT.md', text)
                r = run(proj, 'init_project.py', '--name', 'Boot', '--force')
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                if state is None:
                    self.assertFalse((proj / PROFILE).exists(), 'no profile may be written to hide an unclear PROJECT.md')
                else:
                    doc = json.loads((proj / PROFILE).read_bytes())
                    self.assertEqual((doc['authority_owner'], doc['grants']), ('PROJECT', []))
                    rep = ep.inspect(proj)
                    self.assertEqual(rep['state'], state)
                    self.assertFalse(rep['authority_usable'])
                self.assertIn(ep.PROFILE_REL, r.stdout)

    def test_adopt_new_and_existing_projects(self):
        # no PROJECT.md: the template PROJECT.md (pointer) and the clean profile arrive together
        fresh = self.work / 'adopt-fresh'
        fresh.mkdir()
        (fresh / 'notes.txt').write_text('x', encoding='utf-8')
        r = run(ROOT, 'adopt_project.py', '--project', fresh, '--name', 'Fresh', '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((fresh / PROFILE).read_bytes(), ep.clean_profile_bytes())
        self.assertEqual(ep.inspect(fresh)['state'], 'OK')
        # an existing PROJECT.md with a legacy line: bootstrap owner PROJECT, never prose -> grants
        legacy = self.work / 'adopt-legacy'
        legacy.mkdir()
        write_exact_text(legacy / 'PROJECT.md', project_text(LEGACY_VI))
        r = run(ROOT, 'adopt_project.py', '--project', legacy, '--name', 'Legacy', '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rep = ep.inspect(legacy)
        self.assertEqual((rep['state'], rep['migration_required'], rep['owner']), ('LEGACY', True, 'PROJECT'))
        self.assertIn(LEGACY_VI, (legacy / 'PROJECT.md').read_text(encoding='utf-8'))
        # an existing profile, even a damaged one: bytes kept, no .new
        kept = self.work / 'adopt-kept'
        kept.mkdir()
        (kept / '.agent').mkdir()
        (kept / PROFILE).write_bytes(b'{"keep": "me"}')
        r = run(ROOT, 'adopt_project.py', '--project', kept, '--name', 'Kept', '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((kept / PROFILE).read_bytes(), b'{"keep": "me"}')
        self.assertFalse(list(kept.rglob('EXECUTION_PROFILE*.new')))
        # an ambiguous PROJECT.md: nothing is guessed
        amb = self.work / 'adopt-amb'
        amb.mkdir()
        write_exact_text(amb / 'PROJECT.md', project_text('a', extra='- %s: b\n' % ep.PROJECT_LABELS[1]))
        r = run(ROOT, 'adopt_project.py', '--project', amb, '--name', 'Amb', '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((amb / PROFILE).exists())

    def test_upgrade_keeps_existing_profiles_and_bootstraps_missing_one(self):
        pkg = self.work / 'newpkg'
        cp.materialize(str(pkg))
        proj = self.new(pkg, 'Up')
        # a project made before A-09: no profile, legacy prose
        (proj / PROFILE).unlink()
        write_exact_text(proj / 'PROJECT.md', project_text(LEGACY_VI))
        r = run(pkg, 'upgrade_package.py', '--project', proj, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rep = ep.inspect(proj)
        self.assertEqual((rep['state'], rep['owner']), ('LEGACY', 'PROJECT'))
        self.assertIn(PROFILE, r.stdout)
        # existing profile (chosen, then damaged): never overwritten, never reset, repeated runs are stable
        for raw in (ep.serialize(dict(profile_doc('PROJECT'), host='claude-code')), b'{"damaged": true}'):
            (proj / PROFILE).write_bytes(raw)
            for _ in range(2):
                r = run(pkg, 'upgrade_package.py', '--project', proj, '--apply')
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual((proj / PROFILE).read_bytes(), raw)
        self.assertFalse(list(proj.rglob('EXECUTION_PROFILE*.new')))
        # ambiguous line, no profile: not guessed
        (proj / PROFILE).unlink()
        write_exact_text(proj / 'PROJECT.md', project_text('a', extra='- %s: b\n' % ep.PROJECT_LABELS[1]))
        r = run(pkg, 'upgrade_package.py', '--project', proj, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((proj / PROFILE).exists())

    def test_a_missing_scope_line_or_a_missing_profile_says_what_to_do_and_the_two_paths_end_as_briefed(self):
        """M3-C1/F4. Path 1: no scope line (a project made before A-09) -> the user picks the explicit empty line -> preview, then apply the
        upgrade of the NEW package -> a 0-grant profile, PROJECT/STATE untouched. Path 2: the pointer without its profile -> refused at every
        step, no profile invented, the original bytes restore it. Fake data; no grant, no host, no `init --force`."""
        pkg = self.work / 'newpkg'
        cp.materialize(str(pkg))
        choices = self.work / 'choices.json'
        choices.write_text('{"host": "claude-code"}', encoding='utf-8')
        # ---- path 1
        proj = self.new(pkg, 'Miss')
        (proj / PROFILE).unlink()
        label = ep.PROJECT_LABELS[0]
        text = (proj / 'PROJECT.md').read_text(encoding='utf-8')
        kept = [ln for ln in text.split('\n') if not ln.startswith('- %s:' % label)]
        self.assertNotEqual(kept, text.split('\n'))
        write_exact_text(proj / 'PROJECT.md', '\n'.join(kept))
        example = '- %s: Không có' % label
        r = run(pkg, 'execution_profile.py', 'status', '--project', proj, '--result-json')
        human, data = result_schema.split_output(r.stdout)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertEqual(ep.inspect(proj)['state'], 'PROFILE_ABSENT')
        self.assertIn(example, human)  # the exact line to add, when the user chooses it
        self.assertIn('upgrade_package.py', human)
        self.assertTrue(any(example in a for a in data['next_actions']), data['next_actions'])
        r = run(pkg, 'execution_profile.py', 'preview-config', '--project', proj, '--choices', choices, '--result-json')
        human, data = result_schema.split_output(r.stdout)
        self.assertEqual((r.returncode, data['outcome']['status']), (1, 'REFUSED'), r.stdout)
        self.assertTrue(any(example in a for a in data['next_actions']), data['next_actions'])
        before = tree(proj)
        r = run(pkg, 'upgrade_package.py', '--project', proj, '--result-json')  # preview with no line: nothing to create, the steps are named
        human, data = result_schema.split_output(r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn({'path': PROFILE, 'action': 'add'}, data['files'])
        self.assertTrue(any(example in a for a in data['next_actions']), data['next_actions'])
        self.assertEqual(tree(proj), before)
        # the user's explicit choice
        with open(str(proj / 'PROJECT.md'), 'ab') as f:
            f.write(('\n%s\n' % example).encode('utf-8'))
        project_bytes, state_bytes = (proj / 'PROJECT.md').read_bytes(), (proj / '.agent' / 'STATE.md').read_bytes()
        before = tree(proj)
        r = run(pkg, 'upgrade_package.py', '--project', proj, '--result-json')
        human, data = result_schema.split_output(r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn({'path': PROFILE, 'action': 'add'}, data['files'])  # the preview shows the profile it would create
        self.assertEqual(tree(proj), before)
        r = run(pkg, 'upgrade_package.py', '--project', proj, '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rep = ep.inspect(proj)
        self.assertEqual((rep['state'], rep['owner']), ('OK', 'PROJECT'))
        self.assertEqual(json.loads((proj / PROFILE).read_text(encoding='utf-8')).get('grants') or [], [])
        self.assertEqual([rep['roles'][role]['permission'] for role in ep.CORE_ROLES], ['NO_GRANT'] * 3)  # no role is granted by this path
        self.assertEqual(((proj / 'PROJECT.md').read_bytes(), (proj / '.agent' / 'STATE.md').read_bytes()), (project_bytes, state_bytes))
        # ---- path 2
        ptr = self.new(pkg, 'Ptr')
        original = (ptr / PROFILE).read_bytes()
        (ptr / PROFILE).unlink()
        self.assertEqual(ep.inspect(ptr)['state'], 'PROFILE_ABSENT')
        self.assertIn('POINTER_PROFILE_MISSING', ep.inspect(ptr)['reasons'])
        before = tree(ptr)
        for args in (('status',), ('preview-config', '--choices', choices)):
            r = run(pkg, 'execution_profile.py', *args, '--project', ptr, '--result-json')
            human, data = result_schema.split_output(r.stdout)
            self.assertEqual(r.returncode, 1, r.stdout)
            steps = ' '.join(data['next_actions'])
            self.assertIn('bản sao lưu', steps)  # restore the very profile from a backup
            self.assertIn('không dùng init_project.py --force', steps)  # said as a warning, never as a step
            self.assertNotIn(example, steps)  # the "None" line is the reset a pointer project must not self-apply
        r = run(pkg, 'upgrade_package.py', '--project', ptr, '--apply', '--result-json')
        human, data = result_schema.split_output(r.stdout)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((ptr / PROFILE).exists())  # not created on the user's behalf
        self.assertTrue(any('bản sao lưu' in a for a in data['next_actions']), data['next_actions'])
        after = tree(ptr)
        self.assertEqual({k: v for k, v in after.items() if k.startswith(('PROJECT.md', '.agent/STATE.md'))},
                         {k: v for k, v in before.items() if k.startswith(('PROJECT.md', '.agent/STATE.md'))})
        (ptr / PROFILE).write_bytes(original)  # the user's own backup, same bytes
        self.assertEqual(ep.inspect(ptr)['state'], 'OK')

    def test_agents_entrypoint_is_synced_and_points_at_real_files(self):
        vi = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        en = (ROOT / 'en' / 'AGENTS.md').read_text(encoding='utf-8')
        for text in (vi, en):
            self.assertIn('python tools/execution_profile.py status', text)
            self.assertIn('.agent/EXECUTION_PROFILE.json', text)
            self.assertIn('roles/README.md', text)
        self.assertTrue((ROOT / 'tools' / 'execution_profile.py').is_file() and (ROOT / ep.SCHEMA_REL).is_file())
        readme = (ROOT / 'roles' / 'README.md').read_text(encoding='utf-8')
        self.assertIn('execution_profile.py status', readme)


if __name__ == '__main__':
    unittest.main()
