# AGENTS.md

Two unrelated workflows live in this repo. Apply only the matching section:
1. Socialism DB: `./marxist-db/`
2. Medical DB: `./med-db/`

Do not mix the two domains unless the user explicitly asks for both.

## Shared

- Make the smallest local change that works; if patch context is stale, re-read the exact snippet and retry; treat scratch files as ephemeral unless asked to preserve them.
- For CSV work, start by checking `command -v mlr`, `csvcut`, `csvlook`, `csvstat`, `csvjson`; prefer `mlr`; do not assume a `csvkit` binary exists.
- Re-read the current CSV before every edit, trust file state not memory, validate right after each edit, and prefer CSV-aware checks.
- Ignore validation noise from intentionally empty optional fields.

## Socialism DB (`./marxist-db/`)

- Use for glossary-style CSV work: main glossary, `tmp.csv`, `tmp2.csv`, and similar scratch files.
- Search the main glossary first. Treat `./marxist-db` as the local archive; create it if missing and keep it updated with every newly loaded or used source page.
- Source order: `marxists.org`, then `theanarchistlibrary.org`, then `libcom.org`, then outside sources.
- Reuse validated glossary wording; keep derived scratch CSVs aligned with the glossary unless the user asks for a rewrite; if several phrasings work, choose the one closest to glossary tone.
- CSV format: header exactly `Deutscher Begriff,Englischer Begriff,Bedeutung,Kategorie,Beispiel`; exactly 5 fields; remove `,,,,`; keep everything in German except column 2; convert blank or English column 1 into the proper German term.
- Writing: short glossary definitions, match surrounding wording, leave `Beispiel` empty unless needed, use semicolons in `Bedeutung` unless properly quoted, make criticism explicit in Marxist/revolutionary Marxist/Trotskyist rewrites, and avoid overclaiming.
- Validation: confirm 5 fields per row, replace unintended commas in `Bedeutung` with semicolons, and treat an empty `Beispiel` as fine unless examples are requested.

## Medical DB (`./med-db/`)

- Use for medical, nutritional, or endometriosis literature collection and evidence summaries.
- Prefer formal evidence over general summaries. Evidence order: guidelines > systematic reviews/meta-analyses > randomized trials > observational studies. Use narrative reviews only to fill gaps or locate primary studies. Do not treat risk-association studies as treatment evidence.
- Search in PubMed via NCBI E-utilities, not PubMed HTML. Default flow: `esearch` -> `esummary` -> `efetch` with `rettype=abstract&retmode=text`.
- Before concluding, rerun the exact machine-readable search and record query, access date, PMID, DOI, journal, and study type. Inspect titles because PubMed searches can return irrelevant hits.
- Pitfalls: PubMed HTML may show anti-bot pages; OUP and other publishers may return `403`; guideline landing pages may expose metadata without recommendation text; if full text is blocked, summarize only what is supported by abstract, metadata, PMC, or accessible supplements.
- Writing: use cautious wording for heterogeneous, low-quality, or indirect evidence; do not turn absence of evidence into harm, or mechanistic/animal results into clinical recommendations; explicitly name limits such as pilots, open-label studies, exploratory biomarker work, or poor-quality meta-analyses.
- Treat `./med-db` as the local archive; create it if missing and keep every used search result, abstract, metadata record, and source page updated.
- Default archive command: `python3 ./pubmed-med-db.py --query '...' --archive-first N --validate`; use repeated `--pmid` flags for explicit PMIDs.
- `pubmed-med-db.py` auto-creates `searches/`, `metadata/`, `abstracts/`, assigns the next `sNN-...json`, and syncs `med-db/README.md`.
- Store searches as machine-readable JSON, abstracts as plain text, use stable `pmid-<id>-<slug>` filenames, and keep `med-db/README.md` indexed.
- Run `python3 ./med-db-validate.py` after structural changes and before relying on the local archive; it checks required directories, empty files, JSON validity, metadata/abstract pairing, contiguous search numbering, and README consistency.
