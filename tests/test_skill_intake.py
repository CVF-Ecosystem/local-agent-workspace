"""Tiếp nhận skill/gói: kiểm thử logic trên bản sao tạm của package, không dùng agent thật hay người đánh giá.
Skill/pack intake: logic tests on a disposable copy of the package. No real agent run and no human evaluation here:
these tests only show that the tools keep candidates, accepted skills and root updates apart (see skills/README.md).
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


class PackIntake(IntakeBase):
    def test_shipped_packs_are_deferred_candidates_with_a_record_that_exists(self):
        _, _, data = self.structured('pack.py', 'list')
        for p in data['packs']:
            with self.subTest(pack=p['name']):
                self.assertEqual((p['intake']['state'], p['intake']['reason']), ('candidate', 'deferred'))
                self.assertTrue((self.base / 'packs' / p['name'] / 'references' / 'intake-record.md').is_file())

    def test_candidate_pack_installs_as_review_and_structure_check_is_not_intake(self):
        self.init_project()
        self.set_intake('cang-logistics')  # bỏ hồ sơ để thử trường hợp chưa có hồ sơ / drop the record: the no-record case
        result, _, data = self.structured('pack.py', 'check', 'cang-logistics')
        self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertEqual(data['intake']['cang-logistics']['state'], 'candidate')
        result, _, data = self.structured('pack.py', 'add', 'cang-logistics')
        self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertEqual((data['intake']['state'], data['intake']['reason']), ('candidate', 'no_record'))
        self.assertEqual(self.statuses()[SKILL], 'REVIEW')
        self.assertTrue(data['next_actions'])

    def test_supplement_accepted_but_unproven_duplicate_deferred(self):
        self.init_project()
        cases = {  # gói: (khối intake, trạng thái chỉ mục, lý do) / pack: (intake, index status, reason)
            'cang-logistics': ({'decision': 'ADD_MISSING_PART', 'relation': 'SUPPLEMENT'}, 'AVAILABLE', 'add_missing_part'),
            'hanh-chinh-nhan-su': ({'decision': 'PROJECT_ONLY', 'relation': 'REPLACEMENT'}, 'REVIEW', 'no_comparison'),
            'ke-toan-noi-bo': ({'decision': 'PROJECT_ONLY', 'relation': 'UNKNOWN'}, 'REVIEW', 'native_unknown'),
            'van-thu-luu-tru': ({'decision': 'ROOT_ELIGIBLE', 'relation': 'REPLACEMENT', 'comparison': 'references/ab.md'},
                                'AVAILABLE', 'root_eligible'),
            'phap-ly': ({'decision': 'ADD_MISSING_PART', 'relation': 'SUPPLEMENT', 'record': 'references/missing.md'},
                        'REVIEW', 'record_not_found'),
        }
        for name, (intake, status, reason) in cases.items():
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
                self.assertEqual({self.statuses()[s] for s in skills}, {status})
        # ROOT_ELIGIBLE không kèm quyền ghi gốc thì chưa được cập nhật gốc / no root grant: no root update
        _, _, data = self.structured('pack.py', 'list')
        self.assertFalse({p['name']: p for p in data['packs']}['van-thu-luu-tru']['intake']['root_update'])

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

    def test_version_change_reopens_review_while_user_choices_survive_same_version(self):
        self.init_project()
        self.set_intake('cang-logistics', {'decision': 'ADD_MISSING_PART', 'relation': 'SUPPLEMENT', 'record': self.record('cang-logistics')})
        self.structured('pack.py', 'add', 'cang-logistics')
        self.structured('pack.py', 'add', 'hanh-chinh-nhan-su')  # ứng viên / candidate
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE')
        self.assertEqual(self.statuses()['hr-admin-vn'], 'REVIEW')
        self.set_status('hr-admin-vn', 'AVAILABLE')  # người dùng nhận cho project này / the user accepts it for this project

        for name in ('cang-logistics', 'hanh-chinh-nhan-su'):  # cùng phiên bản, đổi nội dung / same version, changed text
            readme = self.base / 'packs' / name / 'README.md'
            write(readme, read(readme) + '\nSửa nhỏ cùng phiên bản.\n')
            result, _, data = self.structured('pack.py', 'update', name, '--apply')
            self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE')
        self.assertEqual(self.statuses()['hr-admin-vn'], 'AVAILABLE', 'reuse within the same version needs no new approval')

        self.set_status('hr-admin-vn', 'DISABLED')
        for name in ('cang-logistics', 'hanh-chinh-nhan-su'):  # bản mới, hồ sơ cũ / new version, old record
            meta = json.loads(read(self.pack_json(name)))
            meta['version'] = '0.9.0'
            write(self.pack_json(name), json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
        result, human, data = self.structured('pack.py', 'update', 'cang-logistics')
        self.assertEqual((result.returncode, data['status'], data['intake']['reason']), (0, 'preview', 'version_changed'))
        self.assertIn({'path': 'skills/local/packs/cang-logistics/pack.json', 'action': 'update'}, data['files'])
        self.assertIn('REVIEW', human)
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE', 'preview must not change the index')
        self.structured('pack.py', 'update', 'cang-logistics', '--apply')
        self.structured('pack.py', 'update', 'hanh-chinh-nhan-su', '--apply')
        self.assertEqual(self.statuses()[SKILL], 'REVIEW', 'an approved old version does not approve the new one')
        self.assertEqual(self.statuses()['hr-admin-vn'], 'DISABLED', 'the user choice to disable is kept')

    def test_withdrawn_record_in_same_version_returns_to_review_and_refusal_is_reported(self):
        self.init_project()
        rec = self.record('cang-logistics')
        self.set_intake('cang-logistics', {'decision': 'ADD_MISSING_PART', 'relation': 'SUPPLEMENT', 'record': rec})
        self.structured('pack.py', 'add', 'cang-logistics')
        self.assertEqual(self.statuses()[SKILL], 'AVAILABLE')
        # cùng phiên bản, hồ sơ chuyển sang hoãn: AVAILABLE do công cụ ghi không được giữ / same version, record deferred
        self.set_intake('cang-logistics', {'decision': 'DEFER', 'relation': 'SUPPLEMENT', 'record': rec})
        result, _, data = self.structured('pack.py', 'update', 'cang-logistics', '--apply')
        self.assertEqual((result.returncode, data['status']), (0, 'success'))
        self.assertEqual(self.statuses()[SKILL], 'REVIEW')
        # hồ sơ ghi không nhận đúng bản đang cài: update bị chặn, check phải báo / refusal of the installed version
        self.set_intake('cang-logistics', {'decision': 'REJECT_VERSION', 'relation': 'SUPPLEMENT', 'record': rec})
        result, _, data = self.structured('pack.py', 'update', 'cang-logistics', '--apply')
        self.assertEqual((result.returncode, data['status']), (1, 'blocked'))
        result, _, data = self.structured('pack.py', 'check', 'cang-logistics')
        self.assertEqual((result.returncode, data['status']), (1, 'issues'))
        self.assertTrue(any('pack.py remove cang-logistics' in f['message'] for f in data['findings']))

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
        write(self.base / 'packs' / 'cang-logistics' / 'skills' / SKILL / 'scripts' / 'probe.py', probe)
        write(self.base / 'packs' / 'cang-logistics' / 'skills' / SKILL / 'scripts' / '__init__.py', probe)
        self.structured('pack.py', 'check', 'cang-logistics')
        self.structured('pack.py', 'add', 'cang-logistics')
        self.structured('pack.py', 'list')
        self.structured('install_skills.py', '--dest', Path(self.tmp.name) / 'dest', '--all', '--include-packs')
        self.assertFalse(sentinel.exists())


class InstallIntake(IntakeBase):
    def test_only_accepted_local_skills_are_exported(self):
        self.init_project()
        self.structured('pack.py', 'add', 'cang-logistics')  # ứng viên / candidate
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
        self.assertEqual(self.run_in(proj, 'pack.py', 'add', 'cang-logistics').returncode, 0)
        idx = proj / '.agent' / 'SKILL_INDEX.md'
        write(idx, read(idx).replace('| REVIEW | Gói/Pack cang-logistics', '| AVAILABLE | Gói/Pack cang-logistics'))
        installed = proj / 'skills' / 'local' / 'packs' / 'cang-logistics' / 'skills' / SKILL / 'SKILL.md'
        installed_before, index_before = installed.read_bytes(), read(idx)

        root = self.base  # bộ mẫu gốc đổi skill dùng chung và gói / the template root changes a shared skill and a pack
        for rel in ('skills/local/shared/meeting-minutes/SKILL.md', 'packs/cang-logistics/skills/%s/SKILL.md' % SKILL):
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
