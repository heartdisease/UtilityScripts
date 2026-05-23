#!/usr/bin/python3
import argparse
import datetime
import json
import re
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path


EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
DEFAULT_SEARCH_PURPOSE = "Archived via pubmed-med-db.py; review and refine purpose."
DEFAULT_PAPER_PURPOSE = "Archived via pubmed-med-db.py; review and refine purpose."
DEFAULT_WEB_PURPOSE = "Archived web source; review and refine purpose."


def slugify(text, fallback="record", max_words=10, max_length=80):
	text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
	text = text.lower()
	text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
	if not text:
		return fallback
	words = [word for word in text.split("-") if word]
	text = "-".join(words[:max_words])
	return text[:max_length].rstrip("-") or fallback


def next_search_filename(search_dir, slug):
	max_index = 0
	for path in search_dir.glob("s*-*.json"):
		match = re.match(r"s(\d+)-", path.name)
		if match:
			max_index = max(max_index, int(match.group(1)))
	return f"s{max_index + 1:02d}-{slug}.json"


def escape_markdown_cell(text):
	return str(text).replace("|", "\\|").strip()


def fetch_text(endpoint, params, timeout=60):
	url = f"{EUTILS_BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
	request = urllib.request.Request(
		url,
		headers={
			"User-Agent": "UtilityScripts med-db archivist/1.0"
		},
	)
	with urllib.request.urlopen(request, timeout=timeout) as response:
		return response.read().decode("utf-8")


def save_text(path, content):
	path.write_text(content, encoding="utf-8")


def ensure_med_db_structure(med_db):
	for name in ("searches", "metadata", "abstracts", "web"):
		(med_db / name).mkdir(parents=True, exist_ok=True)


def build_common_params(args):
	params = {"db": "pubmed"}
	if args.email:
		params["email"] = args.email
	params["tool"] = "pubmed-med-db"
	return params


def load_existing_readme_entries(readme_path):
	search_entries = {}
	paper_entries = {}
	web_entries = {}

	if not readme_path.is_file():
		return search_entries, paper_entries, web_entries

	for line in readme_path.read_text(encoding="utf-8").splitlines():
		search_match = re.match(
			r"^\| searches/(s\d{2}-[^|`]+\.json) \| `([^`]+)` \| (.+) \|$",
			line,
		)
		if search_match:
			search_entries[search_match.group(1)] = {
				"query": search_match.group(2),
				"purpose": search_match.group(3),
			}
			continue

		paper_match = re.match(
			r"^\| `(pmid-\d+-[^`]+)\.\{json,txt\}` \| (\d+) \| ([^|]+) \| (.+) \|$",
			line,
		)
		if paper_match:
			paper_entries[paper_match.group(1)] = {
				"pmid": paper_match.group(2),
				"url": paper_match.group(3).strip(),
				"purpose": paper_match.group(4),
			}
			continue

		web_match = re.match(
			r"^\| web/([^|` ]+\.html) \| ([^|]+) \| (.+) \|$",
			line,
		)
		if web_match:
			web_entries[web_match.group(1)] = {
				"url": web_match.group(2).strip(),
				"purpose": web_match.group(3),
			}

	return search_entries, paper_entries, web_entries


def query_from_search_json(path):
	data = json.loads(path.read_text(encoding="utf-8"))
	result = data.get("esearchresult", {})
	return result.get("querytranslation") or "Query unavailable; review and refine."


