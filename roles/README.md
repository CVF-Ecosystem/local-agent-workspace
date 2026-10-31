# Vai trò lõi / Core roles

`scout/`, `worker/`, `reviewer/` là hợp đồng nhiệm vụ do bộ khung duy trì. Đây là
thành phần lõi, không đi qua bước tiếp nhận `REVIEW` của gói lĩnh vực trong `packs/`.
Main agent của ứng dụng người dùng vẫn là đầu mối điều phối và giao kết quả.

Main và mọi vai chịu cùng quy tắc kiểm soát của sản phẩm ở `.cvf/rules/CONTROL_RULES.md`
và bảng routing `.cvf/rules/ROUTING_POLICY.json`; hợp đồng task/review/result ở
`.cvf/contracts/`. Vai không tạo đặc quyền: không vai nào tự cấp hoặc mở rộng grant,
review không cấp quyền, và Main không bỏ verdict chặn hay tự duyệt thay Reviewer bắt
buộc. Grant nhóm còn hiệu lực được dùng lại, không hỏi lại từng task.

Mỗi vai có `agent.md` (nhiệm vụ và giới hạn), `checks.md` (đầu ra cần có) và
`config.json` (preset và trạng thái). Hiện cả ba cấu hình đều ghi `PENDING_R4`:
`host_presets` chỉ có ứng viên `CANDIDATE` cho claude-code (Scout Haiku 5.5, Worker và
Reviewer Sonnet 5.5, effort null, chưa đánh giá chất lượng); ứng viên không tự điền vào
profile, không đăng ký agent và không cấp quyền gọi agent phụ. File trong thư mục này không
tự được ứng dụng native nạp; người dùng chủ động xuất bằng `tools/native_agents.py`.

<!-- law-host-session-guidance -->
## Phiên native và exporter / Native session versus exporter

Giới hạn trong `tools/native_agents.py` chỉ áp dụng các file xuất cho Claude Code. Với Cowork, Codex Desktop, Antigravity hoặc host khác, Main kiểm công cụ thật của đúng phiên/vai và có thể chọn tuyến `host_session` chỉ đọc của `office.py compose`; không suy khả năng từ tên host hoặc phần mềm đã cài. Tuyến chuẩn bị không đăng ký agent, không cấp grant và không bỏ quyền do profile giữ. Khi owner là PROFILE, vẫn cần grant hợp lệ theo yêu cầu người dùng; ghi quyền vào tài liệu chat/project không tự sửa profile. Không đặt host `claude-code` chỉ để vượt điều kiện exporter khi đang dùng host khác.

Tách model/effort yêu cầu (có thể là alias) khỏi model/effort thực tế; không suy actual từ alias hay agent tự khai. Tách công cụ của Main khỏi công cụ của subagent; evidence bằng hash chỉ bind bytes lời khai, không xác thực capability. Tách file trong container/VM, tài liệu project của ứng dụng và file Windows/project. Main phải kiểm đường bàn giao, mở đúng artifact và đối chiếu bytes/digest trước tích hợp; ghi rõ phần chưa quan sát. Không tự cài dependency, mở quyền hoặc đổi native để vượt thiếu khả năng. Lệnh `status`/`preview` không thay cho phép thử host thật.

EN: `native_agents.py` limits only its Claude Code exports. Inspect the actual session/role tools on Cowork, Codex Desktop, Antigravity or another host; the optional read-only `host_session` compose route neither registers an agent nor grants authority or bypasses the profile owner. Keep requested aliases/effort separate from observed model/effort, Main tools separate from subagent tools, and container/VM or app-project documents separate from Windows project files. A bound note proves bytes only. Verify delivery and exact artifact bytes before integration; report what was not observed. Do not install dependencies or widen permissions to fill gaps.

## Preset thử thi công — mốc kiểm 17/10/2026

`implementation_trial` trong ba config là cấu hình thử cho agent **xây dựng LAW**,
revision 2, `quality_status: NOT_EVALUATED_ON_LAW`. Các model/effort này chưa được
đánh giá chất lượng thi công trên LAW. Nguồn đã kiểm, phân công theo tranche và
quy tắc cập nhật nằm ở mục 8.4 của roadmap/ROADMAP_HOAN_THIEN.md trong kho nguồn.

| Vai | GPT mặc định | Claude mặc định |
|---|---|---|
| Scout | Luna High | Haiku 5.5 Medium; High khi truy nhiều quan hệ |
| Worker | Sol 6.1 Medium; High theo tranche rủi ro | Sonnet 5.5 High |
| Reviewer | Sol 6.1 High; Medium cho tranche nhẹ | Opus 5.5 High; Medium cho tranche nhẹ |

Luna Extra High và ứng viên Haiku 5.5 High chỉ làm Worker cho phần việc hẹp, có
acceptance rõ và dễ kiểm. Sonnet Extra High là ứng viên khi có vấn đề cần suy luận
sâu hơn; Max dành cho một vấn đề còn vướng sau đó. Ghi lý do/phạm vi trong HANDOFF
trước khi đổi cấu hình; không tự nâng effort hay dùng ứng viên như preset nền.
Extra High được ghi `xhigh` trong config. Mỗi mức còn phụ thuộc phiên/host hỗ trợ.

Khi thử, ghi cấu hình yêu cầu và thực tế quan sát được, kết quả kiểm, lỗi review,
vòng sửa và can thiệp operator trong HANDOFF. Agent có thể cập nhật khi có nguồn
hoặc kết quả thử mới: ghi ngày kiểm, tăng revision, đồng bộ cả ba config và roadmap;
giữ mốc ban đầu `original_baseline_on: 2026-10-17` và lịch sử các lượt đã làm.
Metadata thử không tạo profile sản phẩm, đăng ký native hoặc quyền dispatch.

## Tích hợp sản phẩm R4

R4 sẽ chốt preset theo tài liệu và pilot trên từng host, đặt lựa chọn hiệu lực
của người dùng ở `.agent/EXECUTION_PROFILE.json`, rồi xuất projection sau khi
đã kiểm xung đột với file native. Thay hợp đồng nhiệm vụ cần review/version;
thay model/effort của project không sửa `agent.md`.

Profile (A-09) mới chỉ giữ lựa chọn **được yêu cầu** và chủ sở hữu quyền: chưa có adapter
nên không có vai nào được báo là đã đăng ký hoặc đã áp dụng. `python tools/execution_profile.py status`
cho xem; `preview-config`/`apply-config` chỉ sửa host, model hoặc tier, effort, fallback và giới hạn
được yêu cầu; `preview-migration`/`apply-migration` mới chuyển quyền từ dòng PROJECT.md sang grant v3
trong profile, và chỉ khi có khai báo của người dùng (USER_CONFIRMATION kèm bằng chứng) do người gọi
cung cấp. Khai báo đó là lời khai hợp tác, công cụ không chứng thực.

Các vai lĩnh vực đến từ gói đã được tiếp nhận, dùng cùng hợp đồng giao việc và
giới hạn nguồn/quyền của project. Không tự biến file nguồn hoặc skill cá nhân
thành vai có quyền cao hơn.

The profile (A-09) holds only **requested** choices and the authority owner: the helper does not inspect any host, so registration and
application are reported as NOT_INSPECTED (neither denied nor claimed). Use `python tools/execution_profile.py status`; `preview-config` and
`apply-config` edit only the requested host, model or tier, effort, fallback and limits; `preview-migration`
and `apply-migration` move authority from the PROJECT.md line into v3 grants in the profile, only with a
user-confirmation declaration (with evidence) supplied by the caller. That declaration is a cooperative
claim the tool does not verify.

