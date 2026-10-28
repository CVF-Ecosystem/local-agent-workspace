#!/usr/bin/env python3
"""Profile project: lựa chọn được yêu cầu, chủ sở hữu quyền và migration quyền tường minh. / Project execution profile.

Dùng (từ thư mục gốc của project; --project chỉ tới project khác):
  python tools/execution_profile.py status
  python tools/execution_profile.py preview-config   --choices FILE
  python tools/execution_profile.py apply-config     --choices FILE [--expect-plan SHA]
  python tools/execution_profile.py preview-migration --grants FILE
  python tools/execution_profile.py apply-migration   --grants FILE --expect-plan SHA

Chỉ ghi `.agent/EXECUTION_PROFILE.json` (và, khi migration, một dòng trong PROJECT.md) qua tools/transaction.py.
Profile giữ lựa chọn ĐƯỢC YÊU CẦU (host, model hoặc tier, effort, fallback, giới hạn) và, khi authority_owner là PROFILE,
các record grant v3 chuẩn. Được yêu cầu KHÁC được quan sát: công cụ này không đo host nên host đã nạp, đăng ký hay áp dụng hay chưa đều ghi
NOT_INSPECTED (chưa kiểm), không phủ định cũng không khẳng định. Grant và evidence là lời khai hợp tác: công cụ kiểm cấu trúc, không chứng thực người dùng, nội dung hay hiệu lực.
The profile holds REQUESTED choices and, when authority_owner is PROFILE, canonical v3 grant records. Requested is not observed: this helper
does not inspect any host, so installed, registered and applied are all NOT_INSPECTED (neither denied nor claimed). Grants and evidence are cooperative claims: only structure is checked.

Schema cố định: `.agent/EXECUTION_PROFILE.schema.json` và `.cvf/contracts/v3/control.schema.json` của package đang chạy công cụ;
không nhận schema, $ref hay đường dẫn schema từ dữ liệu vào, không dùng mạng. Thiếu jsonschema (>=4.18) thì báo chưa kiểm và
không ghi gì phụ thuộc vào việc kiểm đó. Mã thoát: 0 đạt/xem trước/đã ghi, 1 bị chặn hoặc cần xử lý, 2 lỗi dùng. Python 3.8+.
"""
import argparse, datetime, hashlib, importlib, importlib.metadata, io, json, os, re, sys
from result_schema import emit, make
import transaction as tx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_REL = '.agent/EXECUTION_PROFILE.json'
SCHEMA_REL = '.agent/EXECUTION_PROFILE.schema.json'
CONTROL_SCHEMA_REL = '.cvf/contracts/v3/control.schema.json'
PROJECT_REL = 'PROJECT.md'
SCHEMA_VERSION = 'law.execution-profile/1'
SCHEMA_ID = 'urn:law:execution-profile:1'
CONTROL_SCHEMA_ID = 'urn:law:cvf:control:3'
CONTROL_VERSION = 'law.cvf.control/3'
STATUS_SCHEMA = 'local-agent-workspace/execution-profile-status-v1'
CORE_ROLES = ('scout', 'worker', 'reviewer')
CONFIG_KEYS = ('host', 'roles', 'fallback', 'requested_limits')
OWNERS = ('PROJECT', 'PROFILE')
MIN_JSONSCHEMA = (4, 18)
MAX_BYTES = 1024 * 1024
USER_CHANNELS = ('USER_MESSAGE', 'HOST_CONFIRMATION_UI', 'USER_AUTHORED_FILE')
# Dòng PROJECT.md giữ quyền gọi agent phụ khi authority_owner là PROJECT; con trỏ khi là PROFILE.
PROJECT_LABELS = ('Phạm vi được giao cho agent phụ', 'Standing scope for sub-agents')
POINTERS = {
    'vi': 'Xem .agent/EXECUTION_PROFILE.json (quyền gọi vai do profile giữ; chưa có grant thì chưa có quyền)',
    'en': 'See .agent/EXECUTION_PROFILE.json (sub-agent authority is held by the profile; no grant means no permission)',
}
NO_GRANT_WORDS = ('không có', 'khong co', 'none')
POINTER_EXAMPLE_NONE = {'vi': '- Phạm vi được giao cho agent phụ: Không có', 'en': '- Standing scope for sub-agents: None'}
_FORBIDDEN_KEY = re.compile(r'(?i)(api|key|token|secret|passw|credential|account|session|cookie|bearer|observed|applied|receipt|runtime)')
_SECRET_VALUE = re.compile(r'^(sk|pk|ghp|gho|xox[a-z])[-_][A-Za-z0-9_-]{16,}')
_FUTURE = re.compile(r'^law\.execution-profile/(\d+)$')
_HOOK = None  # TEST ONLY: _HOOK(point, info), point = apply (đã lập kế hoạch, trước khi ghi) / planned, before the write
LANG = 'vi'


def L(vi, en):
    return en if LANG == 'en' else vi


