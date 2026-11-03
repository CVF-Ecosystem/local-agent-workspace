"""Bounded, offline source intake. Configuration classifies files; it never verifies them."""
import hashlib
import json
import os
import re
import stat

import library
import library_sync
import transaction

CONFIG = '.agent/SOURCE_INTAKE.json'
SCHEMA = 'law.source-intake/1'
MAX_CONFIG = 64 * 1024
MAX_ENTRIES = 100
MAX_FILE = 20 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024
RESERVED = re.compile(r'^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)', re.I)


def refuse(message):
    raise library_sync.SyncError('Intake refused / Từ chối tiếp nhận: ' + message)


def plain_path(value):
    if not isinstance(value, str) or not value or '\\' in value:
        refuse('a plain project-relative path is required')
    parts = value.split('/')
    if any(not p or p in ('.', '..') or p[-1] in '. ' or RESERVED.match(p) or
           any(ord(c) < 32 or c in '<>:"|?*' for c in p) for p in parts):
        refuse('unsafe path: ' + value)
    return parts


def guarded(root, rel):
    plain_path(rel)
    path = os.path.join(root, *rel.split('/'))
    if not library_sync.link_free(path, root) or not library_sync.contained(path, root):
        refuse('link or outside project: ' + rel)
    return path


def config_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate configuration field: ' + key)
        result[key] = value
    return result


def read_config(root):
    path = guarded(root, CONFIG)
    try:
        with open(path, 'rb') as f:
            raw = f.read(MAX_CONFIG + 1)
        if len(raw) > MAX_CONFIG:
            refuse('configuration exceeds 64 KiB')
        cfg = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=config_object)
    except (OSError, ValueError, UnicodeError) as e:
        refuse('configuration unavailable or malformed: %s' % e)
    if not isinstance(cfg, dict) or set(cfg) != {'schema', 'enabled', 'staging', 'mappings'} or cfg['schema'] != SCHEMA:
        refuse('unknown configuration schema or fields')
    if cfg['enabled'] is not True:
        refuse('project intake is not enabled')
    parts = plain_path(cfg['staging'])
    if (len(parts) < 3 or parts[0] != 'references' or parts[1] not in library.GROUP_DIRS or
            not any(p.startswith('_') for p in parts[2:])):
        refuse('staging must be under references/<group>/ with an underscore directory excluded by normal scanners')
    staging = guarded(root, cfg['staging'])
    if not os.path.isdir(staging):
        refuse('staging folder is missing')
    mappings = cfg['mappings']
    if not isinstance(mappings, list) or not 1 <= len(mappings) <= MAX_ENTRIES:
        refuse('mappings must contain 1..100 entries')
    seen = {key: set() for key in ('code', 'canonical_name', 'destination')}
    for item in mappings:
        if not isinstance(item, dict) or set(item) != set(seen):
            refuse('mapping needs exactly code, canonical_name, destination')
        for key in seen:
            value = item[key]
            if (not isinstance(value, str) or not value.strip() or value != value.strip() or len(value) > 240 or
                    any(ord(c) < 32 for c in value)):
                refuse('invalid mapping ' + key)
            if value.casefold() in seen[key]:
                refuse('duplicate mapping ' + key + ': ' + value)
            seen[key].add(value.casefold())
        name = plain_path(item['canonical_name'])
        dest = plain_path(item['destination'])
        if len(name) != 1 or len(dest) < 2 or dest[0] not in library.GROUP_DIRS:
            refuse('canonical name or destination scope is invalid')
        if any(p.startswith(('.', '_', '~$')) for p in dest):
            refuse('destination is outside the managed source scope')
        if os.path.splitext(dest[-1])[1].lower() not in library.FILE_EXT or os.path.splitext(name[0])[1].lower() != os.path.splitext(dest[-1])[1].lower():
            refuse('canonical and destination extensions must match supported source types')
        target = guarded(root, 'references/' + item['destination'])
        if not os.path.isdir(os.path.dirname(target)):
            refuse('destination parent must already exist: ' + item['destination'])
        if library_sync.contained(target, staging):
            refuse('destination overlaps staging')
    return cfg, transaction.sha_bytes(raw)


def request(file=None, code=None):
    if (file is None) != (code is None):
        refuse('--file and --code must be used together')
    if file is not None and (len(plain_path(file)) != 1 or not isinstance(code, str) or not code.strip()):
        refuse('explicit selection needs a basename and a configured code')
    return {'file': file, 'code': code}


