"""Tiếp nhận skill/gói: kiểm thử logic trên bản sao tạm của package, không dùng agent thật hay người đánh giá.
Skill/pack intake: logic tests on a disposable copy of the package. No real agent run and no human evaluation here:
these tests only show that the tools keep a pack's CLAIM, the user's CONFIRMATION and the root update apart, that a
confirmation is bound to the installed content, and that nothing is exported on a label alone (see skills/README.md).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_structured_tools import MARKER, StructuredBase, read, write
import check_package as cp
import result_schema

SKILL = 'port-operations-reports'  # skill của gói cang-logistics / the cang-logistics pack's skill
CANG = 'cang-logistics'
ACCEPT = {'decision': 'ADD_MISSING_PART', 'relation': 'SUPPLEMENT'}


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and '.agent/runtime' not in p.relative_to(root).as_posix()}


class IntakeBase(StructuredBase):
    def pack_json(self, name):
        return self.base / 'packs' / name / 'pack.json'

    def set_intake(self, name, intake=None, **meta):
        p = self.pack_json(name)
        data = json.loads(read(p))
        data.pop('intake', None)
        if intake is not None:
            data['intake'] = dict(intake, version=intake.get('version', data['version']))
        data.update(meta)
        write(p, json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    def record(self, name, rel='references/intake-record.md'):
        write(self.base / 'packs' / name / rel, '# Intake record (synthetic test fixture)\n')
        return rel

    def claim(self, name, **extra):
        """Lời khai hợp lệ, hồ sơ có thật / a valid claim whose record exists."""
        self.set_intake(name, dict(ACCEPT, record=self.record(name), **extra))

    def statuses(self):
        out = {}
        for line in read(self.base / '.agent' / 'SKILL_INDEX.md').splitlines():
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if line.startswith('| ') and len(cells) >= 6 and cells[0] != 'Skill ID' and not set(line) <= set('|- '):
                out[cells[0]] = cells[5]
        return out

    def set_status(self, sid, status):
        f = self.base / '.agent' / 'SKILL_INDEX.md'
        lines = read(f).split('\n')
        for i, line in enumerate(lines):
            cells = line.split('|')
            if line.startswith('| %s |' % sid) and len(cells) > 6:
                cells[6] = ' %s ' % status
                lines[i] = '|'.join(cells)
        write(f, '\n'.join(lines))

    def confirm(self, name, apply=True):
        return self.structured('pack.py', 'confirm', name, *([] if apply else ['--dry-run']))

    def export(self, skill, dest=None):
        dest = dest or Path(self.tmp.name) / 'export'
        result, _, data = self.structured('install_skills.py', '--dest', dest, '--skills', skill, '--yes')
        return result.returncode, data, (dest / skill).exists()

    def bump(self, name, version):
        meta = json.loads(read(self.pack_json(name)))
        meta['version'] = version
        write(self.pack_json(name), json.dumps(meta, ensure_ascii=False, indent=2) + '\n')


class PackIntake(IntakeBase):
    def test_shipped_packs_are_deferred_candidates_with_a_record_that_exists(self):
        _, _, data = self.structured('pack.py', 'list')
        for p in data['packs']:
            with self.subTest(pack=p['name']):
                self.assertEqual((p['intake']['state'], p['intake']['reason']), ('candidate', 'deferred'))
                self.assertTrue((self.base / 'packs' / p['name'] / 'references' / 'intake-record.md').is_file())

    def test_candidate_pack_installs_as_review_and_structure_check_is_not_intake(self):
        self.init_project()
        self.set_intake(CANG)  # bỏ hồ sơ để thử trường hợp chưa có hồ sơ / drop the record: the no-record case
        result, _, data = self.structured('pack.py', 'check', CANG)
        self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertEqual(data['intake'][CANG]['state'], 'candidate')
        result, _, data = self.structured('pack.py', 'add', CANG)
        self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertEqual((data['intake']['state'], data['intake']['reason']), ('candidate', 'no_record'))
        self.assertEqual(self.statuses()[SKILL], 'REVIEW')
        self.assertTrue(data['next_actions'])

    def test_a_claim_never_approves_only_confirm_does(self):
        """SI-01: lời khai tự đính kèm của gói không tự thành AVAILABLE; chỉ xác nhận của người dùng mới nhận."""
        self.init_project()
        cases = {  # gói: (khối intake, lý do của lời khai, xác nhận được không) / pack: (intake, claim reason, confirmable)
            CANG: (dict(ACCEPT), 'add_missing_part', True),
            'hanh-chinh-nhan-su': ({'decision': 'PROJECT_ONLY', 'relation': 'REPLACEMENT'}, 'no_comparison', False),
            'ke-toan-noi-bo': ({'decision': 'PROJECT_ONLY', 'relation': 'UNKNOWN'}, 'native_unknown', False),
            'van-thu-luu-tru': ({'decision': 'ROOT_ELIGIBLE', 'relation': 'REPLACEMENT', 'comparison': 'references/ab.md'}, 'root_eligible', True),
            'phap-ly': (dict(ACCEPT, record='references/missing.md'), 'record_not_found', False),
        }
        for name, (intake, reason, confirmable) in cases.items():
            with self.subTest(pack=name):
                intake = dict(intake)
                intake.setdefault('record', self.record(name))
                if 'comparison' in intake:
                    self.record(name, intake['comparison'])
                self.set_intake(name, intake)
                result, _, data = self.structured('pack.py', 'add', name)
                self.assertEqual((result.returncode, data['status']), (0, 'success'), data['message'])
                self.assertEqual(data['intake']['reason'], reason)
                skills = json.loads(read(self.pack_json(name)))['skills']
                self.assertEqual({self.statuses()[s] for s in skills}, {'REVIEW'}, 'install is never approval')
                result, _, data = self.confirm(name, apply=False)  # xem trước không ghi gì / a preview writes nothing
                self.assertEqual({self.statuses()[s] for s in skills}, {'REVIEW'})
                result, _, data = self.confirm(name)
                if confirmable:
                    self.assertEqual((result.returncode, data['status']), (0, 'success'))
                    self.assertEqual({self.statuses()[s] for s in skills}, {'AVAILABLE'})
                else:
                    self.assertEqual((result.returncode, data['status']), (1, 'blocked'))
                    self.assertEqual({self.statuses()[s] for s in skills}, {'REVIEW'})
        # ROOT_ELIGIBLE không kèm quyền ghi gốc thì chưa được cập nhật gốc / no root grant: no root update
        _, _, data = self.structured('pack.py', 'list')
        self.assertFalse({p['name']: p for p in data['packs']}['van-thu-luu-tru']['intake']['root_update'])

    def test_one_explicit_step_installs_and_accepts(self):
        """Người dùng không phải làm nhiều bước: add --confirm, confirm và update --apply --confirm đều là một lệnh."""
        self.init_project()
        self.claim(CANG)
        result, human, data = self.structured('pack.py', 'add', CANG, '--confirm')
        self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE')
        self.assertIn('bạn đã xác nhận', human)
        self.assertTrue(self.export(SKILL)[2], 'one command is enough to export')
        # cập nhật kèm xác nhận lại: một lệnh / update with re-confirmation: one command
        src = self.base / 'packs' / CANG / 'skills' / SKILL / 'SKILL.md'
        write(src, read(src) + '\nĐổi sau khi xét.\n')
        self.structured('pack.py', 'update', CANG, '--apply')
        self.assertEqual(self.statuses()[SKILL], 'REVIEW', 'without --confirm the change is not silently accepted')
        write(src, read(src) + '\nĐổi thêm.\n')
        result, _, data = self.structured('pack.py', 'update', CANG, '--apply', '--confirm')
        self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE')

    def test_confirm_flag_never_installs_or_accepts_an_invalid_claim(self):
        self.init_project()
        for intake in (None, {'decision': 'DEFER', 'relation': 'SUPPLEMENT', 'record': 'references/intake-record.md'},
                       dict(ACCEPT, record='x'), {'decision': 'REUSE_NO_IMPORT', 'relation': 'SUPPLEMENT', 'record': 'references/intake-record.md'}):
            with self.subTest(intake=intake):
                self.set_intake(CANG, intake)
                before = read(self.base / '.agent' / 'SKILL_INDEX.md')
                result, _, data = self.structured('pack.py', 'add', CANG, '--confirm')
                self.assertEqual((result.returncode, data['status'], data['changes']), (1, 'blocked', False))
                self.assertFalse((self.base / 'skills' / 'local' / 'packs' / CANG).exists(), 'nothing is installed')
                self.assertEqual(read(self.base / '.agent' / 'SKILL_INDEX.md'), before)
        self.claim(CANG)  # không có --confirm thì vẫn cài thử được / without --confirm the trial install still works
        self.structured('pack.py', 'add', CANG)
        self.assertEqual(self.statuses()[SKILL], 'REVIEW')
        self.set_intake(CANG, {'decision': 'DEFER', 'relation': 'SUPPLEMENT', 'record': 'references/intake-record.md'})
        result, _, data = self.structured('pack.py', 'update', CANG, '--apply', '--confirm')
        self.assertEqual((result.returncode, data['status']), (1, 'blocked'))

    def test_unresolvable_locators_are_not_accepted(self):
        """SI-01: 'x', URL, đường dẫn tuyệt đối, '..' hay thư mục không phải hồ sơ giải được / unresolved locators never pass."""
        for bad in ('x', 'https://example.com/record.md', '/etc/passwd', 'C:/Windows/win.ini', '../README.md', 'references', 'references/nope.md'):
            for field in ('record', 'comparison'):
                with self.subTest(locator=bad, field=field):
                    intake = dict(ACCEPT, relation='REPLACEMENT', record=self.record(CANG), comparison=self.record(CANG, 'references/ab.md'))
                    intake[field] = bad
                    self.set_intake(CANG, intake)
                    _, _, data = self.structured('pack.py', 'list')
                    state = {p['name']: p for p in data['packs']}[CANG]['intake']
                    self.assertEqual((state['state'], state['reason']), ('candidate', 'record_not_found'))
        self.set_intake(CANG, dict(ACCEPT, record=self.record(CANG)))  # đối chứng: hồ sơ có thật thì hợp lệ / control: a real record is valid
        _, _, data = self.structured('pack.py', 'list')
        self.assertEqual({p['name']: p for p in data['packs']}[CANG]['intake']['state'], 'accepted')

    def test_refused_decisions_block_install_and_write_nothing(self):
        self.init_project()
        for decision in ('REUSE_NO_IMPORT', 'REJECT_VERSION'):
            with self.subTest(decision=decision):
                self.set_intake('phap-ly', {'decision': decision, 'relation': 'SUPPLEMENT', 'record': self.record('phap-ly')})
                before = read(self.base / '.agent' / 'SKILL_INDEX.md')
                result, _, data = self.structured('pack.py', 'add', 'phap-ly')
                self.assertEqual((result.returncode, data['status'], data['changes']), (1, 'blocked', False))
                self.assertFalse((self.base / 'skills' / 'local' / 'packs' / 'phap-ly').exists())
                self.assertEqual(read(self.base / '.agent' / 'SKILL_INDEX.md'), before)

    def test_content_change_in_the_same_version_voids_the_confirmation(self):
        """SI-02: cùng nhãn phiên bản không đồng nghĩa cùng nội dung đã nhận."""
        self.init_project()
        self.claim(CANG)
        self.structured('pack.py', 'add', CANG)
        self.confirm(CANG)
        self.assertEqual((self.export(SKILL)[0], self.export(SKILL)[2]), (0, True), 'confirmed content is exportable')

        src = self.base / 'packs' / CANG / 'skills' / SKILL / 'SKILL.md'
        write(src, read(src) + '\nChỉ dẫn mới chưa xét.\n')  # cùng phiên bản, nội dung đổi / same version, changed content
        result, human, data = self.structured('pack.py', 'update', CANG)
        self.assertEqual((result.returncode, data['status']), (0, 'preview'))
        self.assertIn('hết hiệu lực', human)
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE', 'preview must not change the index')
        self.structured('pack.py', 'update', CANG, '--apply')
        self.assertEqual(self.statuses()[SKILL], 'REVIEW')
        self.assertFalse(self.export(SKILL, Path(self.tmp.name) / 'e2')[2])
        self.confirm(CANG)  # xét xong, xác nhận lại bản mới / reviewed, confirm the new content
        self.assertTrue(self.export(SKILL, Path(self.tmp.name) / 'e3')[2])

        result, _, data = self.structured('pack.py', 'update', CANG)  # không đổi gì: xác nhận giữ nguyên / unchanged: it holds
        self.assertEqual((data['status'], data['changes']), ('success', False))
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE')

    def test_editing_the_installed_copy_blocks_export_until_confirmed_again(self):
        """SI-02: chỉnh trực tiếp bản đã cài (thêm script, sửa SKILL.md) không giữ quyền cũ."""
        self.init_project()
        self.claim(CANG)
        self.structured('pack.py', 'add', CANG)
        self.confirm(CANG)
        installed = self.base / 'skills' / 'local' / 'packs' / CANG / 'skills' / SKILL
        for edit in ('skill', 'script'):
            with self.subTest(edit=edit):
                if edit == 'skill':
                    write(installed / 'SKILL.md', read(installed / 'SKILL.md') + '\nSửa tay.\n')
                else:
                    write(installed / 'scripts' / 'extra.py', 'print("not run")\n')
                self.assertEqual(self.statuses()[SKILL], 'AVAILABLE', 'the index label alone did not change')
                rc, data, copied = self.export(SKILL, Path(self.tmp.name) / ('x-' + edit))
                self.assertEqual((rc, copied), (1, False))
                self.assertEqual(data['excluded'], [{'skill': SKILL, 'reason': 'pack_content_changed'}])
                result, _, chk = self.structured('pack.py', 'check', CANG)
                self.assertEqual((result.returncode, chk['status']), (1, 'issues'))
                self.confirm(CANG)  # người dùng xét rồi xác nhận lại nội dung hiện tại / the user reviews, confirms again
                self.assertTrue(self.export(SKILL, Path(self.tmp.name) / ('y-' + edit))[2])

    def test_disabled_survives_and_typed_status_is_not_a_confirmation(self):
        self.init_project()
        self.claim(CANG)
        self.structured('pack.py', 'add', CANG)
        self.set_status(SKILL, 'AVAILABLE')  # gõ tay vào chỉ mục, chưa xác nhận / typed by hand, never confirmed
        rc, data, copied = self.export(SKILL)
        self.assertEqual((rc, copied), (1, False))
        self.assertEqual(data['excluded'], [{'skill': SKILL, 'reason': 'pack_not_confirmed'}])
        result, _, chk = self.structured('pack.py', 'check', CANG)
        self.assertEqual((result.returncode, chk['status']), (1, 'issues'))
        self.confirm(CANG)
        self.set_status(SKILL, 'DISABLED')
        src = self.base / 'packs' / CANG / 'README.md'
        write(src, read(src) + '\nđổi.\n')
        self.structured('pack.py', 'update', CANG, '--apply')
        self.assertEqual(self.statuses()[SKILL], 'DISABLED', 'the user choice to disable is kept')

    def test_refusing_the_installed_version_stops_export_but_another_version_does_not(self):
        """SI-03: accepted -> REJECT_VERSION trực tiếp; từ chối bản khác chưa cài không vô hiệu bản đã nhận."""
        self.init_project()
        rec = self.record(CANG)
        self.claim(CANG)
        self.structured('pack.py', 'add', CANG)
        self.confirm(CANG)
        self.assertTrue(self.export(SKILL)[2])

        installed_version = json.loads(read(self.pack_json(CANG)))['version']
        self.set_intake(CANG, {'decision': 'REJECT_VERSION', 'relation': 'SUPPLEMENT', 'record': rec})  # đúng bản đã cài / the installed version
        result, _, data = self.structured('pack.py', 'update', CANG, '--apply')
        self.assertEqual((result.returncode, data['status']), (1, 'blocked'))
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE', 'a blocked update leaves the index alone')
        result, _, chk = self.structured('pack.py', 'check', CANG)
        self.assertEqual((result.returncode, chk['status']), (1, 'issues'))
        self.assertTrue(any('pack.py remove %s' % CANG in f['message'] for f in chk['findings']))
        rc, data, copied = self.export(SKILL, Path(self.tmp.name) / 'refused')
        self.assertEqual((rc, copied), (1, False))
        self.assertEqual(data['excluded'], [{'skill': SKILL, 'reason': 'pack_refused'}])

        # bản 0.9.0 (chưa cài) bị từ chối: bản đã cài đã xác nhận vẫn dùng được / refusing a not-installed version
        self.bump(CANG, '0.9.0')
        self.set_intake(CANG, {'decision': 'REJECT_VERSION', 'relation': 'SUPPLEMENT', 'record': rec, 'version': '0.9.0'})
        self.assertNotEqual(installed_version, '0.9.0')
        self.assertTrue(self.export(SKILL, Path(self.tmp.name) / 'other')[2])

    def test_a_withdrawn_claim_in_the_same_version_voids_the_confirmation(self):
        self.init_project()
        self.claim(CANG)
        self.structured('pack.py', 'add', CANG)
        self.confirm(CANG)
        rec = self.record(CANG)
        self.set_intake(CANG, {'decision': 'DEFER', 'relation': 'SUPPLEMENT', 'record': rec})
        rc, data, copied = self.export(SKILL)
        self.assertEqual((rc, copied, data['excluded']), (1, False, [{'skill': SKILL, 'reason': 'pack_claim_withdrawn'}]))
        self.structured('pack.py', 'update', CANG, '--apply')
        self.assertEqual(self.statuses()[SKILL], 'REVIEW')

    def test_version_change_reopens_review(self):
        self.init_project()
        self.claim(CANG)
        self.structured('pack.py', 'add', CANG)
        self.confirm(CANG)
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE')
        self.bump(CANG, '0.9.0')  # bản mới, hồ sơ cũ / new version, old record
        result, human, data = self.structured('pack.py', 'update', CANG)
        self.assertEqual((result.returncode, data['status'], data['intake']['reason']), (0, 'preview', 'version_changed'))
        self.assertIn('hết hiệu lực', human)
        self.structured('pack.py', 'update', CANG, '--apply')
        self.assertEqual(self.statuses()[SKILL], 'REVIEW', 'an approved old version does not approve the new one')
        result, _, data = self.confirm(CANG)
        self.assertEqual((result.returncode, data['status']), (1, 'blocked'))

    def test_malformed_intake_is_a_structure_error(self):
        self.set_intake('phap-ly', {'decision': 'PASS', 'relation': 'SUPPLEMENT', 'record': 'x', 'scroe': 9})
        result, _, data = self.structured('pack.py', 'check', 'phap-ly')
        self.assertEqual((result.returncode, data['status']), (1, 'issues'))
        messages = ' '.join(f['message'] for f in data['findings'])
        self.assertIn('intake.decision', messages)
        self.assertIn('intake.scroe', messages)

    def test_pack_scripts_are_never_run(self):
        self.init_project()
        sentinel = Path(self.tmp.name) / 'SCRIPT_RAN'
        probe = 'open(%r, "w").write("ran")\n' % str(sentinel)
        write(self.base / 'packs' / CANG / 'skills' / SKILL / 'scripts' / 'probe.py', probe)
        write(self.base / 'packs' / CANG / 'skills' / SKILL / 'scripts' / '__init__.py', probe)
        self.claim(CANG)
        self.structured('pack.py', 'check', CANG)
        self.structured('pack.py', 'add', CANG)
        self.confirm(CANG)
        self.structured('pack.py', 'list')
        self.structured('install_skills.py', '--dest', Path(self.tmp.name) / 'dest', '--all', '--include-packs')
        self.assertFalse(sentinel.exists())


class InstallIntake(IntakeBase):
    def test_only_accepted_local_skills_are_exported(self):
        self.init_project()
        self.structured('pack.py', 'add', CANG)  # ứng viên / candidate
        dest = Path(self.tmp.name) / 'dest'
        result, _, data = self.structured('install_skills.py', '--dest', dest, '--skills', SKILL, '--yes')
        self.assertEqual((result.returncode, data['status']), (1, 'blocked'))
        self.assertEqual(data['excluded'], [{'skill': SKILL, 'reason': 'status_review'}])
        self.assertFalse(dest.exists())

        result, _, data = self.structured('install_skills.py', '--dest', dest, '--all', '--include-packs', '--yes')
        self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertIn({'skill': SKILL, 'reason': 'status_review'}, data['excluded'])
        self.assertFalse((dest / SKILL).exists())
        self.assertTrue((dest / 'meeting-minutes' / 'SKILL.md').is_file())

        self.set_status('data-charts', 'DISABLED')
        for kind in ('external', 'inbox'):  # nguồn ngoài chưa qua tiếp nhận / outside skills never copied
            write(self.base / 'skills' / kind / ('outside-' + kind) / 'SKILL.md', '---\nname: outside-%s\n---\n' % kind)
        idx = self.base / '.agent' / 'SKILL_INDEX.md'
        write(idx, read(idx).replace('\n\n## ', '\n| outside-external | EXTERNAL | PROJECT | skills/external/outside-external/SKILL.md | x | AVAILABLE | test |\n\n## ', 1))
        result, _, data = self.structured('install_skills.py', '--dest', dest, '--skills', 'data-charts')
        self.assertEqual((result.returncode, data['status']), (1, 'blocked'))
        result, _, data = self.structured('install_skills.py', '--dest', dest, '--skills', 'outside-external')
        self.assertEqual((result.returncode, data['status']), (1, 'blocked'))
        result, _, data = self.structured('install_skills.py', '--dest', Path(self.tmp.name) / 'dest3', '--all', '--yes')
        copied = {p.name for p in (Path(self.tmp.name) / 'dest3').iterdir()}
        self.assertFalse(copied & {'data-charts', 'outside-external', 'outside-inbox'})

    def test_copy_needs_an_explicit_choice(self):
        dest = Path(self.tmp.name) / 'dest'
        result, _, data = self.structured('install_skills.py', '--dest', dest, '--yes')
        self.assertEqual((result.returncode, data['status']), (1, 'blocked'))
        self.assertIn('meeting-minutes', data['eligible'])
        self.assertFalse(dest.exists())

    def test_same_name_skill_not_copied_by_package_is_never_overwritten(self):
        dest = Path(self.tmp.name) / 'app-skills'
        native = dest / 'meeting-minutes' / 'SKILL.md'
        write(native, 'NATIVE OR OTHER SOURCE')
        result, _, data = self.structured('install_skills.py', '--dest', dest, '--skills', 'meeting-minutes', '--overwrite', '--yes')
        self.assertEqual((result.returncode, data['status'], data['changes']), (0, 'success', False))
        self.assertEqual(data['files'], [{'path': str(dest / 'meeting-minutes'), 'action': 'skip', 'reason': 'not_from_package'}])
        self.assertEqual(read(native), 'NATIVE OR OTHER SOURCE')

        self.structured('install_skills.py', '--dest', dest, '--skills', 'data-charts', '--yes')
        mark = json.loads(read(dest / 'data-charts' / '.workspace-skill.json'))
        self.assertEqual((mark['package'], mark['skill']), ('local-agent-workspace', 'data-charts'))
        result, _, data = self.structured('install_skills.py', '--dest', dest, '--skills', 'data-charts', '--overwrite', '--yes')
        self.assertEqual((result.returncode, data['status'], data['changes']), (0, 'success', True))
        self.assertEqual(sorted(p.name for p in dest.iterdir()), ['data-charts', 'meeting-minutes'],
                         'no backup folder is left where the app scans for skills')
        self.assertTrue(list((self.base / 'archive').glob('app-skills-backup-*/data-charts/SKILL.md')))


class RootIsolation(IntakeBase):
    def run_in(self, base, script, *args):
        env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        return subprocess.run([sys.executable, str(base / 'tools' / script), *map(str, args)], cwd=str(base), env=env,
                              capture_output=True, encoding='utf-8', timeout=120)

    def test_root_update_reaches_a_project_only_through_explicit_steps(self):
        # bộ mẫu gốc là gói sạch như bản phát hành (projection chung), không phải bản chép nguyên cây kho nguồn có v1/v2 và MANIFEST cũ
        # the template root is the clean shipped package, not a raw copy of the source tree with v1/v2 and a stale MANIFEST
        self.base = Path(self.tmp.name) / 'clean-package'
        cp.materialize(str(self.base), branding=False)
        proj = Path(self.tmp.name) / 'project'
        shutil.copytree(self.base, proj)
        self.assertEqual(self.run_in(proj, 'init_project.py', '--name', 'Demo').returncode, 0)
        self.assertEqual(self.run_in(proj, 'pack.py', 'add', CANG).returncode, 0)
        idx = proj / '.agent' / 'SKILL_INDEX.md'
        write(idx, read(idx).replace('| REVIEW | Gói/Pack cang-logistics', '| AVAILABLE | Gói/Pack cang-logistics'))
        installed = proj / 'skills' / 'local' / 'packs' / CANG / 'skills' / SKILL / 'SKILL.md'
        installed_before, index_before = installed.read_bytes(), read(idx)
        # nhãn gõ tay không đủ để xuất / a hand-typed label is not enough to export
        out = self.run_in(proj, 'install_skills.py', '--dest', Path(self.tmp.name) / 'pe', '--skills', SKILL, '--yes')
        self.assertNotEqual(out.returncode, 0)
        self.assertFalse((Path(self.tmp.name) / 'pe' / SKILL).exists())

        root = self.base  # bộ mẫu gốc đổi skill dùng chung và gói / the template root changes a shared skill and a pack
        for rel in ('skills/local/shared/meeting-minutes/SKILL.md', 'packs/%s/skills/%s/SKILL.md' % (CANG, SKILL)):
            write(root / rel, read(root / rel) + '\nThay đổi ở gốc.\n')
        self.assertEqual(self.run_in(root, 'check_package.py', '--write-manifest').returncode, 0)

        before = snapshot(proj)
        self.assertEqual(snapshot(proj), before)
        r = self.run_in(root, 'upgrade_package.py', '--project', proj)  # xem trước / preview
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(snapshot(proj), before, 'a preview writes nothing into the project')
        r = self.run_in(root, 'upgrade_package.py', '--project', proj, '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('Thay đổi ở gốc.', read(proj / 'skills' / 'local' / 'shared' / 'meeting-minutes' / 'SKILL.md'))
        self.assertEqual(installed.read_bytes(), installed_before, 'an installed pack changes only with pack.py update')
        self.assertEqual(read(idx), index_before, 'upgrade keeps the project index and its statuses')


class AdoptIntake(IntakeBase):
    def test_existing_project_skill_is_recorded_for_review_not_accepted(self):
        target = Path(self.tmp.name) / 'existing'
        write(target / 'skills' / 'local' / 'project' / 'own-skill' / 'SKILL.md',
              '---\nname: own-skill\ndescription: A project skill that existed before the package was brought in.\n---\n')
        write(target / '.agent' / 'SKILL_INDEX.md', read(self.base / '.agent' / 'SKILL_INDEX.md'))
        r = self.run_tool('adopt_project.py', '--project', target, '--name', 'Existing', '--apply')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        rows = [l for l in read(target / '.agent' / 'SKILL_INDEX.md').splitlines() if l.startswith('| own-skill |')]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].split('|')[6].strip(), 'REVIEW')


# ---------------------------------------------------------------- C-01 / T36: kinh nghiệm A -> mẫu cá nhân -> B
# Mọi dự án A/B, bộ mẫu, xác nhận của người dùng và quyền ghi mẫu dưới đây là FIXTURE MÔ PHỎNG trong thư mục tạm;
# không có người dùng hay skill thật nào được tiếp nhận ở đây. Phân biệt hai loại bằng chứng:
#   HỢP TÁC: các bước tách dữ liệu, tiếp nhận, quyền ghi mẫu, so danh sách là quy ước của docs/HUONG_DAN_SKILLS_VI.md mục 11
#            (harness `update_template` đi theo docs, máy không cưỡng chế). Ca âm của chúng chỉ chứng minh trình tự dừng đúng
#            VÀ cây đích thực tế không đổi byte, kể cả MANIFEST không bị ghi lại.
#   MÁY:     manifest/new_project/install_skills là owner có sẵn, không bị monkeypatch; cây A/mẫu/B so bằng hash từng byte.
# All projects, templates, confirmations and grants below are SIMULATED fixtures in a temp folder. COOPERATIVE = the steps
# the guide describes (the harness follows the guide, nothing enforces it); MACHINE = the real owners and byte-level tree hashes.
SID = 'work-handover-checklist'
MANIFEST = 'MANIFEST.sha256'
INDEX_FILES = ('.agent/SKILL_INDEX.md', 'en/.agent/SKILL_INDEX.md')
PRIVATE = 'a-private-skill'
SENTINEL = b'SENTINEL-A-'

VI_SKILL = ('---\nname: @ID@\ndescription: >-\n  Gợi ý lập danh sách bàn giao công việc: việc đã xong, việc còn dở, điều cần xác nhận. '
            'Không tự điền người phụ trách hay hạn chưa có trong nguồn.\n  Kích hoạt khi người dùng nói: “bàn giao công việc”.\n'
            'metadata:\n  version: "1.0"\n---\n\n# Danh sách bàn giao công việc\n\nLấy dữ kiện từ nguồn của dự án đang dùng; khung này không chứa '
            'số liệu hay quyết định của dự án nào. Khung nằm ở `references/handover-frame.md`.\n')
EN_SKILL = ('---\nname: @ID@\ndescription: >-\n  A frame for a work handover list: what is done, what is open, what needs confirmation. '
            'Never fills in an owner or a deadline the source does not give.\n  Use when the user says: "hand over the work".\n'
            'metadata:\n  version: "1.0"\n---\n\n# Work handover checklist\n\nTake facts from the source of the project in use; this frame holds '
            'no figures or decisions of any project. The frame is in `references/handover-frame.md`.\n')
VI_FRAME = '# Khung bàn giao\n\n| Việc | Tình trạng | Cần xác nhận |\n|---|---|---|\n| [lấy từ nguồn] | [đã xong / còn dở] | [ai xác nhận] |\n'
EN_FRAME = '# Handover frame\n\n| Item | Status | Needs confirmation |\n|---|---|---|\n| [take from the source] | [done / open] | [who confirms] |\n'


class Draft:
    """Bản dẫn xuất trong thư mục nháp ngoài A và ngoài mẫu; `selected` là danh sách file người dùng đã xem và xác nhận.
    The derived version in a draft folder outside A and the template; `selected` is the list the user saw and confirmed."""

    def __init__(self, root, sid=SID, vi_extra='', en_extra='', script=None, slot='draft'):
        self.root, self.sid = Path(root) / slot, sid
        vi, en = VI_SKILL.replace('@ID@', sid) + vi_extra, EN_SKILL.replace('@ID@', sid) + en_extra
        write(self.root / 'vi' / 'SKILL.md', vi)
        write(self.root / 'vi' / 'references' / 'handover-frame.md', VI_FRAME)
        write(self.root / 'en' / 'SKILL.md', en)
        write(self.root / 'en' / 'references' / 'handover-frame.md', EN_FRAME)
        write(self.root / 'vi' / 'references' / 'notes-from-a.md', 'Ghi chú riêng. SENTINEL-A-NOTES\n')  # tài nguyên KHÔNG được chọn
        write(self.root / 'second-draft' / 'SKILL.md', '---\nname: second-draft\n---\nSENTINEL-A-SECOND\n')  # skill thứ hai KHÔNG được chọn
        self.script = script
        if script:
            write(self.root / 'vi' / 'scripts' / 'probe.py', 'open(%r, "w").write("ran")\n' % str(script))  # chỉ để xem có bị chạy không
        base, en_base = 'skills/local/shared/%s/' % sid, 'en/skills/local/shared/%s/' % sid
        self.selected = [('vi/SKILL.md', base + 'SKILL.md'), ('vi/references/handover-frame.md', base + 'references/handover-frame.md'),
                         ('en/SKILL.md', en_base + 'SKILL.md'), ('en/references/handover-frame.md', en_base + 'references/handover-frame.md')]
        self.rows = {
            INDEX_FILES[0]: '| %s | LOCAL | SHARED | skills/local/shared/%s/SKILL.md | Lập danh sách bàn giao công việc: đã xong, còn dở, cần xác nhận. | AVAILABLE | Bản dẫn xuất khác ID, đã tách dữ liệu riêng; nhận vào bộ mẫu cá nhân sau xác nhận của người dùng (fixture mô phỏng). |' % (sid, sid),
            INDEX_FILES[1]: '| %s | LOCAL | SHARED | skills/local/shared/%s/SKILL.md | A work handover list: done, open, needs confirmation. | AVAILABLE | Derived under a different ID with private data removed; accepted into the personal template after the user confirmed (simulated fixture). |' % (sid, sid),
        }

    def targets(self):
        return {target for _, target in self.selected}

    def allowed(self):
        return self.targets() | set(INDEX_FILES)

    def digest(self):
        """Dấu vân tay đúng những gì người dùng đã xem: từng file được chọn và hai dòng index. / What the user saw, byte for byte."""
        h = hashlib.sha256()
        for rel, target in sorted(self.selected, key=lambda x: x[1]):
            h.update(target.encode('utf-8') + b'\0' + (self.root / rel).read_bytes() + b'\0')
        for rel, row in sorted(self.rows.items()):
            h.update(rel.encode('utf-8') + b'\0' + row.encode('utf-8') + b'\0')
        return h.hexdigest()

    def confirmation(self, template=None, **override):
        """Xác nhận MÔ PHỎNG: nhận nội dung và quyền ghi mẫu là hai trường riêng. / SIMULATED: accepting content and the right to write are separate."""
        c = {'simulated': True, 'accepted_content': True, 'id': self.sid, 'digest': self.digest(),
             'root_grant': {'target': Path(template or self.root.parent / 'personal-template').resolve().as_posix(), 'ids': [self.sid]}}
        c.update(override)
        return c


ROW_OK = {'status': 'AVAILABLE', 'scope': 'SHARED', 'notes': 'ROOT_ELIGIBLE; hồ sơ: working/intake-fixture.md (mô phỏng)'}


def fingerprint(root):
    """Hash từng byte của mọi file (kể cả dữ liệu vận hành), trừ cache Python. / Every file's hash, minus Python caches."""
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(Path(root).rglob('*')) if p.is_file() and '__pycache__' not in p.parts}