A-10 (Claude Code only, three fixed core roles): `python tools/native_agents.py status|preview|apply [--role scout|worker|reviewer]`
writes one managed native file per role (`<project>/.claude/agents/law-<role>.md`) plus a receipt, from the project's own role
contract and the profile's explicit full model ID. Scout and Reviewer get Read, Grep, Glob; the Worker also gets Write to create
ONE new CANDIDATE artifact, but Write has no path limit and does not prevent overwriting, so "new files only" is a cooperative
duty, not enforcement. The product Reviewer is read-only; the maintainer Reviewer's small-fix permission stays in AGENTS, PROJECT
and the roadmap, not in the native files. `host_presets` are CANDIDATE suggestions only and are never written into the profile.
`preview-retire` / `retire --expect-plan` moves a managed native with one no-replace rename (Windows) out of the host's auto-scan
folder into `<project>/.agent/runtime/native-agents/claude-code/law-<role>.retired.md`; nothing is deleted or reactivated, and
restoring is a manual user act. Everything is disk configuration only: whether the host loads or invokes a role, the model
actually used, any path restriction and whether a running session stopped are NOT_INSPECTED; the receipt is provenance, never
authority. Effort, tier and hard limits are UNSUPPORTED, and the rest of R4 is still pending.

## TASK, RESULT và checkpoint trước tích hợp (A-11)

Dành cho Main khi một việc nhiều bước cần giao cho Scout hoặc Worker rồi nhận kết quả về. Đây là giao thức **hợp tác**
(COOPERATIVE/ADVISORY): không có host hay công cụ nào cưỡng chế nó, và nó không thay việc người dùng duyệt nội dung.

**Việc nhỏ không cần TASK/RESULT.** Sửa một câu, một số liệu, một đoạn, đổi tên, hoặc việc Main làm trọn trong một lượt: làm trực tiếp,
không tạo hồ sơ, không gọi vai. Chỉ dùng TASK/RESULT khi có bàn giao thật sự cho vai khác và kết quả quay lại sau.

### Hồ sơ và bố cục

- Dùng nguyên record `law.cvf.control/3` loại `task` và `result` (schema `.cvf/contracts/v3/control.schema.json`); không có schema, bộ đếm
  hay máy trạng thái riêng. Người dùng không phải viết JSON: Main chuyển yêu cầu tự nhiên thành record, ghi lại căn cứ của người dùng
  và grant, chỗ thiếu thì ghi "cần xác nhận". Record không phải grant và không phải lời yêu cầu của người dùng.
- Mỗi task có **một TASK hiện hành** do Main quản lý; mỗi lần giao việc (assignment) có **slot riêng**, và vai nhận chỉ ghi trong slot đó:

```text
working/<work-id>/<task-id>/TASK.json                              TASK hiện hành, chỉ Main ghi
working/<work-id>/<task-id>/assignments/<assignment-id>/RESULT.json         vai nhận ghi, chỉ CANDIDATE
working/<work-id>/<task-id>/assignments/<assignment-id>/candidate/<file>    candidate mới
```

- Action ghi của TASK chỉ nhắm file trong slot của lần giao hiện tại, không nhắm Index, STATE, HANDOFF, `references/` hay output chung.
  Worker/Scout không sửa TASK hiện hành, Index, STATE/HANDOFF hay output chung; thiếu hoặc mâu thuẫn brief thì trả lại Main, không tự điền quyền.
- RESULT chỉ là `CANDIDATE`. Nó giữ nguyên task, revision, input và output lúc làm; **không sửa binding hay locator của RESULT cũ để ghép sang
  task mới**. Khi giao việc, Main tính sẵn khối `binding` (hàm `binding_stub` bên dưới) để vai nhận chép nguyên văn rồi thêm `outputs`;
  vai nhận không tự tính digest của task.
- Yêu cầu hoặc input liên quan đổi: Main sửa TASK và **tăng `task_revision`** trước khi nhận bất kỳ kết quả nào. Ảnh hưởng nhiều task thì
  cập nhật mọi TASK liên quan (cách bảo thủ được phép: coi cả nhóm là cần giao lại; chưa có lineage, việc đó thuộc B-01/B-02).
  RESULT cũ không còn khớp thì không tích hợp, giao lại slot mới.

### Checkpoint trước khi tích hợp

Trước mỗi lần nhận hoặc ghi, Main chạy checkpoint trên **TASK hiện hành** (đọc từ đường dẫn Main quản lý, không dùng bản TASK đi kèm RESULT) và RESULT:

1. Đọc TASK và RESULT bằng loader/schema v3, so quan hệ binding bằng `binding.compare_binding`. Mọi quan hệ liên quan phải `MATCH`; thiếu,
   mơ hồ hay không hỗ trợ thì dừng phần phụ thuộc. Kết quả này chỉ nói các digest khai báo khớp task: **không là PASS, quyền hay nghiệm thu**.
2. So **bytes hiện tại** của input, `context_refs` và candidate với digest đã bound. Lời khai hash hay hai bản khai khớp nhau không phải là đã đọc file.
   Đường dẫn phải qua `publish_new.path_form_problem` (tương đối project, không `..` hay alias không hỗ trợ) trước khi đọc.
   File thiếu, không đọc được hoặc nằm sau symlink/junction là dừng, không phải "không đổi" (`transaction.link_free`, kiểm tại lúc đọc, không phải mở nguyên tử không theo liên kết).
3. Input hoặc `context_refs` có `source_id`/`revision`: đọc sổ bằng `library.read_book`, tìm đúng **một** dòng bằng `library.record`/`library.id_counts`, so ID, locator và
   revision (số nguyên trong sổ, chuỗi trong record). Thiếu, trùng ID hay sổ lỗi thì dừng. Nguồn chưa có ID thì khai chưa đăng ký, không tự tạo ID.
   `sha12` của sổ không phải SHA đầy đủ và sổ có thể chưa sync, nên bytes nguồn vẫn phải tự hash (bước 2). Không dựng "lựa chọn giao diện" giả để gọi `library.rebind`.
4. Candidate được đọc **một lần**, so SHA đầy đủ với `RESULT.artifacts`; chính bytes đã so là bytes đưa vào writer. Không đọc lại candidate lần nữa để ghi.

