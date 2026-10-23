"""V4 compute route: the narrow `tools/office_compute.py` owner and the opt-in `compute_route` of `office.compose`.

What these tests prove: the owner computes only the preset operations on Decimal over exactly the CSV the current TASK lists, keeps zero / missing /
not-applicable / ambiguous cells apart, never drops duplicates, refuses (before reading the source) on scope, permission, operation, TASK or path problems
without a fallback, writes nothing, and gives a result whose digests can be recomputed; the default compose output and the native exporter are unchanged,
and the opt-in route only adds a separate `ROUTE_READY_UNVERIFIED` / `ROUTE_REFUSED` dimension with a different Worker hand-over.

What they do NOT prove: that a host gave any specialist a shell tool, that a specialist ever called the command, or the quality of any method. A probe
or route receipt checks structure and bytes only. Everything runs on fake data in temporary folders.
"""
import ast
import contextlib
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tests'))
import native_agents  # noqa: E402
import office  # noqa: E402
import office_compute as oc  # noqa: E402
from test_office import make_link, office_root, request, sha, tree  # noqa: E402  (helpers only)

ORDERS = 'working/lab/data/orders.csv'
QUOTES = 'working/lab/data/quotes.csv'
TASK_REL = 'working/lab/t1/TASK.json'
SCOPE_REL = 'working/lab/meta/compute-scope.json'
PROBE_REL = 'working/lab/meta/probe.json'
ORDERS_CSV = ('id,period,qty,net_vnd_per_pack\nO01,2026-10,10,120000\nO02,2026-10,5,126000\nO03,2026-10,0,150000\nO04,2026-10,,120000\n'
              'O05,2026-10,NA,120000\nO06,2026-09,2,118000\nO07,2026-10,3,120000\n')
QUOTES_CSV = ('id,period,unit,price_type,currency,price\nQ01,2026-10,pack,NET,VND,120000\nQ02,2026-10,pack,NET,VND,126000\nQ03,2026-10,piece,NET,VND,15000\n'
              'Q04,2026-10,pack,GROSS,VND,129600\nQ05,2026-09,pack,NET,VND,118000\nQ06,2026-10,pack,NET,USD,5\n')
AGG = {'filters': [{'column': 'period', 'op': 'eq', 'value': '2026-10'}], 'key': ['id'],
       'measures': [{'name': 'rows', 'kind': 'count_rows'}, {'name': 'qty', 'kind': 'sum', 'column': 'qty'},
                    {'name': 'revenue', 'kind': 'sum_product', 'columns': ['qty', 'net_vnd_per_pack']},
                    {'name': 'avg_price', 'kind': 'weighted_mean', 'columns': ['net_vnd_per_pack', 'qty'], 'round_places': 0}]}
CMP = {'columns': {'id': 'id', 'period': 'period', 'unit': 'unit', 'price_type': 'price_type', 'currency': 'currency', 'price': 'price'},
       'frame': {'period': '2026-10', 'price_type': 'NET', 'currency': 'VND', 'unit': 'pack'},
       'conversions': [{'from_unit': 'piece', 'to_unit': 'pack', 'multiply': '10'}], 'round_places': 0}


def write(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode('utf-8') if isinstance(text, str) else text)


def scope_doc(status='ALLOWED', operations=('aggregate', 'compare_prices'), methods=('data-analyst', 'market-analyst')):
    doc = {'schema': oc.SCHEMA_SCOPE, 'scope_id': 'test-lab', 'permission': {'status': status, 'basis': 'fixture'}, 'operations': list(operations),
           'methods': list(methods)}
    if status is None:
        del doc['permission']['status']
    return json.dumps(doc)


class Lab:
    """A project-shaped folder with the office files, two CSV, a lab scope and a marker TASK for one method."""

    def __init__(self, base, method='data-analyst', orders=ORDERS_CSV, quotes=QUOTES_CSV, scope=None):
        self.root = Path(base)
        office_root(self.root, with_source=False)
        write(self.root, ORDERS, orders)
        write(self.root, QUOTES, quotes)
        write(self.root, SCOPE_REL, scope if scope is not None else scope_doc())
        self.method = method
        self.set_task()

    def digest(self, rel):
        return sha((self.root / rel).read_bytes())

    def set_task(self, inputs=(ORDERS, QUOTES), revision=1, method=None, drop_marker=False, role='worker'):
        comp = office.compose({'method': method or self.method, 'reason': 'Kiểm công cụ tính trong test.', 'request': 'Tính trên dữ liệu thử.',
                               'sources': [{'path': p} for p in inputs]}, root=str(self.root))
        frag = comp['task_fragment']
        doc = {'schema_version': 'law.cvf.control/3', 'record_type': 'task', 'task_id': 't1', 'task_revision': revision,
               'authority': {'subject': {'role': role}}, 'envelope': {'role': role},
               'acceptance': {'requirements': [] if drop_marker else [frag['acceptance_requirement']]},
               'context_refs': [] if drop_marker else frag['context_refs'], 'inputs': frag['inputs']}
        write(self.root, TASK_REL, json.dumps(doc))

    def req(self, operation='aggregate', source=ORDERS, params=None, **over):
        r = {'schema': oc.SCHEMA_REQUEST, 'actor': 'test-specialist', 'task': {'path': TASK_REL, 'task_id': 't1', 'task_revision': 1, 'digest': self.digest(TASK_REL)},
             'scope': SCOPE_REL, 'operation': operation, 'inputs': [{'path': source, 'digest': self.digest(source)}],
             'params': copy.deepcopy(params if params is not None else (AGG if operation == 'aggregate' else CMP))}
        r.update(over)
        return r

    def run(self, **kw):
        return oc.run(self.req(**kw), self.root)


