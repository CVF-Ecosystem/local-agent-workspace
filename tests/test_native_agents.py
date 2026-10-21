"""A-10 Scout checks: the thin Claude Code adapter (managed native file + receipt), A-09 host diagnostics, and packaging isolation.

Offline, fake data, temporary folders only. Nothing here starts Claude Code, calls a model, the network, a Worker or CVF, and no profile or native
is created in the repository tree (it is only read). Hooks and patched reads are CONTROLLED interleavings (labelled MOCK), not kernel-race proof.
A real link/junction is created only when the OS allows it; otherwise the test is skipped with the reason.
"""
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
sys.path.insert(0, str(ROOT / 'tests'))
import check_package as cp  # noqa: E402
import result_schema  # noqa: E402
import execution_profile as ep  # noqa: E402
import native_agents as na  # noqa: E402
import transaction as tx  # noqa: E402
from test_execution_profile import (LEGACY_VI, NEED, PROFILE, fake_grant, make_project, profile_doc, project_text, run, tree)  # noqa: E402

NATIVE, RECEIPT = na.NATIVE_REL, na.RECEIPT_REL
MODEL = 'claude-haiku-5-5'


def scout_profile(owner='PROFILE', model=MODEL, host='claude-code', **over):
    doc = profile_doc(owner, host=host)
    doc['roles']['scout'] = {'model': model, 'tier': None, 'effort': None}
    doc.update(over)
    return doc


_DEFAULT = object()


def native_project(parent, name='proj', profile=_DEFAULT, **kw):
    """A project with the real Scout contract/checks copied in and (by default) a valid Scout selection under owner PROFILE + pointer."""
    kw.setdefault('line', ep.POINTERS['vi'])
    root = make_project(parent, name=name, profile=scout_profile() if profile is _DEFAULT else profile, **kw)
    for n in ('agent.md', 'checks.md'):
        shutil.copyfile(str(ROOT / 'roles' / 'scout' / n), str(root / 'roles' / 'scout' / n))
    return root


class Base(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='law-a10-'))
        self.addCleanup(shutil.rmtree, str(self.work), True)
        ep.LANG = 'vi'
        self.addCleanup(setattr, ep, 'LANG', 'vi')

    def project(self, **kw):
        return native_project(self.work, **kw)

    def assertUnchanged(self, root, before):
        self.assertEqual(tree(root), before)

    def install(self, root):
        plan = na.plan(root)
        self.assertEqual(plan['status'], 'PREVIEW', plan)
        res = na.apply(root, plan['plan']['plan_sha256'])
        self.assertEqual(res['status'], 'WRITTEN', res)
        return plan

    def after_capture(self, root, mutate):
        """MOCK: once, right after the adapter's last capture read (its own source), run mutate(root). The capture is already taken."""
        real, fired = ep.read_plain, []

        def spy(path):
            out = real(path)
            if not fired and os.path.basename(path) == 'native_agents.py':
                fired.append(True)
                mutate(root)
            return out
        return mock.patch.object(ep, 'read_plain', spy)


@NEED
class Eligibility(Base):
    def test_unsupported_or_unselected_choices_write_nothing_and_say_why(self):
        base = scout_profile()
        pointer = {'line': ep.POINTERS['vi']}

        def with_(**over):
            d = scout_profile()
            for k, v in over.items():
                if k == 'scout':
                    d['roles']['scout'] = v
                else:
                    d[k] = v
            return d
        sel = lambda **o: dict({'model': MODEL, 'tier': None, 'effort': None}, **o)  # noqa: E731
        cases = {
            'profile_absent': (dict(profile=None), 'PROFILE_ABSENT'),
            'host_null': (dict(profile=with_(host=None)), 'HOST_NOT_SELECTED'),
            'host_other': (dict(profile=with_(host='codex')), 'HOST_UNSUPPORTED'),
            'model_null': (dict(profile=with_(scout=sel(model=None))), 'SCOUT_MODEL_NOT_SELECTED'),
            'alias_haiku': (dict(profile=with_(scout=sel(model='haiku'))), 'MODEL_NOT_FULL_ID'),
            'alias_inherit': (dict(profile=with_(scout=sel(model='inherit'))), 'MODEL_NOT_FULL_ID'),
            'no_version': (dict(profile=with_(scout=sel(model='claude-haiku'))), 'MODEL_NOT_FULL_ID'),
            'yaml_injection': (dict(profile=with_(scout=sel(model='claude-x-1\ntools: Bash'))), 'PROFILE_INVALID'),
            'tier_only': (dict(profile=with_(scout={'model': None, 'tier': 'small', 'effort': None})), 'SCOUT_MODEL_NOT_SELECTED'),
            'effort_set': (dict(profile=with_(scout=sel(effort='high'))), 'SCOUT_CHOICE_UNSUPPORTED'),
            'fallback_on': (dict(profile=with_(fallback={'allowed': True, 'model': None, 'tier': 'small', 'effort': None})), 'FALLBACK_UNSUPPORTED'),
            'limits_set': (dict(profile=with_(requested_limits={'max_concurrency': 2, 'max_depth': None})), 'LIMITS_UNSUPPORTED'),
            'future_profile': (dict(profile=dict(base, schema_version='law.execution-profile/2')), 'PROFILE_UNSUPPORTED_VERSION'),
            'invalid_profile': (dict(profile=b'{"schema_version": "law.execution-profile/1"}'), 'PROFILE_INVALID'),
            'owner_conflict': (dict(profile=scout_profile('PROFILE'), line=LEGACY_VI), 'OWNER_CONFLICT'),
            'contract_missing': (dict(), 'SOURCE_UNREADABLE'),
        }
        self.assertEqual(pointer['line'], ep.POINTERS['vi'])
        for name, (kw, code) in cases.items():
            with self.subTest(name):
                root = self.project(name=name, **kw)
                if name == 'contract_missing':
                    (root / 'roles' / 'scout' / 'agent.md').unlink()
                before = tree(root)
                rep = na.inspect(root)
                self.assertNotIn(rep['state'], ('CURRENT', 'STALE'))
                self.assertIn(code, rep['projection_reasons'] + rep['reasons'])
                plan = na.plan(root)
                self.assertEqual(plan['status'], 'REFUSED', plan)
                self.assertIn(code, plan['reasons'])
                res = na.apply(root, 'x' * 64)
                self.assertIn(res['status'], ('REFUSED',), res)
                self.assertUnchanged(root, before)  # no .claude, no receipt, no runtime folder, no journal
                self.assertFalse((root / '.claude').exists())

    def test_worker_and_reviewer_choices_are_neither_exported_nor_required(self):
        doc = scout_profile()
        doc['roles']['worker'] = {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': 'high'}
        doc['roles']['reviewer'] = {'model': None, 'tier': 'large', 'effort': None}
        root = self.project(profile=doc)
        self.install(root)
        text = (root / NATIVE).read_text(encoding='utf-8')
        self.assertNotIn('claude-sonnet-5-5', text)
        self.assertEqual(sorted(p.name for p in (root / '.claude').rglob('*') if p.is_file()), ['law-scout.md'])

    def test_legacy_owner_project_is_allowed_because_nothing_here_is_authority(self):
        root = self.project(profile=scout_profile('PROJECT'), line=LEGACY_VI)
        self.assertEqual(ep.inspect(root)['state'], 'LEGACY')
        self.install(root)
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['authority_usable']), ('CURRENT', False))
        self.assertEqual(ep.inspect(root)['state'], 'LEGACY')  # the profile and PROJECT.md are untouched and still unmigrated


