# .agent/

Compact working context for the project.

- `STATE.md`: current state, not a log.
- `HANDOFF.md`: work to hand over; keep `None` when unused.
- `INDEX.md`: find sources when needed.
- `SKILL_INDEX.md`: suggests suitable skills; not a fixed calling order.
- `PENDING_LESSONS.md`: an optional place to note lessons likely to be reused.
- `PACKAGE_INFO.json`: package version, language and initialization date (created by `tools/init_project.py`; do not edit by hand).

Checkpoint only when a change matters to the next session. Do not store credentials or
unnecessary sensitive information. Independent tasks with enough context can be done directly,
without reading or writing this folder after every request.
