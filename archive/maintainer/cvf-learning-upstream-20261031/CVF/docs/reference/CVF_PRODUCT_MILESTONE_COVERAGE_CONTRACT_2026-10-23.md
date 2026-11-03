# CVF Product Milestone Coverage Contract

Memory class: POINTER_RECORD
Status: ACTIVE_STANDARD
docType: reference
Date: 2026-10-23

## Purpose

Bind product outcomes to roadmap decisions, dispatch scope and terminal evidence.
This contract extends the existing governed lifecycle; it adds no lifecycle phase,
parallel acceptance ledger or authority to execute a roadmap.

## Scope / Owner Boundary

Applies prospectively to new or materially revised roadmaps, milestone admission,
internal and external dispatch, direct Local work and terminal review. Historical
closed artifacts retain their original evidence. Existing active projects adopt
at the next authorized planning/dispatch boundary; operator-parked projects wait.
The orchestrator owns coverage and selection; workers own their admitted slice;
Local review owns semantic evidence assessment; the operator owns product scope,
business acceptance and changes to authority. Equivalent compact sections suffice
for small direct work; no extra work order is required solely to repeat fields.
External research remains advisory under the existing external-local methods;
Local owns private-source verification and final disposition. This contract grants
no external implementation or closure authority.

## Contract / Requirements

### Roadmap Creation And Progressive Detail

At creation, record the user/receiving consumer, observable final outcome, scope
and exclusions, milestone IDs, acceptance criteria IDs, major dependencies,
uncertainties and accountable roles. A milestone describes usable value or a
necessary decision with an observable result, not a count of commits or tests.
Keep implementation choices provisional until their decision boundary. A draft
with explicit unknowns is valid planning, never an execution grant.
Approved acceptance criteria are mandatory by default. Making one optional,
removing it or changing its acceptance threshold requires the scope owner's decision.

Each checkpoint names its trigger (date, deliverable, budget exhaustion or material
change), evidence required, decision owner and allowed next decisions: continue,
repair within authority, revise through the scope owner, hold or stop. Record the
actual decision and its evidence. A missed date is disclosed, never silently moved.

### Milestone Coverage Reconciliation

Before admitting work, reconcile every acceptance criterion of the selected
approved milestone against identified source versions and current evidence.
Show later milestones and known cross-milestone dependencies at roadmap depth;
do not invent full implementation detail or demand a whole-repository scan.

Use one authoritative table in the roadmap or its existing linked acceptance
surface. A work order references its exact revision/section and selected IDs.

| Criterion ID / user result | State and source/evidence | Remaining gap or unknown | Selected tranche/action | Remainder owner | Destination / re-entry condition |
|---|---|---|---|---|---|
| stable ID from approved milestone | state plus source revision/hash and evidence locator | concrete gap, or explicit none with reason | assigned action ID, or outside this slice | accountable role for unresolved remainder | exact work item/checkpoint and trigger |

States are NOT_STARTED, IMPLEMENTED_UNPROVED, VERIFIED, BLOCKED and UNKNOWN.
VERIFIED requires evidence for the exact relevant version and required acceptance
role; a technical check does not supply human/business acceptance. Record an
exclusion only with the scope owner's decision; deleting a criterion or moving it
outside a tranche cannot make it disappear from the milestone.

Every criterion appears once in the authoritative table. Multiple actions may
reference it, but their proof and remaining responsibility must be distinguishable.
Every unresolved part outside the selected action has an accountable role and a
concrete destination. A role label alone or "later backlog" is insufficient.

### Dispatch And Finite Verification

No coverage table means no implementation dispatch. Unknown coverage of the
selected milestone permits only finite verification: name the unresolved question,
source boundary, output, owner, effort/run ceiling, stop condition and the decision
that follows. Exhaustion returns the unresolved fact to its decision owner; it
does not automatically renew the investigation or create a successor tranche.

An UNKNOWN row can be fully accounted for in a table. Implementation elsewhere
may proceed only after Local establishes, with source evidence, that the unknown
cannot alter that slice's outcome, prerequisites, scope, authority or acceptance.
Record that independence decision; otherwise hold the dependent implementation.

Before dispatch, Local checks the table against the milestone's authoritative
criteria and available sources, not merely against the dispatcher-selected subset.
The work-order acceptance ledger still owns fulfillment of the selected slice.
Coverage admission and fulfillment are separate responsibilities.

### Supporting Work And Change Control

Before changing an approved target, distinguish an operator verification question,
product feedback, a new source fact, an explicit scope decision and a technical
repair within existing authority. A question about how something works or whether
a repository is open source is not by itself a decision to change milestone,
execution lane, provider, acceptance criteria or candidate. Answer from evidence
and retain the approved direction. Do not label an agent inference as operator
clarification. Explicit user changes still apply; record their exact substance,
affected criteria and existing change-control authority without asking again for
authority already granted. If material intent remains unclear, hold only the
dependent scope change and continue independent authorized work.

Select work by its contribution to the current user outcome. Keep one active
product outcome by default; complementary components may serve it together.
Before opening a successor tranche, state the specific missing criterion, why
the current bounded action cannot include it, the evidence it will add and its
return to the product. A new label, failed administrative gate or fresh unknown
does not reset the existing effort budget or justify a new investigation chain.