```python
# law-recipe: task-result-checkpoint
import hashlib, importlib, importlib.util, json, os, posixpath, sys
from pathlib import Path


# Core checks live in product code; loading remains explicit from the trusted LAW tree.
_checkpoint = None


def load_v3(law):
    global _checkpoint
    law = Path(law).resolve()
    tools_dir = str(law / 'tools')
    sys.path[:] = [tools_dir] + [p for p in sys.path if p != tools_dir]
    owner = importlib.import_module('task_checkpoint')
    if Path(owner.__file__).resolve() != law / 'tools' / 'task_checkpoint.py':
        raise RuntimeError('checkpoint owner must come from the fixed LAW tree')
    _checkpoint = owner
    return owner.load_v3(law)


def sha(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def read_file(project, rel):
    return _checkpoint.read_file(project, rel)


def binding_stub(v3, task):
    return _checkpoint.binding_stub(v3, task)


def read_record(v3, project, rel, want):
    return _checkpoint.read_record(v3, project, rel, want)


def checkpoint(v3, project, task_rel, result_rel, staged=None):
    return _checkpoint.checkpoint(v3, project, task_rel, result_rel, staged)


def observe_candidate(v3, project, task_rel, candidate_rel, result_rel, task_raw_digest):
    """Main quan sát digest của ĐÚNG candidate bằng `artifacts.observe_file` (chỉ đọc) để Worker ghi `outputs`/`artifacts` của RESULT; Worker không tự băm.
    `task_raw_digest` là digest thô của TASK Main đã giữ từ lúc chốt giao (không lấy digest vừa đọc thay cho nó). Chỉ cho TASK Worker có marker VÀ context office.
    `observed` True chỉ khi mọi điều kiện đạt; quan sát này là digest bytes của một file, không là PASS, quyền, nguồn mới hay snapshot nguyên tử, và không ghi gì, không tạo RESULT hay binding."""
    out = {'observed': False, 'problems': [], 'observation': None}
    problems = out['problems']
    if not all(k in v3 for k in ('loader', 'owners', 'office')):
        problems.append('OWNER_UNAVAILABLE')  # không có owner thì từ chối, không tự phân tích record
        return out
    if not (isinstance(task_raw_digest, str) and task_raw_digest.startswith('sha256:')):
        problems.append('TASK_RAW_DIGEST_REQUIRED')
        return out
    try:
        import publish_new, transaction
    except ImportError:
        problems.append('OWNER_UNAVAILABLE')
        return out
    if (publish_new.path_form_problem(task_rel) or not isinstance(task_rel, str)
            or len(task_rel.split('/')) != 4 or task_rel.split('/')[0] != 'working' or task_rel.split('/')[-1] != 'TASK.json'):
        problems.append('TASK_PATH_NOT_CURRENT')
        return out
    task, raw, why = read_record(v3, project, task_rel, 'task')
    if why:
        problems.append(why)
        return out
    if task_rel != 'working/%s/%s/TASK.json' % (task['work_id'], task['task_id']):
        problems.append('TASK_PATH_NOT_CURRENT')
        return out
    if raw != task_raw_digest:
        problems.append('TASK_CHANGED_SINCE_DISPATCH')
        return out
    office = v3['office']
    if {task['authority']['subject'].get('role'), task['envelope'].get('role')} != {'worker'}:
        problems.append('TASK_NOT_WORKER')
    has_marker = any(str(r.get('req_id', '')).casefold().startswith('office-method') for r in task['acceptance']['requirements'])
    has_context = any(str(o.get('path', '')).casefold().startswith(office.OFFICE_DIR + '/') for o in task.get('context_refs', []))
    if not (has_marker and has_context):
        problems.append('OFFICE_MARKER_AND_CONTEXT_REQUIRED')  # TASK legacy: guard_task rỗng không đủ cho đường này
    else:
        problems.extend(office.guard_task(task, lambda rel: read_file(project, rel)))
    slot = posixpath.dirname(result_rel) if isinstance(result_rel, str) else ''
    if any(publish_new.path_form_problem(p) for p in (candidate_rel, result_rel)):
        problems.append('PATH_UNSUPPORTED_FORM')
        return out
    elif (posixpath.basename(result_rel) != 'RESULT.json' or posixpath.dirname(slot) != 'working/%s/%s/assignments' % (task['work_id'], task['task_id'])
          or posixpath.dirname(candidate_rel) != slot + '/candidate'):
        problems.append('SLOT_LAYOUT')  # RESULT.json và candidate/<file> cùng một slot của đúng work/task
    actions = task['effects']['actions']
    targets = [t for a in actions for t in a.get('targets', [])]
    if (any(a.get('operation') != 'create_new' or a.get('tool') != 'Write' or a.get('write_zone') != 'working' for a in actions)
            or len(targets) != 2 or set(targets) != {candidate_rel, result_rel}):
        problems.append('TARGETS_NOT_CANDIDATE_AND_RESULT')
    if not problems:
        result_path = os.path.join(project, *result_rel.split('/'))
        if not transaction.link_free(result_path, project):
            problems.append('RESULT_PATH_LINK')
        elif os.path.lexists(result_path):
            problems.append('RESULT_ALREADY_EXISTS')
    if problems:
        return out
    try:
        tools_dir = Path(office.__file__).resolve().parent
        for name in ('artifacts', 'library_sync'):
            cached = sys.modules.get(name)
            origin = getattr(cached, '__file__', None) if cached is not None else getattr(importlib.util.find_spec(name), 'origin', None)
            if not origin or Path(origin).resolve().parent != tools_dir:
                problems.append('OWNER_NOT_FIXED_TREE')
                return out
        artifacts = importlib.import_module('artifacts')
        if Path(artifacts.__file__).resolve().parent != tools_dir:
            problems.append('OWNER_NOT_FIXED_TREE')
            return out
        seen, why = artifacts.observe_file(project, candidate_rel)
    except Exception as exc:  # owner không nạp được hoặc từ chối: giữ chờ, không có digest giả
        problems.append('OBSERVER_ERROR %s' % type(exc).__name__)
        return out
    if seen is None:
        problems.append('CANDIDATE_%s' % str(why).upper())
        return out
    out['observed'] = True
    out['observation'] = {'task': {'path': task_rel, 'task_id': task['task_id'], 'task_revision': task['task_revision'], 'raw_digest': raw},
                          'candidate': {'path': candidate_rel, 'digest': 'sha256:' + seen['sha256'], 'size': seen['size'], 'identity': seen['identity']},
                          'result_path': result_rel, 'observed_by': 'artifacts.observe_file',
                          'limits': ['BYTES_DIGEST_ONLY', 'NOT_PASS_NOT_GRANT_NOT_CONTENT_CHECK', 'NOT_ATOMIC_SNAPSHOT']}
    return out


def publish_inputs(cp, task_rel, result_rel):
    """`inputs` của request P-CN1: bytes THÔ của TASK, RESULT, candidate đã checkpoint, nguồn/context thực dùng, và sổ nếu dùng metadata."""
    art = cp['result']['artifacts'][0]
    items = [{'path': task_rel, 'digest': cp['raw']['task']}, {'path': result_rel, 'digest': cp['raw']['result']},
             {'path': art['path'], 'digest': art['digest']}]
    items += [dict(o) for o in cp['task']['inputs'] + cp['task'].get('context_refs', [])]
    if cp['ledger_snapshot']:
        items.append({'path': 'references/_INDEX.xlsx', 'digest': 'sha256:' + cp['ledger_snapshot']})
    return items


def record_before_effect(project, which, new_bytes, expected_before):
    """Ghi lần giao -> task/revision/slot -> invocation (nếu có) -> writer, request ID, đích dự định vào STATE hoặc HANDOFF TRƯỚC khi gọi writer (P-CTX1).
    (True, kết quả) chỉ khi owner báo WRITTEN sạch. Lệch bytes, giao dịch dở hay UNKNOWN là (False, kết quả): chưa được bắt đầu tác động và phải báo lỗi."""
    import context_update  # tools/ của cây LAW cố định, đã kiểm bởi load_v3
    res = context_update.update(project, which, new_bytes, expected_before=expected_before)
    return res.get('result') == 'WRITTEN' and not res.get('reason'), res


def void_assignment(v3, project, task_rel, new_task, old_result_rel=None):
    """Vô hiệu hóa lần giao cũ: ghi `new_task` (cùng work/task, `task_revision` cao hơn) lên TASK hiện hành rồi ĐỌC LẠI bằng owner.
    `voided` chỉ True khi đọc lại thấy revision mới, binding cấp lúc giao cũ không còn bằng binding của TASK hiện hành và RESULT cũ (nếu đã có)
    không còn qua checkpoint. RESULT/candidate cũ không bị đụng tới. Không nói gì về host (`host_stop` luôn UNCONFIRMED) hay về tác động đã xảy ra."""
    out = {'voided': False, 'problems': [], 'host_stop': 'UNCONFIRMED'}
    old, _, why = read_record(v3, project, task_rel, 'task')
    if why:
        out['problems'].append(why)
        return out
    try:
        payload = json.dumps(new_task, ensure_ascii=False, indent=2).encode('utf-8')
        checked, _ = v3['loader'].inspect_structure(payload, v3['owners'])
    except (TypeError, ValueError, UnicodeError):
        checked = None
    if checked is None or checked.get('record_type') != 'task':
        out['problems'].append('NEW_TASK_REJECTED')
        return out  # không thay TASK hợp lệ bằng record chưa qua owner
    new_task = checked
    same = (new_task.get('work_id'), new_task.get('task_id')) == (old['work_id'], old['task_id'])
    if not same or type(new_task.get('task_revision')) is not int or new_task['task_revision'] <= old['task_revision']:
        out['problems'].append('REVISION_NOT_RAISED')
        return out
    path = os.path.join(project, *task_rel.split('/'))
    tmp, made = path + '.new', False
    try:
        with open(tmp, 'xb') as fh:
            made = True
            fh.write(payload)
        os.replace(tmp, path)
    except OSError:
        if made and os.path.exists(tmp):
            os.remove(tmp)
        out['problems'].append('TASK_WRITE_FAILED')  # chưa xác nhận vô hiệu hóa: giữ chờ mọi tích hợp liên quan
        return out
    now, raw_digest, why = read_record(v3, project, task_rel, 'task')
    if why or raw_digest != sha(payload):
        out['problems'].append('TASK_READBACK_MISMATCH %s' % (why or now['task_revision']))
        return out
    if binding_stub(v3, old) == binding_stub(v3, now):
        out['problems'].append('BINDING_NOT_CHANGED')
        return out
    if old_result_rel and read_file(project, old_result_rel)[0] is not None:
        if not checkpoint(v3, project, task_rel, old_result_rel)['problems']:
            out['problems'].append('OLD_RESULT_STILL_MATCHES')
            return out
    out['voided'] = True
    return out


def reconcile_publish(project, rid, target):
    """Đọc lại tác động P-CN1 của ĐÚNG request ID bằng `status`/`observe` (chỉ đọc). Không gọi `publish`; không gọi `recover` (ghi evidence, dọn staged:
    Main gọi riêng, trong quyền của tác động đó, và khai là phép ghi). decision: WRITTEN | NEEDS_RECOVER | NOT_PUBLISHED | HOLD.
    Evidence thiếu, mâu thuẫn hay UNKNOWN luôn là HOLD, không bao giờ là "chưa ghi"; không sinh ID mới."""
    import publish_new
    out = {'decision': 'HOLD', 'reasons': [], 'terminal': None}
    st = publish_new.status(project, rid)
    if st.get('outcome') != 'STATUS' or not st.get('items'):
        out['reasons'].append('STATUS_%s' % st.get('reason'))
        return out
    item = st['items'][0]
    out['terminal'] = item['terminal']
    seen = publish_new.observe(project, target=target, request_id=rid)
    tgt = seen.get('target') or {}
    if not item['files']:
        out['reasons'] += ['EVIDENCE_MISSING'] + (['TARGET_EXISTS_WITHOUT_EVIDENCE'] if tgt.get('exists') else [])
    elif not item['consistent']:
        out['reasons'] += item['problems'] or ['EVIDENCE_INCONSISTENT']
    elif seen.get('outcome') != 'OBSERVED':
        out['reasons'].append('OBSERVE_%s' % seen.get('reason'))
    else:
        raw, why = read_file(project, '.agent/runtime/publish/%s.prepared.json' % rid)
        prepared = publish_new.validate_evidence(raw, rid, 'prepared') if raw is not None else None
        if prepared is None:
            out['reasons'].append('PREPARED_UNREADABLE')
        elif prepared['task']['effects']['actions'][0]['targets'] != [target]:
            out['reasons'].append('REQUEST_TARGET_MISMATCH')
    if out['reasons']:
        return out
    if item['terminal'] == 'published':
        raw, why = read_file(project, '.agent/runtime/publish/%s.published.json' % rid)
        published = publish_new.validate_evidence(raw, rid, 'published') if raw is not None else None
        if published is None:
            out['reasons'].append('PUBLISHED_UNREADABLE')
        elif tgt.get('identity') != published['identity']:
            out['reasons'].append('TARGET_IDENTITY_CHANGED')
        elif tgt.get('matches_published') is True:
            out['decision'] = 'WRITTEN'
            out['reasons'] += ['CLEANUP_PENDING'] if item['cleanup_pending'] else []
        else:
            out['reasons'].append('TARGET_NOT_MATCHING_PUBLISHED')
    elif item['terminal'] in ('conflict', 'abandoned'):
        out.update(decision='NOT_PUBLISHED', reasons=[item['terminal'].upper()])
    elif item['terminal'] == 'unknown':
        out['reasons'].append('EVIDENCE_UNKNOWN')
    else:
        out.update(decision='NEEDS_RECOVER', reasons=['NO_TERMINAL'] + (['TARGET_EXISTS'] if tgt.get('exists') else []))
    return out


def next_step(f):
    """Giao lại hay chờ, từ các dữ kiện Main đã ghi (voided từ void_assignment, effect từ reconcile_publish hoặc NONE_ATTEMPTED, invocation ENDED|RUNNING|UNKNOWN,
    parallel_safe, grant_ok, capability, retry_left, cost_ok, main_may_draft, no_call_observed). Đây là lời khai hợp tác, không phải bằng chứng host. Trả {'step', 'reasons'}:
    WAIT | NO_SECOND_WRITE | REASSIGN | MAIN_DRAFT. Không tự cấp thêm retry, chi phí, model, provider, tool hay quyền; không đổi profile."""
    out = {'step': 'WAIT', 'reasons': []}
    if not f.get('voided'):
        out['reasons'].append('ASSIGNMENT_NOT_VOIDED')
    elif f.get('effect') == 'WRITTEN':
        out.update(step='NO_SECOND_WRITE', reasons=['EFFECT_ALREADY_WRITTEN'])  # nhận diện kết quả đã ghi, không ghi lần hai
    elif f.get('effect') not in ('NONE_ATTEMPTED', 'NOT_PUBLISHED'):
        out['reasons'].append('EFFECT_%s' % f.get('effect'))
    elif f.get('effect') == 'NONE_ATTEMPTED' and f.get('no_call_observed') is not True:
        out['reasons'].append('NO_CALL_NOT_OBSERVED')  # note lịch sử không chứng minh chưa vượt ranh giới gọi
    elif f.get('invocation') != 'ENDED' and not f.get('parallel_safe'):
        out['reasons'].append('INVOCATION_%s' % f.get('invocation'))
    elif not f.get('grant_ok'):
        out['reasons'].append('GRANT_NOT_COVERING')
    else:
        if f.get('capability') != 'AVAILABLE':
            out['reasons'].append('CAPABILITY_%s' % f.get('capability'))
        if type(f.get('retry_left')) is not int or f['retry_left'] < 1 or not f.get('cost_ok'):
            out['reasons'].append('NO_RETRY_OR_COST_BUDGET')  # không có giới hạn thì không tự cấp retry
        out['step'] = 'REASSIGN' if not out['reasons'] else ('MAIN_DRAFT' if f.get('main_may_draft') else 'WAIT')
    return out


def integration_gate(cp, main_review, review='NOT_REQUIRED'):
    """Quyết định tích hợp của Main SAU checkpoint. `main_review` là phán đoán nội dung của Main {req_id: MET|UNMET|UNKNOWN|BLOCKED} (không có công cụ nào
    kiểm ngữ nghĩa); `review` là NOT_REQUIRED|PASSED|MISSING; PASSED đòi review độc lập đúng binding, không có veto, không chỉ đã xong. Binding và file khớp chưa đủ. Chỉ trả quyết định
    của Main: RESULT của Worker vẫn CANDIDATE và không có USER_ACCEPTED ở đây (nhận bản là việc của người dùng, ghi qua user_acceptance v3)."""
    reasons = list(cp['problems'])
    if not reasons:
        reasons += ['REQUIREMENT %s %s' % (r['req_id'], main_review.get(r['req_id'], 'UNKNOWN')) for r in cp['task']['acceptance']['requirements']
                    if r.get('mandatory') and main_review.get(r['req_id']) != 'MET']
    if review == 'MISSING':
        reasons.append('REVIEW_REQUIRED_BUT_MISSING')  # giữ nháp, chờ review; không tự review hay hạ route
    elif review not in ('NOT_REQUIRED', 'PASSED'):
        reasons.append('REVIEW_NOT_PASSED')  # failed/blocked/unknown/DONE không phải review đạt
    return {'state': 'HOLD' if reasons else 'ACCEPTED_FOR_INTEGRATION', 'reasons': reasons}
```