def changed(before, after):
    return {k for k in set(before) | set(after) if before.get(k) != after.get(k)}


def run_in(base, script, *args):
    env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
    return subprocess.run([sys.executable, '-B', str(Path(base) / 'tools' / script), *map(str, args)], cwd=str(base), env=env,
                          capture_output=True, encoding='utf-8', timeout=180)


def manifest_of(base):
    return dict(reversed(line.split('  ', 1)) for line in read(Path(base) / MANIFEST).splitlines() if line.strip())


def boundary(draft, a_root):
    """Ranh giới CỤ THỂ đã quan sát, không phải scanner dữ liệu nhạy cảm: đường dẫn A, vùng riêng của A, liên kết ra ngoài, URL.
    Concrete boundaries only, not a sensitive-data scanner: A's path, A's private areas, links that leave the skill, URLs."""
    for rel, target in draft.selected:
        for path in (rel, target):
            if not path or path.startswith('/') or '\\' in path or ':' in path or any(x in ('', '.', '..') for x in path.split('/')):
                return 'PATH_FORM'
        if not target.startswith(('skills/local/shared/%s/' % draft.sid, 'en/skills/local/shared/%s/' % draft.sid)):
            return 'TARGET_OUTSIDE'
        source = draft.root / rel
        if draft.root.resolve() not in source.resolve().parents or not source.is_file():
            return 'SOURCE_OUTSIDE'
        part = source
        while part != draft.root:
            if cp._is_link(str(part)):
                return 'SOURCE_LINK'
            part = part.parent
        if cp._is_link(str(draft.root)):
            return 'SOURCE_LINK'
        text = source.read_text(encoding='utf-8')
        if str(a_root) in text or Path(a_root).as_posix() in text:
            return 'A_PATH'
        if 'skills/local/project/' in text or '.agent/runtime' in text:
            return 'A_PROJECT_AREA'
        for target in re.findall(r'\]\(([^)\s]*)', text):
            if not re.fullmatch(r'[\w][\w./-]*', target) or '..' in target.split('/'):
                return 'LINK_OUTSIDE'
        if re.search(r'https?://', text):
            return 'URL'
    return ''


