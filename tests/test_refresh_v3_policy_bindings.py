"""Bounded maintenance replay tests; no live owner/fixture/pin writes.

Coupling cases are a hypothetical projection model, not a deployed design or
backward-compatibility proof. P-CTX1 is declarative in the current artifact
contract: these tests neither require full-chain dependency binding nor evaluate
P-CTX1 actions.
"""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'working/an-c2-repair-20261028/scripts/refresh_v3_policy_bindings.py'
spec = importlib.util.spec_from_file_location('refresh_v3_policy_bindings', HELPER)
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


class RefreshBindings(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'data'
        names = refresh.example_names(ROOT)
        self.rels = [refresh.POLICY, refresh.VECTORS, refresh.CHECK_TEST, refresh.DRAFT_TEST,
                     refresh.EXAMPLES + '/EXPECTED.json'] + [refresh.EXAMPLES + '/' + n for n in names]
        for rel in self.rels:
            dest = self.root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)

    def snapshot(self, root=None):
        return {r: (root or self.root).joinpath(r).read_bytes() for r in self.rels}

    def change_owner(self):
        path = self.root / refresh.POLICY
        raw = path.read_bytes()
        policy = refresh.parse(raw)
        policy['operational_context_protocol']['entrypoint_sha256'] = 'sha256:' + '1' * 64
        path.write_bytes(refresh.serialize(policy, raw))

    def test_real_current_tree_is_noop_and_all_protected_bytes_survive(self):
        before = self.snapshot(ROOT)
        result = refresh.plan(ROOT)
        self.assertEqual(result['changed'], [])
        self.assertEqual(result['allowed_leaves'], 43)
        self.assertEqual(result['pins'], refresh.OLD_PINS)
        self.assertEqual(self.snapshot(ROOT), before)

    def test_changed_owner_refreshes_exactly_23_json_and_two_pin_modules_then_noop(self):
        self.change_owner()
        # Executable-looking data under a temp root must never be loaded.
        evil = self.root / '.cvf/checks/v3/canon.py'
        evil.parent.mkdir(parents=True)
        evil.write_text("raise RuntimeError('untrusted temp code executed')", encoding='utf-8')
        draft = self.root / refresh.DRAFT_TEST
        draft.write_bytes(draft.read_bytes() + b'\n# prior user WIP: keep this exact byte string\n')
        before = self.snapshot()
        result = refresh.plan(self.root)
        self.assertEqual(self.snapshot(), before, 'dry run wrote input bytes')
        self.assertEqual(len(result['changed']), 25)
        self.assertEqual(sum(r.endswith('.json') for r in result['changed']), 23)
        self.assertNotIn(refresh.POLICY, result['changed'])
        self.assertNotIn(refresh.EXAMPLES + '/EXPECTED.json', result['changed'])
        for rel, new in result['after'].items():
            if not rel.endswith('.json'):
                continue
            old = refresh.parse(before[rel])
            changed = refresh.parse(new)
            self.assertTrue(refresh.same_order_shape(old, changed))
            changes = refresh.leaf_paths(old, lambda p, v: refresh.get(changed, p) != v)
            self.assertTrue(all(p[-1] == 'policy_digest' or p == ('policy_digest', 'digest') for p in changes))
            for path in changes:
                self.assertEqual(refresh.get(changed, path), result['digest'])
                refresh.put(changed, path, refresh.get(old, path))
            self.assertEqual(refresh.serialize(changed, new), before[rel])
        refresh.apply(result)
        self.assertEqual(refresh.plan(self.root)['changed'], [])
        self.assertTrue(draft.read_bytes().endswith(b'# prior user WIP: keep this exact byte string\n'))
        self.assertEqual((self.root / refresh.POLICY).read_bytes(), before[refresh.POLICY])
        names = refresh.example_names(self.root)
        joined = '\n'.join(n + ':' + refresh.sha((self.root / refresh.EXAMPLES / n).read_bytes()) for n in names)
        self.assertEqual(result['pins']['examples'], refresh.sha(joined.encode())[:16])

    def test_refuses_stale_digest_shape_key_order_and_serialization_before_any_write(self):
        self.change_owner()
        pristine = self.snapshot()
        vector = self.root / refresh.VECTORS
        original = vector.read_bytes()
        obj = refresh.parse(original)
        bads = []
        stale = copy.deepcopy(obj)
        stale['policy_digest']['digest'] = 'sha256:' + '0' * 64
        bads.append(refresh.serialize(stale, original))
        extra = copy.deepcopy(obj)
        extra['unexpected'] = True
        bads.append(refresh.serialize(extra, original))
        reverse_keys = dict(reversed(list(obj.items())))
        bads.append(refresh.serialize(reverse_keys, original))
        bads.append(original.replace(b'  "', b'   "', 1))
        for bad in bads:
            with self.subTest(kind=bad[:35]):
                vector.write_bytes(bad)
                before = self.snapshot()
                with self.assertRaises(refresh.Refused):
                    refresh.plan(self.root)
                self.assertEqual(self.snapshot(), before)
        vector.write_bytes(original)
        self.assertEqual(self.snapshot(), pristine)

    def test_compare_before_preflight_rejects_late_change_before_any_write(self):
        self.change_owner()
        result = refresh.plan(self.root)
        path = self.root / refresh.DRAFT_TEST
        path.write_bytes(path.read_bytes() + b'\n# concurrent edit\n')
        before = self.snapshot()
        with self.assertRaisesRegex(refresh.Refused, 'compare-before'):
            refresh.apply(result)
        self.assertEqual(self.snapshot(), before)

    def test_crlf_and_no_final_newline_are_preserved_in_data_and_test_wip(self):
        self.change_owner()
        for rel in self.rels:
            if rel == refresh.POLICY:
                continue
            path = self.root / rel
            path.write_bytes(path.read_bytes().replace(b'\r\n', b'\n').rstrip(b'\n').replace(b'\n', b'\r\n'))
        result = refresh.plan(self.root)
        for rel in result['changed']:
            raw = result['after'][rel]
            self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))
            self.assertFalse(raw.endswith(b'\r\n'))
        refresh.apply(result)
        self.assertEqual(refresh.plan(self.root)['changed'], [])

    def test_exact_prefix_filter_excludes_uppercase_expected_and_rejects_extra_examples(self):
        self.assertNotIn('EXPECTED.json', refresh.example_names(self.root))
        (self.root / refresh.EXAMPLES / 'ex99_unexpected.json').write_bytes(b'{}')
        with self.assertRaises(refresh.Refused):
            refresh.plan(self.root)

    def test_modified_trusted_fixture_baseline_is_not_silently_adopted(self):
        real_read = Path.read_bytes

        def changed(path):
            raw = real_read(path)
            return raw + b' ' if path == ROOT / refresh.VECTORS else raw

        with mock.patch.object(Path, 'read_bytes', changed):
            with self.assertRaisesRegex(refresh.Refused, 'trusted fixture baseline changed'):
                refresh.plan(self.root)

    def test_duplicate_examples_pin_assignment_is_refused_before_write(self):
        path = self.root / refresh.CHECK_TEST
        path.write_bytes(path.read_bytes() + b'\nV3_EXAMPLES_PIN = compute_something()\n')
        before = self.snapshot()
        with self.assertRaisesRegex(refresh.Refused, 'ambiguous examples pin assignment'):
            refresh.plan(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_stale_pin_refused_and_unrelated_current_draft_pin_preserved(self):
        self.change_owner()
        path = self.root / refresh.DRAFT_TEST
        raw = path.read_bytes().replace(b"'65fd87929e886393'", b"'1234567890abcdef'")
        path.write_bytes(raw)
        result = refresh.plan(self.root)
        self.assertIn(b"'1234567890abcdef'", result['after'][refresh.DRAFT_TEST])
        path.write_bytes(raw.replace(refresh.OLD_PINS[refresh.POLICY].encode(), b'0000000000000000'))
        before = self.snapshot()
        with self.assertRaisesRegex(refresh.Refused, 'stale pin'):
            refresh.plan(self.root)
        self.assertEqual(self.snapshot(), before)

    def test_unsafe_path_and_mocked_reparse_target_are_refused(self):
        with self.assertRaises(refresh.Refused):
            refresh.safe_path(self.root, '../outside.json')
        real_lstat = Path.lstat
        victim = self.root / refresh.VECTORS

        def linked(path, *args, **kwargs):
            s = real_lstat(path, *args, **kwargs)
            if path == victim:
                return type('Reparse', (), {'st_mode': s.st_mode, 'st_file_attributes': 0x400})()
            return s

        with mock.patch.object(Path, 'lstat', linked):
            with self.assertRaisesRegex(refresh.Refused, 'linked target'):
                refresh.plan(self.root)

    def test_trusted_owner_agrees_with_independent_reference_and_bounded_coupling_model(self):
        ref_path = ROOT / 'tests/test_control_v3_candidate.py'
        ref_spec = importlib.util.spec_from_file_location('_b1_trusted_reference', ref_path)
        reference = importlib.util.module_from_spec(ref_spec)
        ref_spec.loader.exec_module(reference)
        canon = refresh.load_canon()
        policy = refresh.parse((ROOT / refresh.POLICY).read_bytes())
        ctx_changed = copy.deepcopy(policy)
        ctx_changed['operational_context_protocol']['entrypoint_sha256'] = 'sha256:' + '1' * 64
        publish_changed = copy.deepcopy(policy)
        publish_changed['owner_protocols'][0]['entrypoint_sha256'] = 'sha256:' + '2' * 64
        for p in (policy, ctx_changed, publish_changed):
            self.assertEqual(canon.digest_of(canon.policy_part(p)), reference.digest_of(reference.policy_part(p)))
        whole = lambda p: canon.digest_of(canon.policy_part(p))

        def hypothetical_projection(p):
            p = copy.deepcopy(p)
            del p['operational_context_protocol']
            return whole(p)

        self.assertNotEqual(whole(policy), whole(ctx_changed))
        self.assertEqual(hypothetical_projection(policy), hypothetical_projection(ctx_changed))
        self.assertNotEqual(hypothetical_projection(policy), hypothetical_projection(publish_changed))
        # Declarative contract boundary, not an evaluator claim.
        self.assertIn('do not evaluate it', policy['note'])
        self.assertEqual((ROOT / refresh.POLICY).read_bytes(), (self.root / refresh.POLICY).read_bytes())


if __name__ == '__main__':
    unittest.main()