def sync_readme(med_db, search_updates, paper_updates):
	readme_path = med_db / "README.md"
	existing_searches, existing_papers, existing_web = load_existing_readme_entries(readme_path)
	existing_searches.update(search_updates)
	existing_papers.update(paper_updates)

	search_lines = []
	for path in sorted((med_db / "searches").glob("*.json")):
		entry = existing_searches.get(path.name, {})
		query = entry.get("query") or query_from_search_json(path)
		purpose = entry.get("purpose") or DEFAULT_SEARCH_PURPOSE
		search_lines.append(
			f"| searches/{path.name} | `{escape_markdown_cell(query)}` | {escape_markdown_cell(purpose)} |"
		)

	paper_lines = []
	for path in sorted((med_db / "metadata").glob("*.json")):
		stem = path.stem
		match = re.match(r"pmid-(\d+)-", path.name)
		pmid = match.group(1) if match else "unknown"
		entry = existing_papers.get(stem, {})
		url = entry.get("url") or f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
		purpose = entry.get("purpose") or DEFAULT_PAPER_PURPOSE
		paper_lines.append(
			f"| `{stem}.{{json,txt}}` | {pmid} | {escape_markdown_cell(url)} | {escape_markdown_cell(purpose)} |"
		)

	web_lines = []
	for path in sorted((med_db / "web").glob("*.html")):
		entry = existing_web.get(path.name, {})
		url = entry.get("url") or "URL unavailable; review and refine."
		purpose = entry.get("purpose") or DEFAULT_WEB_PURPOSE
		web_lines.append(
			f"| web/{path.name} | {escape_markdown_cell(url)} | {escape_markdown_cell(purpose)} |"
		)

	today = datetime.date.today().isoformat()
	content = [
		"# med-db - Wissenschaftliche Referenzdatenbank",
		"",
		f"Gesammelte Suchresultate, Metadaten und Abstracts. Gespeichert am {today}.",
		"",
		"Quellen: PubMed via NCBI E-utilities und zugaengliche Webquellen.",
		"",
		"Hinweis: Diese Datenbank speichert bewusst maschinenlesbare Suchresultate und greppbare Abstract-Texte statt fragiler HTML-Scrapes von PubMed.",
		"",
		"## Struktur",
		"",
		"- `searches/`: rohe PubMed-`esearch`-Antworten als JSON",
		"- `metadata/`: rohe PubMed-`esummary`-Antworten pro PMID als JSON",
		"- `abstracts/`: rohe PubMed-`efetch`-Abstracts als Textdateien",
		"- `web/`: zugaengliche Webseiten, die im Review verwendet oder geprueft wurden",
		"",
		"---",
		"",
		"## PubMed-Suchanfragen (`searches/*.json`)",
		"",
		"| File | Query | Zweck |",
		"|------|-------|-------|",
	]
	content.extend(search_lines)
	content.extend([
		"",
		"---",
		"",
		"## PubMed-Datensaetze (`metadata/*.json` + `abstracts/*.txt`)",
		"",
		"| Dateien | PMID | URL | Zweck |",
		"|---------|------|-----|-------|",
	])
	content.extend(paper_lines)
	content.extend([
		"",
		"---",
		"",
		"## Webseiten (`web/*`)",
		"",
		"| File | URL | Zweck |",
		"|------|-----|-------|",
	])
	content.extend(web_lines)
	content.extend([
		"",
		"---",
		"",
		"## Nutzungshinweise fuer kuenftige Runs",
		"",
		"- Erst `searches/` pruefen, bevor neue Suchen gestartet werden.",
		"- Fuer verwendete PMIDs zunaechst `metadata/` und `abstracts/` lesen.",
		"- Bei widerspruechlicher Evidenz die Studientypen unterscheiden: Risiko, Therapie, Biomarker, Tiermodell.",
		"- Wenn neue Paper verwendet werden, immer beide Dateitypen nachziehen: `metadata/*.json` und `abstracts/*.txt`.",
	])
	readme_path.write_text("\n".join(content) + "\n", encoding="utf-8")


def archive_search(args, med_db):
	params = build_common_params(args)
	params.update({
		"retmode": "json",
		"term": args.query,
		"retmax": str(args.retmax),
	})
	raw_search = fetch_text("esearch.fcgi", params)
	parsed_search = json.loads(raw_search)
	search_slug = args.search_slug or slugify(args.query, fallback="pubmed-search")
	search_dir = med_db / "searches"
	search_dir.mkdir(parents=True, exist_ok=True)
	search_file = search_dir / next_search_filename(search_dir, search_slug)
	save_text(search_file, raw_search)
	return search_file, parsed_search.get("esearchresult", {}).get("idlist", [])


def archive_pmid(args, med_db, pmid):
	params = build_common_params(args)
	params.update({"retmode": "json", "id": str(pmid)})
	raw_summary = fetch_text("esummary.fcgi", params)
	parsed_summary = json.loads(raw_summary)
	record = parsed_summary.get("result", {}).get(str(pmid), {})
	title = record.get("title") or f"pmid-{pmid}"
	paper_slug = slugify(title, fallback=f"pmid-{pmid}")

	metadata_dir = med_db / "metadata"
	abstracts_dir = med_db / "abstracts"
	metadata_dir.mkdir(parents=True, exist_ok=True)
	abstracts_dir.mkdir(parents=True, exist_ok=True)

	metadata_file = metadata_dir / f"pmid-{pmid}-{paper_slug}.json"
	abstract_file = abstracts_dir / f"pmid-{pmid}-{paper_slug}.txt"
	save_text(metadata_file, raw_summary)

	params = build_common_params(args)
	params.update({
		"id": str(pmid),
		"rettype": "abstract",
		"retmode": "text",
	})
	raw_abstract = fetch_text("efetch.fcgi", params)
	save_text(abstract_file, raw_abstract)

	return metadata_file, abstract_file, title