def intake_gate(row, confirm, draft, template):
    """Quyết định hợp tác (docs bước 3): kết luận ở dòng index của A + xác nhận của người dùng gắn với đúng bản đã xem.
    Cooperative decision: the conclusion on A's index row plus a confirmation bound to the version the user saw."""
    if row['status'] not in ('AVAILABLE', 'ACTIVE'):
        return 'STATUS_' + row['status']
    if row['scope'] != 'SHARED' or 'PROJECT_ONLY' in row['notes']:
        return 'PROJECT_ONLY'
    if 'DEFER' in row['notes']:
        return 'DEFER'
    if 'ROOT_ELIGIBLE' not in row['notes']:
        return 'NOT_ROOT_ELIGIBLE'
    if not confirm or not confirm.get('accepted_content'):
        return 'NO_CONFIRMATION'
    if confirm.get('id') != draft.sid or confirm.get('digest') != draft.digest():
        return 'CONFIRMATION_STALE'
    grant = confirm.get('root_grant') or {}
    if grant.get('target') != Path(template).resolve().as_posix() or draft.sid not in grant.get('ids', []):
        return 'NO_ROOT_GRANT'
    return ''


def known_ids(tpl):
    ids = {p.name.casefold() for p in (tpl / 'skills' / 'local' / 'shared').iterdir()}
    ids |= {p.name.casefold() for p in (tpl / 'packs').glob('*/skills/*')}
    for rel in INDEX_FILES:
        ids |= {line.split('|')[1].strip().casefold() for line in read(tpl / rel).splitlines() if line.startswith('| ') and line.count('|') > 6}
    return ids


