# CVF Workspace Rules

> Local generated workspace copy.
>
> Canonical source: .Controlled-Vibe-Framework-CVF/docs/reference/CVF_WORKSPACE_RULES.md.

## Purpose

This root is a non-git container for the public CVF core clone and sibling
downstream projects. Application work belongs in each project folder.

## Required Layout

~~~text
CVF-Workspace/
  .Controlled-Vibe-Framework-CVF/
  CVF_RULE_PACKS/
  <Application-Project>/
  WORKSPACE_RULES.md
  CVF_WORKSPACE_RULE_PACKS.md
  CVF_WORKSPACE_MEMORY.md
  AGENT_HANDOFF.md
  New-CVF-Governed-Project.ps1
  Run-CVF-NewProject-Enforcement.ps1
  Update-CVF-Workspace.ps1
~~~

## Public Core

- Path: D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF
- Remote: https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git
- Keep downstream application source outside .Controlled-Vibe-Framework-CVF/.
- Run framework maintenance and workspace reconciliation from the public core.

Reconcile the hidden core with the latest public remote:

~~~powershell
powershell -ExecutionPolicy Bypass -File ".\Update-CVF-Workspace.ps1" -RunGate
~~~

If the root update wrapper is missing, run the hidden-core reconciler directly:

~~~powershell
powershell -ExecutionPolicy Bypass -File ".Controlled-Vibe-Framework-CVF\scripts\update_cvf_workspace_public_core.ps1" `
  -WorkspaceRoot "D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace"
~~~

## Rule Packs And Agent Continuity

- CVF_RULE_PACKS/ACTIVE_RULE_PACK.json records the active rule pack when one is installed.
- CVF_WORKSPACE_RULE_PACKS.md explains the installed rule pack and refresh flow.
- CVF_WORKSPACE_MEMORY.md is the workspace-local memory front door.
- AGENT_HANDOFF.md is the workspace-local handoff file.
- Rule packs are selected local guidance; they do not turn this workspace into the private full CVF repository.
- Project-level AGENTS.md, manifests, policies, and handoffs still belong to each downstream project.

## Current Sibling Projects

~~~text
  _cvf_portable_smoke_20260722/
  Auto_docs/
  Bao_gia_dich_vu_container_pkd_edit/
  Bao_gia_phu_thu_Dau DO/
  container-reconciliation-tool/
  Container-team/
  Customer-Care-Monitor/
  CVF_RULE_PACKS/
  cvf-mini-game-doraemon/
  CVF-Operations-Workspace/
  CVF-PaidUserSafe-Proof-20260709/
  CVF-R81-RC-Adopt-20260710/
  CVF-R81-RC-Fresh-20260710/
  Dang_ky_dich_vu_container/
  Document_Translator/
  Edit Dashboard/
  Khai-bao-Cang-vu 07.2026/
  local-agent-workspace/
  Nha tre Maika/
  Policy_Local/
  QD209/
  qt-saigon-works/
  quanlyxalan/
  shift-operations-workspace/
  Smart-Money-Web/
  SOT-Application/
  tan-thuan-port/
  tan-thuan-web/
  tdr_processor-container-2026/
  Trading-Tools/
  VanBanPhapLuat_DatDai/
  vehicle-management-system/
  Viet-ERP/
  XD_App/
~~~

## Development Responsibility And Feedback

Apply `docs/reference/CVF_PRODUCT_MILESTONE_COVERAGE_CONTRACT_2026-10-23.md`
in the sibling CVF core, including "Development-Owned Internal Readiness Before
User Feedback". The development team owns roadmap detail, usable delivery,
justified expected results, bounded tests, required independent/domain review
and real packaged consumer-flow evidence. Non-coders provide goals, business
decisions and feedback after internal readiness; they do not design technical QA.
Keep internal readiness, business acceptance and install/publish authority
separate. Missing evidence blocks the affected capability; preserve mandatory
criteria, correctness/safety gates and parked-project boundaries. Written rules
and generated carriers do not prove runtime enforcement or existing-project
adoption. Existing projects adopt only at an authorized boundary.

Technical checks precede developer-owned product acceptance; business feedback
follows usable delivery, while install/publish authority remains separate.
In the existing acceptance record, answer five questions: what job and trigger;
what output standard; what grounded evidence; what specific added value; and
what delivered workflow and supported environment. Preserve all project criteria.
Scale cases and domain review to the claim and risk; do not make every mechanical
check wait for an expert. Developers prepare assessment cases/sources/rubrics;
ask the operator once for missing assessor/budget authority, without unauthorized
contact or spending. Dependent claims remain blocked pending qualified evidence.
Record source revision/check date and risk-based recheck triggers without automatic
status changes. For overdue unchecked sources, disclose the last check date in
the output (unknown if unknown); do not claim current authority for high-stakes
use. Mark untested environments NOT_TESTED;
verify exact-artifact new and upgrade workflows when claimed. Quality evidence
is separate from enabling or confirming use. Reuse existing records and gates;
do not create a tranche per check or silently drop committed scope.

## Boundary

Workspace doctor PASS proves local enforcement artifacts and public-core
freshness checks. It does not replace live provider-backed governance proof.