Cách dùng: `v3 = load_v3(<thư mục gốc LAW>)`, `cp = checkpoint(v3, <project>, task_rel, result_rel)`; chỉ khi `cp['problems']` rỗng mới lập request.
Kết quả khớp chỉ là quan sát hợp tác, không phải PASS, quyền hay nghiệm thu. Phần đọc/checkpoint dùng owner `tools/task_checkpoint.py`, không thực thi Markdown khi ứng dụng xem việc. Khối mã này là ví dụ Worker tạo đúng một candidate trong slot; chưa nhận luồng Scout trả delta/read-only như một checkpoint thực thi chung.
Năm hàm cuối khối (`record_before_effect`, `void_assignment`, `reconcile_publish`, `next_step`, `integration_gate`) phục vụ mục B-03 bên dưới.
Scout trả delta kèm snapshot để Main kiểm trước khi lập preview sổ hiện hành. Trong project thật, cây LAW và project là cùng một thư mục. Chuỗi này dùng helper nội bộ của checker v3 (trạng thái candidate, không có API công khai khác
ngoài `check_bytes`), nên coi nó là hướng dẫn trình tự, không phải API ổn định.

### Hai pha: Main quan sát digest, Worker ghi RESULT (V2-B)

Worker native chỉ có Read, Grep, Glob, Write và không có công cụ băm; tranche này không thêm Bash hay compute cho Worker. Đường hỗ trợ: Worker ghi candidate, **Main dùng công cụ thật quan sát digest**
(`observe_candidate` trong khối mã trên, gọi `artifacts.observe_file` của cây LAW cố định), rồi **Worker tự ghi RESULT** từ quan sát đó. Main không viết RESULT dưới tên Worker và Worker không khai đã tự băm.