def index_with_row(data, row):
    nl = b'\r\n' if b'\r\n' in data else b'\n'
    at = data.find(nl + nl + b'## ')
    if at < 0:
        raise ValueError('index frame missing')
    return data[:at] + nl + row.encode('utf-8') + data[at:]


def add_index_row(path, row):
    path.write_bytes(index_with_row(path.read_bytes(), row))


def apply_selected(tpl, draft):
    for rel, target in draft.selected:
        dst = tpl / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes((draft.root / rel).read_bytes())
    for rel, row in draft.rows.items():
        add_index_row(tpl / rel, row)


def update_template(tpl, draft, row, confirm, a_root, inject=None):
    """Trình tự của docs bước 2 -> 5 trên bộ mẫu cá nhân. Trả {'result': 'applied'|'stopped', 'code', 'detail'}.
    The guide's steps 2-5 on the personal template."""
    def stop(code, detail=None):
        return {'result': 'stopped', 'code': code, 'detail': detail}
    hit = boundary(draft, a_root)
    if hit:
        return stop('BOUNDARY', hit)
    code = intake_gate(row, confirm, draft, tpl)
    if code:
        return stop(code)
    if (tpl / '.agent' / 'PACKAGE_INFO.json').exists() or run_in(tpl, 'check_package.py', '--verify').returncode != 0:
        return stop('BASELINE')
    if draft.sid.casefold() in known_ids(tpl):
        return stop('ID_COLLISION')
    if any((tpl / t).exists() for t in draft.targets()):
        return stop('PATH_COLLISION')
    preview = run_in(tpl, 'new_project.py', '--name', '_C01_baseline_check')  # read-only delivery inventory guard; verify alone checks only listed hashes
    if preview.returncode != 0:
        return stop('BASELINE')
    if confirm.get('digest') != draft.digest():
        return stop('CONFIRMATION_STALE')
    expected = {target: (draft.root / rel).read_bytes() for rel, target in draft.selected}
    expected.update({rel: index_with_row((tpl / rel).read_bytes(), text) for rel, text in draft.rows.items()})
    before = fingerprint(tpl)
    apply_selected(tpl, draft)
    if inject:
        inject(tpl)  # mô phỏng thay đổi lạ chen vào giữa chừng / simulates an unexpected change slipping in
    extra = changed(before, fingerprint(tpl)) ^ draft.allowed()
    if extra:
        return stop('DELTA_OUTSIDE_SELECTION', sorted(extra))
    mismatched = [rel for rel, data in expected.items() if (tpl / rel).read_bytes() != data]
    if mismatched:
        return stop('DELTA_CONTENT_MISMATCH', sorted(mismatched))
    if run_in(tpl, 'check_package.py', '--write-manifest').returncode != 0 or run_in(tpl, 'check_package.py', '--verify').returncode != 0:
        return stop('VERIFY_FAILED')
    return {'result': 'applied', 'code': '', 'detail': None}