# Mã lý do (ngôn ngữ trung tính) -> (vi, en). Không chép dữ liệu của người dùng vào thông điệp.
REASONS = {
    'PROFILE_ABSENT': ('Chưa có profile.', 'No profile yet.'),
    'PROFILE_NOT_REGULAR_FILE': ('Profile không phải file thường (liên kết hoặc thư mục); giữ nguyên.', 'The profile is not a plain file (link or folder); left as is.'),
    'PROFILE_UNREADABLE': ('Không đọc được profile (không phải JSON UTF-8 hợp lệ, khóa trùng, quá lớn); giữ nguyên bytes.', 'The profile cannot be read (not valid UTF-8 JSON, duplicate keys, too large); bytes kept.'),
    'PROFILE_INVALID': ('Profile sai cấu trúc; giữ nguyên bytes, không tự sửa.', 'The profile has the wrong structure; bytes kept, not repaired.'),
    'PROFILE_UNSUPPORTED_VERSION': ('Profile thuộc phiên bản schema chưa hỗ trợ (hoặc không rõ); giữ nguyên bytes, không đọc như quyền.', 'The profile has an unsupported or unknown schema version; bytes kept, not read as authority.'),
    'GRANT_INVALID': ('Một grant không đúng record grant v3 chuẩn.', 'A grant is not a canonical v3 grant record.'),
    'CREDENTIAL_FIELD': ('Có trường giống khóa/tài khoản/phiên/quan sát/biên nhận; profile không được chứa các trường này.', 'A key, account, session, observed or receipt-like field is present; the profile must not hold these.'),
    'CREDENTIAL_VALUE': ('Có giá trị giống khóa truy cập; profile không được chứa.', 'A value looks like an access key; the profile must not hold it.'),
    'VALIDATOR_UNAVAILABLE': ('Chưa kiểm được cấu trúc: thiếu jsonschema (>=4.18) hoặc schema cố định không dùng được.', 'Structure not checked: jsonschema (>=4.18) or a fixed schema is unusable.'),
    'OWNER_CONFLICT': ('Chủ sở hữu quyền mâu thuẫn giữa profile và PROJECT.md; không dùng quyền từ cả hai nơi.', 'Authority owner conflicts between the profile and PROJECT.md; neither source is used.'),
    'PROJECT_LINE_MISSING': ('PROJECT.md không có dòng quyền gọi agent phụ; không đoán.', 'PROJECT.md has no sub-agent scope line; not guessed.'),
    'PROJECT_LINE_AMBIGUOUS': ('PROJECT.md có nhiều dòng quyền gọi agent phụ; không đoán.', 'PROJECT.md has several sub-agent scope lines; not guessed.'),
    'PROJECT_UNREADABLE': ('Không đọc được PROJECT.md như file thường UTF-8.', 'PROJECT.md cannot be read as a plain UTF-8 file.'),
    'LEGACY_MIGRATION_REQUIRED': ('PROJECT.md còn dòng quyền dạng văn xuôi cũ: chưa phải grant v3, không suy thành quyền; cần migration tường minh.', 'PROJECT.md still holds a legacy prose scope line: not a v3 grant, never read as authority; an explicit migration is required.'),
    'POINTER_PROFILE_MISSING': ('PROJECT.md trỏ tới profile nhưng profile không có; không tự tạo hộ.', 'PROJECT.md points to the profile but it is missing; not created on its behalf.'),
    'TRANSACTION_UNFINISHED': ('Có giao dịch file chưa xong; chạy tools/transaction.py status rồi resume hoặc rollback.', 'A file transaction is unfinished; run tools/transaction.py status, then resume or rollback.'),
    'TRANSACTION_UNKNOWN': ('Không xác định được có giao dịch dở hay không (nhật ký không đọc được); không xóa nhật ký để chạy tiếp.', 'Cannot tell whether a transaction is unfinished (journal unreadable); do not delete journals to continue.'),
    'RUNTIME_UNSAFE': ('Thư mục runtime là hoặc đi qua liên kết; chưa ghi gì.', 'The runtime folder is or passes through a link; nothing written.'),
    'TARGET_NOT_REGULAR_FILE': ('Một file đích là liên kết hoặc không phải file thường; chưa ghi gì.', 'A target is a link or not a plain file; nothing written.'),
    'CONFIG_NOT_OBJECT': ('File lựa chọn phải là một đối tượng JSON.', 'The choices file must be a JSON object.'),
    'CONFIG_FORBIDDEN_FIELD': ('Config chỉ sửa host, roles, fallback, requested_limits; không nhận grants, authority_owner, schema_version hay trường khác.', 'Config edits only host, roles, fallback and requested_limits; grants, authority_owner, schema_version and other fields are refused.'),
    'CONFIG_EMPTY': ('File lựa chọn rỗng; không có gì để đổi.', 'The choices file is empty; nothing to change.'),
    'CONFIG_INVALID': ('Lựa chọn mới không hợp schema; chưa ghi gì.', 'The new choices do not fit the schema; nothing written.'),
    'CONFIG_BLOCKED_STATE': ('Không sửa lựa chọn khi profile/owner ở trạng thái này; giữ nguyên.', 'Choices are not edited in this profile/owner state; left as is.'),
    'MIGRATION_BLOCKED_STATE': ('Migration chỉ chạy khi profile hợp lệ, owner là PROJECT, chưa có grant và PROJECT.md còn đúng một dòng (cũ hoặc trống).', 'Migration needs a valid profile with owner PROJECT, no grants yet and exactly one PROJECT.md scope line (legacy or empty).'),
    'MIGRATION_NO_GRANTS': ('Không có grant nào để migration.', 'There are no grants to migrate.'),
    'MIGRATION_INPUT_NOT_GRANTS': ('Đầu vào migration phải là mảng record grant có cấu trúc (không phải văn xuôi).', 'Migration input must be an array of structured grant records (not prose).'),
    'GRANT_NOT_V3': ('Grant không phải law.cvf.control/3 (v1/v2/thiếu/lạ): không tự nâng cấp.', 'A grant is not law.cvf.control/3 (v1, v2, missing or unknown): never upgraded.'),
    'GRANT_NOT_GRANT_RECORD': ('Một record không phải record_type grant.', 'A record is not record_type grant.'),
    'GRANT_EXAMPLE_OR_INACTIVE': ('Grant là ví dụ hoặc không ở trạng thái ACTIVE.', 'A grant is an example or is not ACTIVE.'),
    'GRANT_ATTRIBUTION_MISSING': ('Grant thiếu khai báo USER_CONFIRMATION kèm kênh người dùng và evidence_locator.', 'A grant lacks a USER_CONFIRMATION declaration with a user channel and evidence_locator.'),
    'GRANT_DUPLICATE_ID': ('Có grant_id trùng.', 'A grant_id is duplicated.'),
    'PREVIEW_REQUIRED': ('Apply migration cần mã kế hoạch (--expect-plan) lấy từ lần xem trước.', 'Applying a migration needs the plan hash (--expect-plan) taken from the preview.'),
    'PLAN_CHANGED': ('Kế hoạch tính lại khác bản đã xem trước (file đổi hoặc đầu vào đổi); chưa ghi gì.', 'The recomputed plan differs from the previewed one (a file or the input changed); nothing written.'),
    'BACKUP_EXISTS': ('Bản sao lưu cùng ngày đã tồn tại; không ghi đè. Chuyển hoặc đổi tên rồi thử lại.', 'A same-day backup already exists; not overwritten. Move or rename it, then retry.'),
    'NOTHING_TO_CHANGE': ('Không có gì thay đổi.', 'Nothing changes.'),
    'EXPECTED_BEFORE_MISMATCH': ('File đã đổi từ lúc đọc; chưa ghi gì.', 'A file changed since it was read; nothing written.'),
    'WRITE_REFUSED': ('Giao dịch từ chối trước khi ghi; chưa ghi file người dùng.', 'The transaction refused before writing; no user file was written.'),
    'PARTIAL_WRITE': ('Ghi dở: một phần đã ghi, giao dịch còn mở; dùng status/resume/rollback, không xóa nhật ký.', 'Partial write: some of it was written and the transaction is open; use status/resume/rollback, do not delete journals.'),
    'POST_WRITE_MISMATCH': ('Sau khi ghi, bytes không như kế hoạch; kiểm giao dịch và file trước khi tin.', 'After writing, the bytes differ from the plan; check the transaction and files before trusting them.'),
}


def reason_text(code):
    vi_en = REASONS.get(code)
    return L(*vi_en) if vi_en else code