def groups(res):
    return res['result']['groups']


def measure(res, name, group=0):
    return next(m for m in groups(res)[group]['measures'] if m['name'] == name)


class ComputeBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.lab = Lab(self._tmp.name)

    def refused(self, res, stage, code_prefix=''):
        self.assertEqual(res['outcome'], 'REFUSED', res)
        self.assertEqual(res['stage'], stage, res)
        self.assertTrue(res['code'].startswith(code_prefix), res)
        self.assertEqual(res['writes'], [])
        return res


class Positive(ComputeBase):
    def test_orders_month_totals_and_classes(self):
        res = self.lab.run()
        self.assertEqual(res['outcome'], 'COMPUTED', res)
        self.assertEqual([s['step'] for s in res['result']['steps']], ['load', 'filter'])
        self.assertEqual((res['result']['steps'][0]['rows'], res['result']['steps'][1]['rows_after']), (7, 6))
        self.assertEqual(measure(res, 'rows')['value'], '6')
        qty = measure(res, 'qty')
        self.assertEqual(qty['value'], '18')
        self.assertEqual((qty['rows_counted'], qty['rows_zero'], qty['rows_excluded']), (4, 1, 2))
        reasons = {e['key']['id']: e['reasons']['qty'] for e in qty['excluded']}
        self.assertEqual(reasons, {'O04': 'MISSING', 'O05': 'NOT_APPLICABLE'})
        self.assertEqual(measure(res, 'revenue')['value'], '2190000')
        self.assertEqual(measure(res, 'avg_price')['value'], '121667')
        self.assertEqual(res['result']['totals_status'], 'CLEAN_AS_DEFINED')
        self.assertEqual(res['result']['issues'], [])

    def test_cross_check_by_independent_route(self):
        """Totals recomputed with csv + Fraction, a route that shares no code with the owner."""
        import csv
        rows = [r for r in csv.DictReader(io.StringIO(ORDERS_CSV)) if r['period'] == '2026-10']
        good = [r for r in rows if r['qty'] not in ('', 'NA')]
        qty = sum(int(r['qty']) for r in good)
        revenue = sum(int(r['qty']) * int(r['net_vnd_per_pack']) for r in good)
        avg = Fraction(revenue, qty)
        res = self.lab.run()
        self.assertEqual((measure(res, 'qty')['value'], measure(res, 'revenue')['value']), (str(qty), str(revenue)))
        self.assertEqual(measure(res, 'avg_price')['value'], str(int((Decimal(avg.numerator) / Decimal(avg.denominator)).quantize(Decimal(1), rounding=ROUND_HALF_UP))))

    def test_group_by_and_filter_in(self):
        params = {'filters': [{'column': 'period', 'op': 'in', 'values': ['2026-10', '2026-09']}], 'group_by': ['period'], 'key': ['id'],
                  'measures': [{'name': 'qty', 'kind': 'sum', 'column': 'qty'}]}
        res = self.lab.run(params=params)
        self.assertEqual([(g['group']['period'], g['measures'][0]['value']) for g in groups(res)], [('2026-09', '2'), ('2026-10', '18')])

    def test_compare_prices_frame_and_conversion(self):
        res = self.lab.run(operation='compare_prices', source=QUOTES)
        self.assertEqual(res['outcome'], 'COMPUTED', res)
        rows = {r['id']: r for r in res['result']['rows']}
        self.assertEqual([i for i, r in rows.items() if r['in_frame']], ['Q01', 'Q02', 'Q03'])
        self.assertEqual((rows['Q03']['converted_price'], rows['Q03']['formula']), ('150000', '15000 x 10 (piece -> pack)'))
        self.assertEqual(rows['Q04']['reasons'], ['OUT_OF_FRAME:price_type=GROSS'])
        self.assertEqual(rows['Q05']['reasons'], ['OUT_OF_FRAME:period=2026-09'])
        self.assertEqual(rows['Q06']['reasons'], ['OUT_OF_FRAME:currency=USD'])
        stats = res['result']['stats']
        self.assertEqual((stats['count'], stats['min'], stats['max'], stats['spread'], stats['mean']), (3, '120000', '150000', '30000', '132000'))
        self.assertEqual(res['result']['stats_status'], 'CLEAN_AS_DEFINED')

    def test_no_conversion_means_excluded_not_guessed(self):
        csv_text = QUOTES_CSV + 'Q07,2026-10,carton,NET,VND,1000\n'
        lab = Lab(self._tmp.name + '/b', quotes=csv_text)
        res = lab.run(operation='compare_prices', source=QUOTES)
        row = next(r for r in res['result']['rows'] if r['id'] == 'Q07')
        self.assertEqual((row['in_frame'], row['reasons']), (False, ['UNIT_NO_CONVERSION:carton']))

    def test_large_exact_fraction_survives_aggregate_and_price_conversion(self):
        price = '999999999999999999.99'
        factor = '999999999999999999'
        expected = '999999999999999998990000000000000000.01'
        orders = 'id,price,qty\nO1,%s,%s\n' % (price, factor)
        quotes = 'id,period,unit,price_type,currency,price\nQ1,2026-10,piece,NET,VND,%s\n' % price
        lab = Lab(self._tmp.name + '/exact', orders=orders, quotes=quotes)
        aggregate = lab.run(params={'measures': [{'name': 'product', 'kind': 'sum_product', 'columns': ['price', 'qty']}]})
        self.assertEqual(aggregate['outcome'], 'COMPUTED', aggregate)
        self.assertEqual(measure(aggregate, 'product')['value'], expected)
        compare = copy.deepcopy(CMP)
        compare['conversions'][0]['multiply'] = factor
        compare['round_places'] = 2
        result = lab.run(operation='compare_prices', source=QUOTES, params=compare)
        self.assertEqual(result['outcome'], 'COMPUTED', result)
        self.assertEqual(result['result']['rows'][0]['converted_price'], expected)
        self.assertEqual(result['result']['stats']['mean'], expected)

    def test_deterministic_and_digests_recompute(self):
        before = tree(self.lab.root)
        a, b = self.lab.run(), self.lab.run()
        self.assertEqual(a, b)
        self.assertEqual(before, tree(self.lab.root), 'the owner must write nothing')
        body = {k: v for k, v in a.items() if k != 'result_digest'}
        self.assertEqual(a['result_digest'], oc.sha_of(json.dumps(body, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('utf-8')))
        self.assertEqual(a['request_digest'], oc.sha_of(json.dumps(self.lab.req(), ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode('utf-8')))
        self.assertEqual(a['inputs'][0]['digest'], self.lab.digest(ORDERS))
        self.assertEqual((a['task']['task_id'], a['task']['method'], a['actor_declared']), ('t1', 'data-analyst', 'test-specialist'))
        self.assertFalse(any(a['claims'].values()))

    def test_reads_are_exactly_the_bound_files_and_source_last(self):
        res = self.lab.run()
        self.assertEqual(res['reads'][0], TASK_REL)
        self.assertEqual(res['reads'][-1], ORDERS)
        self.assertEqual(sorted(set(res['reads'])), sorted([TASK_REL, 'roles/office/catalog.json', 'roles/office/data-analyst.md', SCOPE_REL, ORDERS]))
        self.assertNotIn(QUOTES, res['reads'])


class DataIssues(ComputeBase):
    DIRTY = 'id,period,qty,net_vnd_per_pack\nO01,2026-10,10,120000\nO02,2026-10,5,126000\nO02,2026-10,7,126000\nO03,2026-10,1.234,150000\n'

    def test_duplicate_key_and_ambiguous_number_are_not_resolved(self):
        lab = Lab(self._tmp.name + '/d', orders=self.DIRTY)
        res = lab.run()
        self.assertEqual(res['outcome'], 'COMPUTED', res)
        self.assertEqual(res['result']['totals_status'], 'NOT_CLEAN')
        issues = res['result']['issues']
        self.assertEqual(sorted(i['code'] for i in issues if i['code'] == 'DUPLICATE_KEY'), ['DUPLICATE_KEY'])
        self.assertEqual(sorted(i['measure'] for i in issues if i['code'] == 'AMBIGUOUS_NUMBER'), ['avg_price', 'qty', 'revenue'])
        dup = next(i for i in res['result']['issues'] if i['code'] == 'DUPLICATE_KEY')
        self.assertEqual((dup['key'], dup['conflicting'], [r['line'] for r in dup['rows']]), ({'id': 'O02'}, True, [3, 4]))
        qty = measure(res, 'qty')
        self.assertEqual(qty['value'], '22', 'duplicates stay in the total as given; the ambiguous row is not in it')
        self.assertEqual(qty['ambiguous_rows'][0]['raw'], {'qty': '1.234'})
        self.assertEqual(qty['alternatives']['totals_if'], {'thousands': '1256', 'decimal': '23.234'})

    def test_identical_duplicate_is_flagged_not_dropped(self):
        lab = Lab(self._tmp.name + '/e', orders='id,period,qty,net_vnd_per_pack\nA,2026-10,1,10\nA,2026-10,1,10\n')
        res = lab.run()
        self.assertEqual(measure(res, 'qty')['value'], '2')
        self.assertEqual([(i['code'], i['conflicting']) for i in res['result']['issues']], [('DUPLICATE_KEY', False)])

    def test_market_conflict_same_id_two_prices(self):
        conflict = QUOTES_CSV + 'Q02,2026-10,pack,NET,VND,127000\n'
        lab = Lab(self._tmp.name + '/f', quotes=conflict)
        res = lab.run(operation='compare_prices', source=QUOTES)
        self.assertEqual(res['result']['stats_status'], 'NOT_CLEAN')
        issue = res['result']['issues'][0]
        self.assertEqual((issue['code'], issue['id'], issue['conflicting']), ('DUPLICATE_ID', 'Q02', True))
        self.assertEqual(sorted(r['cells']['price'] for r in issue['rows']), ['126000', '127000'])
        self.assertEqual(res['result']['stats']['count'], 4, 'both rows stay in the frame; the tool does not pick one')

    def test_classify_table(self):
        got = {raw: oc.classify(raw)[0] for raw in ('', 'NA', '0', '-0', '12', '12.5', '1.234', '1,234', '1.234.567', '12,5', ' 5', 'abc', '1e3', '5.', '0.000')}
        self.assertEqual(got, {'': 'MISSING', 'NA': 'NOT_APPLICABLE', '0': 'ZERO', '-0': 'ZERO', '12': 'NUMBER', '12.5': 'NUMBER', '1.234': 'AMBIGUOUS',
                               '1,234': 'AMBIGUOUS', '1.234.567': 'AMBIGUOUS', '12,5': 'AMBIGUOUS', ' 5': 'INVALID', 'abc': 'INVALID', '1e3': 'INVALID',
                               '5.': 'INVALID', '0.000': 'AMBIGUOUS'})

    def test_malformed_csv_and_missing_column_are_refused(self):
        lab = Lab(self._tmp.name + '/g', orders='id,period,qty\nA,2026-10\n')
        self.refused(lab.run(params={'measures': [{'name': 'n', 'kind': 'count_rows'}]}), 'DATA_REFUSED', 'CSV_ROW_SHAPE')
        self.refused(self.lab.run(params={'measures': [{'name': 's', 'kind': 'sum', 'column': 'nope'}]}), 'DATA_REFUSED', 'COLUMN_NOT_FOUND')
        lab2 = Lab(self._tmp.name + '/h', orders='\ufeffid,period\nA,1\n')
        self.refused(lab2.run(params={'measures': [{'name': 'n', 'kind': 'count_rows'}]}), 'DATA_REFUSED', 'CSV_BOM')


class Refusals(ComputeBase):
    """Every refusal happens before the source is read (spy on the one read gate) and no fallback runs."""

    def spy(self):
        seen = []
        orig = oc._read

        def spy(root, rel, limit):
            seen.append(rel)
            return orig(root, rel, limit)
        return seen, mock.patch.object(oc, '_read', spy)

    def refused_before_source(self, req, stage, code_prefix=''):
        seen, patch = self.spy()
        with patch:
            res = oc.run(req, self.lab.root)
        self.refused(res, stage, code_prefix)
        self.assertNotIn(ORDERS, seen, 'the source was read before the refusal')
        return res

    def test_permission_missing_unknown_not_allowed(self):
        for text, code in ((None, 'SCOPE_MISSING'), (scope_doc(status=None), 'PERMISSION_UNKNOWN'), (scope_doc(status='UNKNOWN'), 'PERMISSION_UNKNOWN'),
                           (scope_doc(status='NOT_ALLOWED'), 'PERMISSION_NOT_ALLOWED'), (scope_doc(status='allowed'), 'PERMISSION_UNKNOWN'),
                           ('{"schema":"x"}', 'SCOPE_INVALID'), ('not json', 'SCOPE_INVALID')):
            with self.subTest(code=code, text=(text or '')[:20]):
                if text is None:
                    (self.lab.root / SCOPE_REL).unlink()
                else:
                    write(self.lab.root, SCOPE_REL, text)
                self.refused_before_source(self.lab.req(), 'SCOPE_REFUSED', code)
                write(self.lab.root, SCOPE_REL, scope_doc())

    def test_scope_path_outside_working_or_traversal(self):
        for bad in ('../x.json', '/abs/x.json', 'working\\x.json', 'references/x.json', 'working'):
            with self.subTest(bad=bad):
                self.refused_before_source(self.lab.req(scope=bad), 'SCOPE_REFUSED', 'SCOPE_PATH')

    def test_operation_and_method_must_be_in_scope(self):
        write(self.lab.root, SCOPE_REL, scope_doc(operations=('compare_prices',)))
        self.refused_before_source(self.lab.req(), 'SCOPE_REFUSED', 'OPERATION_OR_METHOD')
        write(self.lab.root, SCOPE_REL, scope_doc(methods=('market-analyst',)))
        self.refused_before_source(self.lab.req(), 'SCOPE_REFUSED', 'OPERATION_OR_METHOD')

    def test_negative_conversion_factor_is_refused_before_source(self):
        params = copy.deepcopy(CMP)
        params['conversions'][0]['multiply'] = '-10'
        req = self.lab.req(operation='compare_prices', source=QUOTES, params=params)
        seen, patch = self.spy()
        with patch:
            result = oc.run(req, self.lab.root)
        self.refused(result, 'PARAMS_INVALID', 'PARAMS_INVALID:conversions.multiply')
        self.assertNotIn(QUOTES, seen)

    def test_operation_must_be_preset_and_params_are_data(self):
        for op in ('eval', 'exec', 'shell', 'python', 'AGGREGATE'):
            with self.subTest(op=op):
                self.refused_before_source(self.lab.req(operation=op), 'REQUEST_INVALID', 'REQUEST_INVALID:operation')
        for params in ({'measures': [{'name': 'x', 'kind': 'eval', 'column': 'qty'}]}, {'measures': [{'name': 'x', 'kind': 'sum', 'column': 'qty', 'code': '1'}]},
                       {'measures': [{'name': 'x', 'kind': 'count_rows'}], 'script': 'rm -rf'}, {'measures': []}, {'filters': [], 'measures': [{'name': 'X', 'kind': 'count_rows'}]},
                       {'filters': [{'column': 'a', 'op': 'regex', 'value': '.*'}], 'measures': [{'name': 'x', 'kind': 'count_rows'}]}):
            with self.subTest(params=params):
                self.refused_before_source(self.lab.req(params=params), 'PARAMS_INVALID')

    def test_request_shape(self):
        good = self.lab.req()
        for key in oc.REQUEST_KEYS:
            req = copy.deepcopy(good)
            del req[key]
            self.refused_before_source(req, 'REQUEST_INVALID', 'REQUEST_INVALID:%s.MISSING' % key)
        req = copy.deepcopy(good)
        req['callback'] = 'x'
        self.refused_before_source(req, 'REQUEST_INVALID', 'REQUEST_INVALID:UNKNOWN_FIELD')
        req = copy.deepcopy(good)
        req['inputs'] = [{'path': ORDERS, 'digest': 'sha256:abc'}]
        self.refused_before_source(req, 'REQUEST_INVALID', 'REQUEST_INVALID:inputs')
        req = copy.deepcopy(good)
        req['inputs'] = [good['inputs'][0], good['inputs'][0]]
        self.refused_before_source(req, 'REQUEST_INVALID', 'REQUEST_INVALID:inputs')

    def test_task_binding(self):
        good = self.lab.req()
        for patch, code in (({'task_id': 'other'}, 'TASK_ID_OR_REVISION_MISMATCH'), ({'task_revision': 2}, 'TASK_ID_OR_REVISION_MISMATCH'),
                            ({'digest': 'sha256:' + '0' * 64}, 'TASK_CHANGED'), ({'path': 'working/lab/t1/NOPE.json'}, 'TASK_UNREADABLE'),
                            ({'path': 'references/TASK.json'}, 'TASK_PATH'), ({'path': '../TASK.json'}, 'TASK_PATH')):
            with self.subTest(code=code, patch=patch):
                req = copy.deepcopy(good)
                req['task'].update(patch)
                self.refused_before_source(req, 'TASK_REFUSED', code)

    def test_task_without_marker_or_with_wrong_role_or_bytes_changed(self):
        self.lab.set_task(drop_marker=True)
        self.refused_before_source(self.lab.req(), 'TASK_REFUSED', 'TASK_NOT_OFFICE_METHOD')
        self.lab.set_task(role='scout')
        self.refused_before_source(self.lab.req(), 'TASK_REFUSED', 'TASK_GUARD:OFFICE_ROLE_MISMATCH')
        self.lab.set_task()
        req = self.lab.req()
        with open(self.lab.root / 'roles/office/data-analyst.md', 'ab') as fh:
            fh.write(b'\n')
        self.refused_before_source(req, 'TASK_REFUSED', 'TASK_GUARD:OFFICE_CONTRACT_BYTES_CHANGED')

    def test_input_must_be_in_task_with_same_digest(self):
        write(self.lab.root, 'working/lab/data/other.csv', 'id\n1\n')
        req = self.lab.req(source='working/lab/data/other.csv')
        self.refused_before_source(req, 'TASK_REFUSED', 'INPUT_NOT_IN_TASK')
        req = self.lab.req(source=QUOTES)
        req['inputs'][0]['digest'] = 'sha256:' + '1' * 64
        self.refused_before_source(req, 'TASK_REFUSED', 'INPUT_DIGEST_NOT_TASK')

    def test_source_changed_after_task_is_refused_without_fallback(self):
        req = self.lab.req()
        write(self.lab.root, ORDERS, ORDERS_CSV + 'O08,2026-10,9,1\n')
        seen, patch = self.spy()
        with patch:
            res = oc.run(req, self.lab.root)
        self.refused(res, 'INPUT_REFUSED', 'INPUT_CHANGED')
        self.assertEqual(seen.count(ORDERS), 1)
        self.assertNotIn('result', res)

    def test_path_forms_zone_and_links(self):
        for bad in ('../orders.csv', '/etc/orders.csv', 'working/../orders.csv', 'working\\lab\\data\\orders.csv', 'C:/x/orders.csv', 'working/lab/data/orders.csv:ads',
                    'tools/office.py', 'roles/office/catalog.json', 'orders.csv'):
            with self.subTest(bad=bad):
                doc = json.loads((self.lab.root / TASK_REL).read_text(encoding='utf-8'))
                doc['inputs'] = [{'path': bad, 'digest': 'sha256:' + '2' * 64}]
                write(self.lab.root, TASK_REL, json.dumps(doc))
                req = self.lab.req()
                req['inputs'] = [{'path': bad, 'digest': 'sha256:' + '2' * 64}]
                seen, patch = self.spy()
                with patch:
                    res = oc.run(req, self.lab.root)
                self.refused(res, 'INPUT_REFUSED', 'INPUT_')
                self.assertNotEqual(seen[-1], bad, 'the refused path must not be opened as the source')

    def test_directory_link_in_source_path_is_refused(self):
        real = self.lab.root / 'working' / 'real'
        real.mkdir(parents=True)
        write(real, 'x.csv', 'id\n1\n')
        if not make_link(self.lab.root / 'working' / 'lnk', real):
            self.skipTest('no directory link can be made here')
        rel = 'working/lnk/x.csv'
        digest = sha((real / 'x.csv').read_bytes())
        doc = json.loads((self.lab.root / TASK_REL).read_text(encoding='utf-8'))
        doc['inputs'] = [{'path': rel, 'digest': digest}]
        write(self.lab.root, TASK_REL, json.dumps(doc))
        req = self.lab.req()
        req['inputs'] = [{'path': rel, 'digest': digest}]
        req['params'] = {'measures': [{'name': 'n', 'kind': 'count_rows'}]}
        self.refused(oc.run(req, self.lab.root), 'INPUT_REFUSED', 'INPUT_UNREADABLE')

    def test_refusal_has_no_result_and_no_writes(self):
        before = tree(self.lab.root)
        res = oc.run(self.lab.req(operation='eval'), self.lab.root)
        self.assertEqual(res['outcome'], 'REFUSED')
        self.assertTrue(all(k not in res for k in ('result', 'result_digest', 'inputs')))
        self.assertEqual(before, tree(self.lab.root))


class OwnerShape(unittest.TestCase):
    def test_no_dynamic_code_network_or_writes(self):
        tree_ = ast.parse((ROOT / 'tools' / 'office_compute.py').read_text(encoding='utf-8'))
        imported = {a.name.split('.')[0] for n in ast.walk(tree_) if isinstance(n, ast.Import) for a in n.names}
        imported |= {n.module.split('.')[0] for n in ast.walk(tree_) if isinstance(n, ast.ImportFrom) and n.module}
        self.assertFalse(imported & {'subprocess', 'socket', 'urllib', 'http', 'requests', 'shutil', 'importlib', 'pickle', 'ctypes', 'os.system'}, imported)
        calls = {n.func.id for n in ast.walk(tree_) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        self.assertFalse(calls & {'eval', 'exec', 'compile', '__import__'}, calls)
        modes = [n.args[1].value for n in ast.walk(tree_) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'open' and len(n.args) > 1]
        self.assertEqual(modes, ['rb', 'rb'], 'only read-binary opens are allowed (own digest and --request)')

    def test_core_exporter_and_default_capabilities_unchanged(self):
        self.assertIsNone(office.CAP_TOOLS['compute'])
        for role in ('scout', 'worker', 'reviewer'):
            self.assertNotIn('Bash', native_agents.TOOLS_BY_ROLE[role])
        self.assertEqual(sorted(native_agents.TOOLS_BY_ROLE['worker']), ['Glob', 'Grep', 'Read', 'Write'])


class Cli(ComputeBase):
    def call(self, *args, stdin=None):
        env = dict(os.environ, PYTHONUTF8='1', PYTHONDONTWRITEBYTECODE='1')
        return subprocess.run([sys.executable, '-X', 'utf8', '-B', str(ROOT / 'tools' / 'office_compute.py')] + [str(a) for a in args], cwd=str(self._tmp.name), env=env,
                              input=stdin, capture_output=True, timeout=120)

    def test_run_from_stdin_and_exit_codes(self):
        done = self.call('run', '--project', self.lab.root, '--request', '-', stdin=json.dumps(self.lab.req()).encode('utf-8'))
        self.assertEqual(done.returncode, 0, done.stderr)
        out = json.loads(done.stdout.decode('utf-8'))
        self.assertEqual(out['outcome'], 'COMPUTED')
        self.assertEqual(out, self.lab.run(), 'CLI and API agree')
        bad = self.call('run', '--project', self.lab.root, '--request', '-', stdin=json.dumps(self.lab.req(operation='eval')).encode('utf-8'))
        self.assertEqual(bad.returncode, 1)
        self.assertEqual(json.loads(bad.stdout.decode('utf-8'))['outcome'], 'REFUSED')
        self.assertEqual(self.call().returncode, 2)

    def test_bad_inputs_to_cli(self):
        for stdin in (b'not json', b'{"a":1,"a":2}', b'x' * (oc.MAX_REQUEST + 1), b'[1]'):
            done = self.call('run', '--project', self.lab.root, '--request', '-', stdin=stdin)
            self.assertEqual(done.returncode, 1, stdin[:20])
            self.assertEqual(json.loads(done.stdout.decode('utf-8'))['outcome'], 'REFUSED')
        done = self.call('run', '--project', self.lab.root / 'nope', '--request', '-', stdin=b'{}')
        self.assertEqual(json.loads(done.stdout.decode('utf-8'))['code'], 'PROJECT_NOT_A_DIRECTORY')

    def test_canary_reads_no_file_and_matches_api(self):
        with mock.patch.object(oc, '_read', side_effect=AssertionError('canary must not read files')):
            receipt = oc.canary('client', '1', 'main')
        done = self.call('canary', '--client', 'client', '--client-version', '1', '--observed-by', 'main')
        out = json.loads(done.stdout.decode('utf-8'))
        for key in ('schema', 'owner_digest', 'canary_digest', 'layer', 'specialist_tool_observed'):
            self.assertEqual(out[key], receipt[key])
        self.assertIs(out['specialist_tool_observed'], False)
        self.assertEqual(out['layer'], 'CALLING_PROCESS_ONLY')


class Route(ComputeBase):
    def save_probe(self, **over):
        probe = oc.canary('test-client', '0', 'main')
        probe.update(over)
        write(self.lab.root, PROBE_REL, json.dumps(probe))
        return probe

    def prepare(self):
        return oc.prepare_route({'probe': PROBE_REL, 'scope': SCOPE_REL}, self.lab.root)

    def test_ready_is_unverified_and_specialist_call_not_observed(self):
        self.save_probe()
        route = self.prepare()
        self.assertEqual((route['state'], route['problems']), ('ROUTE_READY_UNVERIFIED', []))
        dims = route['dimensions']
        self.assertEqual((dims['exporter'], dims['specialist_call'], dims['permission']['status'], dims['host_probe']['status'], dims['host_probe']['layer']),
                         ('ABSENT', 'NOT_OBSERVED', 'ALLOWED', 'MATCHES_OWNER', 'CALLING_PROCESS_ONLY'))
        self.assertIn('<LAW>/tools/office_compute.py', ' '.join(route['command']))

    def test_refused_cases_stay_refused(self):
        cases = {}
        (self.lab.root / PROBE_REL).parent.mkdir(parents=True, exist_ok=True)
        cases['PROBE_MISSING'] = lambda: None
        cases['PROBE_INVALID'] = lambda: write(self.lab.root, PROBE_REL, 'not json')
        cases['PROBE_OWNER_CHANGED'] = lambda: self.save_probe(owner_digest='sha256:' + '0' * 64)
        cases['PROBE_CANARY_MISMATCH'] = lambda: self.save_probe(canary_digest='sha256:' + '0' * 64)
        cases['PROBE_CLAIMS_MORE_THAN_MAIN'] = lambda: self.save_probe(specialist_tool_observed=True)
        for code, setup in cases.items():
            with self.subTest(code=code):
                if (self.lab.root / PROBE_REL).exists():
                    (self.lab.root / PROBE_REL).unlink()
                setup()
                route = self.prepare()
                self.assertEqual(route['state'], 'ROUTE_REFUSED')
                self.assertTrue(route['problems'][0].startswith(code), route['problems'])
                self.assertEqual(route['command'], [])
                self.assertEqual(route['dimensions']['specialist_call'], 'NOT_OBSERVED')

    def test_layer_other_than_calling_process_is_refused(self):
        self.save_probe(layer='SPECIALIST')
        self.assertTrue(self.prepare()['problems'][0].startswith('PROBE_CLAIMS_MORE_THAN_MAIN'))

    def test_permission_gates_the_route(self):
        self.save_probe()
        for text, status in ((scope_doc(status='NOT_ALLOWED'), 'PERMISSION_NOT_ALLOWED'), (scope_doc(status=None), 'PERMISSION_UNKNOWN'), (None, 'NOT_VERIFIED')):
            with self.subTest(status=status):
                if text is None:
                    (self.lab.root / SCOPE_REL).unlink()
                else:
                    write(self.lab.root, SCOPE_REL, text)
                route = self.prepare()
                self.assertEqual(route['state'], 'ROUTE_REFUSED')
                self.assertEqual(route['dimensions']['permission']['status'], status)
                write(self.lab.root, SCOPE_REL, scope_doc())

    def test_probe_path_cannot_leave_working(self):
        self.save_probe()
        route = oc.prepare_route({'probe': '../probe.json', 'scope': SCOPE_REL}, self.lab.root)
        self.assertEqual(route['state'], 'ROUTE_REFUSED')


class ComposeRoute(ComputeBase):
    def compose(self, method='data-analyst', route=True, **over):
        req = request(method, sources=[{'path': ORDERS}], needs_compute=True, reason='Cần tính tổng đơn hàng tháng 10.', request='Tổng hợp đơn hàng tháng 10.')
        req.pop('resources_used', None)
        if route:
            req['compute_route'] = {'probe': PROBE_REL, 'scope': SCOPE_REL}
        req.update(over)
        return office.compose(req, root=str(self.lab.root))

    def ready(self):
        write(self.lab.root, PROBE_REL, json.dumps(oc.canary('test-client', '0', 'main')))

    def test_default_has_no_route_and_keeps_core_handover(self):
        res = self.compose(route=False)
        self.assertEqual((res['state'], res['held']), ('NEEDS_CAPABILITY', ['compute']))
        self.assertNotIn('compute_route', res)
        self.assertTrue(all('route' not in r for r in res['capabilities']))
        self.assertIn('Bạn chỉ có Read/Grep/Glob/Write', res['brief'])
        self.assertNotIn('MỘT lệnh', res['brief'])
        en = self.compose(route=False, lang='en')
        self.assertIn('You only have Read/Grep/Glob/Write', en['brief'])

    def test_ready_route_opens_compute_dimension_but_not_exporter(self):
        self.ready()
        res = self.compose()
        self.assertEqual((res['state'], res['held']), ('PREPARED', []))
        compute = next(r for r in res['capabilities'] if r['capability'] == 'compute')
        self.assertEqual((compute['exporter'], compute['status'], compute['route'], compute['grant'], compute['host']),
                         ('ABSENT', 'ROUTE_READY_UNVERIFIED', 'ROUTE_READY_UNVERIFIED', 'NOT_INSPECTED', 'NOT_INSPECTED'))
        self.assertEqual(res['compute_route']['dimensions']['specialist_call'], 'NOT_OBSERVED')
        self.assertEqual(res['claims'], {'prepared': True, 'invoked': False, 'content_checked': False})
        self.assertIn('office_compute.py', res['brief'])
        self.assertIn('MỘT lệnh', res['brief'])
        self.assertNotIn('Bạn chỉ có Read/Grep/Glob/Write', res['brief'])
        self.assertIn('Bạn không có công cụ băm', res['brief'], 'the two-phase digest hand-over is unchanged')
        en = self.compose(lang='en')
        self.assertIn('ONE command', en['brief'])
        self.assertNotIn('You only have Read/Grep/Glob/Write', en['brief'])

    def test_refused_route_keeps_needs_capability_and_core_handover(self):
        write(self.lab.root, SCOPE_REL, scope_doc(status='UNKNOWN'))
        self.ready()
        res = self.compose()
        self.assertEqual((res['state'], res['held']), ('NEEDS_CAPABILITY', ['compute']))
        self.assertEqual(res['compute_route']['state'], 'ROUTE_REFUSED')
        self.assertIn('Bạn chỉ có Read/Grep/Glob/Write', res['brief'])
        self.assertIn('ROUTE_REFUSED', res['brief'])

    def test_scope_must_cover_composed_method_and_operation(self):
        self.ready()
        for scope in (scope_doc(methods=('market-analyst',)), scope_doc(operations=('compare_prices',))):
            with self.subTest(scope=scope):
                write(self.lab.root, SCOPE_REL, scope)
                res = self.compose()
                self.assertEqual((res['state'], res['held']), ('NEEDS_CAPABILITY', ['compute']))
                self.assertEqual(res['compute_route']['state'], 'ROUTE_REFUSED')
                self.assertIn('OPERATION_OR_METHOD_NOT_ALLOWED', res['compute_route']['problems'])
                self.assertIn('Bạn chỉ có Read/Grep/Glob/Write', res['brief'])

    def test_missing_probe_keeps_needs_capability(self):
        res = self.compose()
        self.assertEqual((res['state'], res['compute_route']['state']), ('NEEDS_CAPABILITY', 'ROUTE_REFUSED'))
        self.assertTrue(res['compute_route']['problems'][0].startswith('PROBE_MISSING'))

    def test_optional_compute_method_can_use_route(self):
        self.ready()
        res = self.compose('market-analyst', sources=[{'path': QUOTES}])
        self.assertEqual((res['state'], res['held']), ('PREPARED', []))

    def test_route_not_applicable_or_malformed_is_refused(self):
        self.ready()
        self.assertEqual(self.compose('research-assistant')['problems'], ['REQUEST_INVALID:compute_route.NOT_APPLICABLE'])
        self.assertEqual(self.compose('evidence-reviewer')['problems'], ['REQUEST_INVALID:compute_route.NOT_APPLICABLE'])
        for bad in ({'probe': PROBE_REL}, {'probe': PROBE_REL, 'scope': SCOPE_REL, 'x': 'y'}, {'probe': 1, 'scope': SCOPE_REL}, 'path', None):
            with self.subTest(bad=bad):
                self.assertEqual(self.compose(compute_route=bad)['problems'], ['REQUEST_INVALID:compute_route'])
        no_compute = self.compose('executive-secretary', needs_compute=False)
        self.assertEqual(no_compute['problems'], ['REQUEST_INVALID:compute_route.NOT_APPLICABLE'])

    def test_route_task_fragment_feeds_the_compute_owner(self):
        """compose (route) -> TASK marker/context -> owner accepts it: the chain a Main would run, on fake data."""
        self.ready()
        res = self.compose()
        self.lab.set_task()
        out = self.lab.run()
        self.assertEqual(out['outcome'], 'COMPUTED', out)
        self.assertEqual(res['task_fragment']['acceptance_requirement']['req_id'], 'OFFICE-METHOD:data-analyst:v1')

    def test_legacy_checkpoint_guard_is_untouched(self):
        task = {'acceptance': {'requirements': []}, 'context_refs': []}
        self.assertEqual(office.guard_task(task, lambda rel: (None, 'x')), [])


if __name__ == '__main__':
    unittest.main()