def observe(root, selection):
    if not isinstance(selection, dict) or set(selection) != {'file', 'code'}:
        refuse('malformed selection')
    selection = request(selection['file'], selection['code'])
    cfg, config_sha = read_config(root)
    folder = guarded(root, cfg['staging'])
    try:
        names = sorted(os.listdir(folder))
    except OSError as e:
        refuse('cannot list staging: %s' % e)
    if len(names) > MAX_ENTRIES:
        refuse('staging exceeds 100 entries')
    inventory, data, total = {}, {}, 0
    for name in names:
        path = guarded(root, cfg['staging'] + '/' + name)
        try:
            before = os.lstat(path)
            if not stat.S_ISREG(before.st_mode) or getattr(before, 'st_file_attributes', 0) & 0x400:
                refuse('staging entry is not a plain file: ' + name)
            if before.st_size > MAX_FILE:
                refuse('source exceeds 20 MiB: ' + name)
            if os.path.splitext(name)[1].lower() not in library.FILE_EXT or name.startswith(('.', '_', '~$')):
                refuse('unsupported staging entry: ' + name)
            with open(path, 'rb') as f:
                raw = f.read(MAX_FILE + 1)
            after = os.stat(path)
            if len(raw) > MAX_FILE or (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                refuse('source changed while reading: ' + name)
        except OSError as e:
            refuse('cannot read staging entry %s: %s' % (name, e))
        total += len(raw)
        if total > MAX_TOTAL:
            refuse('staging exceeds 100 MiB')
        inventory[name] = {'sha256': transaction.sha_bytes(raw), 'size': len(raw)}
        data[name] = raw
    if not names:
        refuse('staging has no files')
    if selection['file'] is not None and selection['file'] not in inventory:
        refuse('selected file is missing')
    selected, used = [], set()
    for name in names:
        if selection['file'] is not None and name != selection['file']:
            continue
        stem = library.fold(os.path.splitext(name)[0]).replace('_', '-')
        if stem.endswith('ban-gioi-thieu'):
            refuse('introduction suffix is not an original full-text source: ' + name)
        codes = [m for m in cfg['mappings'] if re.search(r'(?<![^\W_])' + re.escape(m['code']) + r'(?![^\W_])', name, re.I)]
        exact = [m for m in cfg['mappings'] if m['canonical_name'].casefold() == name.casefold()]
        if len(codes) > 1:
            refuse('multiple codes in ' + name)
        explicit = [m for m in cfg['mappings'] if m['code'] == selection['code']] if selection['code'] is not None else []
        if selection['code'] is not None and len(explicit) != 1:
            refuse('explicit code is not configured')
        candidates = explicit or exact or codes
        if len(candidates) != 1:
            refuse('no unique configured code in %s; old laws or similar topics are suggestions only; use an exact canonical name or explicit selection' % name)
        item = candidates[0]
        if codes and codes[0] != item:
            refuse('filename code conflicts with classification: ' + name)
        if item['code'] in used:
            refuse('multiple files for code: ' + item['code'])
        used.add(item['code'])
        if os.path.splitext(name)[1].lower() != os.path.splitext(item['destination'])[1].lower():
            refuse('source and destination extensions differ: ' + name)
        target = guarded(root, 'references/' + item['destination'])
        if os.path.lexists(target):
            refuse('destination already exists (even identical bytes are not overwritten): ' + item['destination'])
        selected.append(dict(item, source=cfg['staging'] + '/' + name, sha256=inventory[name]['sha256'], data=data[name]))
    return {'config_sha256': config_sha, 'inventory': inventory, 'staging': cfg['staging'],
            'selection': selection, 'selected': selected}


def binding(observation):
    return {k: observation[k] for k in ('config_sha256', 'inventory', 'staging', 'selection')}


def summary(result):
    return {k: v for k, v in result.items() if k not in ('bytes', 'create_files', 'observation')}


def command(rest, cli_library=None):
    cli = cli_library or library
    rest = list(rest)
    as_json = '--json' in rest
    apply = '--apply' in rest
    rest = [x for x in rest if x not in ('--json', '--apply')]
    token = cli.option(rest, '--expect-plan')
    file, code = cli.option(rest, '--file', None), cli.option(rest, '--code', None)
    if rest or (apply and not token) or (not apply and token):
        cli.stop('Usage: intake [--file BASENAME --code CODE] [--apply --expect-plan TOKEN] [--json]')
    try:
        selection = request(file, code)
        result = library_sync.intake_apply(cli.ROOT, selection, token) if apply else library_sync.intake_plan(cli.ROOT, selection)
    except library_sync.IntakeWriteError as e:
        actions = ['python tools/transaction.py status']
        if e.transaction and e.changes is not False:
            actions += ['python tools/transaction.py resume ' + e.transaction,
                        'python tools/transaction.py rollback ' + e.transaction]
        cli.set_result('partial' if e.changes is not False else 'blocked', 1, str(e),
                           changes=e.changes, files=e.files, transaction=e.transaction, next_actions=actions,
                           unchecked=[{'reason': 'write_effects_unknown'}] if e.changes is None else [])
        raise SystemExit(str(e))
    except (library_sync.SyncError, library.ContentError, transaction.TransactionError, OSError, ValueError) as e:
        cli.stop(str(e), reason='intake_refused')
    text = ('Intake committed; staging retained.' if apply else 'Preview only; classification does not verify identity, full text or current validity.')
    cli.set_result('success' if apply else 'preview', 0, text, changes=apply,
                       files=[{'path': 'references/' + x['destination'], 'action': 'create'} for x in result['items']] +
                             [{'path': 'references/_INDEX.xlsx', 'action': 'write'}],
                       plan_token=result['plan_token'], snapshot=result['snapshot'], protection=result.get('protection'))
    if as_json:
        print(json.dumps(summary(result), ensure_ascii=False))
    else:
        print(text)
        for item in result['items']:
            print('  %s -> %s [%s, revision 1, Cần đối chiếu]' % (item['source'], item['destination'], item['id']))
        print('  plan_token: ' + result['plan_token'])
    return 0