For capability adapters, apply the existing reuse standard's sections 2.1/2.2:
identify the native provider/repository capability, supported invocation surface,
reused CVF owner and smallest missing connection. Reuse suitable native auth,
execution, tooling and recovery facilities; add only demonstrated CVF contract,
permission, evidence or noncoder interaction gaps. Reimplementation requires a
named capability gap and comparison with native reuse and no-change. Open-source
provenance does not imply local execution; API use alone does not justify rejection.
User taste about an output is distinct from repository capability evidence.

Each supporting repair, investigation or governance task identifies the criterion
or evidenced blocker it serves, why it is necessary now, its bounded cost/effort,
stop condition and the next product action it enables. General improvements go
to an owned backlog destination. Scope changes require their existing authority.

Reconcile affected rows when source identity, acceptance criteria, scope, important
dependencies or evidence change, and at checkpoint/terminal review. Preserve valid
unaffected evidence. Record invalidated proof and the bounded verification needed;
do not rerun unrelated suites or silently reset a spent budget.

### Development-Owned Internal Readiness Before User Feedback

The development team, including the orchestrator, workers and reviewers, owns
turning the approved user outcome into an actionable roadmap, a usable product
and internal acceptance evidence. This duty applies to CVF core, downstream
products, packages, skills and templates. The non-coder supplies goals, business
decisions, available business sources and later suitability feedback; they are
not required to design technical tests, invent an oracle or expected output,
debug the implementation, or perform technical QA before the team can proceed.
Ask for genuinely missing business decisions with their consequences; the team
resolves ordinary technical choices within existing authority.

Before presenting a capability as internally ready for feedback, the team owns:

- observable acceptance criteria and a bounded set of representative, boundary,
  failure and recovery cases appropriate to the claimed use;
- expected results supported by authoritative sources, reproducible calculations
  or other justified evidence independent of the generated answer; do not invent
  gold data or treat agreement among AI outputs as proof;
- exact-version execution evidence, recorded failures and limitations, and the
  independent review required by the existing risk and role rules; and
- a real packaged consumer flow, including installation or opening, normal use,
  useful output and applicable recovery, exercised in a permitted environment.
  Component checks, document presence and a successful script alone do not prove
  that the delivered product is usable.

The team must organize qualified domain verification when the capability's
correctness, safety or professional claim requires it. An AI cannot certify its
own professional competence. Missing source, semantic or expert evidence blocks
the affected capability or claim; the team owns the gap and its next condition.
Independent capabilities may proceed only with an evidenced independence decision
under this contract. An authorized experimental component may be delivered under an explicit
experimental label, with its unmet criteria and use limits stated and without
a ready-for-use claim. Its
mandatory criteria remain unmet: do not relabel them optional, N/A or accepted
merely to ship, or lower correctness/safety gates. Changing committed scope still
requires its existing scope-owner authority.

