"""Offline mock data and CLI screening; no OS sandbox claim."""
import base64
import builtins
import copy
import importlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import unittest
from unittest.mock import patch
from tools import source_response as sr
ROOT = Path(__file__).resolve().parents[1]
SECRET = 'secret-DO-NOT-ECHO-https://example.invalid/?token=123'

class ClassifierTests(unittest.TestCase):
    def check(self, body='<main>Văn bản công khai</main>', status=200, headers=None, expected=True):
        return sr.classify_response(status, headers or {}, body, expected)

    def decision(self, want, body='<main>Văn bản công khai</main>', **kw):
        r = self.check(body, **kw)
        self.assertEqual(r['status'], want, r)
        for flag in ('identity_verified', 'fulltext_verified', 'importable'):
            self.assertIs(r[flag], False)
        return r

    def test_contract_and_status(self):
        self.decision('allow_parse')
        self.decision('unknown', expected=False)
        for status in (302, 500): self.decision('unknown', status=status)
        for status in (401, 403, 429):
            r = self.decision('blocked', b'\xff', status=status, headers={'Retry-After':'30'})
            self.assertIn('http_'+str(status), r['reasoncodes'])
            self.assertEqual(r['safe_evidence']['retry_after'], {'kind':'seconds','value':30})
        self.decision('blocked', b'%PDF-1.7', headers={'Cf-Mitigated':' ChAlLeNgE '})

    def test_retry_after(self):
        r = self.check(status=429, headers={'Retry-After':'Wed, 21 Oct 2015 07:28:00 GMT'})
        self.assertEqual(r['safe_evidence']['retry_after'], {'kind':'date','value':'2015-10-21T07:28:00+00:00'})
        for value in (SECRET, '-1', '1.2', '99999999999', 'Sun, 99 Xxx 2020 12:00:00 GMT'):
            self.assertIsNone(self.check(status=429, headers={'Retry-After':value})['safe_evidence']['retry_after'])

    def test_strong_regression_signals(self):
        for body in ('<title>Just a moment...</title>', '<form id="challenge-form"><input></form>',
                     '<main>Verify you are human before proceeding</main>', '<main>Vui lòng đăng nhập để tiếp tục</main>',
                     '<title>Login required</title>', '<div>checking your browser</div>'):
            with self.subTest(body=body): self.decision('blocked', body)
        for body in ('<form><input type="password"></form>', '<form><input type="password">',
                     '<main><input type="PASSWORD"></main>'):
            self.decision('unknown', body)

    def test_incidental_hidden(self):
        body = '''<title>Văn bản thuế</title><script>captcha login required</script>
        <!-- verify you are human --><main>Public</main>
        <footer><button>Đăng nhập</button><div class="g-recaptcha"></div></footer>'''
        self.decision('allow_parse', body)
        self.decision('unknown', body, expected=False)
        for a in ('hidden','aria-hidden="true"','style="display: none"','style="visibility: hidden"','class="d-none"'):
            self.decision('allow_parse', '<main>Public</main><div '+a+
                          '><form><input type="password"></form>verify you are human</div>')
        self.decision('allow_parse', '<main>Public</main><template>login required</template>')

    def test_duplicate_attributes_fail_closed(self):
        for body in ('<form><input type="password" type="text"></form>',
                     '<form><input TYPE="password" type="text"></form>',
                     '<main id="a" id="b">ok</main>',
                     '<form style="display:block" style="display:none"><input type=password></form>'):
            with self.subTest(body=body): self.decision('unknown', body)
        self.decision('allow_parse', '<main id="a">ok</main>')

    def test_binary_mime_utf8_and_truncation(self):
        for body,h in [(b'%PDF-1.7\n',{}),(b'<main>fake PDF</main>',{'Content-Type':'application/pdf'}),
                       (b'<main>html</main>',{'Content-Type':'application/json'}),(b'\x89PNG\x00data',{}),
                       (b'<main>\xff</main>',{}),(b'<main>cut',{}),(b'<main>ok</main><',{}),
                       (b'<main>ok</main><img',{}),(b'<main>ok</main><!-- cut',{}),
                       (b'plain text',{}),(b'<div><p>bad nesting</div>',{})]:
            with self.subTest(body=body): self.decision('unknown',body,headers=h)
        self.decision('allow_parse',headers={'Content-Type':'text/html; charset=utf-8'})
        self.decision('allow_parse','<!doctype html><html><body><main>ok</main></body></html>')

    def test_limits_and_types(self):
        self.assertEqual(self.check(b'x'*(sr.BODY_LIMIT+1))['reasoncodes'],['input_error'])
        self.assertEqual(self.check(headers={'X':'x'*sr.HEADER_LIMIT})['reasoncodes'],['input_error'])
        for body in ('<div>'*65+'</div>'*65, '<main>'+'<br>'*sr.MAX_EVENTS+'</main>'):
            self.assertEqual(self.check(body)['reasoncodes'], ['parser_limit'])
        for status in (True,False,'200',0,99,600,None,200.0):
            self.assertEqual(self.check(status=status)['reasoncodes'],['input_error'])
        for h in ([],None,{'x':1},{'a':'v','A':'w'},{'bad\n':'secret'},{'x':'bad\r\n'}):
            self.assertEqual(sr.classify_response(200,h,b'<main>ok</main>',True)['reasoncodes'],['input_error'])
        for body in (None,bytearray(b'abc'),1):
            self.assertEqual(self.check(body)['reasoncodes'],['input_error'])
        self.assertEqual(self.check(expected=1)['reasoncodes'],['input_error'])

    def test_no_mutation_leaks_or_io(self):
        h={'Cookie':SECRET,'Retry-After':SECRET,'Content-Type':'text/html'}
        before=copy.deepcopy(h)
        with patch.object(builtins,'open',side_effect=AssertionError('file IO')), patch.object(socket,'socket',side_effect=AssertionError('network')):
            importlib.reload(sr)
            for body,status in (('<main>'+SECRET+'</main>',200),('<title>Login required '+SECRET+'</title>',200),(SECRET,429),(b'\xff',200)):
                self.assertNotIn(SECRET,json.dumps(self.check(body,status=status,headers=h)))
        self.assertEqual(h,before)
        self.assertEqual(set(self.check()['safe_evidence']),{'http_status','body_bytes','body_sha256'})