@NEED
class CreateAndUpdate(Base):
    def test_preview_and_status_change_nothing(self):
        root = self.project()
        before = tree(root)
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['native']['disk'], rep['receipt']['disk']), ('ABSENT', 'ABSENT', 'ABSENT'))
        plan = na.plan(root)
        self.assertEqual(plan['status'], 'PREVIEW')
        self.assertEqual([t['path'] for t in plan['plan']['targets']], [NATIVE, RECEIPT])
        self.assertEqual(plan['plan']['host_application'], 'NOT_INSPECTED')
        self.assertIn('PHIÊN MỚI', plan['plan']['consequence'])
        self.assertUnchanged(root, before)
        self.assertEqual(na.apply(root)['reasons'], ['PREVIEW_REQUIRED'])
        self.assertEqual(na.apply(root, 'f' * 64)['reasons'], ['PLAN_CHANGED'])
        self.assertUnchanged(root, before)

    def test_create_writes_the_exact_native_and_a_valid_receipt_then_is_idempotent(self):
        root = self.project()
        files_before = tree(root)
        plan = self.install(root)
        data = (root / NATIVE).read_bytes()
        text = data.decode('utf-8')
        head, _, rest = text.partition('\n---\n')
        lines = head.split('\n')
        self.assertEqual(lines[0], '---')
        self.assertEqual([l.split(':', 1)[0] for l in lines[1:]], ['name', 'description', 'model', 'tools'])  # nothing else: no Bash/Edit/MCP/permission fields
        self.assertEqual(dict(l.split(': ', 1) for l in lines[1:] if not l.startswith('description'))['tools'], 'Read, Grep, Glob')
        self.assertIn('name: law-scout', lines)
        self.assertIn('model: ' + MODEL, lines)
        self.assertEqual(json.loads(lines[2].split(': ', 1)[1]), na.DESCRIPTIONS['vi'])  # valid single-line YAML scalar
        self.assertTrue(rest.lstrip().startswith('<!-- LAW-MANAGED'))  # the marker sits after the frontmatter: YAML is not broken
        self.assertIn((ROOT / 'roles' / 'scout' / 'agent.md').read_text(encoding='utf-8').strip().split('\n')[0], text)
        for forbidden in ('fake-grant', 'authority_owner', 'grants', 'EXECUTION_PROFILE', 'STATE.md', 'Bash', 'Edit', 'bypassPermissions'):
            self.assertNotIn(forbidden, text, forbidden)
        self.assertNotIn(b'\r', data)
        receipt = json.loads((root / RECEIPT).read_bytes())
        self.assertTrue(na._receipt_ok(receipt))
        self.assertEqual((receipt['native']['sha256'], receipt['confirmation']['plan_sha256']), (ep.sha256(data), plan['plan']['plan_sha256']))
        self.assertEqual(receipt['host_state'], {'disk_projection': 'WRITTEN', 'host_list': 'NOT_INSPECTED', 'invocation': 'NOT_INSPECTED'})
        for secret in ('fake-grant', 'PROJECT.md line', LEGACY_VI):
            self.assertNotIn(secret, json.dumps(receipt))
        after = tree(root)
        changed = {p for p in after if after[p] != files_before.get(p)}
        self.assertTrue({NATIVE, RECEIPT} <= changed)
        self.assertEqual({p for p in changed if not (p.startswith('.claude') or p.startswith('.agent/runtime'))}, set())  # nothing else moved
        for protected in (PROFILE, 'PROJECT.md', 'roles/scout/agent.md', 'roles/scout/config.json', 'roles/worker/config.json'):
            self.assertEqual(after[protected], files_before[protected], protected)  # profile, PROJECT.md and role files never change
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['receipt']['valid'], rep['reasons'], rep['receipt_inputs_changed']), ('CURRENT', True, [], []))
        self.assertEqual((rep['host_list_observation'], rep['invocation'], rep['model_observed'], rep['path_restriction']), ('NOT_INSPECTED', 'NOT_INSPECTED', 'NOT_INSPECTED', 'NONE'))
        again = tree(root)
        self.assertEqual(na.plan(root)['status'], 'UNCHANGED')
        self.assertEqual(na.apply(root, plan['plan']['plan_sha256'])['status'], 'UNCHANGED')
        self.assertEqual(tree(root), again)

    def test_english_package_gets_the_english_description(self):
        root = self.project()
        (root / '.agent' / 'PACKAGE_INFO.json').write_text(json.dumps({'language': 'en'}), encoding='utf-8')
        self.install(root)
        self.assertIn(json.dumps(na.DESCRIPTIONS['en']), (root / NATIVE).read_text(encoding='utf-8'))

    def test_update_follows_changes_in_contract_checks_and_model_even_with_the_same_adapter_version(self):
        root = self.project()
        self.install(root)
        for name, change in (('contract', lambda r: (r / 'roles/scout/agent.md').write_text('# Scout\nđã sửa hợp đồng\n', encoding='utf-8')),
                             ('checks', lambda r: (r / 'roles/scout/checks.md').write_text('# Kiểm\nđã sửa\n', encoding='utf-8')),
                             ('model', lambda r: (r / PROFILE).write_bytes(ep.serialize(scout_profile(model='claude-sonnet-5-5'))))):
            with self.subTest(name):
                change(root)
                self.assertEqual(na.inspect(root)['state'], 'STALE')
                plan = na.plan(root)
                self.assertEqual((plan['status'], plan['plan']['action']), ('PREVIEW', 'update'))
                self.assertEqual(plan['plan']['targets'][0]['before_sha256'], ep.sha256((root / NATIVE).read_bytes()))
                res = na.apply(root, plan['plan']['plan_sha256'])
                self.assertEqual(res['status'], 'WRITTEN', res)
                self.assertEqual(na.inspect(root)['state'], 'CURRENT')
        self.assertIn('model: claude-sonnet-5-5', (root / NATIVE).read_text(encoding='utf-8'))
        self.assertIn('đã sửa', (root / NATIVE).read_text(encoding='utf-8'))

    def test_unrelated_profile_edit_requires_a_fresh_confirmation_even_when_native_bytes_match(self):
        root = self.project()
        self.install(root)
        self.assertEqual(ep.apply_config(root, {'roles': {'worker': {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': None}}})['status'], 'WRITTEN')
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['receipt_inputs_changed']), ('STALE', ['profile']))
        native_before = (root / NATIVE).read_bytes()
        receipt_before = (root / RECEIPT).read_bytes()
        preview = na.plan(root)
        self.assertEqual((preview['status'], preview['plan']['action']), ('PREVIEW', 'update'))
        res = na.apply(root, preview['plan']['plan_sha256'])
        self.assertEqual(res['status'], 'WRITTEN')
        self.assertEqual(res['files'], [{'path': RECEIPT, 'action': 'written'}])
        self.assertEqual((root / NATIVE).read_bytes(), native_before)
        self.assertNotEqual((root / RECEIPT).read_bytes(), receipt_before)
        self.assertEqual(na.inspect(root)['receipt_inputs_changed'], [])
        self.assertEqual(na.inspect(root)['state'], 'CURRENT')

    def test_config_bytes_changed_without_version_change_require_fresh_confirmation(self):
        root = self.project()
        self.install(root)
        native_before = (root / NATIVE).read_bytes()
        cfg = root / 'roles/scout/config.json'
        cfg.write_bytes(cfg.read_bytes() + b'\n')
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['receipt_inputs_changed']), ('STALE', ['config']))
        self.install(root)
        self.assertEqual((root / NATIVE).read_bytes(), native_before)
        self.assertEqual(na.inspect(root)['receipt_inputs_changed'], [])


@NEED
class OwnershipAndCollisions(Base):
    def test_a_same_name_native_without_a_receipt_is_the_users_even_with_identical_bytes_or_our_marker(self):
        template = self.project(name='tpl')
        self.install(template)
        ours = (template / NATIVE).read_bytes()
        for name, content in (('theirs', b'---\nname: law-scout\ndescription: mine\n---\nmy own prompt\n'), ('identical_bytes', ours),
                              ('marker_only', b'---\nname: law-scout\n---\n<!-- LAW-MANAGED native-agent claude-code/law-scout -->\nhi\n')):
            with self.subTest(name):
                root = self.project(name=name)
                (root / '.claude' / 'agents').mkdir(parents=True)
                (root / NATIVE).write_bytes(content)
                before = tree(root)
                self.assertEqual(na.inspect(root)['state'], 'FOREIGN')
                plan = na.plan(root)
                self.assertEqual((plan['status'], plan['reasons']), ('REFUSED', ['NATIVE_FOREIGN']))
                self.assertEqual(na.apply(root, 'a' * 64)['status'], 'REFUSED')
                self.assertUnchanged(root, before)  # the user's file keeps its bytes; no receipt is created to legitimise it

    def test_missing_or_invalid_receipt_never_auto_adopts(self):
        base = self.project(name='base')
        self.install(base)
        good = (base / RECEIPT).read_bytes()
        broken = {'garbage': b'{not json', 'empty_object': b'{}', 'wrong_host': good.replace(b'"claude-code"', b'"codex"', 1),
                  'bad_sha': good.replace(json.loads(good)['native']['sha256'].encode(), b'zz'), 'extra_key': good.replace(b'"schema"', b'"x": 1, "schema"', 1)}
        for name, raw in broken.items():
            with self.subTest(name):
                root = self.project(name='r-' + name)
                self.install(root)
                (root / RECEIPT).write_bytes(raw)
                before = tree(root)
                self.assertEqual(na.inspect(root)['state'], 'RECEIPT_INVALID')
                plan = na.plan(root)
                self.assertEqual(plan['status'], 'REFUSED', plan)
                self.assertEqual(na.apply(root, 'b' * 64)['status'], 'REFUSED')
                self.assertUnchanged(root, before)
        root = self.project(name='r-missing')  # native present, receipt deleted
        self.install(root)
        (root / RECEIPT).unlink()
        before = tree(root)
        self.assertEqual(na.inspect(root)['state'], 'FOREIGN')
        self.assertEqual(na.plan(root)['reasons'], ['NATIVE_FOREIGN'])
        self.assertUnchanged(root, before)

    def test_user_edit_after_install_is_kept_and_a_deleted_native_is_only_reported(self):
        root = self.project()
        self.install(root)
        (root / NATIVE).write_text('---\nname: law-scout\n---\nmy edit\n', encoding='utf-8', newline='')
        before = tree(root)
        self.assertEqual(na.inspect(root)['state'], 'MODIFIED')
        self.assertEqual(na.plan(root)['reasons'], ['NATIVE_MODIFIED'])
        self.assertEqual(na.apply(root, 'c' * 64)['status'], 'REFUSED')
        self.assertUnchanged(root, before)
        (root / NATIVE).unlink()
        before = tree(root)
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['reasons']), ('NATIVE_MISSING', ['NATIVE_MISSING']))
        self.assertEqual(na.plan(root)['reasons'], ['NATIVE_MISSING'])
        self.assertUnchanged(root, before)  # not recreated, the receipt is not deleted

    def test_other_user_files_under_claude_are_never_touched(self):
        root = self.project()
        (root / '.claude' / 'agents').mkdir(parents=True)
        (root / '.claude' / 'agents' / 'mine.md').write_bytes(b'---\nname: mine\n---\nkeep\n')
        (root / '.claude' / 'settings.json').write_bytes(b'{"keep": true}')
        mine = {p: (root / p).read_bytes() for p in ('.claude/agents/mine.md', '.claude/settings.json')}
        self.install(root)
        self.assertEqual({p: (root / p).read_bytes() for p in mine}, mine)