def dedupe(values):
	seen = set()
	ordered = []
	for value in values:
		if value in seen:
			continue
		seen.add(value)
		ordered.append(value)
	return ordered


def run_validator(med_db):
	validator = Path(__file__).with_name("med-db-validate.py")
	if not validator.is_file():
		print(f"validator script not found: {validator}", file=sys.stderr)
		return 1

	result = subprocess.run(
		[sys.executable, str(validator), "--med-db", str(med_db)],
		check=False,
	)
	return result.returncode


def parse_args():
	parser = argparse.ArgumentParser(
		description="Archive PubMed searches and selected papers into the local med-db schema.",
	)
	parser.add_argument("--query", help="PubMed search query to archive.")
	parser.add_argument("--search-slug", help="Optional slug for the saved search file.")
	parser.add_argument(
		"--pmid",
		action="append",
		default=[],
		help="PMID to archive. May be passed multiple times.",
	)
	parser.add_argument(
		"--archive-first",
		type=int,
		default=0,
		help="Also archive the first N PMIDs returned by --query.",
	)
	parser.add_argument(
		"--retmax",
		type=int,
		default=20,
		help="How many PubMed hits to request for the archived search JSON.",
	)
	parser.add_argument(
		"--med-db",
		default="med-db",
		help="Target med-db directory. Defaults to ./med-db.",
	)
	parser.add_argument(
		"--email",
		help="Optional contact email passed to NCBI E-utilities.",
	)
	parser.add_argument(
		"--delay",
		type=float,
		default=0.34,
		help="Delay between PMID fetches in seconds. Defaults to 0.34.",
	)
	parser.add_argument(
		"--validate",
		action="store_true",
		help="Run med-db-validate.py after the archival step and return its exit status on failure.",
	)
	args = parser.parse_args()
	if not args.query and not args.pmid:
		parser.error("provide --query and/or at least one --pmid")
	if args.archive_first < 0:
		parser.error("--archive-first must be >= 0")
	if args.archive_first and not args.query:
		parser.error("--archive-first requires --query")
	if args.retmax < 1:
		parser.error("--retmax must be >= 1")
	return args


def main():
	args = parse_args()
	med_db = Path(args.med_db)
	med_db.mkdir(parents=True, exist_ok=True)
	ensure_med_db_structure(med_db)

	search_file = None
	search_updates = {}
	paper_updates = {}
	pmids = list(args.pmid)
	if args.query:
		search_file, search_hits = archive_search(args, med_db)
		search_updates[search_file.name] = {
			"query": args.query,
			"purpose": DEFAULT_SEARCH_PURPOSE,
		}
		pmids.extend(search_hits[:args.archive_first])

	pmids = dedupe([str(pmid) for pmid in pmids])
	archived = []
	for index, pmid in enumerate(pmids):
		metadata_file, abstract_file, title = archive_pmid(args, med_db, pmid)
		archived.append((pmid, metadata_file, abstract_file, title))
		paper_updates[metadata_file.stem] = {
			"pmid": str(pmid),
			"url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
			"purpose": DEFAULT_PAPER_PURPOSE,
		}
		if index < len(pmids) - 1 and args.delay > 0:
			time.sleep(args.delay)

	sync_readme(med_db, search_updates, paper_updates)

	if search_file:
		print(f"saved search: {search_file}")
	else:
		print("saved search: none")

	if not archived:
		print("archived PMIDs: none")
		return 0

	print("archived PMIDs:")
	for pmid, metadata_file, abstract_file, title in archived:
		print(f"- {pmid}: {title}")
		print(f"  metadata: {metadata_file}")
		print(f"  abstract: {abstract_file}")

	if args.validate:
		print("running validator...")
		return run_validator(med_db)

	return 0


if __name__ == "__main__":
	try:
		raise SystemExit(main())
	except KeyboardInterrupt:
		print("cancelled", file=sys.stderr)
		raise SystemExit(130)