class CLITests(unittest.TestCase):
    def payload(self,body='<main>ok</main>',status=200,expected=True):
        return {'status':status,'headers':{},'body_base64':base64.b64encode(body.encode()).decode(),'expected_content':expected}

    def cli(self,value=None,raw=None,args=()):
        if raw is None: raw=json.dumps(value,ensure_ascii=False).encode()
        p=subprocess.run([sys.executable,'-X','utf8','-B','tools/source_response.py']+list(args),input=raw,
            capture_output=True,cwd=str(ROOT),env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),timeout=10)
        self.assertNotIn(SECRET.encode(),p.stdout+p.stderr)
        self.assertEqual(p.stderr,b'')
        self.assertTrue(p.stdout.startswith(b'@@RESULT_JSON@@'),p.stdout[:100])
        r=json.loads(p.stdout.decode()[len('@@RESULT_JSON@@'):])
        self.assertEqual(r['schema'],'local-agent-workspace/result-v1')
        self.assertEqual(r['code'],p.returncode)
        return p.returncode,r

    def test_agreement(self):
        for body,status,expected in (('<main>ok</main>',200,True),('<main>ok</main>',200,False),
            ('<title>Just a moment</title>',200,True),('<main>'+SECRET+'</main>',403,True)):
            code,r=self.cli(self.payload(body,status,expected))
            api=sr.classify_response(status,{},body,expected)
            self.assertEqual(r['response_check'],api)
            self.assertEqual(code,0 if api['status']=='allow_parse' else 1)
            self.assertFalse(r['changes'])

    def test_malformed_and_usage(self):
        for raw in (b'{',b'[]',b'{"status":200,"status":200}',b'{"status":NaN}',
            b'{"headers":{"x":"a","x":"b"}}',b'"'+SECRET.encode()+b'"',b'['*1100,b'x'*(sr.INPUT_LIMIT+1)):
            self.assertEqual(self.cli(raw=raw)[0],2)
        for key,bad in (('status',True),('status',600),('headers',{'X':'v'*sr.HEADER_LIMIT}),
            ('body_base64','%%%'+SECRET),('body_base64','Zh=='),
            ('body_base64',base64.b64encode(b'x'*(sr.BODY_LIMIT+1)).decode()),('expected_content',1),('unknown',SECRET)):
            v=self.payload(); v[key]=bad
            self.assertEqual(self.cli(v)[0],2,key)
        self.assertEqual(self.cli(raw=b'',args=('--'+SECRET,))[0],2)

    def test_help(self):
        p=subprocess.run([sys.executable,'-X','utf8','-B','tools/source_response.py','--help'],capture_output=True,cwd=str(ROOT),timeout=10)
        self.assertEqual(p.returncode,0)
        self.assertIn('chưa phải nhận nguồn',p.stdout.decode())

if __name__=='__main__': unittest.main(verbosity=2)