@NEED
class DriftAndInterleavings(Base):
    def test_any_input_changed_between_preview_and_apply_is_stale_and_writes_nothing(self):
        mutations = {
            'profile': lambda r: (r / PROFILE).write_bytes(ep.serialize(scout_profile(model='claude-sonnet-5-5'))),
            'profile_same_meaning_new_bytes': lambda r: (r / PROFILE).write_bytes((r / PROFILE).read_bytes().replace(b'\n', b'\r\n')),
            'project': lambda r: (r / 'PROJECT.md').write_text(project_text(ep.POINTERS['vi']) + '\nextra\n', encoding='utf-8', newline=''),
            'contract': lambda r: (r / 'roles/scout/agent.md').write_text('# changed\n', encoding='utf-8'),
            'checks': lambda r: (r / 'roles/scout/checks.md').write_text('# changed\n', encoding='utf-8'),
            'package_language': lambda r: (r / na.INFO_REL).write_text('{\"language\": \"en\"}', encoding='utf-8'),
            'config_same_status': lambda r: (r / 'roles/scout/config.json').write_text((r / 'roles/scout/config.json').read_text(encoding='utf-8') + '\n', encoding='utf-8'),
            'native_appears': lambda r: ((r / '.claude' / 'agents').mkdir(parents=True), (r / NATIVE).write_bytes(b'mine')),
            'receipt_appears': lambda r: ((r / RECEIPT).parent.mkdir(parents=True), (r / RECEIPT).write_bytes(b'{}')),
        }
        for name, mutate in mutations.items():
            with self.subTest(name):
                root = self.project(name=name)
                token = na.plan(root)['plan']['plan_sha256']
                mutate(root)
                before = tree(root)
                res = na.apply(root, token)
                self.assertIn(res['status'], ('CONFLICT', 'REFUSED'), res)
                self.assertUnchanged(root, before)
                if name not in ('native_appears', 'receipt_appears'):
                    self.assertEqual(res['reasons'], ['PLAN_CHANGED'])
                self.assertFalse(any('.bak' in p for p in before))

    def test_update_drift_native_or_receipt_changed_after_preview(self):
        for name in ('native', 'receipt'):
            with self.subTest(name):
                root = self.project(name=name)
                self.install(root)
                (root / 'roles/scout/agent.md').write_text('# new contract\n', encoding='utf-8')
                token = na.plan(root)['plan']['plan_sha256']
                target = root / (NATIVE if name == 'native' else RECEIPT)
                target.write_bytes(target.read_bytes() + b' ')
                before = tree(root)
                res = na.apply(root, token)
                self.assertIn(res['status'], ('CONFLICT', 'REFUSED'), res)
                self.assertUnchanged(root, before)

    def test_inputs_changed_after_the_capture_inside_apply_are_refused_before_any_write(self):
        """MOCK interleaving: the files change right after the capture the plan was built from."""
        mutations = {
            'package_language': lambda r: (r / na.INFO_REL).write_text('{\"language\": \"en\"}', encoding='utf-8'),
            'contract': lambda r: (r / 'roles/scout/agent.md').write_text('# changed after capture\n', encoding='utf-8'),
            'profile': lambda r: (r / PROFILE).write_bytes(ep.serialize(scout_profile(model='claude-sonnet-5-5'))),
            'project': lambda r: (r / 'PROJECT.md').write_text(project_text(LEGACY_VI), encoding='utf-8', newline=''),
        }
        for name, mutate in mutations.items():
            with self.subTest(name):
                root = self.project(name=name)
                token = na.plan(root)['plan']['plan_sha256']
                with self.after_capture(root, mutate):
                    res = na.apply(root, token)
                self.assertEqual((res['status'], res['reasons']), ('CONFLICT', ['EXPECTED_BEFORE_MISMATCH']), res)
                self.assertFalse((root / '.claude').exists())
                self.assertFalse((root / '.agent' / 'runtime').exists())

    def test_native_created_by_the_user_at_the_write_point_is_not_overwritten(self):
        """MOCK: the transaction's own planned-but-not-written hook; create requires the target absent at commit time too."""
        root = self.project()
        token = na.plan(root)['plan']['plan_sha256']

        def user_creates(point, info):
            (root / '.claude' / 'agents').mkdir(parents=True, exist_ok=True)
            (root / NATIVE).write_bytes(b'user wrote this first')
        with mock.patch.object(ep, '_HOOK', user_creates):
            res = na.apply(root, token)
        self.assertNotEqual(res['status'], 'WRITTEN', res)
        self.assertEqual((root / NATIVE).read_bytes(), b'user wrote this first')
        self.assertFalse((root / RECEIPT).exists())

    def test_user_edit_of_the_native_at_the_write_point_during_update_is_kept(self):
        root = self.project()
        self.install(root)
        (root / 'roles/scout/agent.md').write_text('# new contract\n', encoding='utf-8')
        token = na.plan(root)['plan']['plan_sha256']
        mine = b'---\nname: law-scout\n---\nedited at the worst moment\n'
        with mock.patch.object(ep, '_HOOK', lambda point, info: (root / NATIVE).write_bytes(mine)):
            res = na.apply(root, token)
        self.assertNotEqual(res['status'], 'WRITTEN', res)
        self.assertEqual((root / NATIVE).read_bytes(), mine)

    def interrupted(self, root):
        token = na.plan(root)['plan']['plan_sha256']
        with mock.patch.dict(os.environ, {tx.FAULT_ENV: 'commit:1'}):  # the native lands, the receipt does not
            return na.apply(root, token)

    def test_interrupt_between_native_and_receipt_is_detected_and_owner_rollback_restores(self):
        root = self.project()
        res = self.interrupted(root)
        self.assertEqual((res['status'], res['reasons']), ('PARTIAL', ['PARTIAL_WRITE']))
        self.assertEqual({f['path']: f['action'] for f in res['files']}, {NATIVE: 'written', RECEIPT: 'not_written'})
        self.assertTrue(any('rollback' in a for a in res['next_actions']))
        rep = na.inspect(root)
        self.assertEqual(rep['state'], 'INTERRUPTED_OR_UNKNOWN')  # not "foreign": a transaction is open
        self.assertIn('TRANSACTION_UNFINISHED', rep['reasons'])
        before = tree(root)
        self.assertEqual(na.plan(root)['status'], 'REFUSED')
        self.assertEqual(na.apply(root, 'd' * 64)['status'], 'REFUSED')
        self.assertUnchanged(root, before)  # the receipt is not written or deleted to legitimise anything; the journal stays
        out = tx.rollback(root, res['txid'])
        self.assertEqual(out['status'], 'success', out)
        self.assertFalse((root / NATIVE).exists())
        self.assertEqual(na.inspect(root)['state'], 'ABSENT')
        self.install(root)
        self.assertEqual(na.inspect(root)['state'], 'CURRENT')

    def test_interrupt_then_owner_resume_completes_the_pair(self):
        root = self.project()
        res = self.interrupted(root)
        out = tx.resume(root, res['txid'])
        self.assertEqual(out['status'], 'success', out)
        self.assertEqual(na.inspect(root)['state'], 'CURRENT')

    def test_interrupt_then_user_edit_keeps_user_bytes_and_stays_blocked(self):
        root = self.project()
        res = self.interrupted(root)
        (root / RECEIPT).parent.mkdir(parents=True, exist_ok=True)
        (root / RECEIPT).write_bytes(b'the user put this here after the interruption')
        mine = (root / RECEIPT).read_bytes()
        native_now = (root / NATIVE).read_bytes()
        out = tx.resume(root, res['txid'])
        self.assertNotEqual(out['status'], 'success')
        self.assertEqual((root / RECEIPT).read_bytes(), mine)  # user bytes survive recovery; the receipt is not forged to legitimise the native
        self.assertEqual((root / NATIVE).read_bytes(), native_now)
        self.assertEqual(na.inspect(root)['state'], 'INTERRUPTED_OR_UNKNOWN')

    def test_native_edited_after_the_interruption_is_kept_and_then_reads_as_modified(self):
        root = self.project()
        res = self.interrupted(root)
        (root / NATIVE).write_bytes(b'edited after the interruption')
        out = tx.resume(root, res['txid'])  # only the receipt was pending, so recovery completes it
        self.assertEqual(out['status'], 'success', out)
        self.assertEqual((root / NATIVE).read_bytes(), b'edited after the interruption')
        self.assertEqual(na.inspect(root)['state'], 'MODIFIED')  # the receipt describes the written bytes, the file differs: the user's version, never overwritten

    def test_an_unreadable_journal_is_unknown_not_clean(self):
        root = self.project()
        txdir = root / '.agent' / 'runtime' / 'transactions' / '20260101-000000-abcd1234'
        txdir.mkdir(parents=True)
        (txdir / 'journal.json').write_text('{broken', encoding='utf-8')
        before = tree(root)
        rep = na.inspect(root)
        self.assertEqual((rep['state'], 'TRANSACTION_UNKNOWN' in rep['reasons']), ('INTERRUPTED_OR_UNKNOWN', True))
        self.assertEqual(na.apply(root, 'e' * 64)['status'], 'REFUSED')
        self.assertUnchanged(root, before)


def make_junction(link, target):
    """A directory link the OS allows without elevation: a junction on Windows, a symlink elsewhere. Returns False when it cannot be made."""
    try:
        if os.name == 'nt':
            r = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(target)], capture_output=True, timeout=60)
            return r.returncode == 0 and os.path.exists(str(link))
        os.symlink(str(target), str(link), target_is_directory=True)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


