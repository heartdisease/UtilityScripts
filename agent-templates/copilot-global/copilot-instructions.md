---
name: "Global Coding Preferences"
description: "Use when helping <FIRSTNAME LASTNAME> with TypeScript, React, Node tooling, or Python work; when user asks why; when planning multi-file changes; when choosing search or CLI tools; or when scoping exploratory or large-feature tasks."
applyTo: "**"
---

# Global Coding Preferences

## Communication

- Skip foundational explanations unless asked.
- "why?" → explain reasoning + tradeoffs; no restate what code does.
- User wrong → say so, name tradeoff/risk. No silent comply.
- Reference code as `path/to/file.ts:42` when jump helps.

## Workflow

- Reproduce failing behavior first — failing test, repro script, or UI step.
- Intent ambiguous + wrong guess wastes work → use question tooling, offer concise options.
- Exploratory asks → 2-3 sentence rec + main tradeoff. Keep direction changeable.
- Interview before large feature implementation.
- Multi-file / unfamiliar / unclear scope → plan mode. Not one-line fix.
- 3+ files → use `explorer` sub-agent to summarize first.
- Multi-step work → task list, mark done immediately.
- Prefer clear context between unrelated tasks over stale state.

## Tooling

- Ask before invoking `gh`.
- Prefer dedicated workspace tools over shell wrappers when both exist.
- Prefer search tools over shelling out to `rg`.
- `yq` for YAML, `jq` for JSON, `xq` for XML, `difft` for structure-aware diffs.
- `ast-grep` read-only fine; ask before write/update forms.
- `watchexec` for rerun-on-change when fits.
- Prefer CLI data tools over ad hoc `python -c` / `node -e` scripts.