# Bước xử lý cụ thể cho trạng thái bị chặn. Chỉ là hướng dẫn: không bước nào tự cấp quyền, tự tạo profile mẫu hay đặt lại grant.
# Concrete next steps for a blocked state. Guidance only: no step grants authority, creates a sample profile or resets grants.
def next_steps(code, project=None, package=None):
    """Danh sách câu hướng dẫn (ngôn ngữ hiện tại) cho một mã trạng thái, hoặc [] nếu không có. project/package là đường dẫn thật khi biết.
    Localised guidance lines for a state code, or [] when there is none; project/package are real paths when known."""
    proj = '"%s"' % project if project else L('"<thư-mục-project>"', '"<project-folder>"')
    pkg = '"%s"' % os.path.join(package, 'tools', 'upgrade_package.py') if package else L('"<package-mới>/tools/upgrade_package.py"', '"<new-package>/tools/upgrade_package.py"')
    example = POINTER_EXAMPLE_NONE[LANG if LANG in POINTER_EXAMPLE_NONE else 'vi']
    if code == 'PROJECT_LINE_MISSING':
        return [
            L('Agent chỉ thêm dòng quyền vào PROJECT.md khi bạn giao việc đó. Nếu bạn chọn không giao quyền gọi agent phụ, thêm đúng một dòng: %s',
              'An agent adds the scope line to PROJECT.md only when you assign that. If you choose to grant no sub-agent scope, add exactly one line: %s') % example,
            L('Rồi xem trước bằng package MỚI (không ghi gì): python %s --project %s', 'Then preview with the NEW package (writes nothing): python %s --project %s') % (pkg, proj),
            L('Thấy dòng "Tạo .agent/EXECUTION_PROFILE.json (owner quyền PROJECT, chưa có grant)" thì chạy lại lệnh đó thêm --apply. PROJECT.md và STATE.md không bị ghi đè; bước này chưa cấp quyền gọi vai nào.',
              'When it lists "Create .agent/EXECUTION_PROFILE.json (authority owner PROJECT, no grants)", run the same command with --apply. PROJECT.md and STATE.md are not overwritten; this step grants no role.')]
    if code == 'PROJECT_LINE_AMBIGUOUS':
        return [L('PROJECT.md có nhiều hơn một dòng quyền gọi agent phụ. Chủ sở hữu project giữ đúng một dòng (agent không tự chọn dòng nào đúng), rồi chạy lại: python tools/execution_profile.py status',
                  'PROJECT.md has more than one sub-agent scope line. The project owner keeps exactly one (an agent does not pick which is right), then run again: python tools/execution_profile.py status')]
    if code == 'POINTER_PROFILE_MISSING':
        return [
            L('PROJECT.md đã trỏ tới profile nhưng .agent/EXECUTION_PROFILE.json không còn. Khôi phục đúng file đó từ bản sao lưu của chính project này (giữ nguyên bytes) trước khi cấu hình.',
              'PROJECT.md points to the profile but .agent/EXECUTION_PROFILE.json is gone. Restore exactly that file from the backup of this very project (same bytes) before configuring anything.'),
            L('Không có bản sao lưu thì giữ nguyên trạng thái chặn: không dựng profile mẫu, không sửa dòng PROJECT.md thành "Không có" để lách, không dùng init_project.py --force. Nhờ chủ sở hữu project xác nhận cách khôi phục hoặc đặt lại quyền (một quyết định riêng).',
              'With no backup, stay blocked: do not build a sample profile, do not change the PROJECT.md line to "None" to get around it, and do not use init_project.py --force. Ask the project owner to confirm how to restore or reset the authority (a separate decision).')]
    if code == 'PROFILE_BOOTSTRAP':
        return [L('Dòng quyền trong PROJECT.md đã rõ. Tạo profile (owner PROJECT, chưa có grant) bằng package MỚI: xem trước python %s --project %s, rồi thêm --apply.',
                  'The PROJECT.md scope line is clear. Create the profile (owner PROJECT, no grants) with the NEW package: preview python %s --project %s, then add --apply.') % (pkg, proj)]
    return []


def steps_for(rep, project=None, package=None):
    """Bước xử lý cho kết quả inspect(); chỉ khi profile chưa có. / Next steps for an inspect() report; only while the profile is absent."""
    if 'POINTER_PROFILE_MISSING' in (rep.get('reasons') or []):
        return next_steps('POINTER_PROFILE_MISSING', project, package)
    if rep.get('state') == 'PROFILE_ABSENT':
        kind = rep.get('project_line')
        if kind in ('MISSING', 'AMBIGUOUS'):
            return next_steps('PROJECT_LINE_' + kind, project, package)
        if kind in ('EMPTY', 'PLACEHOLDER'):
            return next_steps('PROFILE_BOOTSTRAP', project, package)
    return []


# ---------------------------------------------------------------- bytes, JSON
def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _is_link(path):
    if os.path.islink(path):
        return True
    try:
        return bool(getattr(os.lstat(path), 'st_file_attributes', 0) & 0x400)  # Windows reparse point (junction)
    except OSError:
        return False


def _abs(root, rel):
    return os.path.join(root, *rel.split('/'))


def read_plain(path):
    """(bytes, None) | (None, 'ABSENT'|'NOT_REGULAR'|'UNREADABLE'). Không theo liên kết. / Never follows a link."""
    if not os.path.lexists(path):
        return None, 'ABSENT'
    if _is_link(path) or not os.path.isfile(path):
        return None, 'NOT_REGULAR'
    try:
        with open(path, 'rb') as f:
            data = f.read(MAX_BYTES + 1)
    except OSError:
        return None, 'UNREADABLE'
    if len(data) > MAX_BYTES:
        return None, 'UNREADABLE'
    return data, None


class JsonError(Exception):
    pass


def _no_dupes(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise JsonError('duplicate key')
        out[k] = v
    return out


def _no_constants(name):
    raise JsonError('non-finite number')


def parse_json_bytes(data):
    """Parse nghiêm: UTF-8, khóa không trùng, không NaN/Infinity. Thông điệp lỗi cố định, không chép dữ liệu. / Strict parse, fixed messages."""
    try:
        text = data.decode('utf-8')
        if text.startswith('﻿'):
            text = text[1:]
        return json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_no_constants)
    except (UnicodeDecodeError, ValueError, RecursionError, JsonError):
        raise JsonError('not valid UTF-8 JSON')


def serialize(doc):
    return (json.dumps(doc, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def default_profile(owner='PROFILE'):
    empty = {'model': None, 'tier': None, 'effort': None}
    return {
        'schema_version': SCHEMA_VERSION,
        'authority_owner': owner,
        'host': None,
        'roles': dict((r, dict(empty)) for r in CORE_ROLES),
        'fallback': dict(empty, allowed=False),
        'requested_limits': {'max_concurrency': None, 'max_depth': None},
        'grants': [],
    }


def clean_profile_bytes():
    """Bytes của profile sạch giao đi: owner PROFILE, không lựa chọn, không grant. / The clean profile that ships."""
    return serialize(default_profile('PROFILE'))


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(',', ':'))


# ---------------------------------------------------------------- PROJECT.md
def _line_re(label):
    return re.compile(r'^(- %s: )(.*?)(\r?)$' % re.escape(label), re.M)


def project_line(text):
    """(loại, giá trị, nhãn) của dòng quyền trong PROJECT.md. Loại: MISSING | AMBIGUOUS | EMPTY | PLACEHOLDER | POINTER | LEGACY.
    Chỉ đọc đúng một dòng; thiếu hoặc nhiều hơn một dòng thì không đoán. / Kind of the single scope line; never guesses on 0 or 2+ lines."""
    found = []
    for label in PROJECT_LABELS:
        found += [(m, label) for m in _line_re(label).finditer(text)]
    if not found:
        return 'MISSING', '', None
    if len(found) > 1:
        return 'AMBIGUOUS', '', None
    m, label = found[0]
    value = m.group(2).strip()
    if value in POINTERS.values():
        return 'POINTER', value, label
    if not value or value.lower().rstrip('.') in NO_GRANT_WORDS:
        return 'EMPTY', value, label
    if value.startswith('[') and value.endswith(']'):
        return 'PLACEHOLDER', value, label
    return 'LEGACY', value, label


def replace_project_line(text, label, new_value):
    """Thay giá trị của đúng một dòng, giữ kiểu xuống dòng. Trả về text mới hoặc None nếu không còn đúng một dòng. / Replace the one line."""
    pat = _line_re(label)
    if len(pat.findall(text)) != 1:
        return None
    return pat.sub(lambda m: m.group(1) + new_value + m.group(3), text, count=1)


def pointer_for(label):
    return POINTERS['en'] if label == PROJECT_LABELS[1] else POINTERS['vi']


# ---------------------------------------------------------------- validators
_VALIDATOR_CACHE = {}


def _has_remote_ref(node):
    stack = [node]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for key in ('$ref', '$dynamicRef', '$recursiveRef'):
                ref = cur.get(key)
                if isinstance(ref, str) and not ref.startswith('#'):
                    return True
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return False


def _jsonschema_ok():
    try:
        jsonschema = importlib.import_module('jsonschema')
        importlib.import_module('referencing')
        version = tuple(int(x) for x in re.findall(r'\d+', importlib.metadata.version('jsonschema'))[:2])
    except Exception:
        return None
    if version < MIN_JSONSCHEMA or not hasattr(jsonschema, 'Draft202012Validator'):
        return None
    return jsonschema


def _make_validator(rel, schema_id):
    """Validator Draft 2020-12 cho một schema CỐ ĐỊNH của package đang chạy; refs chỉ cục bộ, không tải gì. None nếu không dùng được."""
    jsonschema = _jsonschema_ok()
    if jsonschema is None:
        return None
    data, bad = read_plain(_abs(ROOT, rel))
    if data is None:
        return None
    key = (rel, sha256(data))
    if key in _VALIDATOR_CACHE:
        return _VALIDATOR_CACHE[key]
    validator = None
    try:
        from referencing import Registry
        from referencing.exceptions import NoSuchResource
        schema = parse_json_bytes(data)
        if isinstance(schema, dict) and schema.get('$id') == schema_id and not _has_remote_ref(schema):
            def deny(uri):
                raise NoSuchResource(ref=uri)
            jsonschema.Draft202012Validator.check_schema(schema)
            validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker(),
                                                        registry=Registry(retrieve=deny))
    except Exception:
        validator = None
    _VALIDATOR_CACHE[key] = validator
    return validator


