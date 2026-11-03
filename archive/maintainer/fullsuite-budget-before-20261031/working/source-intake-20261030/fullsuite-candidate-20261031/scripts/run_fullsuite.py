"""Revision11 candidate helper; execute only after independent Main PRE.

No test, oracle, unittest result or skip monkeypatch. Cooperative audit hooks are
not an OS sandbox and are not inherited by arbitrary child/native processes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import runpy
import shutil
import subprocess
import sys
import time


def sha(data):
    return hashlib.sha256(data).hexdigest()


def within(path, root):
    try:
        return os.path.commonpath((os.path.normcase(os.path.abspath(path)),
                                   os.path.normcase(os.path.abspath(root)))) == os.path.normcase(os.path.abspath(root))
    except (ValueError, TypeError):
        return False


def plain(path):
    for item in (Path(path), *Path(path).parents):
        if item.exists() or item.is_symlink():
            st = item.lstat()
            if item.is_symlink() or getattr(st, 'st_file_attributes', 0) & 0x400:
                raise ValueError('link/reparse input: ' + str(item))


def relative(value):
    if not isinstance(value, str) or '\\' in value:
        raise ValueError('noncanonical map path')
    p = PurePosixPath(value)
    if p.is_absolute() or str(p) != value or any(x in ('', '.', '..') or ':' in x for x in p.parts):
        raise ValueError('unsafe map path: ' + value)
    return Path(*p.parts)


def checked(path, digest, size=None):
    plain(path)
    data = Path(path).read_bytes()
    if sha(data) != digest or (size is not None and len(data) != size):
        raise ValueError('input binding mismatch: ' + str(path))
    return data


def write_json(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n')


def windows_executable_resolver():
    """Conservative CreateProcessW module resolution, not a shell parser.

    Python 3.11 audits the converted Windows command line, with executable=None
    for normal list argv. Child env/cwd do not supply the executable search path.
    Restrict ambiguous syntax instead of attempting CreateProcess's unquoted
    path-with-spaces retries. Explicit lpApplicationName remains authoritative.
    """
    if os.name != 'nt':
        raise RuntimeError('reviewed Windows process resolver required')
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetModuleFileNameW.argtypes = (wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD)
    kernel.GetModuleFileNameW.restype = wintypes.DWORD
    for name in ('GetSystemDirectoryW', 'GetWindowsDirectoryW'):
        function = getattr(kernel, name)
        function.argtypes = (wintypes.LPWSTR, wintypes.UINT)
        function.restype = wintypes.UINT

    def directory(name):
        buffer = ctypes.create_unicode_buffer(32768)
        count = getattr(kernel, name)(buffer, len(buffer))
        if not count or count >= len(buffer):
            raise OSError('cannot bind Windows search directory: ' + name)
        return buffer.value

    buffer = ctypes.create_unicode_buffer(32768)
    count = kernel.GetModuleFileNameW(None, buffer, len(buffer))
    if not count or count >= len(buffer):
        raise OSError('cannot bind loaded application directory')
    appdir = os.path.dirname(buffer.value)
    systemdir = directory('GetSystemDirectoryW')
    windowsdir = directory('GetWindowsDirectoryW')

    def resolve(executable, argv):
        if isinstance(argv, (list, tuple)):
            # Audit shape on other Python versions / direct callback controls.
            argv = subprocess.list2cmdline(argv)
        if not isinstance(argv, str) or not argv or '\0' in argv:
            raise PermissionError('empty or invalid command line')
        if executable is not None:
            module = os.fsdecode(executable)
            explicit = True
        else:
            explicit = False
            if argv[0].isspace():
                raise PermissionError('leading whitespace module is ambiguous')
            if argv.startswith('"'):
                end = argv.find('"', 1)
                if end < 0 or (len(argv) > end + 1 and not argv[end + 1].isspace()):
                    raise PermissionError('malformed quoted module')
                module = argv[1:end]
            else:
                module = argv.split(maxsplit=1)[0]
                if '"' in module:
                    raise PermissionError('ambiguous module quotation')
        if not module or any(c in module for c in '\0"\r\n\t'):
            raise PermissionError('invalid module')
        # No drive-relative, rooted-current-drive, device, UNC or ADS forms.
        drive, tail = os.path.splitdrive(module)
        if (drive and (not tail.startswith(('\\', '/')) or len(drive) != 2)) or (
                not drive and module.startswith(('\\', '/'))) or ':' in tail:
            raise PermissionError('ambiguous or unsupported module path')
        has_directory = bool(os.path.dirname(module))
        if explicit:
            # lpApplicationName partial paths use parent cwd, with no PATH or
            # implicit extension. Spaces are literal here, not token delimiters.
            candidates = [os.path.abspath(module)]
        elif has_directory:
            if not os.path.splitext(module)[1]:
                raise PermissionError('path module requires explicit extension')
            candidates = [os.path.abspath(module)]
        else:
            if module.endswith('.'):
                raise PermissionError('trailing-dot module is unsupported')
            name = module if os.path.splitext(module)[1] else module + '.exe'
            # Resolve each search directory at event time against parent cwd.
            # Empty PATH components mean parent cwd; quoted PATH is refused.
            pathdirs = os.environ.get('PATH', '').split(os.pathsep)
            if any('"' in part for part in pathdirs):
                raise PermissionError('quoted parent PATH unsupported')
            directories = [appdir, os.getcwd(), systemdir,
                           os.path.join(windowsdir, 'System'), windowsdir, *pathdirs]
            candidates = [os.path.abspath(os.path.join(item, name)) for item in directories]
        for candidate in candidates:
            if os.path.isfile(candidate):
                # Do not skip an earlier existing unbound image to find an
                # allowlisted one later in PATH. The hook checks this exact hit.
                return candidate
        raise PermissionError('module not found by reviewed Windows search')

    return resolve


def make_audit_hook(source, session, executables, audit):
    """Exact shared hook for suite child and Main's narrow real-child probe."""
    source = str(Path(source).resolve())
    session = Path(session).resolve()
    null_device = os.path.normcase(os.path.abspath(os.devnull))
    allowed = {os.path.normcase(str(Path(x['path']).resolve())) for x in executables}
    resolve_executable = windows_executable_resolver()
    mutation_events = {'os.remove', 'os.rmdir', 'os.mkdir', 'os.chmod', 'os.utime',
                       'os.truncate', 'os.rename', 'os.link', 'os.symlink'}

    def path_check(value, write=False):
        if not isinstance(value, (str, bytes, os.PathLike)):
            return
        p = os.path.abspath(os.fsdecode(value))
        # Windows resolves DEVNULL to the standard device \\.\nul. This is
        # process stdio, not a filesystem destination outside the session.
        if os.path.normcase(p) == null_device:
            return
        if within(p, source):
            audit.write(json.dumps({'event': 'DENY_PATH', 'path': p, 'write': write,
                                    'reason': 'real SOURCE'}) + '\n')
            raise PermissionError('real SOURCE access denied: ' + p)
        if write and not within(p, session):
            audit.write(json.dumps({'event': 'DENY_PATH', 'path': p, 'write': write,
                                    'reason': 'outside owned session'}) + '\n')
            raise PermissionError('write outside owned session: ' + p)

    def hook(event, args):
        if event == 'open':
            mode = args[1] if len(args) > 1 else None
            flags = args[2] if len(args) > 2 else 0
            writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
                isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)))
            path_check(args[0], writing)
        elif event in ('os.listdir', 'os.scandir', 'os.chdir'):
            path_check(args[0])
        elif event in mutation_events:
            # Rename/link have two paths; symlink target is checked as well.
            for value in args[:2] if event in ('os.rename', 'os.link', 'os.symlink') else args[:1]:
                path_check(value, True)
        elif event == 'subprocess.Popen':
            executable, argv, cwd, env = args
            record = {'event': event, 'executable': executable, 'argv': argv, 'cwd': cwd}
            try:
                found = resolve_executable(executable, argv)
                record['resolved_executable'] = found
                if os.path.normcase(str(Path(found).resolve())) not in allowed:
                    raise PermissionError('unbound child executable: ' + found)
                if not within(os.getcwd(), session) or (cwd is not None and not within(cwd, session)):
                    raise PermissionError('child cwd outside owned session')
                for arg in argv if isinstance(argv, (list, tuple)) else [argv]:
                    if isinstance(arg, str) and os.path.normcase(source).replace('/', '\\') in os.path.normcase(arg).replace('/', '\\'):
                        raise PermissionError('real SOURCE referenced by child argv')
                record['decision'] = 'ALLOW'
            except (PermissionError, ValueError, TypeError, OSError) as error:
                record.update(decision='DENY', reason=str(error))
                raise PermissionError('child process denied: ' + str(error)) from error
            finally:
                audit.write(json.dumps(record, ensure_ascii=False, default=str) + '\n')
        elif event in ('socket.connect', 'socket.bind'):
            address = args[1]
            audit.write(json.dumps({'event': event, 'address': address}, default=str) + '\n')
            if isinstance(address, tuple) and address[0] not in ('127.0.0.1', '::1', 'localhost'):
                raise PermissionError('non-loopback network denied')
        elif event in ('os.system', 'os.exec', 'os.posix_spawn'):
            raise PermissionError('unreviewed process API: ' + event)

    return hook