1. **Main chốt gói giao.** TASK Worker có marker và context office, mọi action là `create_new`/`Write`/`working`, targets chỉ gồm `candidate/<file>` và `RESULT.json` trong slot mới của lần giao;
   `expected_outputs` chỉ là candidate (RESULT là metadata, không là artifact của chính nó). Main giữ digest thô của TASK, tính `binding_stub` từ chính TASK đó, kiểm grant/host riêng,
   rồi giao brief, TASK path/revision, binding, candidate path và RESULT path. Thiếu đường gọi helper ở phiên của Main thì giữ chờ.
2. **Worker pha 1** ghi đúng một candidate và báo cần Main quan sát digest; chưa ghi RESULT.
3. **Main quan sát:** `observe_candidate(v3, project, task_rel, candidate_rel, result_rel, task_raw_digest)`. Từ chối (không digest, không ghi) khi thiếu hoặc đổi digest TASK, TASK không phải Worker
   office, đích khác hai path của slot, action khác, RESULT đã tồn tại, path/link/hardlink/file không thường hoặc observer lỗi. Kết quả `observation` gồm TASK path/id/revision/digest thô,
   candidate path/`sha256:`/size/identity và `observed_by`. Main chuyển nguyên văn nó cho Worker qua kênh tiếp việc thật; không đưa vào `inputs`/`context_refs` của TASK (làm binding đổi) và không bắt thêm sidecar.
4. **Worker pha 2** ghi `RESULT.json`: `binding` giao nguyên văn cộng `outputs` = `[{path, digest, role: ACTUAL_BYTES}]`, `artifacts` là cùng object đó, `evidence` ghi `kind: TOOL_OBSERVED` với `scope`
   nêu digest do Main quan sát bằng `artifacts.observe_file` và Worker không tự băm, `requirements` giữ `UNKNOWN`, `acceptance_states: [CANDIDATE]`, `produced_by`/`state_set_by` là Worker.
5. **Main nhận** bằng `checkpoint` như trên. Candidate đổi sau quan sát bị chặn (`CANDIDATE_CHANGED`); không sửa digest RESULT để ghép. TASK/nguồn/scope đổi thì tăng revision và slot mới, giữ candidate/RESULT cũ.

Quan sát chỉ là digest bytes của một file: không là PASS, quyền, nguồn mới, nội dung đúng hay snapshot nguyên tử, và chưa chứng minh host hay actor được xác thực. Hai pha là trình tự logic: host phải thật sự
tiếp việc đúng child, hoặc có mapping hai invocation vào cùng một lần giao trong quyền đã cấp. Gợi ý SendMessage trong trace cũ chưa là bằng chứng tool khả dụng hay tiếp việc thành công; không suy
`Agent.resume` hay `--resume` của CLI cha là tiếp việc child. Chỉ có hai instance thì khai đúng hai invocation. Chưa đủ điều kiện thì giữ chờ, không bịa identity hay provenance.

### Ghi kết quả: một writer, kiểm ngay trước mỗi lần gọi

Scout chỉ trả delta kèm snapshot; Main kiểm rồi mới ghi, mỗi lần qua đúng một writer hiện có. **Ngay trước mỗi lần gọi writer**, Main chạy lại checkpoint
(task, nguồn) và kiểm grant còn hiệu lực cho nhóm việc đó. Writer này không giữ hộ điều kiện của writer kia, và không writer nào kiểm review, yêu cầu, nội dung hay
nghiệm thu của người dùng; các việc đó vẫn kiểm riêng, không dựa vào nhãn vai.

| Ghi gì | Writer | Bảo vệ thực sự có |
|---|---|---|
| File mới (bản tích hợp) | `publish_new.publish(project, request, staged, request_id=rid)` (P-CN1) | Không ghi đè; input phải đúng digest ngay lúc publish; đích đã có thì `CONFLICT` |
| STATE hoặc HANDOFF | `context_update.preview/update(project, 'state'\|'handoff', bytes, expected_before=...)` (P-CTX1) | Chỉ bảo vệ bytes đích (`expected_before`); không phải CAS của TASK hay nguồn |
| Sổ nguồn (`_INDEX.xlsx`) | `library_sync.plan(root)` rồi `library_sync.apply(root, expected_preview=library_sync.preview_binding(plan))` | Plan tính lại dưới khóa phải khớp bản đã xem; lệch thì `PreviewMismatch`, không ghi |