class PersonalReuse(unittest.TestCase):
    """C-01/T36. Bộ mẫu sạch được dựng bằng owner (`materialize`), A và B bằng `new_project.py` thật. Không importer, không sync ngầm.
    The clean template comes from the owner (`materialize`); A and B are made by the real `new_project.py`. No importer, no hidden sync."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='personal-reuse-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tpl = self.root / 'personal-template'
        cp.materialize(str(self.tpl), branding=False)
        self.projects = self.root / 'projects'
        self.projects.mkdir()
        self.script_ran = self.root / 'SCRIPT_RAN'

    def new_project(self, tpl, name, lang='vi'):
        r = run_in(tpl, 'new_project.py', '--name', name, '--dest', self.projects, '--lang', lang, '--apply', '--result-json')
        _, data = result_schema.split_output(r.stdout)
        self.assertIsNotNone(data, r.stdout + r.stderr)
        return r, data, self.projects / name

    def make_a(self):
        """A: dự án thật do CLI tạo từ bộ mẫu CHƯA có bản dẫn xuất, rồi gắn dữ liệu riêng GIẢ có dấu hiệu phân biệt.
        A is made by the real CLI from the template BEFORE the derivative exists, then given distinct FAKE private data."""
        r, data, a = self.new_project(self.tpl, 'Du an A')
        self.assertEqual((r.returncode, data['status']), (0, 'success'), data['message'])
        for rel, text in (('PROJECT.md', '\n- Ghi chú riêng: SENTINEL-A-PROJECT\n'), ('.agent/STATE.md', '\nSENTINEL-A-STATE\n'),
                          ('.agent/HANDOFF.md', '\nSENTINEL-A-HANDOFF\n')):
            with (a / rel).open('ab') as f:
                f.write(text.encode('utf-8'))
        write(a / 'references' / 'policies' / 'quy-che-rieng-a.md', 'SENTINEL-A-SOURCE\n')
        write(a / 'output' / 'ket-qua-a.md', 'SENTINEL-A-OUTPUT\n')
        write(a / 'skills' / 'local' / 'project' / PRIVATE / 'SKILL.md', '---\nname: %s\n---\nSENTINEL-A-SKILL\n' % PRIVATE)
        write(a / 'skills' / 'local' / 'project' / PRIVATE / 'references' / 'so-lieu.md', 'SENTINEL-A-RESOURCE\n')
        add_index_row(a / '.agent' / 'SKILL_INDEX.md', '| %s | LOCAL | PROJECT | skills/local/project/%s/SKILL.md | Skill riêng của A. | AVAILABLE | SENTINEL-A-INDEX |' % (PRIVATE, PRIVATE))
        write(a / '.agent' / 'runtime' / 'grants.json', '{"grant": "SENTINEL-A-GRANT", "accepted_output": "SENTINEL-A-ACCEPTED"}\n')
        write(a / '.claude' / 'agents' / 'a-worker.md', 'SENTINEL-A-NATIVE\n')
        return a

    def assert_nothing_of_a(self, b):
        """B không mang nguồn, quyền, STATE, đầu ra hay skill riêng của A (so từng byte và từng đường dẫn). / Nothing of A in B."""
        for p in b.rglob('*'):
            rel = p.relative_to(b).as_posix()
            self.assertNotIn(PRIVATE, rel)
            self.assertNotIn('quy-che-rieng-a', rel)
            self.assertNotIn('ket-qua-a', rel)
            if p.is_file():
                self.assertNotIn(SENTINEL, p.read_bytes(), rel)
                self.assertNotIn(b'Du an A', p.read_bytes(), rel)
        for rel in ('.claude', '.agent/runtime/grants.json'):
            self.assertFalse((b / rel).exists(), rel)

    def assert_unselected_absent(self, base):
        """Skill thứ hai, tài nguyên riêng và script không được chọn không sang mẫu hay B. / Unselected parts never travel."""
        files = {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}
        self.assertFalse([f for f in files if 'second-draft' in f or 'notes-from-a' in f or f.endswith('probe.py')], base)
        self.assertFalse(self.script_ran.exists(), 'a skill script must never be run')

    def test_a_to_template_to_b_in_vi_and_en(self):
        """Ca dương T36: A có skill riêng + sentinel -> bản dẫn xuất khác ID vào mẫu cá nhân -> B VI và B EN. A không đổi theo mẫu."""
        a = self.make_a()
        draft = Draft(self.root, script=self.script_ran)
        tpl0, a0, man0 = fingerprint(self.tpl), fingerprint(a), manifest_of(self.tpl)
        self.assertFalse((self.tpl / '.agent' / 'PACKAGE_INFO.json').exists(), 'the personal template is clean and isolated')

        out = update_template(self.tpl, draft, ROW_OK, draft.confirmation(), a)
        self.assertEqual(out['result'], 'applied', out)
        tpl1 = fingerprint(self.tpl)
        self.assertEqual(changed(tpl0, tpl1), draft.allowed() | {MANIFEST}, 'the whole template delta is the chosen set plus the manifest')
        man1 = manifest_of(self.tpl)
        self.assertEqual({k for k in set(man0) | set(man1) if man0.get(k) != man1.get(k)}, draft.allowed(),
                         'the fixture manifest changes only for the chosen files')
        self.assertEqual(run_in(self.tpl, 'check_package.py', '--verify').returncode, 0)
        self.assertEqual(fingerprint(a), a0, 'A does not change when the template does')
        self.assert_unselected_absent(self.tpl)

        r, data, b_vi = self.new_project(self.tpl, 'Du an B')
        self.assertEqual((r.returncode, data['status']), (0, 'success'), data['message'])
        r, data, b_en = self.new_project(self.tpl, 'Project B', lang='en')
        self.assertEqual((r.returncode, data['status']), (0, 'success'), data['message'])
        self.assertEqual(fingerprint(self.tpl), tpl1, 'creating B leaves the template untouched')
        self.assertEqual(fingerprint(a), a0, 'creating B leaves A untouched')

        for b, lang in ((b_vi, 'vi'), (b_en, 'en')):
            with self.subTest(lang=lang):
                for rel, target in draft.selected:
                    if rel.startswith(lang + '/'):
                        self.assertEqual((b / target.replace('en/', '', 1) if lang == 'en' else b / target).read_bytes(), (draft.root / rel).read_bytes())
                self.assertEqual((b / 'skills' / 'local' / 'shared' / SID / 'SKILL.md').read_bytes(), (draft.root / lang / 'SKILL.md').read_bytes(),
                                 'the skill in B is the chosen language version')
                index = read(b / '.agent' / 'SKILL_INDEX.md')
                self.assertIn(draft.rows[INDEX_FILES[0 if lang == 'vi' else 1]], index.splitlines())
                self.assertEqual(index.count('| %s |' % SID), 1)
                self.assertEqual(run_in(b, 'check_package.py', '--verify').returncode, 0)
                self.assert_nothing_of_a(b)
                self.assert_unselected_absent(b)
                self.assertEqual((b / '.agent' / 'EXECUTION_PROFILE.json').read_bytes(), (self.tpl / '.agent' / 'EXECUTION_PROFILE.json').read_bytes(),
                                 'a clean profile: no choice or grant is inherited')
                self.assertNotIn(PRIVATE, index)
        self.assertEqual(read(b_vi / 'PROJECT.md').count('Du an B'), 1)

        # phạm vi/native: skill riêng của A không xuất được; shared trong B chỉ được liệt kê, không tự thành native/profile/grant
        # scope/native: A's private skill is never exported; the shared one in B is only listed, nothing is created
        host = self.root / 'host-skills'
        for base, present, absent in ((a, set(), {PRIVATE, SID}), (b_vi, {SID}, {PRIVATE})):
            r = run_in(base, 'install_skills.py', '--dest', host, '--result-json')
            _, data = result_schema.split_output(r.stdout)
            self.assertEqual((r.returncode, data['status'], data['changes']), (0, 'preview', False), 'listing only; a choice is required')
            self.assertTrue(present <= set(data['eligible']), data['eligible'])
            self.assertFalse(absent & set(data['eligible']), data['eligible'])
        r = run_in(a, 'install_skills.py', '--dest', host, '--skills', PRIVATE, '--result-json')
        self.assertEqual(r.returncode, 1)
        self.assertFalse(host.exists(), 'no installer writes into the host folder')
        self.assertEqual(fingerprint(a), a0)

    def test_not_accepted_or_without_grant_stops_the_template_update(self):
        """Ca âm T36 (HỢP TÁC + cây đích thật): REVIEW, PROJECT_ONLY, DEFER, nhãn gõ tay, xác nhận cũ, thiếu quyền ghi mẫu."""
        a = self.make_a()
        tpl0, man_stat = fingerprint(self.tpl), (self.tpl / MANIFEST).stat().st_mtime_ns
        draft = Draft(self.root)
        stale = draft.confirmation()
        stale_draft = Draft(self.root, vi_extra='\nSửa sau khi người dùng đã xem.\n', slot='draft-edited')  # nội dung đổi sau xác nhận / edited after the user saw it
        cases = [
            ('REVIEW', draft, dict(ROW_OK, status='REVIEW'), draft.confirmation(), 'STATUS_REVIEW'),
            ('DISABLED', draft, dict(ROW_OK, status='DISABLED'), draft.confirmation(), 'STATUS_DISABLED'),
            ('PROJECT_ONLY', draft, dict(ROW_OK, scope='PROJECT', notes='PROJECT_ONLY'), draft.confirmation(), 'PROJECT_ONLY'),
            ('DEFER', draft, dict(ROW_OK, notes='DEFER: thiếu bằng chứng'), draft.confirmation(), 'DEFER'),
            ('typed AVAILABLE, no conclusion', draft, dict(ROW_OK, notes='tự gõ'), draft.confirmation(), 'NOT_ROOT_ELIGIBLE'),
            ('label without any confirmation', draft, ROW_OK, None, 'NO_CONFIRMATION'),
            ('content not accepted', draft, ROW_OK, draft.confirmation(accepted_content=False), 'NO_CONFIRMATION'),
            ('eligible but no root grant', draft, ROW_OK, draft.confirmation(root_grant=None), 'NO_ROOT_GRANT'),
            ('grant for another id', draft, ROW_OK, draft.confirmation(root_grant={'target': 'personal-template', 'ids': ['other']}), 'NO_ROOT_GRANT'),
            ('confirmation of an older version', stale_draft, ROW_OK, stale, 'CONFIRMATION_STALE'),
        ]
        for name, d, row, confirm, code in cases:
            with self.subTest(case=name):
                out = update_template(self.tpl, d, row, confirm, a)
                self.assertEqual((out['result'], out['code']), ('stopped', code))
                self.assertEqual(fingerprint(self.tpl), tpl0, 'the template tree is byte-identical')
                self.assertEqual((self.tpl / MANIFEST).stat().st_mtime_ns, man_stat, 'write-manifest was not run to get past the condition')
        r, data, b = self.new_project(self.tpl, 'Du an B')
        self.assertEqual((r.returncode, data['status']), (0, 'success'), data['message'])
        self.assertFalse((b / 'skills' / 'local' / 'shared' / SID).exists())
        self.assertNotIn(SID, read(b / '.agent' / 'SKILL_INDEX.md'))
        self.assert_nothing_of_a(b)
        self.assertEqual(fingerprint(self.tpl), tpl0)

    def test_selection_is_narrow_and_nothing_existing_is_overwritten(self):
        """Chọn lọc: ID/đường dẫn trùng giữ nguyên đích; liên kết/phụ thuộc về A giữ chờ; script không chạy. Chỉ ranh giới cụ thể."""
        a = self.make_a()
        tpl0 = fingerprint(self.tpl)
        meeting = self.tpl / 'skills' / 'local' / 'shared' / 'meeting-minutes' / 'SKILL.md'
        for sid in ('meeting-minutes', 'Meeting-Minutes'):  # kể cả khác hoa/thường (Windows) / including a case-only difference
            with self.subTest(collision=sid):
                out = update_template(self.tpl, Draft(self.root, sid=sid), ROW_OK, Draft(self.root, sid=sid).confirmation(), a)
                self.assertEqual((out['result'], out['code']), ('stopped', 'ID_COLLISION'))
                self.assertEqual(fingerprint(self.tpl), tpl0)
        # va chạm đường dẫn: file người dùng đã có ở đích en/ (ID chưa có trong index) / a path collision at the en/ target
        copy = self.root / 'collision-copy'
        shutil.copytree(self.tpl, copy)
        draft = Draft(self.root)
        write(copy / 'en' / 'skills' / 'local' / 'shared' / SID / 'SKILL.md', 'FILE CỦA NGƯỜI DÙNG\n')
        copy0 = fingerprint(copy)
        out = update_template(copy, draft, ROW_OK, draft.confirmation(copy), a)
        self.assertEqual((out['result'], out['code']), ('stopped', 'PATH_COLLISION'))
        self.assertEqual(fingerprint(copy), copy0)

        for name, extra, kind in (
                ('A path', '\nXem %s/quy-che.md\n' % a.as_posix(), 'A_PATH'),
                ('private area', '\nDùng skills/local/project/%s/SKILL.md trước.\n' % PRIVATE, 'A_PROJECT_AREA'),
                ('runtime', '\nĐọc .agent/runtime/grants.json.\n', 'A_PROJECT_AREA'),
                ('link up to A', '\n[riêng](../../project/%s/SKILL.md)\n' % PRIVATE, 'LINK_OUTSIDE'),
                ('absolute link', '\n[riêng](/etc/hosts)\n', 'LINK_OUTSIDE'),
                ('external link', '\n[nguồn](https://example.com/nguon)\n', 'LINK_OUTSIDE'),
                ('bare url', '\nXem https://example.com/nguon\n', 'URL')):
            with self.subTest(boundary=name):
                d = Draft(self.root, vi_extra=extra)
                out = update_template(self.tpl, d, ROW_OK, d.confirmation(), a)
                self.assertEqual((out['result'], out['code'], out['detail']), ('stopped', 'BOUNDARY', kind))
                self.assertEqual(fingerprint(self.tpl), tpl0)
        d = Draft(self.root, vi_extra='\nXem [khung](references/handover-frame.md).\n')  # liên kết trong chính skill thì được / a link inside the skill is fine
        self.assertEqual(boundary(d, a), '')

        # script được chọn đi theo như dữ liệu, không bao giờ bị chạy bởi harness, materialize hay new_project
        # a selected script travels as data and is never run by the harness, materialize or new_project
        draft = Draft(self.root, script=self.script_ran)
        draft.selected.append(('vi/scripts/probe.py', 'skills/local/shared/%s/scripts/probe.py' % SID))
        out = update_template(self.tpl, draft, ROW_OK, draft.confirmation(), a)
        self.assertEqual(out['result'], 'applied', out)
        r, data, b = self.new_project(self.tpl, 'Du an B')
        self.assertEqual((r.returncode, data['status']), (0, 'success'), data['message'])
        self.assertTrue((b / 'skills' / 'local' / 'shared' / SID / 'scripts' / 'probe.py').is_file())
        self.assertFalse(self.script_ran.exists())
        self.assertTrue(meeting.is_file())

    def test_manifest_guard_is_real_and_not_a_substitute_for_the_list(self):
        """Guard manifest: không monkeypatch. Thêm/sửa shared mà chưa dựng manifest thì new_project từ chối; delta lạ dừng, không rebaseline."""
        a = self.make_a()
        draft = Draft(self.root)

        def refused(base, expect):
            before = fingerprint(base)
            r, data, b = self.new_project(base, 'Du an B')
            self.assertEqual((r.returncode, data['status'], data['changes']), (1, 'blocked', False), data['message'])
            self.assertIn(expect, ' '.join(f['message'] for f in data['findings']))
            self.assertFalse(b.exists())
            self.assertEqual(fingerprint(base), before)

        added = self.root / 'added-no-manifest'  # (a) thêm shared mới, manifest cũ -> thiếu/thừa tập file / new shared skill, stale manifest
        shutil.copytree(self.tpl, added)
        apply_selected(added, draft)
        refused(added, 'MANIFEST_SET_MISMATCH')
        edited = self.root / 'edited-no-manifest'  # (b) sửa shared cũ, manifest cũ -> hash lệch / old shared skill edited, stale manifest
        shutil.copytree(self.tpl, edited)
        with (edited / 'skills' / 'local' / 'shared' / 'meeting-minutes' / 'SKILL.md').open('ab') as f:
            f.write('\nĐã sửa.\n'.encode('utf-8'))
        refused(edited, 'SOURCE_MANIFEST_INCONSISTENT')

        slipped = self.root / 'stray-change'  # (c) thay đổi ngoài tập đã chọn chen vào: dừng, không dựng manifest / stray change: stop, no rebaseline
        shutil.copytree(self.tpl, slipped)
        man0, stat0 = (slipped / MANIFEST).read_bytes(), (slipped / MANIFEST).stat().st_mtime_ns

        def stray(tpl):
            with (tpl / 'AGENTS.md').open('ab') as f:
                f.write('\nGhi chú lạ.\n'.encode('utf-8'))
        out = update_template(slipped, draft, ROW_OK, draft.confirmation(slipped), a, inject=stray)
        self.assertEqual((out['result'], out['code'], out['detail']), ('stopped', 'DELTA_OUTSIDE_SELECTION', ['AGENTS.md']))
        self.assertEqual(((slipped / MANIFEST).read_bytes(), (slipped / MANIFEST).stat().st_mtime_ns), (man0, stat0), 'no rebaseline')
        refused(slipped, 'MANIFEST_SET_MISMATCH')

        # giới hạn cần biết: nếu người dùng tự chạy --write-manifest bỏ qua bước so danh sách thì máy KHÔNG chặn file thừa;
        # đó là lý do docs cấm chạy nó trước khi so danh sách. / the known limit: the machine does not catch the stray file once the manifest is rebuilt
        legit = self.root / 'rebaselined'
        shutil.copytree(slipped, legit)
        self.assertEqual(run_in(legit, 'check_package.py', '--write-manifest').returncode, 0)
        r = run_in(legit, 'new_project.py', '--name', 'X', '--dest', self.projects, '--result-json')
        self.assertEqual(result_schema.split_output(r.stdout)[1]['status'], 'preview')

        base = self.root / 'dirty-baseline'  # (d) mẫu đã lệch MANIFEST trước khi sửa: không đụng tới, không rebaseline / drifted before editing
        shutil.copytree(self.tpl, base)
        with (base / 'AGENTS.md').open('ab') as f:
            f.write('\nSửa trước.\n'.encode('utf-8'))
        base0 = fingerprint(base)
        out = update_template(base, draft, ROW_OK, draft.confirmation(base), a)
        self.assertEqual((out['result'], out['code']), ('stopped', 'BASELINE'))
        self.assertEqual(fingerprint(base), base0)

        r, data, b = self.new_project(self.tpl, 'Du an B')  # đối chứng: mẫu gốc của fixture vẫn tạo được / control: the untouched fixture still works
        self.assertEqual((r.returncode, data['status']), (0, 'success'), data['message'])

    def test_a_and_b_stay_independent(self):
        """A/B độc lập: dự án đã khởi tạo không làm mẫu; sửa A không đổi B; sửa B không đổi A hay mẫu; chấp nhận ở A không sang B."""
        a = self.make_a()
        draft = Draft(self.root)
        self.assertEqual(update_template(self.tpl, draft, ROW_OK, draft.confirmation(), a)['result'], 'applied')
        r, data, b = self.new_project(self.tpl, 'Du an B')
        self.assertEqual((r.returncode, data['status']), (0, 'success'), data['message'])

        a0, tpl0 = fingerprint(a), fingerprint(self.tpl)
        r = run_in(a, 'new_project.py', '--name', 'Tu A', '--dest', self.projects, '--apply', '--result-json')
        data = result_schema.split_output(r.stdout)[1]
        self.assertEqual((r.returncode, data['status'], data['role'], data['changes']), (1, 'blocked', 'project', False))
        self.assertFalse((self.projects / 'Tu A').exists(), 'A is never used as a template')
        self.assertEqual(fingerprint(a), a0)

        b0 = fingerprint(b)
        with (a / 'skills' / 'local' / 'project' / PRIVATE / 'SKILL.md').open('ab') as f:
            f.write(b'\nSENTINEL-A-EDITED\n')
        write(a / 'references' / 'policies' / 'nguon-moi-a.md', 'SENTINEL-A-NEW-SOURCE\n')
        write(a / '.agent' / 'runtime' / 'acceptance.json', '{"accepted": "SENTINEL-A-ACCEPTED-2"}\n')
        self.assertNotEqual(fingerprint(a), a0)
        self.assertEqual(fingerprint(b), b0, 'editing A does not change B')
        self.assertEqual(fingerprint(self.tpl), tpl0, 'editing A does not change the template')

        a1 = fingerprint(a)
        with (b / '.agent' / 'STATE.md').open('ab') as f:
            f.write('\nTiến độ riêng của B.\n'.encode('utf-8'))
        with (b / 'skills' / 'local' / 'shared' / SID / 'SKILL.md').open('ab') as f:
            f.write('\nB sửa bản dùng lại của mình.\n'.encode('utf-8'))
        write(b / 'references' / 'policies' / 'nguon-cua-b.md', 'Nguồn của B.\n')
        self.assertNotEqual(fingerprint(b), b0)
        self.assertEqual(fingerprint(a), a1, 'editing B does not change A')
        self.assertEqual(fingerprint(self.tpl), tpl0, 'editing B does not change the template')
        self.assert_nothing_of_a(b)


class PersonalReuseReview(unittest.TestCase):
    """Reviewer regressions: bind the target and bytes, reject stray baseline files and source junctions."""
    setUp = PersonalReuse.setUp

    def test_grant_for_a_different_template_preserves_the_destination(self):
        a = self.root / 'A'
        a.mkdir()
        draft = Draft(self.root)
        before = fingerprint(self.tpl)
        confirm = draft.confirmation(root_grant={'target': 'another-template', 'ids': [SID]})
        out = update_template(self.tpl, draft, ROW_OK, confirm, a)
        self.assertEqual((out['result'], out['code']), ('stopped', 'NO_ROOT_GRANT'))
        self.assertEqual(fingerprint(self.tpl), before)

    def test_changed_approved_payload_or_index_is_not_rebaselined(self):
        a = self.root / 'A'
        a.mkdir()
        draft = Draft(self.root)
        for name, target in [('payload', draft.selected[0][1]), ('index', INDEX_FILES[0])]:
            with self.subTest(name=name):
                tpl = self.root / ('template-' + name)
                shutil.copytree(self.tpl, tpl)
                before = (tpl / MANIFEST).read_bytes()

                def inject(base):
                    with (base / target).open('ab') as fh:
                        fh.write(b'\nUNAPPROVED_BYTES\n')

                confirm = draft.confirmation(root_grant={'target': tpl.resolve().as_posix(), 'ids': [SID]})
                out = update_template(tpl, draft, ROW_OK, confirm, a, inject=inject)
                self.assertEqual((out['result'], out['code']), ('stopped', 'DELTA_CONTENT_MISMATCH'))
                self.assertEqual((tpl / MANIFEST).read_bytes(), before)

    def test_unlisted_baseline_file_is_not_absorbed_into_the_manifest(self):
        a = self.root / 'A'
        a.mkdir()
        write(self.tpl / 'unexpected.md', 'Not part of the clean template.\n')
        self.assertEqual(run_in(self.tpl, 'check_package.py', '--verify').returncode, 0, 'verify alone checks listed hashes')
        before = fingerprint(self.tpl)
        draft = Draft(self.root)
        out = update_template(self.tpl, draft, ROW_OK, draft.confirmation(), a)
        self.assertEqual((out['result'], out['code']), ('stopped', 'BASELINE'))
        self.assertEqual(fingerprint(self.tpl), before)

    @unittest.skipUnless(os.name == 'nt', 'real NTFS junction probe; skipped, not passed elsewhere')
    def test_selected_source_junction_cannot_copy_a_private_resource(self):
        a = self.root / 'A'
        a.mkdir()
        write(a / 'private' / 'resource.md', 'Neutral text reached through a junction.\n')
        draft = Draft(self.root)
        link = draft.root / 'vi' / 'linked'
        made = subprocess.run(['cmd', '/c', 'mklink', '/J', str(link), str(a / 'private')], capture_output=True, text=True)
        if made.returncode:
            self.skipTest('junction could not be created: ' + made.stderr)
        self.addCleanup(lambda: os.path.isdir(link) and os.rmdir(link))  # remove the junction itself before TemporaryDirectory cleanup
        draft.selected.append(('vi/linked/resource.md', 'skills/local/shared/%s/references/resource.md' % SID))
        before = fingerprint(self.tpl)
        out = update_template(self.tpl, draft, ROW_OK, draft.confirmation(), a)
        self.assertEqual((out['result'], out['code']), ('stopped', 'BOUNDARY'))
        self.assertEqual(fingerprint(self.tpl), before)


if __name__ == '__main__':
    unittest.main()