@NEED
class LinksAndUnverifiable(Base):
    def test_a_claude_folder_that_is_a_link_is_refused_and_its_target_is_untouched(self):
        root = self.project()
        outside = self.work / 'outside'
        outside.mkdir()
        (outside / 'sentinel.txt').write_text('keep', encoding='utf-8')
        if not make_junction(root / '.claude', outside):
            self.skipTest('this OS/account cannot create a directory link here')
        before, outside_before = tree(root), tree(outside)
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['reasons']), ('UNSAFE_PATH', ['PATH_UNSAFE']))
        self.assertEqual(na.plan(root)['status'], 'REFUSED')
        self.assertEqual(na.apply(root, 'f' * 64)['status'], 'REFUSED')
        self.assertEqual(tree(outside), outside_before)
        self.assertEqual(tree(root), before)

    def test_a_linked_source_folder_is_refused(self):
        root = self.project()
        outside = self.work / 'outside-roles'
        outside.mkdir()
        shutil.copyfile(str(ROOT / 'roles' / 'scout' / 'agent.md'), str(outside / 'agent.md'))
        shutil.copyfile(str(ROOT / 'roles' / 'scout' / 'checks.md'), str(outside / 'checks.md'))
        shutil.copyfile(str(ROOT / 'roles' / 'scout' / 'config.json'), str(outside / 'config.json'))
        shutil.rmtree(str(root / 'roles' / 'scout'))
        if not make_junction(root / 'roles' / 'scout', outside):
            self.skipTest('this OS/account cannot create a directory link here')
        before = tree(root)
        plan = na.plan(root)
        self.assertEqual(plan['status'], 'REFUSED')
        self.assertIn('PATH_UNSAFE', plan['reasons'])
        self.assertEqual(tree(root), before)
        self.assertFalse((root / '.claude').exists())

    def test_a_native_that_is_a_folder_or_a_runtime_that_is_linked_is_refused(self):
        root = self.project(name='folder')
        (root / '.claude' / 'agents' / 'law-scout.md').mkdir(parents=True)
        before = tree(root)
        self.assertEqual(na.inspect(root)['state'], 'UNSAFE_PATH')
        self.assertEqual(na.plan(root)['status'], 'REFUSED')
        self.assertEqual(tree(root), before)
        root = self.project(name='runtime')
        (root / '.agent' / 'runtime').mkdir()
        outside = self.work / 'rt-outside'
        outside.mkdir()
        shutil.rmtree(str(root / '.agent' / 'runtime'))
        if not make_junction(root / '.agent' / 'runtime', outside):
            self.skipTest('this OS/account cannot create a directory link here')
        self.assertEqual(na.inspect(root)['state'], 'INTERRUPTED_OR_UNKNOWN')  # the journal folder cannot be read safely: unknown, never clean
        self.assertEqual(na.plan(root)['status'], 'REFUSED')
        res = na.apply(root, 'a' * 64)
        self.assertEqual(res['status'], 'REFUSED', res)
        self.assertFalse((root / '.claude').exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_unverifiable_reads_fail_closed(self):
        """MOCK: the OS reports an unreadable native / unreadable contract. The adapter must neither guess nor write."""
        root = self.project()
        before = tree(root)
        real = ep.read_plain

        def native_unreadable(path):
            return (None, 'UNREADABLE') if path.endswith('law-scout.md') else real(path)

        def contract_unreadable(path):
            return (None, 'UNREADABLE') if path.endswith('agent.md') else real(path)
        with mock.patch.object(ep, 'read_plain', native_unreadable):
            self.assertEqual(na.inspect(root)['state'], 'UNSAFE_PATH')
            self.assertEqual(na.plan(root)['status'], 'REFUSED')
        with mock.patch.object(ep, 'read_plain', contract_unreadable):
            plan = na.plan(root)
            self.assertEqual((plan['status'], 'SOURCE_UNREADABLE' in plan['reasons']), ('REFUSED', True))
        self.assertUnchanged(root, before)


@NEED
class HostDiagnosticsAreNotDenied(Base):
    def test_a09_status_says_not_inspected_instead_of_denying_host_state(self):
        root = self.project()
        rep = ep.inspect(root)
        self.assertEqual(rep['host_application'], 'NOT_INSPECTED')
        for role in ep.CORE_ROLES:
            self.assertEqual((rep['roles'][role]['applied'], rep['roles'][role]['registration']), ('NOT_INSPECTED', 'NOT_INSPECTED'))
        blob = json.dumps(rep)
        self.assertNotIn('NOT_APPLIED', blob)
        self.assertNotIn('NOT_REGISTERED', blob)
        self.assertFalse(rep['authority_usable'])
        self.install(root)  # even with a native on disk the A-09 helper does not look at hosts or natives: it never imports the adapter
        rep2 = ep.inspect(root)
        self.assertEqual(rep2['roles']['scout']['registration'], 'NOT_INSPECTED')
        self.assertEqual(rep2, rep)
        self.assertNotIn('native_agents', (ROOT / 'tools' / 'execution_profile.py').read_text(encoding='utf-8'))
        self.assertEqual(ep.reason_text('PROFILE_ABSENT'), ep.REASONS['PROFILE_ABSENT'][0])

    def test_write_results_are_still_real_values_not_unknown(self):
        root = self.project()
        res = ep.apply_config(root, {'roles': {'worker': {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': None}}})
        self.assertEqual(res['status'], 'WRITTEN')  # whether files were written is measured, never NOT_INSPECTED
        self.assertEqual(res['plan']['host_application'], 'NOT_INSPECTED')  # whether any host applied the choice is the unmeasured part
        self.assertEqual(ep.apply_config(root, {'host': 'claude-code'})['status'], 'UNCHANGED')

    def test_cli_status_preview_apply_and_exit_codes(self):
        root = self.project()
        r = run(ROOT, 'native_agents.py', 'status', '--project', root)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn('ABSENT', r.stdout)
        r = run(ROOT, 'native_agents.py', 'preview', '--project', root, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        digest = result_schema.split_output(r.stdout)[1]['outcome']['plan']['plan_sha256']
        self.assertFalse((root / '.claude').exists())
        self.assertEqual(run(ROOT, 'native_agents.py', 'apply', '--project', root).returncode, 1)  # --expect-plan is required
        r = run(ROOT, 'native_agents.py', 'apply', '--project', root, '--expect-plan', digest, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        r = run(ROOT, 'native_agents.py', 'status', '--project', root)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('CURRENT', r.stdout)
        self.assertIn('NOT_INSPECTED', r.stdout)
        self.assertEqual(run(ROOT, 'native_agents.py').returncode, 2)


@NEED
class ReviewRegressions(Base):
    def test_receipt_only_refresh_failure_before_write_reports_no_native_write(self):
        """MOCK write refusal before Transaction.run writes anything; the same-byte native is still guarded by add."""
        root = self.project()
        self.install(root)
        cfg = root / 'roles/scout/config.json'
        cfg.write_bytes(cfg.read_bytes() + b'\n')
        preview = na.plan(root)
        before = tree(root)
        with mock.patch.object(tx.Transaction, 'run', side_effect=OSError('simulated refusal before any write')):
            res = na.apply(root, preview['plan']['plan_sha256'])
        self.assertEqual((res['status'], res['reasons']), ('REFUSED', ['WRITE_REFUSED']), res)
        self.assertEqual(res.get('files', []), [])
        self.assertEqual(tree(root), before)

    def test_matching_receipt_without_the_literal_marker_is_never_adopted(self):
        root = self.project()
        self.install(root)
        mine = b'---\nname: law-scout\n---\nUser prompt without the managed marker\n'
        (root / NATIVE).write_bytes(mine)
        receipt = json.loads((root / RECEIPT).read_bytes())
        receipt['native']['sha256'] = ep.sha256(mine)
        (root / RECEIPT).write_bytes(ep.serialize(receipt))
        before = tree(root)
        self.assertEqual(na.inspect(root)['state'], 'MODIFIED')
        self.assertEqual(na.plan(root)['status'], 'REFUSED')
        self.assertEqual(tree(root), before)

    def test_duplicate_name_in_another_project_file_is_refused(self):
        for name in ('law-scout', '"law-scout"', "'law-scout'"):
            with self.subTest(name):
                root = self.project(name=str(len(list(self.work.iterdir()))))
                other = root / '.claude/agents/custom.md'
                other.parent.mkdir(parents=True)
                other.write_text('---\nname: ' + name + '\ndescription: user\n---\nuser prompt\n', encoding='utf-8')
                before = tree(root)
                self.assertEqual(na.plan(root)['reasons'], ['NATIVE_NAME_COLLISION'])
                self.assertEqual(na.apply(root, 'a' * 64)['status'], 'REFUSED')
                self.assertEqual(tree(root), before)

    def test_uninterpretable_agent_names_are_unsupported(self):
        for header in ('name: >\n  law-scout', 'name: &alias law-scout', 'name: first\nname: second', 'description: missing-name'):
            with self.subTest(header):
                root = self.project(name=str(len(list(self.work.iterdir()))))
                other = root / '.claude/agents/custom.md'
                other.parent.mkdir(parents=True)
                other.write_text('---\n' + header + '\n---\nuser prompt\n', encoding='utf-8')
                before = tree(root)
                self.assertEqual(na.plan(root)['reasons'], ['NATIVE_DEFINITION_UNSUPPORTED'])
                self.assertEqual(tree(root), before)

    def test_inventory_changes_after_preview_and_after_capture_are_refused(self):
        for point in ('preview', 'capture'):
            with self.subTest(point):
                root = self.project(name=point)
                token = na.plan(root)['plan']['plan_sha256']
                def mutate(r):
                    other = r / '.claude/agents/custom.md'
                    other.parent.mkdir(parents=True)
                    other.write_text('---\nname: custom\n---\nuser\n', encoding='utf-8')
                if point == 'preview':
                    mutate(root)
                    out = na.apply(root, token)
                else:
                    with self.after_capture(root, mutate):
                        out = na.apply(root, token)
                self.assertEqual(out['status'], 'CONFLICT', out)
                self.assertFalse((root / NATIVE).exists())
                self.assertFalse((root / RECEIPT).exists())

    def test_linked_profile_parent_is_rejected_before_reading_the_profile(self):
        root = self.project()
        outside = self.work / 'outside-agent'
        shutil.move(str(root / '.agent'), str(outside))
        if not make_junction(root / '.agent', outside):
            self.skipTest('cannot create directory link')
        real = ep.read_plain
        reads = []
        def spy(path):
            if str(path).endswith('EXECUTION_PROFILE.json'):
                reads.append(path)
            return real(path)
        with mock.patch.object(ep, 'read_plain', spy):
            self.assertEqual(na.plan(root)['status'], 'REFUSED')
        self.assertEqual(reads, [])


ROLES = na.ROLES
TOOLS = {'scout': 'Read, Grep, Glob', 'worker': 'Read, Grep, Glob, Write', 'reviewer': 'Read, Grep, Glob'}
FORBIDDEN_IN_NATIVE = ('fake-grant', 'authority_owner', 'grants', 'EXECUTION_PROFILE', 'STATE.md', 'Bash', 'Edit', 'bypassPermissions', 'mcp__', 'WebFetch', 'WebSearch')
MAINTAINER_ONLY = ('sửa ngay lỗi nhỏ', 'directly fix', 'quyền bảo trì', 'kho nguồn LAW', 'LAW source reviews', 'Khi thử thi công LAW', 'chọn model/effort Worker', 'effort reviewer')


def roles_project(parent, name='proj', models=None, **kw):
    """A project with all three real role contracts and a profile (owner PROFILE + pointer) that selects a full model ID per role."""
    models = {'scout': 'claude-haiku-5-5', 'worker': 'claude-sonnet-5-5', 'reviewer': 'claude-sonnet-5-5'} if models is None else models
    doc = profile_doc('PROFILE', host='claude-code')
    for r in ROLES:
        doc['roles'][r] = {'model': models.get(r), 'tier': None, 'effort': None}
    kw.setdefault('line', ep.POINTERS['vi'])
    root = make_project(parent, name=name, profile=doc, **kw)
    for r in ROLES:
        for n in ('agent.md', 'checks.md'):
            shutil.copyfile(str(ROOT / 'roles' / r / n), str(root / 'roles' / r / n))
    return root


class RolesBase(Base):
    def project(self, **kw):
        return roles_project(self.work, **kw)

    def install(self, root, role='scout'):
        plan = na.plan(root, role)
        self.assertEqual(plan['status'], 'PREVIEW', plan)
        res = na.apply(root, plan['plan']['plan_sha256'], role)
        self.assertEqual(res['status'], 'WRITTEN', res)
        return plan


@NEED
class ThreeRoles(RolesBase):
    def test_each_role_gets_its_fixed_native_with_exact_name_tools_model_and_contract(self):
        for role in ROLES:
            with self.subTest(role):
                root = self.project(name=role)
                before = tree(root)
                self.install(root, role)
                data = (root / na.native_rel(role)).read_bytes()
                text = data.decode('utf-8')
                head, _, rest = text.partition('\n---\n')
                lines = head.split('\n')
                self.assertEqual([l.split(':', 1)[0] for l in lines[1:]], ['name', 'description', 'model', 'tools'])
                self.assertIn('name: law-' + role, lines)
                self.assertIn('model: ' + {'scout': 'claude-haiku-5-5'}.get(role, 'claude-sonnet-5-5'), lines)
                self.assertIn('tools: ' + TOOLS[role], lines)
                self.assertEqual(json.loads(lines[2].split(': ', 1)[1]), na.DESCRIPTIONS_BY_ROLE[role]['vi'])
                self.assertTrue(rest.lstrip().startswith('<!-- LAW-MANAGED native-agent claude-code/law-' + role))
                contract = (ROOT / 'roles' / role / 'agent.md').read_text(encoding='utf-8').replace('\r\n', '\n').strip('\n')
                checks = (ROOT / 'roles' / role / 'checks.md').read_text(encoding='utf-8').replace('\r\n', '\n').strip('\n')
                self.assertIn(contract, text)  # the role's own contract and checks, verbatim
                self.assertIn(checks, text)
                for forbidden in FORBIDDEN_IN_NATIVE:
                    self.assertNotIn(forbidden, text, forbidden)
                if role != 'worker':
                    self.assertNotIn('Write', text)
                self.assertNotIn(b'\r', data)
                receipt = json.loads((root / na.receipt_rel(role)).read_bytes())
                self.assertTrue(na._receipt_ok(receipt, role))
                self.assertEqual((receipt['role'], receipt['requested']['tools'], receipt['adapter']), (role, TOOLS[role].split(', '), na.ADAPTER))
                self.assertEqual({r for r in ROLES if na._receipt_ok(receipt, r)}, {role})  # a receipt is bound to its own role
                after = tree(root)
                changed = {p for p in after if after[p] != before.get(p)}
                self.assertTrue({na.native_rel(role), na.receipt_rel(role)} <= changed)
                self.assertEqual({p for p in changed if not (p.startswith('.claude') or p.startswith('.agent/runtime'))}, set())
                for other in ROLES:
                    if other != role:
                        self.assertFalse((root / na.native_rel(other)).exists())
                for protected in (PROFILE, 'PROJECT.md'):
                    self.assertEqual(after[protected], before[protected])

    def test_roles_are_independent_and_do_not_make_each_other_stale(self):
        root = self.project()
        self.install(root, 'scout')
        first = (root / na.native_rel('scout')).read_bytes()
        self.install(root, 'worker')
        self.install(root, 'reviewer')
        for role in ROLES:
            self.assertEqual(na.inspect(root, role)['state'], 'CURRENT', role)
            self.assertEqual(na.plan(root, role)['status'], 'UNCHANGED')
        self.assertEqual((root / na.native_rel('scout')).read_bytes(), first)
        (root / 'roles' / 'worker' / 'agent.md').write_text('# Worker\nđã sửa\n', encoding='utf-8')  # one role's source changes
        self.assertEqual({r: na.inspect(root, r)['state'] for r in ROLES}, {'scout': 'CURRENT', 'worker': 'STALE', 'reviewer': 'CURRENT'})

    def test_default_role_stays_scout_for_every_call(self):
        root = self.project()
        self.assertEqual(na.inspect(root)['role'], 'scout')
        self.install(root)
        self.assertTrue((root / na.NATIVE_REL).is_file() and na.NATIVE_REL == na.native_rel('scout') and na.RECEIPT_REL == na.receipt_rel('scout'))

    def test_worker_native_says_write_is_cooperative_not_enforced(self):
        root = self.project()
        plan = na.plan(root, 'worker')
        self.assertIn('cưỡng chế', plan['plan']['write_tool'])
        self.assertEqual(plan['plan']['requested']['tools'], ['Read', 'Grep', 'Glob', 'Write'])
        self.assertNotIn('write_tool', na.plan(root, 'scout')['plan'])
        self.install(root, 'worker')
        text = (root / na.native_rel('worker')).read_text(encoding='utf-8')
        for needle in ('CANDIDATE', 'đã tồn tại', 'Write không tự ngăn ghi đè', 'nghĩa vụ hợp tác', 'không phải điều máy chủ cưỡng chế', 'trả lại Main'):
            self.assertIn(needle, text, needle)
        for claim in ('sandbox', 'được bảo vệ', 'enforced by the host'):
            self.assertNotIn(claim, text)
        en = self.work / 'en'
        en.mkdir()
        root_en = roles_project(en)
        (root_en / '.agent' / 'PACKAGE_INFO.json').write_text(json.dumps({'language': 'en'}), encoding='utf-8')
        self.install(root_en, 'worker')
        text = (root_en / na.native_rel('worker')).read_text(encoding='utf-8')
        for needle in ('does not prevent overwriting', 'cooperative duty', 'not something the host enforces', 'already exists'):
            self.assertIn(needle, text, needle)

    def test_the_product_reviewer_carries_no_maintainer_fix_permission(self):
        for rel in ('roles/reviewer/agent.md', 'roles/reviewer/checks.md'):
            text = (ROOT / rel).read_text(encoding='utf-8')
            for needle in MAINTAINER_ONLY:
                self.assertNotIn(needle, text, rel + ': ' + needle)
        agent = (ROOT / 'roles/reviewer/agent.md').read_text(encoding='utf-8')
        self.assertIn('không tự sửa', agent)  # the product constraints stay
        self.assertIn('không cấp hoặc mở rộng grant', agent)
        root = self.project()
        self.install(root, 'reviewer')
        native = (root / na.native_rel('reviewer')).read_text(encoding='utf-8')
        for needle in MAINTAINER_ONLY:
            self.assertNotIn(needle, native, needle)
        self.assertIn('Không sửa artifact', native)
        self.assertIn('verdict của bạn không cấp quyền', native)

    def test_unselected_or_unsupported_worker_and_reviewer_choices_write_nothing(self):
        cases = {
            'worker_model_null': ({'worker': None}, 'worker', 'WORKER_MODEL_NOT_SELECTED'),
            'reviewer_model_null': ({'reviewer': None}, 'reviewer', 'REVIEWER_MODEL_NOT_SELECTED'),
            'worker_alias': ({'worker': 'sonnet'}, 'worker', 'MODEL_NOT_FULL_ID'),
            'reviewer_inherit': ({'reviewer': 'inherit'}, 'reviewer', 'MODEL_NOT_FULL_ID'),
        }
        for name, (models, role, code) in cases.items():
            with self.subTest(name):
                root = self.project(name=name, models=dict({'scout': 'claude-haiku-5-5'}, **models))
                before = tree(root)
                rep = na.inspect(root, role)
                self.assertNotIn(rep['state'], ('CURRENT', 'STALE'))
                self.assertIn(code, rep['projection_reasons'])
                plan = na.plan(root, role)
                self.assertEqual((plan['status'], code in plan['reasons']), ('REFUSED', True), plan)
                self.assertEqual(na.apply(root, 'x' * 64, role)['status'], 'REFUSED')
                self.assertUnchanged(root, before)
                self.assertFalse((root / '.claude').exists())
                self.assertEqual(na.plan(root, 'scout')['status'], 'PREVIEW')  # the other roles are independent
        for role in ('worker', 'reviewer'):
            with self.subTest('effort_' + role):
                doc = profile_doc('PROFILE', host='claude-code')
                doc['roles'][role] = {'model': 'claude-sonnet-5-5', 'tier': None, 'effort': 'high'}
                root = roles_project(self.work, name='effort-' + role)
                (root / PROFILE).write_bytes(ep.serialize(doc))
                before = tree(root)
                plan = na.plan(root, role)
                self.assertEqual(plan['status'], 'REFUSED')
                self.assertIn(role.upper() + '_CHOICE_UNSUPPORTED', plan['reasons'])
                self.assertUnchanged(root, before)

    def test_factory_candidates_are_shown_but_never_fill_the_profile_or_register(self):
        expected = {'scout': 'claude-haiku-5-5', 'worker': 'claude-sonnet-5-5', 'reviewer': 'claude-sonnet-5-5'}
        trial = {'scout': ('claude-haiku-5-5', 'medium'), 'worker': ('claude-sonnet-5-5', 'high'), 'reviewer': ('claude-opus-5-5', 'high')}
        for role, model in expected.items():
            cfg = json.loads((ROOT / 'roles' / role / 'config.json').read_text(encoding='utf-8'))
            preset = cfg['host_presets']['claude-code']
            self.assertEqual((set(cfg['host_presets']), preset['status'], preset['model'], preset['tier'], preset['effort'], preset['quality_status']),
                             ({'claude-code'}, 'CANDIDATE', model, None, None, 'NOT_EVALUATED_ON_LAW_PRODUCT'), role)
            self.assertEqual(cfg['status'], 'PENDING_R4')
            self.assertIn('Not applied', preset['note'])
            self.assertEqual(preset['observed'] is None, role != 'scout')  # only the Scout read was observed; nothing for Worker/Reviewer
            self.assertEqual((cfg['implementation_trial']['revision'], cfg['implementation_trial']['quality_status'],
                              cfg['implementation_trial']['claude']['default']), (2, 'NOT_EVALUATED_ON_LAW', {'model': trial[role][0], 'effort': trial[role][1]}))
        root = self.project(models={'scout': 'claude-haiku-5-5'})  # Worker and Reviewer: nothing chosen
        before = tree(root)
        rep = na.inspect(root, 'worker')
        self.assertEqual((rep['candidate_preset'], rep['requested']), ({'status': 'CANDIDATE', 'model': 'claude-sonnet-5-5'}, None))
        self.assertIn('CHƯA áp dụng', na.format_status(rep))
        self.assertEqual(na.plan(root, 'worker')['status'], 'REFUSED')
        self.assertEqual(na.apply(root, 'a' * 64, 'worker')['status'], 'REFUSED')
        self.assertUnchanged(root, before)  # the profile was not filled in, nothing registered, nothing granted
        prof = ep.inspect(root)
        for role in ('worker', 'reviewer'):
            info = prof['roles'][role]
            self.assertEqual((info['config'], info['permission'], info['product_presets'], info['candidate_presets']), ('NOT_CONFIGURED', 'NO_GRANT', False, True))
        self.assertFalse(prof['authority_usable'])
        # an explicit choice always wins over the candidate, and a malformed preset block is simply not shown
        root2 = self.project(name='override', models={'scout': 'claude-haiku-5-5', 'reviewer': 'claude-opus-5-5'})
        self.install(root2, 'reviewer')
        self.assertIn('model: claude-opus-5-5', (root2 / na.native_rel('reviewer')).read_text(encoding='utf-8'))
        (root2 / 'roles' / 'worker' / 'config.json').write_text(json.dumps({'role': 'worker', 'status': 'PENDING_R4', 'host_presets': []}), encoding='utf-8')
        self.assertIsNone(na.inspect(root2, 'worker')['candidate_preset'])
        self.assertFalse(ep.inspect(root2)['roles']['worker']['product_presets'])

    def test_a_valid_scout_receipt_of_the_older_adapter_stays_managed_and_only_goes_stale(self):
        root = self.project()
        self.install(root, 'scout')
        native = (root / na.NATIVE_REL).read_bytes()
        receipt = json.loads((root / na.RECEIPT_REL).read_bytes())
        receipt['adapter'] = na.LEGACY_ADAPTERS['scout'][0]
        receipt['inputs']['adapter'] = 'f' * 64  # what the older adapter's bytes hashed to
        (root / na.RECEIPT_REL).write_bytes(ep.serialize(receipt))
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['receipt']['valid'], rep['receipt_inputs_changed']), ('STALE', True, ['adapter']))
        plan = na.plan(root)
        self.assertEqual((plan['status'], plan['plan']['action']), ('PREVIEW', 'update'))
        self.assertEqual(plan['plan']['targets'][0]['before_sha256'], ep.sha256(native))
        res = na.apply(root, plan['plan']['plan_sha256'])
        self.assertEqual(res['status'], 'WRITTEN', res)
        self.assertEqual(json.loads((root / na.RECEIPT_REL).read_bytes())['adapter'], na.ADAPTER)
        self.assertEqual(na.inspect(root)['state'], 'CURRENT')
        # the older id is accepted for Scout only; for Worker it is a damaged receipt and the file stays the user's
        self.install(root, 'worker')
        w = json.loads((root / na.receipt_rel('worker')).read_bytes())
        w['adapter'] = na.LEGACY_ADAPTERS['scout'][0]
        (root / na.receipt_rel('worker')).write_bytes(ep.serialize(w))
        before = tree(root)
        self.assertEqual(na.inspect(root, 'worker')['state'], 'RECEIPT_INVALID')
        self.assertEqual(na.plan(root, 'worker')['status'], 'REFUSED')
        self.assertUnchanged(root, before)

    def test_cli_role_flag_and_default(self):
        root = self.project()
        r = run(ROOT, 'native_agents.py', 'preview', '--role', 'worker', '--project', root, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        plan = result_schema.split_output(r.stdout)[1]['outcome']['plan']
        self.assertEqual((plan['role'], plan['requested']['tools']), ('worker', ['Read', 'Grep', 'Glob', 'Write']))
        self.assertFalse((root / '.claude').exists())
        r = run(ROOT, 'native_agents.py', 'apply', '--role', 'worker', '--project', root, '--expect-plan', plan['plan_sha256'])
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(run(ROOT, 'native_agents.py', 'status', '--role', 'worker', '--project', root).returncode, 0)
        r = run(ROOT, 'native_agents.py', 'status', '--project', root)  # default role: Scout, not written
        self.assertEqual(r.returncode, 1)
        self.assertIn('Scout', r.stdout)
        self.assertIn('ABSENT', r.stdout)
        self.assertEqual(run(ROOT, 'native_agents.py', 'status', '--role', 'owner', '--project', root).returncode, 2)


def pair(role):
    return na.native_rel(role), na.receipt_rel(role), na.retired_rel(role)


@NEED
@unittest.skipUnless(os.name == 'nt', 'retire is measured on Windows only; elsewhere it refuses (see test_unsupported_os_...)')
class Retire(RolesBase):
    """Retire = one no-replace os.rename of the managed native into a fixed slot. Hooks and patched calls are CONTROLLED interleavings (MOCK), not kernel-race proof."""

    def installed(self, **kw):
        root = self.project(**kw)
        self.install(root)
        return root

    def retire(self, root, role='scout'):
        plan = na.plan_retire(root, role)
        self.assertEqual(plan['status'], 'PREVIEW', plan)
        return na.retire(root, plan['plan']['plan_sha256'], role)

    def set_hook(self, point, fn):
        def hook(p, info):
            if p == point:
                fn(info)
        real, ep._HOOK = ep._HOOK, hook
        self.addCleanup(setattr, ep, '_HOOK', real)

    def test_preview_and_status_are_read_only_and_say_what_would_move(self):
        root = self.installed()
        before = tree(root)
        plan = na.plan_retire(root)
        self.assertEqual(plan['status'], 'PREVIEW')
        p, native, receipt, retired = plan['plan'], *pair('scout')
        self.assertEqual((p['move']['from'], p['move']['to'], p['housekeeping'], p['host_application']), (native, retired, [], 'NOT_INSPECTED'))
        self.assertEqual((p['receipt']['path'], p['receipt']['change']), (receipt, 'none (kept as provenance)'))
        self.assertEqual(p['bound']['retired_slot'], 'ABSENT')
        self.assertEqual(p['bound']['profile_sha256'], ep.sha256((root / PROFILE).read_bytes()))
        self.assertEqual(p['bound']['project_sha256'], ep.sha256((root / 'PROJECT.md').read_bytes()))
        self.assertIn(retired, p['restore'])
        self.assertIn('PHIÊN MỚI', p['consequence'])
        self.assertEqual(na.inspect(root)['state'], 'CURRENT')
        self.assertUnchanged(root, before)  # no folder, no probe
        empty = self.project(name='empty')
        before = tree(empty)
        res = na.plan_retire(empty)
        self.assertEqual((res['status'], res['reasons']), ('REFUSED', ['NOTHING_TO_RETIRE']))
        self.assertEqual(na.retire(empty, 'a' * 64)['status'], 'REFUSED')
        self.assertUnchanged(empty, before)
        self.assertFalse((empty / '.claude').exists() or (empty / '.agent' / 'runtime').exists())

    def test_retire_moves_exactly_the_native_keeps_the_receipt_and_never_resurrects(self):
        root = self.installed()
        self.install(root, 'worker')
        native, receipt, retired = pair('scout')
        before = tree(root)
        native_bytes, receipt_bytes = (root / native).read_bytes(), (root / receipt).read_bytes()
        res = self.retire(root)
        self.assertEqual((res['status'], res['reasons']), ('RETIRED', []), res)
        self.assertEqual(res['observed'], {'active': 'ABSENT', 'retired_slot': ep.sha256(native_bytes)})
        self.assertIsInstance(res['dir_pins'], bool)
        after = tree(root)
        self.assertNotIn(native, after)
        self.assertEqual(after[retired], native_bytes)  # the very bytes, moved not copied
        self.assertEqual(after[receipt], receipt_bytes)  # provenance kept
        self.assertEqual({p for p in set(before) | set(after) if before.get(p) != after.get(p)}, {native, retired})  # nothing else changed, no folder made
        self.assertEqual(na.inspect(root, 'worker')['state'], 'CURRENT')  # another role is untouched
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['reasons'], rep['retired']['disk'], rep['receipt']['valid']), ('RETIRED', ['NATIVE_RETIRED'], 'PRESENT', True))
        self.assertEqual(rep['host_list_observation'], 'NOT_INSPECTED')
        again = tree(root)
        self.assertEqual(na.plan_retire(root)['status'], 'UNCHANGED')
        self.assertEqual(na.retire(root, 'a' * 64)['status'], 'UNCHANGED')
        plan = na.plan(root)  # a normal apply must say it is retired and must not recreate the file
        self.assertEqual((plan['status'], plan['reasons']), ('REFUSED', ['NATIVE_RETIRED']))
        self.assertEqual(na.apply(root, 'b' * 64)['status'], 'REFUSED')
        self.assertIn('.retired.md', na.reason_text('NATIVE_RETIRED'))
        self.assertEqual(tree(root), again)
        self.assertFalse((root / native).exists())

    def test_retire_needs_the_preview_token(self):
        root = self.installed()
        before = tree(root)
        self.assertEqual(na.retire(root)['reasons'], ['PREVIEW_REQUIRED'])
        res = na.retire(root, 'c' * 64)
        self.assertEqual((res['status'], res['reasons']), ('CONFLICT', ['PLAN_CHANGED']))
        self.assertUnchanged(root, before)

    def test_retire_does_not_depend_on_projection_eligibility_and_binds_the_raw_profile(self):
        def model_unset(r):
            d = ep.parse_json_bytes((r / PROFILE).read_bytes())
            d['roles']['scout']['model'] = None
            (r / PROFILE).write_bytes(ep.serialize(d))

        def host_changed(r):
            d = ep.parse_json_bytes((r / PROFILE).read_bytes())
            d['host'] = 'codex'
            (r / PROFILE).write_bytes(ep.serialize(d))
        mutations = {
            'model_unset': (model_unset, True),
            'host_changed': (host_changed, True),
            'parse_invalid': (lambda r: (r / PROFILE).write_bytes(b'{broken'), True),
            'future_version': (lambda r: (r / PROFILE).write_bytes(ep.serialize(dict(ep.parse_json_bytes((r / PROFILE).read_bytes()), schema_version='law.execution-profile/2'))), True),
            'profile_absent': (lambda r: (r / PROFILE).unlink(), False),
            'project_absent': (lambda r: (r / 'PROJECT.md').unlink(), True),
        }
        for name, (mutate, profile_present) in mutations.items():
            with self.subTest(name):
                root = self.installed(name=name)
                mutate(root)
                self.assertNotIn(na.inspect(root)['state'], ('CURRENT', 'RETIRED'))  # projection is no longer possible (or stale)
                plan = na.plan_retire(root)
                self.assertEqual(plan['status'], 'PREVIEW', plan)
                bound = plan['plan']['bound']
                want = lambda rel: ep.sha256((root / rel).read_bytes()) if (root / rel).is_file() else 'ABSENT'  # noqa: E731
                self.assertEqual((bound['profile_sha256'], bound['project_sha256']), (want(PROFILE), want('PROJECT.md')))
                self.assertEqual(profile_present, bound['profile_sha256'] != 'ABSENT')
                native_bytes = (root / na.NATIVE_REL).read_bytes()
                res = na.retire(root, plan['plan']['plan_sha256'])
                self.assertEqual(res['status'], 'RETIRED', res)
                self.assertEqual((root / na.retired_rel('scout')).read_bytes(), native_bytes)

    def test_an_unreadable_or_linked_profile_or_project_fails_closed(self):
        for rel in (PROFILE, 'PROJECT.md'):
            with self.subTest(rel):
                root = self.installed(name=rel.replace('/', '_'))
                (root / rel).unlink()
                (root / rel).mkdir()  # no longer a plain file: cannot be bound
                before = tree(root)
                plan = na.plan_retire(root)
                self.assertEqual((plan['status'], plan['reasons']), ('REFUSED', ['PATH_UNSAFE']))
                self.assertEqual(na.retire(root, 'd' * 64)['status'], 'REFUSED')
                self.assertUnchanged(root, before)
                self.assertTrue((root / na.NATIVE_REL).is_file())

    def test_anything_not_managed_is_refused_and_every_byte_is_kept(self):
        native, receipt, retired = pair('scout')

        def foreign(r):
            (r / receipt).unlink()

        def edited(r):
            (r / native).write_bytes((r / native).read_bytes() + b'\nuser line\n')

        def bad_receipt(r):
            (r / receipt).write_bytes(b'{"receipt":')

        def native_gone(r):
            (r / native).unlink()

        def marker_stripped(r):
            data = (r / native).read_bytes().replace(na.marker('scout').encode('utf-8'), b'')
            (r / native).write_bytes(data)
            rec = json.loads((r / receipt).read_bytes())
            rec['native']['sha256'] = ep.sha256(data)  # even a receipt that matches does not make a marker-less file ours
            (r / receipt).write_bytes(ep.serialize(rec))
        cases = {'foreign': (foreign, 'NATIVE_FOREIGN'), 'edited': (edited, 'NATIVE_MODIFIED'), 'bad_receipt': (bad_receipt, 'RECEIPT_INVALID'),
                 'native_gone': (native_gone, 'NATIVE_MISSING'), 'marker_stripped': (marker_stripped, 'NATIVE_MODIFIED')}
        for name, (mutate, code) in cases.items():
            with self.subTest(name):
                root = self.installed(name=name)
                mutate(root)
                before = tree(root)
                plan = na.plan_retire(root)
                self.assertEqual(plan['status'], 'REFUSED', plan)
                self.assertIn(code, plan['reasons'])
                self.assertEqual(na.retire(root, 'e' * 64)['status'], 'REFUSED')
                self.assertUnchanged(root, before)
                self.assertFalse((root / retired).exists())

    def test_an_occupied_or_inconsistent_retired_slot_is_a_conflict_nothing_is_chosen(self):
        native, receipt, retired = pair('scout')
        root = self.installed(name='both')
        (root / retired).write_bytes(b'someone else')
        before = tree(root)
        plan = na.plan_retire(root)
        self.assertEqual((plan['status'], plan['reasons']), ('REFUSED', ['RETIRE_SLOT_CONFLICT']))
        self.assertEqual(na.inspect(root)['state'], 'RETIRE_CONFLICT')
        self.assertEqual(na.retire(root, 'f' * 64)['status'], 'REFUSED')
        self.assertEqual(na.plan(root)['status'], 'REFUSED')  # normal apply is blocked too
        self.assertUnchanged(root, before)
        root = self.installed(name='same-bytes')
        (root / retired).write_bytes((root / native).read_bytes())  # identical bytes in both places is still a conflict, no mtime guess
        before = tree(root)
        self.assertEqual(na.plan_retire(root)['reasons'], ['RETIRE_SLOT_CONFLICT'])
        self.assertUnchanged(root, before)
        root = self.installed(name='drifted')  # retired earlier, then the slot was edited
        self.retire(root)
        (root / retired).write_bytes((root / retired).read_bytes() + b'x')
        before = tree(root)
        self.assertEqual(na.inspect(root)['state'], 'RETIRE_CONFLICT')
        self.assertEqual(na.plan_retire(root)['status'], 'REFUSED')
        self.assertEqual(na.plan(root)['status'], 'REFUSED')
        self.assertUnchanged(root, before)
        root = self.project(name='stray')  # a lone file in the slot with no receipt is not ours either
        (root / retired).parent.mkdir(parents=True)
        (root / retired).write_bytes(b'stray')
        self.assertEqual(na.inspect(root)['state'], 'RETIRE_CONFLICT')

    def test_an_older_adapter_receipt_can_still_be_retired(self):
        root = self.installed()
        receipt = json.loads((root / na.RECEIPT_REL).read_bytes())
        receipt['adapter'] = na.LEGACY_ADAPTERS['scout'][0]
        receipt['inputs']['adapter'] = 'e' * 64
        (root / na.RECEIPT_REL).write_bytes(ep.serialize(receipt))
        native_bytes = (root / na.NATIVE_REL).read_bytes()
        self.assertEqual(self.retire(root)['status'], 'RETIRED')
        self.assertEqual((root / na.retired_rel('scout')).read_bytes(), native_bytes)

    def test_links_and_unknown_journals_refuse_before_any_move(self):
        for what, rel in (('claude', '.claude'), ('native_agents', '.agent/runtime/native-agents')):
            with self.subTest(what):
                root = self.installed(name=what)
                real = self.work / ('moved-' + what)
                shutil.move(str(root / rel), str(real))
                if not make_junction(root / rel, real):
                    self.skipTest('this OS/account cannot create a directory link here')
                outside = tree(real)
                before = tree(root)
                plan = na.plan_retire(root)
                self.assertEqual((plan['status'], plan['reasons']), ('REFUSED', ['PATH_UNSAFE']), plan)
                self.assertEqual(na.retire(root, '1' * 64)['status'], 'REFUSED')
                self.assertEqual(tree(real), outside)
                self.assertEqual(tree(root), before)
        root = self.installed(name='journal')
        txdir = root / '.agent' / 'runtime' / 'transactions' / '20260101-000000-abcd1234'
        txdir.mkdir(parents=True)
        (txdir / 'journal.json').write_text('{broken', encoding='utf-8')
        before = tree(root)
        plan = na.plan_retire(root)
        self.assertEqual((plan['status'], plan['reasons'][0]), ('REFUSED', 'INTERRUPTED_OR_UNKNOWN'))
        self.assertEqual(na.retire(root, '2' * 64)['status'], 'REFUSED')
        self.assertUnchanged(root, before)

    def test_changes_after_the_preview_stop_the_move(self):
        native, receipt, retired = pair('scout')
        mutations = {
            'project': lambda r: (r / 'PROJECT.md').write_bytes((r / 'PROJECT.md').read_bytes() + b'\n- extra: line\n'),
            'profile': lambda r: (r / PROFILE).write_bytes((r / PROFILE).read_bytes() + b'\n'),
            'receipt': lambda r: (r / receipt).write_bytes((r / receipt).read_bytes() + b'\n'),
            'native': lambda r: (r / native).write_bytes((r / native).read_bytes() + b'user\n'),
            'slot': lambda r: (r / retired).write_bytes(b'new'),
        }
        for name, mutate in mutations.items():
            with self.subTest(name):
                root = self.installed(name=name)
                token = na.plan_retire(root)['plan']['plan_sha256']
                mutate(root)
                before = tree(root)
                res = na.retire(root, token)
                self.assertIn(res['status'], ('CONFLICT', 'REFUSED'), res)
                self.assertNotEqual(res['status'], 'RETIRED')
                self.assertUnchanged(root, before)
                self.assertTrue((root / native).is_file())  # nothing moved

    def test_changes_at_the_recheck_point_stop_the_move_and_keep_the_users_bytes(self):
        native, receipt, retired = pair('scout')
        root = self.installed(name='project')
        self.set_hook('retire_before_recheck', lambda info: (root / 'PROJECT.md').write_bytes((root / 'PROJECT.md').read_bytes() + b'\nnote\n'))  # MOCK
        token = na.plan_retire(root)['plan']['plan_sha256']
        res = na.retire(root, token)
        self.assertEqual((res['status'], res['reasons'][0]), ('CONFLICT', 'EXPECTED_BEFORE_MISMATCH'), res)
        self.assertTrue((root / native).is_file() and not (root / retired).exists())
        root = self.installed(name='native')
        edited = (root / native).read_bytes() + b'\nmy own line\n'
        self.set_hook('retire_before_recheck', lambda info: (root / native).write_bytes(edited))  # MOCK: the user edits right after the token check
        res = na.retire(root, na.plan_retire(root)['plan']['plan_sha256'])
        self.assertEqual(res['status'], 'CONFLICT', res)
        self.assertEqual((root / native).read_bytes(), edited)
        self.assertFalse((root / retired).exists())

    def test_a_destination_that_appears_at_the_move_is_never_replaced(self):
        native, receipt, retired = pair('scout')
        root = self.installed()
        native_bytes, receipt_bytes = (root / native).read_bytes(), (root / receipt).read_bytes()
        self.set_hook('retire_before_rename', lambda info: (root / retired).write_bytes(b'users file'))  # MOCK: after the last re-check, before the rename
        with mock.patch.object(os, 'replace', side_effect=AssertionError('os.replace must not be used')), \
                mock.patch.object(shutil, 'move', side_effect=AssertionError('shutil.move must not be used')):
            res = na.retire(root, na.plan_retire(root)['plan']['plan_sha256'])
        self.assertEqual((res['status'], res['reasons']), ('CONFLICT', ['RETIRE_SLOT_OCCUPIED']), res)
        self.assertEqual((root / native).read_bytes(), native_bytes)  # the Windows rename refused to replace
        self.assertEqual((root / retired).read_bytes(), b'users file')
        self.assertEqual((root / receipt).read_bytes(), receipt_bytes)

    def test_a_failed_rename_reports_the_observed_state_and_uses_no_fallback(self):
        native, receipt, retired = pair('scout')
        root = self.installed()
        before = tree(root)
        token = na.plan_retire(root)['plan']['plan_sha256']
        with mock.patch.object(os, 'rename', side_effect=PermissionError('locked')), \
                mock.patch.object(os, 'replace', side_effect=AssertionError('no replace')), \
                mock.patch.object(shutil, 'move', side_effect=AssertionError('no move')), \
                mock.patch.object(shutil, 'copyfile', side_effect=AssertionError('no copy')), \
                mock.patch.object(os, 'remove', side_effect=AssertionError('no delete')), \
                mock.patch.object(os, 'unlink', side_effect=AssertionError('no delete')):
            res = na.retire(root, token)
        self.assertEqual((res['status'], res['reasons']), ('REFUSED', ['RETIRE_RENAME_FAILED']), res)
        self.assertEqual(res['observed'], {'active': ep.sha256((root / native).read_bytes()), 'retired_slot': 'ABSENT'})
        self.assertUnchanged(root, before)

    def test_the_result_is_decided_from_the_files_not_from_the_return_of_rename(self):
        native, receipt, retired = pair('scout')
        real = os.rename
        # MOCK: the move really happened, then the call reports an error
        root = self.installed(name='late-error')
        native_bytes = (root / native).read_bytes()

        def moved_then_error(src, dst):
            real(src, dst)
            raise OSError('reported late')
        with mock.patch.object(os, 'rename', moved_then_error):
            res = na.retire(root, na.plan_retire(root)['plan']['plan_sha256'])
        self.assertEqual((res['status'], res['reasons']), ('RETIRED', ['RETIRE_OBSERVED_AFTER_ERROR']), res)
        self.assertEqual((root / retired).read_bytes(), native_bytes)
        # MOCK: a crash after the move, before the function returns: the files alone tell the story, and nothing is retried or restored
        root = self.installed(name='crash')
        native_bytes = (root / native).read_bytes()

        def crash(info):
            raise RuntimeError('crash after the move')
        self.set_hook('retire_after_rename', crash)
        token = na.plan_retire(root)['plan']['plan_sha256']
        with self.assertRaises(RuntimeError):
            na.retire(root, token)
        ep._HOOK = None
        self.assertEqual(na.inspect(root)['state'], 'RETIRED')
        with mock.patch.object(os, 'rename', side_effect=AssertionError('no second rename')):
            self.assertEqual(na.retire(root, token)['status'], 'UNCHANGED')
        self.assertEqual((root / retired).read_bytes(), native_bytes)
        self.assertFalse((root / native).exists())
        # MOCK: the user's edit lands after the last re-check, so the moved bytes are not the receipt's: kept where they are, never called a clean retire
        root = self.installed(name='edited-at-move')
        edited = (root / native).read_bytes() + b'\nlate edit\n'
        self.set_hook('retire_before_rename', lambda info: (root / native).write_bytes(edited))
        res = na.retire(root, na.plan_retire(root)['plan']['plan_sha256'])
        self.assertEqual((res['status'], res['reasons']), ('CONFLICT', ['RETIRE_MOVED_BYTES_DIFFER']), res)
        self.assertEqual((root / retired).read_bytes(), edited)
        self.assertFalse((root / native).exists())
        ep._HOOK = None
        self.assertEqual(na.inspect(root)['state'], 'RETIRE_CONFLICT')
        # MOCK: both paths vanish / nothing moves although no error: unknown, never a success
        root = self.installed(name='both-gone')
        token = na.plan_retire(root)['plan']['plan_sha256']
        with mock.patch.object(os, 'rename', lambda src, dst: os.unlink(src)):
            res = na.retire(root, token)
        self.assertEqual((res['status'], res['reasons']), ('UNKNOWN', ['RETIRE_BOTH_ABSENT']), res)
        root = self.installed(name='no-op')
        token = na.plan_retire(root)['plan']['plan_sha256']
        with mock.patch.object(os, 'rename', lambda src, dst: None):
            res = na.retire(root, token)
        self.assertEqual((res['status'], res['reasons']), ('UNKNOWN', ['RETIRE_UNKNOWN_RESULT']), res)
        self.assertTrue((root / native).is_file())

    def test_manual_restore_is_reinspected_like_any_other_native(self):
        native, receipt, retired = pair('scout')
        root = self.installed()
        original = (root / native).read_bytes()
        self.retire(root)
        os.rename(str(root / retired), str(root / native))  # the user's own, deliberate restore
        rep = na.inspect(root)
        self.assertEqual((rep['state'], rep['retired']['disk']), ('CURRENT', 'ABSENT'))
        self.assertEqual((root / native).read_bytes(), original)
        self.assertEqual(self.retire(root)['status'], 'RETIRED')  # and it can be retired again
        os.rename(str(root / retired), str(root / native))
        (root / native).write_bytes(original + b'edit')  # a restore that was then edited is the user's
        self.assertEqual(na.inspect(root)['state'], 'MODIFIED')
        self.assertEqual(na.plan_retire(root)['status'], 'REFUSED')

    def test_cli_preview_retire_and_retire(self):
        root = self.project()
        self.install(root, 'worker')
        r = run(ROOT, 'native_agents.py', 'preview-retire', '--role', 'worker', '--project', root, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        digest = result_schema.split_output(r.stdout)[1]['outcome']['plan']['plan_sha256']
        self.assertTrue((root / na.native_rel('worker')).is_file())
        self.assertEqual(run(ROOT, 'native_agents.py', 'retire', '--role', 'worker', '--project', root).returncode, 1)  # token required
        r = run(ROOT, 'native_agents.py', 'retire', '--role', 'worker', '--project', root, '--expect-plan', digest, '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(result_schema.split_output(r.stdout)[1]['outcome']['status'], 'RETIRED')
        self.assertFalse((root / na.native_rel('worker')).exists())
        self.assertTrue((root / na.retired_rel('worker')).is_file())
        r = run(ROOT, 'native_agents.py', 'status', '--role', 'worker', '--project', root)
        self.assertEqual(r.returncode, 1)
        self.assertIn('RETIRED', r.stdout)
        self.assertIn('NATIVE_RETIRED', r.stdout)


@NEED
class RetireRefusesWhereItCannotBeMeasured(RolesBase):
    def test_unsupported_os_and_filesystem_refuse_with_nothing_moved(self):
        root = self.project()
        self.install(root)
        before = tree(root)
        with mock.patch.object(na, '_windows_supported', return_value=False):
            plan = na.plan_retire(root)
            self.assertEqual((plan['status'], plan['reasons']), ('REFUSED', ['RETIRE_OS_UNSUPPORTED']))
            self.assertEqual(na.retire(root, 'a' * 64)['status'], 'REFUSED')
        self.assertUnchanged(root, before)
        if os.name == 'nt':  # MOCK: the folders report different volumes
            real = os.stat

            class Other:
                def __init__(self, st):
                    self.__dict__.update({k: getattr(st, k) for k in dir(st) if k.startswith('st_')})
                    self.st_dev = 4242
            with mock.patch.object(os, 'stat', lambda p, *a, **k: Other(real(p, *a, **k)) if str(p).endswith('law-scout.md') else real(p, *a, **k)):
                plan = na.plan_retire(root)
            self.assertEqual((plan['status'], plan['reasons']), ('REFUSED', ['RETIRE_FILESYSTEM_UNSUPPORTED']))
            self.assertUnchanged(root, before)


@NEED
class RemainingReview(RolesBase):
    def test_foreign_sibling_filename_never_bypasses_inventory_or_unknown_name_checks(self):
        for kind in ('absent_receipt', 'bad_receipt', 'modified_managed'):
            with self.subTest(kind):
                root = self.project(name=kind)
                sibling = root / na.native_rel('worker')
                if kind == 'modified_managed':
                    self.install(root, 'worker')
                sibling.parent.mkdir(parents=True, exist_ok=True)
                sibling.write_text('---\nname: >\n  law-scout\n---\nforeign prompt\n', encoding='utf-8')
                if kind == 'bad_receipt':
                    rec = root / na.receipt_rel('worker')
                    rec.parent.mkdir(parents=True, exist_ok=True)
                    rec.write_bytes(b'{}')
                before = tree(root)
                self.assertEqual(na.plan(root)['reasons'], ['NATIVE_DEFINITION_UNSUPPORTED'])
                self.assertEqual(tree(root), before)

    def test_foreign_sibling_bytes_are_bound_even_with_a_clear_unrelated_name(self):
        root = self.project()
        sibling = root / na.native_rel('worker')
        sibling.parent.mkdir(parents=True)
        sibling.write_text('---\nname: foreign-worker\n---\nfirst\n', encoding='utf-8')
        token = na.plan(root)['plan']['plan_sha256']
        sibling.write_bytes(sibling.read_bytes() + b'changed\n')
        before = tree(root)
        self.assertEqual(na.apply(root, token)['reasons'], ['PLAN_CHANGED'])
        self.assertEqual(tree(root), before)

    def test_inactive_slot_appearing_after_capture_blocks_normal_apply(self):
        root = self.project()
        token = na.plan(root)['plan']['plan_sha256']
        def mutate(r):
            slot = r / na.retired_rel('scout')
            slot.parent.mkdir(parents=True)
            slot.write_bytes(b'user inactive slot')
        with self.after_capture(root, mutate):
            res = na.apply(root, token)
        self.assertEqual((res['status'], res['reasons']), ('CONFLICT', ['EXPECTED_BEFORE_MISMATCH']), res)
        self.assertFalse((root / na.NATIVE_REL).exists())
        self.assertFalse((root / na.RECEIPT_REL).exists())
        self.assertEqual((root / na.retired_rel('scout')).read_bytes(), b'user inactive slot')

    @unittest.skipUnless(os.name == 'nt', 'positive retire requires Windows; refusal is tested separately')
    def test_retire_reports_a_changed_active_file_as_conflict(self):
        root = self.project()
        self.install(root)
        token = na.plan_retire(root)['plan']['plan_sha256']
        mine = b'user changed the active file'
        def hook(point, info):
            if point == 'retire_before_rename':
                (root / na.NATIVE_REL).write_bytes(mine)
        with mock.patch.object(ep, '_HOOK', hook), mock.patch.object(os, 'rename', side_effect=PermissionError('simulated locked source')):
            res = na.retire(root, token)
        self.assertEqual((res['status'], res['reasons']), ('CONFLICT', ['RETIRE_ACTIVE_BYTES_DIFFER']), res)
        self.assertEqual((root / na.NATIVE_REL).read_bytes(), mine)

    @unittest.skipUnless(os.name == 'nt', 'positive retire requires Windows; refusal is tested separately')
    def test_guard_error_after_move_is_reconciled_instead_of_reporting_no_effect(self):
        root = self.project()
        self.install(root)
        token = na.plan_retire(root)['plan']['plan_sha256']
        native, receipt = (root / na.NATIVE_REL).read_bytes(), (root / na.RECEIPT_REL).read_bytes()
        def hook(point, info):
            if point == 'retire_after_rename':
                raise tx.TransactionError('simulated late guard error')
        with mock.patch.object(ep, '_HOOK', hook):
            res = na.retire(root, token)
        self.assertEqual((res['status'], res['reasons']), ('RETIRED', ['RETIRE_OBSERVED_AFTER_ERROR']), res)
        self.assertFalse((root / na.NATIVE_REL).exists())
        self.assertEqual((root / na.retired_rel('scout')).read_bytes(), native)
        self.assertEqual((root / na.RECEIPT_REL).read_bytes(), receipt)

    def test_inactive_matching_receipt_without_a_marker_is_not_a_retired_managed_file(self):
        root = self.project()
        self.install(root)
        data = b'foreign inactive file without the managed marker'
        (root / na.NATIVE_REL).write_bytes(data)
        rec = json.loads((root / na.RECEIPT_REL).read_bytes())
        rec['native']['sha256'] = ep.sha256(data)
        (root / na.RECEIPT_REL).write_bytes(ep.serialize(rec))
        os.rename(str(root / na.NATIVE_REL), str(root / na.retired_rel('scout')))
        before = tree(root)
        self.assertEqual(na.inspect(root)['state'], 'RETIRE_CONFLICT')
        self.assertEqual(na.plan(root)['status'], 'REFUSED')
        self.assertEqual(tree(root), before)


class PackagingIsolation(unittest.TestCase):
    """Host-native project state and its receipt never travel: not into MANIFEST, release trees or projects made from the source; adopt/upgrade keep the user's."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='law-a10-pkg-')
        cls.pkg = Path(cls.tmp.name) / 'pkg'
        cp.materialize(str(cls.pkg))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix='law-a10-w-'))
        self.addCleanup(shutil.rmtree, str(self.work), True)

    def plant(self, base):
        for rel, data in (('.claude/agents/law-scout.md', b'native from a maintainer'), ('.claude/settings.json', b'{"x": 1}'),
                          ('.claude/agents/law-worker.md', b'worker native'), ('.claude/agents/law-reviewer.md', b'reviewer native'),
                          (RECEIPT, b'{"receipt": true}'), ('.agent/runtime/native-agents/claude-code/law-worker.json', b'{"receipt": true}'),
                          ('.agent/runtime/native-agents/claude-code/law-worker.retired.md', b'retired worker native'),
                          ('.agent/runtime/native-agents/other.json', b'{}')):
            p = Path(base) / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)

    def test_all_files_and_the_manifest_skip_only_the_root_claude_folder(self):
        src = self.work / 'src'
        shutil.copytree(str(self.pkg), str(src))
        self.plant(src)
        nested = src / 'docs' / '.claude'
        nested.mkdir()
        (nested / 'x.md').write_text('nested is ordinary content', encoding='utf-8')
        with mock.patch.object(cp, 'ROOT', str(src)):
            files = cp.all_files()
            self.assertFalse([f for f in files if f.startswith('.claude/') or f.startswith('.agent/runtime')], files)
            self.assertIn('docs/.claude/x.md', files)  # only the root folder is the project's native state
            self.assertTrue(any('.claude' in p for p in cp.tree_problems()))  # a release tree must not carry it
        self.assertTrue(cp.in_manifest('tools/native_agents.py'))

    def test_a_project_made_from_a_source_with_native_gets_no_native_or_receipt(self):
        src = self.work / 'src'
        shutil.copytree(str(self.pkg), str(src))
        self.plant(src)
        r = run(src, 'new_project.py', '--name', 'B', '--dest', self.work, '--lang', 'vi', '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        b = self.work / 'B'
        self.assertFalse((b / '.claude').exists())
        self.assertFalse((b / '.agent' / 'runtime' / 'native-agents').exists())
        self.assertNotIn('.claude', (b / 'MANIFEST.sha256').read_text(encoding='utf-8'))
        self.assertNotIn('native-agents', (b / 'MANIFEST.sha256').read_text(encoding='utf-8'))
        self.assertTrue((b / 'tools' / 'native_agents.py').is_file())  # the adapter itself is package code and does travel
        self.assertEqual(run(b, 'check_package.py', '--verify').returncode, 0)

    def test_adopt_and_upgrade_keep_the_users_native_byte_for_byte(self):
        mine = {'.claude/agents/law-scout.md': b'the user\'s own agent', '.claude/agents/other.md': b'other', '.claude/settings.json': b'{"keep": 1}',
                '.claude/agents/law-worker.md': b'my worker', '.claude/agents/law-reviewer.md': b'my reviewer'}
        proj = self.work / 'P'
        r = run(self.pkg, 'new_project.py', '--name', 'P', '--dest', self.work, '--lang', 'vi', '--apply', '--result-json')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for rel, data in mine.items():
            (proj / rel).parent.mkdir(parents=True, exist_ok=True)
            (proj / rel).write_bytes(data)
        for _ in range(2):
            r = run(self.pkg, 'upgrade_package.py', '--project', proj, '--apply')
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual({rel: (proj / rel).read_bytes() for rel in mine}, mine)
        self.assertEqual(run(proj, 'check_package.py', '--verify').returncode, 0)  # user native is not "a modified package file"
        adopt = self.work / 'A'
        for rel, data in mine.items():
            (adopt / rel).parent.mkdir(parents=True, exist_ok=True)
            (adopt / rel).write_bytes(data)
        r = run(self.pkg, 'adopt_project.py', '--project', adopt, '--name', 'A', '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual({rel: (adopt / rel).read_bytes() for rel in mine}, mine)
        self.assertEqual([p for p in adopt.rglob('*.new') if '.claude' in p.parts], [])

    def test_the_repository_holds_no_native_and_no_maintainer_profile(self):
        self.assertFalse((ROOT / '.claude').exists())
        self.assertFalse((ROOT / PROFILE).exists())
        self.assertFalse((ROOT / '.agent' / 'runtime' / 'native-agents').exists())


if __name__ == '__main__':
    unittest.main()