**Publish là một task P-CN1 riêng.** Người gọi chọn `rid` trước (32 ký tự hex), giữ `pcn1-<rid>`/revision 1 và cùng task đó qua dispatch, effect, publish và accept như tài liệu
`publish_new.py`. Gắn với task điều phối bằng cùng `work_id` **và** `request.inputs = publish_inputs(...)`: digest bytes thô của TASK hiện hành, RESULT, candidate, nguồn/context thực dùng
(và snapshot sổ nếu dùng metadata; sổ đổi ở bất kỳ dòng nào thì request đã bind snapshot cũ không dùng lại được, checkpoint lại từ đầu, không có projection theo dòng hay registry). `work_id` riêng lẻ không đủ. Lập request ngay từ checkpoint vừa đạt; **không đổi hash trong request để hợp thức hóa một RESULT đã cũ**.
`staged` là chính `cp['candidate']`: P-CN1 nhận bytes staged tự do và `input` của candidate không chứng minh staged trùng candidate, nên quan hệ đó chỉ do `checkpoint(..., staged=...)` bảo đảm.
RESULT của Worker vẫn trỏ candidate gốc; kết quả publish là một record riêng trỏ artifact đích và biên nhận do công cụ ghi. Đích chọn vào output chung không nhận ngầm là người dùng đã duyệt.

Nếu TASK, RESULT, candidate hoặc nguồn đổi sau checkpoint thì `publish` từ chối (`INPUT_CHANGED_SINCE_READ`) trước khi ghi gì; nếu yêu cầu đổi thì TASK tăng revision và checkpoint cũ không còn dùng được.

### Dừng, timeout, kết quả muộn và mở lại phiên (B-03)

Vẫn là giao thức hợp tác ở trên, dùng lại TASK/RESULT, checkpoint và các writer; không thêm trạng thái, bộ đếm hay kho vòng đời. Các hàm
`record_before_effect`, `void_assignment`, `reconcile_publish`, `next_step`, `integration_gate` cuối khối mã chỉ là trình tự chạy được trên dữ liệu giả của probe:
chúng không điều khiển tiến trình, không ngăn Worker ghi và không thay phán đoán của Main.

1. **Ghi trước tác động.** Trước khi giao hoặc gọi writer, Main ghi vào STATE/HANDOFF hiện có (P-CTX1, `record_before_effect`) một đoạn văn xuôi: lần giao → task/revision/slot →
   invocation nếu host cho biết → writer, request ID và đích dự định. Ghi lỗi (CONFLICT, `TRANSACTION_UNFINISHED`, UNKNOWN) thì chưa bắt đầu tác động và phải báo.
   Note chỉ bảo vệ bytes của chính nó, không khóa TASK hay nguồn. Ngay trước khi vượt ranh giới gọi writer, ghi rằng lệnh có thể đã bắt đầu/chưa rõ kết quả; không để note cũ “chưa gọi” làm bằng chứng sau mở lại phiên.
2. **Dừng, timeout hoặc hủy lần giao: vô hiệu hóa trước.** Main tăng `task_revision` trên TASK hiện hành (`void_assignment`) trước lần nhận hoặc tích hợp kế tiếp, kể cả khi yêu cầu và
   nguồn không đổi; nếu không, TASK cũ và RESULT muộn vẫn `MATCH`. RESULT và candidate cũ giữ nguyên bytes. Revision mới đang giữ để reconcile thì chưa dispatch: ghi "đang chờ" và nơi có
   bằng chứng vào STATE/HANDOFF. Chỉ báo "đã vô hiệu hóa" khi đọc lại TASK thấy revision mới; ghi hoặc đọc lại lỗi thì giữ chờ mọi tích hợp liên quan. Từ lúc yêu cầu dừng đến lúc vô hiệu hóa
   thành công còn một khoảng hở: không tích hợp trong lúc đó. Request P-CN1 lập trước đó đã bind TASK thô bị guard input của writer từ chối (`INPUT_CHANGED_SINCE_READ`); publish đã
   hoàn tất trước lúc đó vẫn tồn tại và phải reconcile (mục 4).
3. **Dừng và tác động là hai việc riêng.** Chỉ ghi "đã yêu cầu dừng" hoặc "chưa xác nhận" nếu không quan sát được host đúng invocation. Retire native, mất phản hồi, timeout hay file kết quả
   đều không chứng minh invocation đã dừng, và một xác nhận dừng của host cũng không chứng minh không có tác động. `void_assignment` luôn trả `host_stop: UNCONFIRMED`.
4. **Reconcile trước khi thử lại.** Khi mất phản hồi, đọc lại bằng owner trước mọi lần giao lại: P-CN1 là `status`/`observe` cho đúng request ID (`reconcile_publish`); STATE/HANDOFF là bytes hiện
   tại; sổ nguồn là sổ và giao dịch dở. `recover` của `publish_new` ghi evidence và dọn file tạm nên là phép **ghi**: chỉ gọi khi cần phục hồi, trong quyền của tác động đó, và khai là đã ghi.
   Đích phải khớp đích trong prepared của đúng ID; bản published cần khớp cả bytes lẫn identity đã ghi, bản thay thế cùng bytes vẫn giữ chờ. Đã ghi (`WRITTEN`) thì nhận diện đúng kết quả đó, không ghi lần hai, không sinh ID mới; bằng chứng đã ghi không làm kết quả cũ được tích hợp vào task mới. Evidence thiếu hoặc mâu thuẫn, UNKNOWN
   hay giao dịch dở thì giữ chờ, không suy "chưa ghi". `NONE_ATTEMPTED` cần Main biết chắc trong cùng ngữ cảnh sống rằng chưa vượt ranh giới gọi (`no_call_observed=True`), đồng thời evidence và đích đều vắng.
   Note lịch sử “chưa gọi” không đủ: sau mở lại phiên, evidence/đích vắng vẫn giữ chờ nếu thiếu bằng chứng độc lập chưa dispatch. Không tự xóa hay rollback thành quả đã có.
5. **Giao lại có điều kiện** (`next_step`). Chỉ giao lại khi đã vô hiệu hóa và reconcile, invocation cũ đã kết thúc (hoặc chứng minh được an toàn chạy song song), grant còn bao trùm, còn giới hạn
   retry/chi phí và khả năng còn đáp ứng. Giao lại dùng TASK hiện hành (đã tăng revision) và **slot mới**; mọi sửa TASK, kể cả chỉ đổi slot, tăng revision và ghi lại bằng `void_assignment`; không sửa RESULT cũ, không bind lại candidate cũ. Không có giới hạn retry/chi phí thì không tự cấp
   retry. Thiếu tool, quota hoặc provider thì nêu rõ phần chưa làm. Không tăng retry, chi phí, model, provider, tool hay xác thực; không tự cài thêm; không sửa profile hay file native để lách
   các cấu hình đang UNSUPPORTED (fallback, bật/tắt, effort, giới hạn cứng).
6. **Mở lại phiên.** Đọc TASK hiện hành, STATE/HANDOFF và evidence của đúng tác động từ đĩa, rồi chạy lại checkpoint (bytes nguồn, candidate, sổ) trước khi tiếp tục. Không dùng mtime, bản TASK đi kèm
   RESULT, việc file đầu ra tồn tại hay trí nhớ phiên trước làm nguồn quyết định. Note thiếu hoặc mâu thuẫn với TASK/evidence thì giữ phần phụ thuộc, không đoán lần giao đang hiệu lực. Con trỏ
   "Nháp hiện tại" (`current_draft`) chỉ điều hướng, không là trạng thái vòng đời và không là việc người dùng nhận bản.
7. **Fallback một agent.** Khi không gọi được Worker, Main có thể làm nháp trong grant. Nếu tác động cần Reviewer độc lập mà không có, giữ nháp và chờ review; không tự review, đổi tên actor, hạ route
   hay lấy checker đạt thay review.
