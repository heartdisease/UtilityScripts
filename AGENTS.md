# AGENTS.md

## Scope

- Use for glossary-style CSV work in this repo.
- Main cases: main glossary, `tmp.csv`, `tmp2.csv`, similar scratch files.

## Sources

- Search the main glossary first.
- Treat `./marxist-db` as the local archive folder in repo root for loaded source pages and lookup material.
- Keep `marxist-db` updated with every newly loaded or actually used source page.
- Create `marxist-db` if it does not exist before doing source collection; do not assume it already exists on checkout.
- Look up leftist terminology on `marxists.org` first.
- If not found there, use `theanarchistlibrary.org` next.
- If still not found there, use `libcom.org` next.
- Use Wikipedia or other outside sources only after checking those three first.
- Reuse validated glossary wording when possible.
- Keep derived scratch CSVs aligned with main glossary wording unless user asks for rewrite.
- If several phrasings work, pick the one closest to glossary tone.

## CSV Tooling

- Start each new CSV session by testing local CSV tools.
- Check real commands, not package names: `command -v mlr`, `command -v csvcut`, `command -v csvlook`, `command -v csvstat`, `command -v csvjson`.
- Prefer `mlr` for inspect, filter, reshape, and validate.
- Prefer `csvcut`, `csvlook`, `csvstat`, and `csvjson` when they fit.
- Do not assume a `csvkit` binary exists.
- If CSV tools are missing, use narrow delimiter-aware fallback checks.

## CSV Workflow

- Re-read the current CSV before every edit.
- Trust file state, not memory.
- Keep the header exactly: `Deutscher Begriff,Englischer Begriff,Bedeutung,Kategorie,Beispiel`.
- Keep exactly 5 fields per row.
- Remove placeholder rows like `,,,,`.
- Convert a blank or English first column into the proper German term; keep the English term in column 2.
- Keep everything in German except column 2 for this glossary pattern.

## Writing

- Write short definitions in glossary style.
- Match surrounding wording.
- Leave `Beispiel` empty unless needed.
- Use semicolons in `Bedeutung` unless the field is properly quoted.
- Make criticism explicit in Marxist, revolutionary Marxist, or Trotskyist rewrites.
- Stay precise and do not overclaim when the source base is thin.

## Validation

- Prefer CSV-aware CLI checks first.
- Confirm 5 fields per row after each edit.
- Watch for commas in `Bedeutung`; replace them with semicolons unless intentionally quoted.
- Validate right after each edit.
- Treat an empty `Beispiel` as fine unless user asks for examples.
- Ignore checks that only flag empty example cells.

## Editing

- Make the smallest local change that works.
- If the user names rows, edit only those rows.
- If patch context is stale, re-read the exact snippet and retry.
- Treat scratch CSVs as ephemeral.
