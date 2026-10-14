"""Tiếp nhận skill/gói: kiểm thử logic trên bản sao tạm của package, không dùng agent thật hay người đánh giá.
Skill/pack intake: logic tests on a disposable copy of the package. No real agent run and no human evaluation here:
these tests only show that the tools keep a pack's CLAIM, the user's CONFIRMATION and the root update apart, that a
confirmation is bound to the installed content, and that nothing is exported on a label alone (see skills/README.md).
"""
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from test_structured_tools import MARKER, StructuredBase, read, write
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
        return self.structured('pack.py', 'confirm', name, *(['--apply'] if apply else []))

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


if __name__ == '__main__':
    unittest.main()