8. **Nội dung và nhận bản** (`integration_gate`). Reviewer bắt buộc phải đạt, đúng binding và không veto (`review=PASSED`); DONE, FAILED, BLOCKED hay UNKNOWN đều giữ chờ. Chỉ dùng NOT_REQUIRED khi route không yêu cầu review. Binding, file hay checker đạt không xác nhận mọi requirement nội dung. Mỗi requirement bắt buộc cần Main xác nhận `MET` bằng phán đoán nội dung riêng
   (phần ngữ nghĩa là phán đoán hợp tác, không có công cụ kiểm); thiếu, UNKNOWN, FAILED hay BLOCKED thì giữ chờ, không là `ACCEPTED_FOR_INTEGRATION`. RESULT của Worker vẫn `CANDIDATE`; bản đã
   publish, chọn hay mở cũng chưa là `USER_ACCEPTED`. Người dùng nhận bản A không truyền sang bản B dù cùng `work_id`, cùng tên hay cùng bytes khi binding, revision, result hoặc artifact khác: dùng
   `result.user_acceptance` v3 sẵn có (mục 8 hợp đồng v3), không tạo biên nhận mới và không giả `USER_CONFIRMATION` trong project thật.

### Giới hạn cần nói rõ

- Hợp tác, không cưỡng chế: Write của native không giới hạn đường dẫn và không chặn ghi đè, nên "chỉ ghi vào slot" và "chỉ tạo file mới" là nghĩa vụ của vai, không phải bảo đảm của host.
  Không ngăn Main cố dùng một snapshot cũ; chỉ làm việc đó lộ ra ở checkpoint và ở guard input của writer.
- Còn khoảng hở giữa checkpoint và ghi (TOCTOU cuối), `expected_before`/digest không phải khóa của hệ điều hành, và không có giao dịch nguyên tử giữa nhiều writer.
- Binding khớp chỉ là khớp; không là PASS tổng quát, quyền hay nghiệm thu của người dùng. `profile_ref` vẫn `UNSUPPORTED`; không mở rộng workflow để có PASS.
- Chưa có ở đây: nhiều phần và vòng sửa tự động, lineage (B-01/B-02, `tools/artifacts.py`), bằng chứng host đã dừng hay quota/fallback thật, và cưỡng chế nghĩa vụ vô hiệu hóa:
  khoảng hở trước khi `void_assignment` thành công còn nguyên, Worker cũ vẫn có thể ghi muộn vào slot (chỉ bị lộ ra ở checkpoint).

Probe tích hợp của kho nguồn (`test_task_result_flow.py` trong thư mục tests của kho nguồn, không nằm trong bản phân phối) chạy đúng các hàm trên bằng API thật trên dữ liệu giả, gồm các ca B-03 (host, quota, provider và Reviewer thiếu chỉ là dữ kiện giả lập có nhãn); nó không chứng minh một agent sống đã làm đúng trình tự.

### TASK/RESULT in short (EN)

For multi-step work handed to Scout or Worker, Main keeps ONE current TASK per task (`working/<work-id>/<task-id>/TASK.json`) and gives every assignment its own slot
(`.../assignments/<assignment-id>/RESULT.json` plus the candidate directory); the receiving role writes only there and only a CANDIDATE. Records are plain `law.cvf.control/3` task/result
records: no new schema, counter or task engine. Small jobs need no TASK/RESULT. When the request or an input changes, Main raises `task_revision`; an older RESULT keeps its own
binding and is never integrated again. Before every integration (and again immediately before each writer call) Main runs the checkpoint above: current TASK vs RESULT binding
(`binding.compare_binding`), current bytes of inputs, `context_refs` and the candidate against the bound digests, and, for inputs or `context_refs` with a `source_id`, exactly one ledger row
(`library.read_book`/`record`/`id_counts`) with the same ID, locator and revision. An empty `problems` list means the checked relations match; it is not a PASS, a grant or user
acceptance. Paths first use the existing `publish_new.path_form_problem`; unsupported aliases are refused before reading. This executable example handles one Worker candidate, not a general Scout delta workflow. The candidate is read once and those exact bytes are what the single writer receives (P-CN1 for a new file with the raw TASK/RESULT/candidate/source/ledger digests in
`request.inputs`; P-CTX1 with `expected_before` for STATE/HANDOFF; `library_sync.apply(..., expected_preview=...)` for the ledger). The protocol is cooperative: native Write has no path
sandbox or new-only mode, a final TOCTOU window remains, and there is no atomicity across writers.

Two phases for the digest (V2-B): the native Worker has no hashing tool and none is added. The Worker writes one candidate; Main observes its digest with a real tool
(`observe_candidate` in the recipe, a read-only wrapper over `artifacts.observe_file` of the fixed LAW tree) and passes the observation verbatim; then the Worker writes its own RESULT from it. Main never writes a
RESULT under the Worker's name and the Worker never claims to have hashed. The helper takes the raw TASK digest Main kept at dispatch and refuses, writing nothing, when it is missing or changed, when
the TASK is not an Office Worker TASK (marker and context both required), when the write targets are not exactly `candidate/<file>` and `RESULT.json` of one slot under `create_new`/`Write`/`working`,
when the RESULT already exists, or when the path, link, hardlink, non-regular file or the observer fails. The RESULT carries the delivered binding plus `outputs` = `artifacts` = `[{path, digest, role: ACTUAL_BYTES}]`,
`evidence` of kind `TOOL_OBSERVED` scoped to the digest Main observed, requirements `UNKNOWN`, and `CANDIDATE` only. The observation is a bytes digest, not a PASS, a grant, fresh source, correct content or an atomic
snapshot; it is not added to the TASK (the binding must not change), a candidate changed afterwards is stopped by the checkpoint, and the digest in a RESULT is never edited to fit. The phases are a logical sequence:
the host must really continue the same child, or map two invocations onto one assignment inside the grant. A hint to SendMessage in an old trace does not prove the tool is available, and neither `Agent.resume` nor the parent
CLI `--resume` is a child continuation; with two instances declare two invocations; otherwise hold and invent no identity or provenance.

Stop, timeout, late results and reopening (B-03): a stop, timeout or cancelled assignment is handled by voiding first. Main raises `task_revision` on the current TASK (`void_assignment`,
read back through the owner loader) before accepting or integrating anything else, even when the request and the sources did not change; otherwise the old TASK and a late RESULT still MATCH.
The old RESULT and candidate keep their bytes. Until the read-back shows the new revision Main reports the assignment as not voided and integrates nothing related. Stopping and effects are
separate: a stop request, retire, silence, timeout or an output file proves neither that the invocation stopped nor that nothing was written. Before any retry Main reconciles with the owner
for the exact request ID (`reconcile_publish` = P-CN1 `status`/`observe`, read only; `recover` writes evidence, so it is called separately, inside the grant, and reported as a write). Missing,
contradictory or UNKNOWN evidence holds. The target must equal the prepared target; published bytes and file identity must both match. A historical no-call note is not proof of no dispatch after reopening; NONE_ATTEMPTED needs positive same-context no-call observation and absent evidence/target. Required review needs a bound, veto-free PASSED verdict; DONE or unknown holds. A written result is recognised and never written twice; no new ID is minted. Reassign only into a new slot under the current revision, inside the grant and
the stated retry/cost limits, without raising any limit and without touching the profile or native files; with a tool, quota or provider missing, report the unfinished part, or let Main draft inside
the grant (a required independent review that is missing stays pending). A reopened session re-reads TASK, notes and evidence from disk and reruns the checkpoint. A matching binding never proves the
content: mandatory requirements need Main's own content judgement, a Worker RESULT stays a CANDIDATE, a published, selected or opened draft is not `USER_ACCEPTED`, and the user's acceptance of draft A
does not carry over to draft B (the v3 `user_acceptance` is bound to task, revision, result and artifacts). All of this is cooperative; the probe uses labelled simulations and proves nothing about a
real host. Lineage belongs to B-01/B-02.

## Phương pháp văn phòng trên vai lõi (V1-A) / Office methods on the core roles