def profile_validator():
    return _make_validator(SCHEMA_REL, SCHEMA_ID)


def control_validator():
    return _make_validator(CONTROL_SCHEMA_REL, CONTROL_SCHEMA_ID)


def schema_errors(validator, doc, limit=6):
    """[{'path', 'rule'}] ổn định, KHÔNG chép giá trị của dữ liệu. / Stable error locations, never the data values."""
    out = []
    try:
        errs = sorted(validator.iter_errors(doc), key=lambda e: (list(map(str, e.absolute_path)), e.validator))
    except Exception:
        return [{'path': '/', 'rule': 'validator_error'}]
    for e in errs[:limit]:
        out.append({'path': '/' + '/'.join(str(p) for p in e.absolute_path), 'rule': e.validator})
    return out


def schema_problems():
    """Lỗi tự thân của schema/mặc định (cho check_package). [] khi ổn hoặc khi chưa có jsonschema. / Self-check of schema and default."""
    data, bad = read_plain(_abs(ROOT, SCHEMA_REL))
    if data is None:
        return ['Thiếu hoặc không đọc được %s.' % SCHEMA_REL]
    try:
        schema = parse_json_bytes(data)
    except JsonError:
        return ['%s không phải JSON hợp lệ.' % SCHEMA_REL]
    if not isinstance(schema, dict) or schema.get('$id') != SCHEMA_ID or _has_remote_ref(schema):
        return ['%s: $id sai hoặc có $ref không cục bộ.' % SCHEMA_REL]
    if _jsonschema_ok() is None:
        return []
    validator = profile_validator()
    if validator is None:
        return ['%s không dùng được như schema Draft 2020-12.' % SCHEMA_REL]
    out = []
    for owner in OWNERS:
        errs = schema_errors(validator, default_profile(owner))
        if errs:
            out.append('Profile mặc định (owner %s) không hợp %s: %s' % (owner, SCHEMA_REL, errs[0]))
    return out


# ---------------------------------------------------------------- kiểm nội dung profile
def forbidden_findings(doc):
    """Mã CREDENTIAL_FIELD / CREDENTIAL_VALUE ngoài grants (grants có trường riêng như session_ref của actor). / Outside grants only."""
    found = set()
    stack = [doc]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if cur is doc and k == 'grants':
                    continue
                if isinstance(k, str) and _FORBIDDEN_KEY.search(k):
                    found.add('CREDENTIAL_FIELD')
                stack.append(v)
        elif isinstance(cur, list):
            stack.extend(cur)
        elif isinstance(cur, str) and _SECRET_VALUE.search(cur):
            found.add('CREDENTIAL_VALUE')
    return sorted(found)


def grant_problems(grant, index, validator):
    """Mã vấn đề của MỘT record grant (cấu trúc v3 + điều kiện migration), kèm vị trí; không chép nội dung. / Problem codes for one grant."""
    codes = set()
    if not isinstance(grant, dict):
        return ['GRANT_NOT_GRANT_RECORD']
    if grant.get('schema_version') != CONTROL_VERSION:
        codes.add('GRANT_NOT_V3')
    if grant.get('record_type') != 'grant':
        codes.add('GRANT_NOT_GRANT_RECORD')
    if 'GRANT_NOT_V3' not in codes and 'GRANT_NOT_GRANT_RECORD' not in codes:
        if schema_errors(validator, grant, limit=1):
            codes.add('GRANT_INVALID')
    return sorted(codes)


def migration_grant_problems(grant):
    """Điều kiện thêm cho grant đưa vào migration: ACTIVE, không ví dụ, khai báo USER_CONFIRMATION kênh người dùng + evidence_locator."""
    codes = set()
    if grant.get('example_only') is not None or grant.get('status') != 'ACTIVE':
        codes.add('GRANT_EXAMPLE_OR_INACTIVE')
    ref = grant.get('issuer_ref')
    att = ref.get('attribution') if isinstance(ref, dict) else None
    if not (isinstance(att, dict) and att.get('source_class') == 'USER_CONFIRMATION' and att.get('channel') in USER_CHANNELS
            and isinstance(att.get('evidence_locator'), str) and att.get('evidence_locator').strip()):
        codes.add('GRANT_ATTRIBUTION_MISSING')
    return sorted(codes)


def evaluate_doc(doc):
    """Đánh giá một đối tượng profile đã parse. Trả (status, reasons, detail): status = OK | UNSUPPORTED | INVALID | UNVALIDATED."""
    if not isinstance(doc, dict):
        return 'INVALID', ['PROFILE_INVALID'], []
    version = doc.get('schema_version')
    if version != SCHEMA_VERSION:
        if isinstance(version, str):
            return 'UNSUPPORTED', ['PROFILE_UNSUPPORTED_VERSION'], []
        return 'INVALID', ['PROFILE_INVALID'], [{'path': '/schema_version', 'rule': 'required'}]
    validator = profile_validator()
    if validator is None:
        return 'UNVALIDATED', ['VALIDATOR_UNAVAILABLE'], []
    errs = schema_errors(validator, doc)
    reasons = set()
    if errs:
        reasons.add('PROFILE_INVALID')
    reasons.update(forbidden_findings(doc))
    grants = doc.get('grants')
    if not errs and isinstance(grants, list) and grants:
        cv = control_validator()
        if cv is None:
            return 'UNVALIDATED', ['VALIDATOR_UNAVAILABLE'], []
        for i, g in enumerate(grants):
            bad = grant_problems(g, i, cv)
            if bad:
                reasons.add('GRANT_INVALID')
                errs.append({'path': '/grants/%d' % i, 'rule': ','.join(bad)})
        ids = [g.get('grant_id') for g in grants if isinstance(g, dict)]
        if len(set(map(str, ids))) != len(ids):
            reasons.add('GRANT_INVALID')
            errs.append({'path': '/grants', 'rule': 'GRANT_DUPLICATE_ID'})
    if reasons:
        return 'INVALID', sorted(reasons), errs
    return 'OK', [], []


# ---------------------------------------------------------------- trạng thái
def package_language(root):
    data, _ = read_plain(_abs(root, '.agent/PACKAGE_INFO.json'))
    if data:
        try:
            return 'en' if parse_json_bytes(data).get('language') == 'en' else 'vi'
        except (JsonError, AttributeError):
            pass
    return 'vi'