def child(pre_path, session_path):
    """Unmodified unittest CLI, with advisory path/process/network auditing."""
    session = Path(session_path).resolve()
    pre = json.loads(Path(pre_path).read_text(encoding='utf-8'))
    root = session / 'root'
    # Open evidence FD before installing the hook. Retained FD/native operations
    # are a documented limitation, not a claim of complete interception.
    audit = (session / 'audit.jsonl').open('x', encoding='utf-8', buffering=1)
    hook = make_audit_hook(pre['source'], session, pre['executables'], audit)
    sys.addaudithook(hook)
    os.chdir(root)
    # Direct validators first; presence/heuristic schema checks are insufficient.
    # This is a new narrow preflight, not a rewrite of the prior formal receipt.
    sys.path.insert(0, str(root / 'tools'))
    import importlib.metadata
    import jsonschema
    from referencing.exceptions import NoSuchResource
    import execution_profile as ep
    formal = {'dependencies': {}, 'schemas': [], 'positive': [], 'retrieval_denied': []}
    for package in ('jsonschema', 'referencing', 'openpyxl'):
        formal['dependencies'][package] = importlib.metadata.version(package)
    for rel in ('.agent/EXECUTION_PROFILE.schema.json', '.cvf/contracts/v3/control.schema.json'):
        schema = json.loads((root / rel).read_text(encoding='utf-8'))
        jsonschema.Draft202012Validator.check_schema(schema)
        formal['schemas'].append(rel)
    validators = (ep.profile_validator(), ep.control_validator())
    for validator in validators:
        if not isinstance(validator, jsonschema.Draft202012Validator):
            raise ValueError('direct formal validator unavailable')
    for label, validator, value in (
            ('default_PROJECT', validators[0], ep.default_profile('PROJECT')),
            ('default_PROFILE', validators[0], ep.default_profile('PROFILE')),
            ('clean_profile', validators[0], json.loads((root / '.agent/EXECUTION_PROFILE.json').read_text(encoding='utf-8'))),
            ('v3_policy', validators[1], json.loads((root / '.cvf/rules/v3/ROUTING_POLICY.json').read_text(encoding='utf-8')))):
        validator.validate(value)
        formal['positive'].append(label)
    for label, validator in zip(('profile', 'control'), validators):
        try:
            validator._registry.get_or_retrieve('https://formal-probe.invalid/blocked')
        except NoSuchResource:
            formal['retrieval_denied'].append(label)
        else:
            raise ValueError('validator registry unexpectedly permits retrieval')
    write_json(session / 'direct-formal.json', formal)
    # Same CLI semantics as python -B -m unittest discover -s tests -v.
    # Do not count AST definitions as discovery IDs or alter the loader/result.
    sys.path.insert(0, str(root))
    sys.argv = ['python -m unittest', 'discover', '-s', 'tests', '-v']
    runpy.run_module('unittest', run_name='__main__', alter_sys=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pre')
    parser.add_argument('--session')
    parser.add_argument('--child', nargs=2, metavar=('PRE', 'SESSION'))
    args = parser.parse_args()
    if args.child:
        child(*args.child)
        return
    if not args.pre or not args.session:
        parser.error('--pre and --session required; no implicit authorization')
    pre_path = Path(args.pre).resolve()
    plain(pre_path)
    pre = json.loads(pre_path.read_text(encoding='utf-8'))
    if pre.get('status') != 'MAIN_PRE_AUTHORIZED' or pre.get('revision') != 11:
        raise ValueError('missing exact revision11 Main PRE')
    helper = Path(__file__).resolve()
    checked(helper, pre['helper_sha256'])
    source = Path(pre['source']).resolve()
    plain(source)
    if Path(sys.executable).resolve() != Path(pre['python']).resolve():
        raise ValueError('interpreter mismatch')
    session = Path(args.session).absolute()
    plain(session.parent)
    if session.exists() or within(session, source) or within(source, session):
        raise ValueError('session must be new and separate from real SOURCE')
    if str(session) != pre['session']:
        raise ValueError('session mismatch')
    map_path = Path(pre['input_map']).resolve()
    mapping = json.loads(checked(map_path, pre['input_map_sha256']).decode('utf-8'))
    for executable in pre['executables']:
        checked(Path(executable['path']), executable['sha256'])
    if os.path.normcase(str(Path(sys.executable).resolve())) not in {
            os.path.normcase(str(Path(x['path']).resolve())) for x in pre['executables']}:
        raise ValueError('interpreter not bound as child executable')
    files = mapping['files']
    overlays = mapping['clean_overlays']
    staged, destinations = [], set()
    # Validate every map record and every byte before creating the session.
    for entry in files:
        src_rel, dst_rel = relative(entry['source_path']), relative(entry['destination_path'])
        key = dst_rel.as_posix().casefold()
        if key in destinations:
            raise ValueError('duplicate destination')
        destinations.add(key)
        staged.append((dst_rel, checked(source / src_rel, entry['sha256'], entry['size'])))
    for entry in overlays:
        src_rel, dst_rel = relative(entry['source']), relative(entry['target'])
        if src_rel.parts[0] != 'release_templates':
            raise ValueError('clean overlay must come from public release_templates')
        if dst_rel.as_posix().startswith('tests/'):
            raise ValueError('test/oracle overlays forbidden')
        staged.append((dst_rel, checked(source / src_rel, entry['sha256'], entry['size'])))
    expected = sorted(e['destination_path'] for e in files if e['destination_path'].startswith('tests/test') and e['destination_path'].endswith('.py'))
    if expected != sorted(pre['expected_test_modules']):
        raise ValueError('expected complete module set mismatch')
    session.mkdir()
    root = session / 'root'
    root.mkdir()
    for rel, data in staged:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    # Only this one empty parent is needed by the unmodified ownership tests.
    (root / 'working/source-intake-20261030/config-ownership').mkdir(parents=True, exist_ok=True)
    for name in ('tmp', 'home', 'appdata', 'localappdata'):
        (session / name).mkdir()
    (session / 'runner.py').write_bytes(helper.read_bytes())
    write_json(session / 'bound-pre.json', pre)
    write_json(session / 'materialization.json', {
        'map_sha256': pre['input_map_sha256'], 'files': len(files), 'overlays': len(overlays),
        'expected_test_modules': expected, 'root': str(root), 'retained': True,
        'test_bytes': {e['destination_path']: e['sha256'] for e in files if e['destination_path'] in expected}})
    env = {key: value for key, value in os.environ.items() if key.upper() in ('SYSTEMROOT', 'WINDIR', 'COMSPEC', 'PATHEXT')}
    env.update(PATH=pre['path'], PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
               PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1',
               TEMP=str(session / 'tmp'), TMP=str(session / 'tmp'), TMPDIR=str(session / 'tmp'),
               HOME=str(session / 'home'), USERPROFILE=str(session / 'home'),
               USERNAME='DATAMOCK', USER='DATAMOCK',
               APPDATA=str(session / 'appdata'), LOCALAPPDATA=str(session / 'localappdata'),
               GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_ATTR_NOSYSTEM='1',
               GIT_CEILING_DIRECTORIES=str(session), PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1',
               NO_PROXY='127.0.0.1,localhost,::1')
    # Main may bind the existing browser cache by explicit path, never download.
    if pre.get('playwright_browsers_path'):
        env['PLAYWRIGHT_BROWSERS_PATH'] = pre['playwright_browsers_path']
    command = [sys.executable, '-I', '-B', str(session / 'runner.py'), '--child', str(session / 'bound-pre.json'), str(session)]
    write_json(session / 'invocation.json', {'command': command, 'cwd': str(root), 'env': env,
                                           'timeout': pre['timeout_seconds'], 'cooperative_only': True})
    started = time.time()
    result = {'status': 'STARTED', 'started_epoch': started, 'command': command}
    with (session / 'stdout.log').open('xb') as stdout, (session / 'stderr.log').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=root, env=env, stdout=stdout, stderr=stderr,
                                   stdin=subprocess.DEVNULL, close_fds=True)
        result['pid'] = process.pid
        try:
            result['actual_exit'] = process.wait(timeout=pre['timeout_seconds'])
            result['status'] = 'EXITED'
        except subprocess.TimeoutExpired:
            result.update(status='TIMEOUT_RECONCILE_REQUIRED', actual_exit=None)
            # Stop only the known immediate PID; descendant state remains UNKNOWN.
            process.terminate()
            try:
                result['exit_after_terminate'] = process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                result['exit_after_terminate'] = None
    result.update(elapsed_seconds=time.time() - started, root_retained=True,
                  descendants='NOT_INDEPENDENTLY_RECONCILED',
                  stdout_sha256=sha((session / 'stdout.log').read_bytes()),
                  stderr_sha256=sha((session / 'stderr.log').read_bytes()))
    result['test_byte_changes'] = [e['destination_path'] for e in files
                                   if e['destination_path'] in expected and
                                   (not (root / e['destination_path']).is_file() or
                                    sha((root / e['destination_path']).read_bytes()) != e['sha256'])]
    write_json(session / 'exit.json', result)
    print(json.dumps({'session': str(session), **result}, ensure_ascii=False))
    return result.get('actual_exit') if result.get('actual_exit') is not None else 124


if __name__ == '__main__':
    sys.exit(main())