`roles/office/` giữ danh mục `catalog.json` (`law.office-methods/1`), sáu hợp đồng phương pháp và `MAIN.md` (hướng dẫn cho Main). Đây là
**phương pháp của nhiệm vụ**, không phải vai mới: người nhận vẫn là Scout, Worker hoặc Reviewer lõi, chịu quy tắc và grant của project.
Không có schema, pack, trường profile hay model riêng cho từng phương pháp (`preset_mode = INHERIT_CORE_PROFILE`); model và effort theo
profile của vai lõi. Không tự được native nạp: vai nhận đọc hợp đồng vì brief và `context_refs` chỉ đúng file.

| Mã | Vai lõi | Việc |
|---|---|---|
| `research-assistant` | scout | khảo sát độ đủ, đúng kỳ, đúng loại của căn cứ |
| `executive-secretary` | worker | tổng hợp báo cáo/biên bản theo kỳ và người đọc |
| `correspondence` | worker | nháp thư trả lời cục bộ, không gửi, không chạm hộp thư |
| `market-analyst` | worker | so sánh/nhận định thị trường đúng kỳ, đơn vị, loại giá |
| `data-analyst` | worker | tính toán có truy vết trên dữ liệu; cần công cụ tính thật |
| `evidence-reviewer` | reviewer | mở nguồn kiểm candidate/claim trọng yếu |

- **Helper chỉ đọc** `python tools/office.py list|validate|compose`: kiểm catalog/hợp đồng và soạn MỘT brief cho method ID mà Main đã chọn,
  kèm `context_refs` (SHA-256 bytes thô của catalog, hợp đồng và skill thực dùng), checklist khả năng và phần thiếu. Không phân loại yêu cầu
  bằng từ khóa, không ghi file, không tạo TASK, không dùng mạng, không gọi vai, không cấp quyền. `PREPARED` chỉ là đã chuẩn bị giao việc.
- `inputs_proposal` và `task_fragment.inputs` chỉ đề xuất path/digest bytes. Trước khi ghi TASK, Main dùng owner thư viện hiện có để bổ sung
  hoặc giữ `source_id`/`revision` cho nguồn đã đăng ký; checkpoint ở trên đối chiếu đúng một ID, locator, revision và bytes. Nguồn thực sự
  chưa đăng ký phải khai rõ; lỗi sổ không phải bằng chứng chưa đăng ký và phần phụ thuộc phải chờ. Không tự tạo ID.
- **Khả năng tách bốn chiều:** được yêu cầu / có trong exporter native (Scout, Reviewer: Read, Grep, Glob; Worker thêm Write) / grant / quan sát
  host. Grant và host luôn `NOT_INSPECTED` ở helper. Khả năng bắt buộc mà adapter lõi không có (`compute`, `office_files`) cho `NEEDS_CAPABILITY`:
  giữ chờ phần phụ thuộc, không cấp shell, không suy từ việc máy có Python.
- **Tuyến compute host-session (V4, chủ động chọn):** chỉ khi yêu cầu compose có thêm khóa `compute_route` = `{probe, scope}`; mặc định và exporter
  native không đổi. `tools/office_compute.py` (công cụ tính hẹp, chỉ đọc CSV trong `inputs` của TASK, `aggregate`/`compare_prices` trên Decimal)
  chuẩn bị ra `ROUTE_READY_UNVERIFIED` hoặc `ROUTE_REFUSED` từ probe phía Main và quyền lab (`permission.status=ALLOWED`); chiều `specialist_call`
  luôn `NOT_OBSERVED` khi chuẩn bị. Khi sẵn sàng, handover Worker nêu công cụ shell của host với đúng một lệnh thay vì bảo chỉ có bốn công cụ;
  handover mặc định không đổi. Đây là quyền bảo trì ở host-session, không phải native `law-worker`, sandbox hay grant sản phẩm. Hai pha
  (Worker ghi candidate, Main quan sát digest, Worker ghi RESULT) giữ nguyên; lệnh tính không băm candidate. Chuyên viên phải tự gọi và lời gọi
  được quan sát mới là "tính thật bằng công cụ của chuyên viên"; Main không tính hộ rồi ghi dưới tên chuyên viên.
- **Ràng buộc vào TASK:** Main bind catalog, hợp đồng và skill đã dùng qua `context_refs`, và thêm đúng một requirement bắt buộc
  `OFFICE-METHOD:<mã>:v<phiên bản>` vào `acceptance.requirements`. Checkpoint ở trên gọi `office.guard_task`: chỉ cần thấy marker hoặc một context
  dưới `roles/office/` là phải đủ cả hai phía (một marker hợp lệ; một catalog và đúng một hợp đồng khớp; mã, phiên bản, vai lõi, bytes còn khớp;
  hợp đồng đủ các mục). Marker lạ hoặc trùng, mất marker còn refs, mất refs còn marker đều chặn, không rơi về legacy. TASK không marker và không
  context office là legacy, chạy như trước. Xóa đồng thời marker và refs làm RESULT cũ không còn khớp binding. Guard chỉ kiểm cấu trúc và bytes,
  không kiểm đúng ngữ nghĩa nghề hay grant; người sửa được toàn bộ record vẫn nằm trong giới hạn hợp tác, không phải chống giả mạo.
- **Giới hạn:** `PREPARED` ≠ đã gọi vai ≠ nội dung đã kiểm. Gói này không chứa dấu vết host rằng một vai thật đã đọc hợp đồng và dùng công cụ.
  Review không thay quyền và không nhận bản thay người dùng.

Office methods in short (EN): `roles/office/` holds a catalog, six method contracts and the Main guide. They are task methods on the three
core roles, not new roles, and carry no schema, pack, profile field or model of their own (models follow the core-role profile). `tools/office.py`
is read-only: it validates the catalog and composes one brief for the method Main chose, with `context_refs` over raw bytes, a four-dimension
capability checklist (requested / in the exporter / granted / observed on the host, the last two never inspected) and the missing parts; a
missing required capability such as `compute` is `NEEDS_CAPABILITY`. Only when the compose request opts in with `compute_route` = `{probe, scope}`
does `tools/office_compute.py` (read-only, CSV in the TASK `inputs`, `aggregate`/`compare_prices` on Decimal) prepare a `ROUTE_READY_UNVERIFIED` or `ROUTE_REFUSED`
host-session route from Main's probe and the lab permission; `specialist_call` stays `NOT_OBSERVED` at preparation, the Worker hand-over then names the host shell tool
with one command, and the default hand-over is unchanged. It is maintenance authority, not a native law-worker, sandbox or product grant. A TASK binds the catalog, contract and skills through `context_refs`
while input proposals contain only byte path/digest; before writing the TASK, Main uses the existing library owner to retain/add `source_id`
and `revision` for registered sources, checks unique ID, locator, revision and bytes, identifies genuinely unregistered sources, and holds on
ledger errors without inventing an ID. The TASK also carries exactly one mandatory `OFFICE-METHOD:<id>:v<n>` requirement, and the checkpoint
above blocks a lone marker, lone refs, duplicate or foreign
markers, a version/role/locator mismatch and changed bytes, while a legacy task without either passes unchanged. `PREPARED` is not invoked and
not content-checked; no live host trace is part of this package.

Core role contracts live here; domain extensions remain in accepted packs.
Main and every role follow `.cvf/rules/CONTROL_RULES.md` and its routing policy;
a role label grants no authority and a review grants no permission.
The implementation trial presets were checked on 2026-10-17 (revision 2), with
quality not yet evaluated on LAW. Product `host_presets` and native integration
remain pending R4 (only CANDIDATE host presets exist). Trial metadata does not register agents or grant permissions.