def pending_transactions(root):
    """('NONE'|'UNFINISHED'|'UNKNOWN', ids). Nhật ký không đọc được là UNKNOWN, không phải NONE. / An unreadable journal is UNKNOWN, never NONE."""
    if tx.runtime_problem(root):  # runtime là hoặc đi qua liên kết: không đọc được nhật ký nên không được coi là "không có giao dịch dở"
        return 'UNKNOWN', []
    try:
        items = tx.incomplete(root, strict=True)
    except (OSError, ValueError, TypeError, AttributeError, tx.TransactionError):
        return 'UNKNOWN', []
    if items:
        return 'UNFINISHED', [i['id'] for i in items]
    return 'NONE', []


def role_catalog(root, role):
    data, bad = read_plain(_abs(root, 'roles/%s/config.json' % role))
    if data is None:
        return {'catalog': 'MISSING' if bad == 'ABSENT' else 'INVALID'}
    try:
        cfg = parse_json_bytes(data)
    except JsonError:
        return {'catalog': 'INVALID'}
    if not isinstance(cfg, dict) or cfg.get('role') != role:
        return {'catalog': 'INVALID'}
    presets = cfg.get('host_presets')
    presets = list(presets.values()) if isinstance(presets, dict) else ([presets] if presets else [])
    candidate = [isinstance(p, dict) and p.get('status') == 'CANDIDATE' for p in presets]
    # A CANDIDATE factory preset is a suggestion for the user, never a qualified product preset (A-10).
    return {'catalog': 'PRESENT', 'catalog_status': cfg.get('status') if isinstance(cfg.get('status'), str) else None,
            'product_presets': not all(candidate) if presets else False, 'candidate_presets': any(candidate)}


def _grant_claims_role(grant, role):
    if not isinstance(grant, dict) or grant.get('status') != 'ACTIVE' or 'example_only' in grant:
        return False
    scope = grant.get('scope')
    callees = scope.get('delegate_callees') if isinstance(scope, dict) else None
    return any(isinstance(c, dict) and c.get('role_class') == 'core' and c.get('role_name') == role
               for c in (callees if isinstance(callees, list) else []))


def _capture(root):
    """Đọc MỘT lần PROJECT.md, profile và tình trạng giao dịch. Kiểm owner/state và lập kế hoạch cùng dùng đúng các bytes này, không đọc lại.
    Chỉ nằm trong bộ nhớ của lần gọi; không vào status/log và không là quyền. / One read of PROJECT.md, the profile and the transaction state;
    validation and planning use exactly these bytes. In memory for one call only: not in status or logs, and not authority."""
    return {'tx': pending_transactions(root), 'project': read_plain(_abs(root, PROJECT_REL)), 'profile': read_plain(_abs(root, PROFILE_REL))}


def inspect(root):
    """Báo cáo trạng thái, CHỈ ĐỌC. Không bao giờ ghi, tạo, sửa hay chuẩn hóa file. / Read-only status report."""
    root = os.path.abspath(root)
    return _inspect_capture(root, _capture(root))[0]


def _inspect_capture(root, cap):
    """(rep, doc): đánh giá trên snapshot đã chụp; doc là profile đã parse khi hợp lệ, nếu không None. / Evaluates a captured snapshot."""
    rep = {'schema': STATUS_SCHEMA, 'state': None, 'reasons': [], 'profile': {'path': PROFILE_REL, 'status': None},
           'owner': None, 'project_line': None, 'migration_required': False, 'authority_usable': False,
           'grant_claims': 0, 'requested': None, 'roles': {}, 'transaction': {'state': 'NONE', 'ids': []}, 'detail': [],
           'host_application': 'NOT_INSPECTED',
           'unchecked': ['host_application', 'native_registration', 'grant_authenticity', 'grant_expiry', 'requested_limits_enforcement']}
    pstate, pids = cap['tx']
    rep['transaction'] = {'state': pstate, 'ids': pids}
    proj, pbad = cap['project']
    line = ('UNREADABLE', '', None)
    if proj is not None:
        try:
            line = project_line(proj.decode('utf-8'))
        except UnicodeDecodeError:
            proj = None
    rep['project_line'] = line[0]
    data, bad = cap['profile']
    doc, status, reasons = None, None, []
    if bad == 'ABSENT':
        status, reasons = 'ABSENT', ['PROFILE_ABSENT']
    elif bad == 'NOT_REGULAR':
        status, reasons = 'INVALID', ['PROFILE_NOT_REGULAR_FILE']
    elif data is None:
        status, reasons = 'INVALID', ['PROFILE_UNREADABLE']
    else:
        try:
            doc = parse_json_bytes(data)
        except JsonError:
            status, reasons = 'INVALID', ['PROFILE_UNREADABLE']
        else:
            status, reasons, detail = evaluate_doc(doc)
            rep['detail'] = detail
    rep['profile']['status'] = status
    rep['profile']['sha256'] = sha256(data) if data is not None else None
    if isinstance(doc, dict) and isinstance(doc.get('schema_version'), str):
        rep['profile']['schema_version'] = doc['schema_version']
    owner = doc.get('authority_owner') if status == 'OK' else None
    rep['owner'] = owner
    state, extra = None, []
    if pstate == 'UNKNOWN':
        state, extra = 'TRANSACTION_UNKNOWN', ['TRANSACTION_UNKNOWN']
    elif pstate == 'UNFINISHED':
        state, extra = 'TRANSACTION_UNFINISHED', ['TRANSACTION_UNFINISHED']
    elif status != 'OK':
        state = {'ABSENT': 'PROFILE_ABSENT', 'INVALID': 'INVALID', 'UNSUPPORTED': 'UNSUPPORTED', 'UNVALIDATED': 'UNVALIDATED'}[status]
        extra = list(reasons)
        if status == 'ABSENT' and line[0] == 'LEGACY':
            extra.append('LEGACY_MIGRATION_REQUIRED')
            rep['migration_required'] = True
        if status == 'ABSENT' and line[0] == 'POINTER':
            extra.append('POINTER_PROFILE_MISSING')
    elif proj is None:
        state, extra = 'PROJECT_UNREADABLE', ['PROJECT_UNREADABLE']
    elif line[0] in ('MISSING', 'AMBIGUOUS'):
        state, extra = 'PROJECT_LINE_' + line[0], ['PROJECT_LINE_' + line[0]]
    else:
        grants = doc.get('grants') or []
        if owner == 'PROJECT':
            conflict = bool(grants) or line[0] == 'POINTER'
        else:
            conflict = line[0] != 'POINTER'
        if conflict:
            state, extra = 'OWNER_CONFLICT', ['OWNER_CONFLICT']
        elif owner == 'PROJECT' and line[0] == 'LEGACY':
            state, extra = 'LEGACY', ['LEGACY_MIGRATION_REQUIRED']
            rep['migration_required'] = True
        else:
            state = 'OK'
    rep['state'], rep['reasons'] = state, extra
    ok = state in ('OK', 'LEGACY')  # lựa chọn đọc được; quyền chỉ khi OK
    if status == 'OK' and ok:
        rep['requested'] = {'host': doc['host'], 'fallback': doc['fallback'], 'requested_limits': doc['requested_limits']}
    # A profile contains claims only. No authority is made usable by this helper;
    # grant_claims and GRANT_CLAIMED below are storage diagnostics, not permission.
    for role in CORE_ROLES:
        info = role_catalog(root, role)
        choice = doc['roles'][role] if (status == 'OK' and ok) else None
        configured = bool(choice and any(choice.get(k) is not None for k in ('model', 'tier', 'effort')))
        if choice is None:
            config = 'UNAVAILABLE'
        else:
            config = 'REQUESTED' if configured else 'NOT_CONFIGURED'
        if state == 'LEGACY':
            permission = 'LEGACY_UNMIGRATED'
        elif state == 'OK' and owner == 'PROFILE' and any(_grant_claims_role(g, role) for g in doc.get('grants') or []):
            permission = 'GRANT_CLAIMED'
        elif state == 'OK':
            permission = 'NO_GRANT'
        else:
            permission = 'BLOCKED'
        info.update(requested=choice, config=config, applied='NOT_INSPECTED', registration='NOT_INSPECTED', permission=permission)
        rep['roles'][role] = info
    if state == 'OK' and owner == 'PROFILE':
        rep['grant_claims'] = len(doc.get('grants') or [])
    return rep, (doc if status == 'OK' else None)