Keep three decisions explicit in the existing roadmap and terminal return:
internal readiness (team evidence and required review), user feedback/business
acceptance (fit to the user's needs), and permission to install, publish, deploy
or otherwise act externally (the applicable authority). Internal readiness is a
prerequisite for requesting product-use feedback, not a substitute for business
acceptance or an external-action grant. Feedback may identify further work; its
absence does not transfer unresolved internal testing or expertise to the user.

#### Three Acceptance Layers And A Compact Evidence Record

Make the order explicit: technical verification, then developer-owned product
acceptance against defined content and workflow criteria, then a usable delivery
for user suitability feedback/business acceptance. The orchestrator owns the
integrated product outcome and all milestone gaps. Installation, activation,
confirmation and publishing authority remain separate from these quality layers.
Technical checks or a user enabling a package do not establish product quality.

Use the existing acceptance/intake record for five questions, preserving every
applicable project criterion rather than adding a parallel ledger:

1. What job does the component perform, with which user-request triggers,
   inputs, outputs, exclusions and reuse boundary?
2. What output standard was defined before testing, including provenance,
   usage terms, permissions, limitations and missing/invalid-input behaviour?
3. Which revision-bound cases, justified expectations, actual outputs and
   independent review demonstrate that standard, and what remains untested?
4. What concrete value does it add over the existing approach, with evidence
   for that claim and fair comparison where duplication requires it?
5. Which exact delivered artifact, environment and consumer workflow were
   exercised, including new-project and upgrade paths when claimed, preservation
   of user files/choices/permissions and applicable recovery?

Scale evidence to claim and risk: ordinary tasks need representative and
missing-input cases with content review; numeric or format constraints add
measurable checks and typical failures. High-consequence claims require source
verification and appropriate domain assessment of the parts needing professional
judgement. Mechanical checks need not all await a specialist. Developers prepare
cases, sources, rubrics and questions for assessment. Where authority to recruit
or pay is missing, ask the operator once in business language about the assessor
and budget; reuse existing decisions, do not self-hire, contact or pay anyone
without authorization. Keep dependent claims blocked until qualified evidence
exists; continue independent checks rather than waiting for user-designed QA.
Distinguish regressions used to tune behaviour from evidence for new-task claims.
Do not use AI agreement as the sole oracle or demand a large benchmark for every
skill. A concrete template-compliance or error-reduction claim can be tested as
such without claiming universal superiority over native capability.

For changeable sources, record the revision, check date, unresolved verification
and risk-based recheck events/dates; a deadline triggers reassessment, not an
assumption of continuing validity or an automatic status downgrade. If an overdue
source has not been rechecked, state "not rechecked since <last check date>" in
the output (unknown if unknown); do not present it as current authority for
high-consequence claims. Record the
actual OS/runtime/host/tool/format support matrix, marking unknown combinations
NOT_TESTED. Test new and upgrade flows on the artifact being claimed, not just
the development checkout. Reuse existing release gates; these questions do not
add an approval gate, intake enum or universal project schema. Existing packages
and skills need revision-bound evidence for readiness claims; legacy availability
labels are not proof, and missing evidence does not authorize blanket status
changes or silent removal of committed scope.

#### Required Verification And Evidence Custody

Before a ready-for-use claim, run the applicable required release/package suite
on the exact candidate in the declared supported environment. Focused checks
alone do not replace that suite when the changed delivered surface requires it.
Reviewers consume valid producer evidence; repeat only required phase gates or
bounded checks justified by a named gap/contradiction, expected information gain
and cost reason under the existing review-cost rules. This is not a requirement
to rerun unrelated suites for every documentation change.

The existing test report lists each skipped test identifier, reason/environment,
any equivalent platform coverage attempted, and its effect on the claim (or NONE
when no cases were skipped). A skip is not PASS. Use a real supported equivalent
where available; otherwise retain NOT_TESTED and the affected readiness limit.

Before replacing an existing untracked/unversioned coordination document, retain
its exact prior bytes in an appropriate archive and record the hash and replacement
identity. Modify CVF rules at their canonical governance source, then use the
existing public/workspace projection. An explicitly authorized temporary edit in
a generated/downstream copy retains a hashed patch, the label NOT_UPSTREAMED and
a source-owner destination until forward synchronization reconciles it.

### Two Terminal Conclusions

Every terminal return/review states both:

1. Tranche outcome: selected requirements satisfied or blocked, with evidence and
   limits. Preserve the existing work-order terminal vocabulary.
2. Product milestone position: what the user can demonstrably do, outstanding
   criterion IDs and required acceptance, plus owner/destination of the next work.

Workers report slice evidence, affected rows and the last Local-approved milestone
position with its revision; Local reconciles and owns the aggregate conclusion.
Workers cannot infer acceptance for work outside their slice. Business acceptance
remains with the operator or the explicitly authorized acceptance role.

Never derive product completion or a percentage from test, patch, commit or tranche
counts. Close a milestone only when all its mandatory criteria and required role
acceptances are evidenced. A parked product remains parked after foundation work.

## Verification And Enforcement Boundary

Local reviews criterion coverage, semantic evidence and necessity. Existing Core
F2G dispatch bindings may require a declared action/verification plan for this
control; they do not compute coverage completeness. Existing acceptance-ledger
checks validate selected requirements, not the completeness of their selection.

Downstream carriers project this written rule. Profile1.1's APPL control checks
work-order status/closeability; it does not inspect roadmap coverage. Profile1.2
adds CVF-DG-COV-01 and Core dispatch quality uses the same stdlib validator under
`docs/reference/downstream_gate_profile/CVF_MILESTONE_COVERAGE_MACHINE_CONTRACT.md`.
Local-admitted milestone pointers, section identity, exact criterion sets, owned
remainder and phase/conclusion joins are checked mechanically. File presence or a passing shape check never
proves agent compliance, installed-project adoption or runtime AI enforcement.

The development-owned readiness rule and the 2026-10-25 intent-preservation
and native-reuse clarification are written semantic review obligations. Existing validators bind declared criteria and control
identity; they do not infer conversational intent or detect redundant native code.

## Related Artifacts

- docs/reference/CVF_GOVERNED_WORK_LIFECYCLE_AND_DESIGN_CONTROL_STANDARD_2026-06-11.md
- docs/reference/CVF_KNOWLEDGE_ABSORPTION_AND_EXTENSION_PRIORITY_STANDARD_2026-04-13.md
- docs/reference/CVF_AGENT_WORK_ORDER_TEMPLATE_2026-05-19.md
- docs/reference/work_order_template/CVF_WORK_ORDER_ACCEPTANCE_LEDGER_ADDENDUM.md
- docs/reference/downstream_gate_profile/CVF_PROJECT_LEARNING_LOOP_STANDARD.md
- docs/reference/downstream_gate_profile/CVF_DOWNSTREAM_GATE_PROFILE_STANDARD.md

## Public Export Disposition

DEFERRED_PRIVATE_ONLY

## Claim Boundary

EPISTEMIC_PROCESS_NA_WITH_REASON: normative contract and declared boundaries;
source observations, adoption and validation evidence belong to the linked learning.
Written rule plus bounded mechanical joins; no runtime AI control, automatic
semantic reviewer or public rollout.