def format_status(rep):
    lines = [L('Profile project: %s', 'Project profile: %s') % rep['state']]
    for code in rep['reasons']:
        lines.append('  - %s: %s' % (code, reason_text(code)))
    lines.append(L('  File: %s (%s)  Owner quyền: %s  Dòng PROJECT: %s', '  File: %s (%s)  Authority owner: %s  PROJECT line: %s') % (
        rep['profile']['path'], rep['profile']['status'], rep['owner'] or '-', rep['project_line']))
    for role in CORE_ROLES:
        info = rep['roles'][role]
        req = info['requested']
        shown = '-' if not req else ', '.join('%s=%s' % (k, req[k]) for k in ('model', 'tier', 'effort') if req.get(k) is not None) or '-'
        lines.append('  %-9s %s: %s | %s=%s | %s | %s' % (
            role, L('yêu cầu', 'requested'), shown, L('áp dụng', 'applied'), info['applied'], info['registration'], info['permission']))
    lines.append(L('  Chưa kiểm/không có: host có áp dụng lựa chọn hay không, đăng ký native, tính xác thực và hạn của grant, thực thi giới hạn.',
                   '  Not checked/not available: whether a host applies choices, native registration, grant authenticity and expiry, limit enforcement.'))
    return '\n'.join(lines)


# ---------------------------------------------------------------- bootstrap (init / adopt / upgrade)
def bootstrap_plan(project_text):
    """Profile thiếu: chỉ bootstrap khi PROJECT.md đủ rõ. Không copy/parse văn xuôi ra grant. Trả dict {bytes|None, state, reasons}.
    Missing profile: bootstrap only when PROJECT.md is clear; prose is never turned into grants."""
    kind = project_line(project_text)[0]
    if kind in ('MISSING', 'AMBIGUOUS'):
        return {'bytes': None, 'state': 'PROJECT_LINE_' + kind, 'reasons': ['PROJECT_LINE_' + kind]}
    if kind == 'POINTER':
        return {'bytes': None, 'state': 'POINTER_PROFILE_MISSING', 'reasons': ['POINTER_PROFILE_MISSING']}
    if kind == 'LEGACY':
        return {'bytes': serialize(default_profile('PROJECT')), 'state': 'LEGACY', 'reasons': ['LEGACY_MIGRATION_REQUIRED']}
    return {'bytes': serialize(default_profile('PROJECT')), 'state': 'OK', 'reasons': []}


# ---------------------------------------------------------------- ghi
def _result(status, reasons=(), **kw):
    out = {'status': status, 'reasons': list(reasons)}
    out.update(kw)
    return out


def _hook(point, info):
    if _HOOK is not None:
        _HOOK(point, info)


def _preflight_write(root, rels):
    """Từ chối TRƯỚC khi lập giao dịch: runtime qua liên kết, file đích không thường, giao dịch dở/không rõ."""
    if tx.runtime_problem(root):
        return ['RUNTIME_UNSAFE']
    for rel in rels:
        path = _abs(root, rel)
        if os.path.lexists(path) and (_is_link(path) or not os.path.isfile(path)):
            return ['TARGET_NOT_REGULAR_FILE']
    state, ids = pending_transactions(root)
    if state != 'NONE':
        return ['TRANSACTION_' + state]
    return []


def _classify(root, ops, txid, exc):
    """Quyết định kết quả từ chính file, không chỉ từ ngoại lệ. ops: [(rel, before_sha, after_sha)]. / Outcome decided from the files."""
    seen = []
    for rel, before, after in ops:
        data, _ = read_plain(_abs(root, rel))
        cur = sha256(data) if data is not None else None
        seen.append('after' if cur == after else ('before' if cur == before else 'other'))
    done = seen.count('after')
    if exc is None:
        if done == len(seen):
            return _result('WRITTEN', files=[{'path': r, 'action': 'written'} for r, _, _ in ops], txid=txid)
        return _result('UNKNOWN', ['POST_WRITE_MISMATCH'], txid=txid)
    if done == 0:  # chưa file nào được thay: không phải ghi dở / nothing was replaced: not a partial write
        if 'other' in seen:  # người dùng (hoặc tiến trình khác) sửa file sau khi lập kế hoạch: giữ nguyên bytes của họ / someone edited it after planning
            return _result('CONFLICT', ['EXPECTED_BEFORE_MISMATCH'], txid=txid)
        return _result('REFUSED', ['WRITE_REFUSED'], detail=str(exc)[:200], txid=txid)
    return _result('PARTIAL', ['PARTIAL_WRITE'], txid=txid,
                   files=[{'path': r, 'action': {'after': 'written', 'before': 'not_written'}.get(s, 'changed_by_other')} for (r, _, _), s in zip(ops, seen)],
                   next_actions=['python tools/transaction.py status', 'python tools/transaction.py resume %s' % txid,
                                 'python tools/transaction.py rollback %s' % txid])


def _after_run(root, ops, txid, exc):
    """Như _classify, và nêu giao dịch còn mở (đã/chưa ghi gì, resume hoặc rollback) khi có. / Also names an open transaction when there is one."""
    res = _classify(root, ops, txid, exc)
    if res['status'] != 'WRITTEN' and 'next_actions' not in res and pending_transactions(root)[0] != 'NONE':
        res['reasons'] = list(res['reasons']) + ['TRANSACTION_UNFINISHED']
        res['next_actions'] = ['python tools/transaction.py status', 'python tools/transaction.py resume %s' % txid,
                               'python tools/transaction.py rollback %s' % txid]
    return res


def _sha_of(root, rel):
    data, _ = read_plain(_abs(root, rel))
    return sha256(data) if data is not None else None


def _write_group(root, kind, writes, backups=()):
    """writes: [(rel, new_bytes, before_sha)]; backups: [(rel, bytes)] tạo bằng create_exclusive. Một giao dịch nhóm có phục hồi, không nguyên tử.
    One grouped, recoverable transaction; not atomic across files."""
    t = tx.Transaction(root, kind, prune=False)
    ops = []
    try:
        for rel, data in backups:
            t.add(rel, data, 'create_exclusive')
        for rel, data, before in writes:
            if t.add(rel, data, 'write', expected_before=before) is not None:
                ops.append((rel, before, sha256(data)))
    except tx.TransactionError as exc:  # lập kế hoạch chỉ đọc: lỗi ở đây nghĩa là chưa ghi gì / planning only reads
        if any(_sha_of(root, rel) != before for rel, _, before in writes):
            return _result('CONFLICT', ['EXPECTED_BEFORE_MISMATCH'])
        return _result('REFUSED', ['WRITE_REFUSED'], detail=str(exc)[:200])
    _hook('apply', {'root': root, 'kind': kind})
    exc = None
    try:
        t.run()
    except (tx.TransactionError, OSError) as e:  # kết quả quyết định từ chính file, không chỉ từ ngoại lệ
        exc = e
    finally:
        t.close()
    return _after_run(root, ops, t.txid, exc)


# ---------------------------------------------------------------- config lane
def _load_for_edit(root, blocked_code):
    """(rep, doc, cap, refusal). Chỉ cho sửa khi profile hợp lệ, không giao dịch dở, state OK hoặc LEGACY. doc và cap là cùng một lần đọc với rep.
    doc and cap come from the same single read as rep."""
    cap = _capture(root)
    rep, doc = _inspect_capture(root, cap)
    if doc is None or rep['state'] not in ('OK', 'LEGACY'):
        return rep, None, cap, _result('REFUSED', [blocked_code] + [r for r in rep['reasons'] if r != blocked_code], state=rep['state'])
    return rep, doc, cap, None


def _merge_choices(doc, choices):
    out = json.loads(json.dumps(doc))
    for key in CONFIG_KEYS:
        if key not in choices:
            continue
        val = choices[key]
        if key == 'roles':
            if not isinstance(val, dict):
                return None
            for role, choice in val.items():
                out['roles'][role] = choice  # vai lạ bị schema từ chối / an unknown role is refused by the schema
        else:
            out[key] = val
    return out


def _changes(before, after, prefix=''):
    out = []
    if isinstance(before, dict) and isinstance(after, dict):
        for k in sorted(set(before) | set(after)):
            out += _changes(before.get(k), after.get(k), '%s%s.' % (prefix, k))
    elif before != after:
        out.append({'path': prefix.rstrip('.'), 'before': before, 'after': after})
    return out


def plan_config(root, choices):
    """Xem trước sửa lựa chọn (host/roles/fallback/requested_limits). Không nhận grants, owner hay trường khác. / Choices-only edit plan."""
    root = os.path.abspath(root)
    if not isinstance(choices, dict):
        return _result('REFUSED', ['CONFIG_NOT_OBJECT'])
    if not choices:
        return _result('REFUSED', ['CONFIG_EMPTY'])
    if set(choices) - set(CONFIG_KEYS):
        return _result('REFUSED', ['CONFIG_FORBIDDEN_FIELD'], fields=sorted(str(k) for k in set(choices) - set(CONFIG_KEYS))[:6])
    bad = forbidden_findings(choices)
    if bad:
        return _result('REFUSED', bad)
    rep, doc, cap, refusal = _load_for_edit(root, 'CONFIG_BLOCKED_STATE')
    if refusal:
        return refusal
    data, project_before = cap['profile'][0], sha256(cap['project'][0])  # PROJECT.md: điều kiện chỉ đọc, không ghi / read-only precondition
    new = _merge_choices(doc, choices)
    if new is None:
        return _result('REFUSED', ['CONFIG_INVALID'])
    status, reasons, detail = evaluate_doc(new)
    if status != 'OK':
        return _result('REFUSED', ['CONFIG_INVALID'], detail=detail[:6])
    if new == doc:
        return _result('UNCHANGED', ['NOTHING_TO_CHANGE'])
    after = serialize(new)
    core = {'action': 'config', 'profile_before': sha256(data), 'profile_after': sha256(after), 'project_before': project_before}
    return _result('PREVIEW', plan={'action': 'config', 'changes': _changes(doc, new), 'profile_before_sha256': sha256(data),
                                    'profile_after_sha256': sha256(after), 'project_before_sha256': project_before, 'host_application': 'NOT_INSPECTED',
                                    'grants_changed': False, 'plan_sha256': sha256(canonical(core).encode('utf-8'))},
                   _bytes=after, _before=sha256(data), _project_before=project_before)


def apply_config(root, choices, expect_plan=None):
    root = os.path.abspath(root)
    plan = plan_config(root, choices)
    if plan['status'] != 'PREVIEW':
        return plan
    if expect_plan is not None and expect_plan != plan['plan']['plan_sha256']:
        return _result('CONFLICT', ['PLAN_CHANGED'])
    pre = _preflight_write(root, [PROFILE_REL])
    if pre:
        return _result('REFUSED', pre)
    if _sha_of(root, PROJECT_REL) != plan['_project_before']:  # PROJECT.md quyết định owner/state của snapshot này: đã đổi thì không ghi
        return _result('CONFLICT', ['EXPECTED_BEFORE_MISMATCH'])
    res = _write_group(root, 'profile-config', [(PROFILE_REL, plan['_bytes'], plan['_before'])])
    res['plan'] = plan['plan']
    return res


# ---------------------------------------------------------------- migration lane
def _grant_list(grants):
    if isinstance(grants, dict) and isinstance(grants.get('grants'), list) and set(grants) == {'grants'}:
        grants = grants['grants']
    return grants if isinstance(grants, list) else None


def _grant_summary(g):
    scope = g.get('scope') or {}
    return {'grant_id': g.get('grant_id'), 'grant_revision': g.get('grant_revision'), 'subject_roles': (g.get('subject') or {}).get('roles'),
            'operations': scope.get('operations'), 'task_classes': scope.get('task_classes'), 'paths': scope.get('paths'),
            'delegate_callees': [c.get('role_name') for c in scope.get('delegate_callees') or [] if isinstance(c, dict)],
            'limits': g.get('limits') or {}}


def plan_migration(root, grants):
    """Xem trước chuyển quyền PROJECT -> PROFILE. Evidence chỉ là lời khai do người gọi cung cấp; không tạo, không chứng thực.
    Preview of PROJECT -> PROFILE authority migration; evidence is the caller's claim, never created or verified here."""
    root = os.path.abspath(root)
    items = _grant_list(grants)
    if items is None or any(not isinstance(g, dict) for g in items):
        return _result('REFUSED', ['MIGRATION_INPUT_NOT_GRANTS'])
    if not items:
        return _result('REFUSED', ['MIGRATION_NO_GRANTS'])
    cap = _capture(root)
    rep, doc = _inspect_capture(root, cap)
    if doc is None or rep['state'] not in ('OK', 'LEGACY') or rep['owner'] != 'PROJECT' \
            or rep['project_line'] not in ('LEGACY', 'EMPTY', 'PLACEHOLDER'):
        return _result('REFUSED', ['MIGRATION_BLOCKED_STATE'] + [r for r in rep['reasons'] if r != 'MIGRATION_BLOCKED_STATE'], state=rep['state'])
    cv = control_validator()
    if cv is None:
        return _result('REFUSED', ['VALIDATOR_UNAVAILABLE'])
    reasons, where = set(), []
    for i, g in enumerate(items):
        bad = grant_problems(g, i, cv)
        if not bad:
            bad = migration_grant_problems(g)
        if bad:
            reasons.update(bad)
            where.append({'index': i, 'reasons': bad})
    ids = [g.get('grant_id') for g in items]
    if len(set(map(str, ids))) != len(ids):
        reasons.add('GRANT_DUPLICATE_ID')
    if reasons:
        return _result('REFUSED', sorted(reasons), grants=where)
    pdata, proj = cap['profile'][0], cap['project'][0]  # đúng bytes đã kiểm ở trên / the very bytes validated above
    jdoc = json.loads(json.dumps(doc))
    jdoc['authority_owner'] = 'PROFILE'
    jdoc['grants'] = json.loads(json.dumps(items))
    status, rs, detail = evaluate_doc(jdoc)
    if status != 'OK':
        return _result('REFUSED', rs or ['PROFILE_INVALID'], detail=detail[:6])
    text = proj.decode('utf-8')
    kind, value, label = project_line(text)
    new_text = replace_project_line(text, label, pointer_for(label))
    if new_text is None:
        return _result('REFUSED', ['PROJECT_LINE_AMBIGUOUS'])
    after_profile, after_project = serialize(jdoc), new_text.encode('utf-8')
    core = {'action': 'migrate', 'profile_before': sha256(pdata), 'profile_after': sha256(after_profile),
            'project_before': sha256(proj), 'project_after': sha256(after_project)}
    plan = {'action': 'migrate', 'owner_before': 'PROJECT', 'owner_after': 'PROFILE', 'grants': [_grant_summary(g) for g in jdoc['grants']],
            'grants_sha256': sha256(canonical(jdoc['grants']).encode('utf-8')),
            'project_line': {'label': label, 'kind_before': kind, 'before': value, 'after': pointer_for(label)},
            'profile_before_sha256': core['profile_before'], 'profile_after_sha256': core['profile_after'],
            'project_before_sha256': core['project_before'], 'project_after_sha256': core['project_after'],
            'evidence': 'CLAIM_ONLY', 'host_application': 'NOT_INSPECTED', 'plan_sha256': sha256(canonical(core).encode('utf-8'))}
    return _result('PREVIEW', plan=plan, _profile_bytes=after_profile, _project_bytes=after_project,
                   _before=(core['profile_before'], core['project_before']), _backups=(pdata, proj))


def apply_migration(root, grants, expect_plan=None):
    root = os.path.abspath(root)
    if not expect_plan:
        return _result('REFUSED', ['PREVIEW_REQUIRED'])
    plan = plan_migration(root, grants)
    if plan['status'] != 'PREVIEW':
        return plan
    if expect_plan != plan['plan']['plan_sha256']:
        return _result('CONFLICT', ['PLAN_CHANGED'])
    pre = _preflight_write(root, [PROFILE_REL, PROJECT_REL])
    if pre:
        return _result('REFUSED', pre)
    stamp = datetime.date.today().strftime('%Y%m%d')
    backups = [(PROFILE_REL + '.bak-' + stamp, plan['_backups'][0]), (PROJECT_REL + '.bak-' + stamp, plan['_backups'][1])]
    for rel, _ in backups:
        if os.path.lexists(_abs(root, rel)):
            return _result('REFUSED', ['BACKUP_EXISTS'], files=[{'path': rel, 'action': 'exists'}])
    pb, jb = plan['_before']
    res = _write_group(root, 'profile-migration',
                       [(PROFILE_REL, plan['_profile_bytes'], pb), (PROJECT_REL, plan['_project_bytes'], jb)], backups=backups)
    res['plan'] = plan['plan']
    return res


# ---------------------------------------------------------------- CLI
def _public(res):
    return dict((k, v) for k, v in res.items() if not k.startswith('_'))


def _read_input(path):
    data, bad = read_plain(os.path.abspath(path))
    if data is None:
        raise JsonError('input file is missing, not a plain file or too large')
    return parse_json_bytes(data)


def _emit(res, args, lang_message):
    out = _public(res)
    status = res['status']
    mapping = {'PREVIEW': ('preview', 0), 'WRITTEN': ('success', 0), 'UNCHANGED': ('success', 0), 'PARTIAL': ('partial', 1),
               'ERROR': ('error', 1), 'CONFLICT': ('blocked', 1), 'REFUSED': ('blocked', 1), 'UNKNOWN': ('partial', 1)}
    st, code = mapping.get(status, ('error', 1))
    print('%s: %s' % (status, lang_message))
    for r in res['reasons']:
        print('  - %s: %s' % (r, reason_text(r)))
    if res.get('detail') is not None:
        detail = res['detail']
        print('  detail: ' + (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)))
    if res.get('plan'):
        print(json.dumps(res['plan'], ensure_ascii=False, indent=2))
    if res.get('next_actions'):
        for a in res['next_actions']:
            print('  > ' + a)
    if getattr(args, 'result_json', False):
        emit(make(st, code=code, message=status, changes=(status in ('WRITTEN', 'PARTIAL')) or None, files=res.get('files'),
                  next_actions=res.get('next_actions'), outcome=out))
    return code


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    global LANG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd')
    for name in ('status', 'preview-config', 'apply-config', 'preview-migration', 'apply-migration'):
        p = sub.add_parser(name)
        p.add_argument('--project', default=ROOT, help='thư mục project / project folder')
        p.add_argument('--result-json', action='store_true', help=argparse.SUPPRESS)
        if name.endswith('config'):
            p.add_argument('--choices', required=True, help='JSON: chỉ host, roles, fallback, requested_limits')
        if name.endswith('migration'):
            p.add_argument('--grants', required=True, help='JSON: mảng record grant v3 chuẩn kèm khai báo USER_CONFIRMATION')
        if name.startswith('apply'):
            p.add_argument('--expect-plan', default=None, help='plan_sha256 từ lần xem trước')
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_usage(sys.stderr)
        return 2
    root = os.path.abspath(a.project)
    LANG = package_language(root)
    if a.cmd == 'status':
        rep = inspect(root)
        print(format_status(rep))
        steps = steps_for(rep, root)
        for line in steps:
            print('  > ' + line)
        code = 0 if rep['state'] == 'OK' else 1
        if a.result_json:
            emit(make('success' if code == 0 else 'issues', code=code, message=rep['state'], changes=False,
                      findings=[{'severity': 'error' if r != 'LEGACY_MIGRATION_REQUIRED' else 'warning', 'message': '%s: %s' % (r, reason_text(r))} for r in rep['reasons']],
                      next_actions=steps or None, unchecked=rep['unchecked'], outcome=rep))
        return code
    try:
        src = _read_input(a.choices if a.cmd.endswith('config') else a.grants)
    except JsonError as e:
        code = _emit(_result('REFUSED', ['MIGRATION_INPUT_NOT_GRANTS' if a.cmd.endswith('migration') else 'CONFIG_NOT_OBJECT']), a, str(e))
        return code
    expect = getattr(a, 'expect_plan', None)
    if a.cmd.endswith('config'):
        res = plan_config(root, src) if a.cmd == 'preview-config' else apply_config(root, src, expect)
        msg = L('Lựa chọn được yêu cầu (chưa kiểm host nào đã áp dụng hay chưa).', 'Requested choices (whether any host applied them is not inspected).')
    else:
        res = plan_migration(root, src) if a.cmd == 'preview-migration' else apply_migration(root, src, expect)
        msg = L('Migration quyền PROJECT -> PROFILE (evidence chỉ là lời khai).', 'Authority migration PROJECT -> PROFILE (evidence is a claim only).')
    if res['status'] == 'REFUSED' and 'next_actions' not in res and {'CONFIG_BLOCKED_STATE', 'MIGRATION_BLOCKED_STATE'} & set(res['reasons']):
        res['next_actions'] = steps_for(inspect(root), root) or None  # chặn vì trạng thái: nói rõ làm gì tiếp, không tự sửa / blocked by state: say what to do next, change nothing
        if res['next_actions'] is None:
            del res['next_actions']
    return _emit(res, a, msg)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:  # lỗi bất ngờ: báo gọn, không in dữ liệu / unexpected: short, no data
        print('ERROR: %s' % type(e).__name__, file=sys.stderr)
        sys.exit(1)
