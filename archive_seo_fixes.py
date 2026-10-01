"""
Archives old seo_fixes.md PUBLISHED entries to keep the live file small.

Root cause of SEO Draft job truncating every night since 2026-09-29: the Draft
skill's Step 1 instructs the agent to "scan existing files" including seo_fixes.md
before choosing a keyword. That file has grown every single night (8KB on 9/20 to
36.7KB now) because every PUBLISHED entry's full narrative (before/after title,
meta, H1, internal links, publish verification...) accumulates forever. Once the
file crossed ~35KB around 9/28-29, there wasn't enough output budget left for the
model to both read it all and write a full 800-1200 word page + schema + FAQ
output in one turn -> truncation every night since.

Fix: keep only the MOST RECENT PUBLISHED entry in full in seo_fixes.md (the Draft
skill genuinely needs recent context to avoid re-targeting the same keyword), move
everything older into seo_fixes_archive.md verbatim (nothing deleted, just moved),
and leave a one-line pointer for each archived entry so history isn't invisible.

Strategic/reference sections at the top of the file (GSC snapshot, title/meta
conventions, "what not to do next", etc.) are NOT touched - those aren't growing
and the Draft job genuinely needs them every run.
"""
import re

PATH = r"C:\Users\khora\Documents\colddirect-website\seo_fixes.md"
ARCHIVE_PATH = r"C:\Users\khora\Documents\colddirect-website\seo_fixes_archive.md"

with open(PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Find every "## PUBLISHED — ..." section header and its position
published_pattern = re.compile(r"^## PUBLISHED — .+$", re.MULTILINE)
matches = list(published_pattern.finditer(content))

print(f"Found {len(matches)} PUBLISHED sections")
for m in matches:
    print(" -", m.group(0))

if len(matches) < 2:
    print("Fewer than 2 PUBLISHED sections — nothing to archive, exiting without changes.")
    raise SystemExit(0)

# Everything before the FIRST "## PUBLISHED" header is the strategic/reference
# preamble - keep it in seo_fixes.md untouched.
preamble_end = matches[0].start()
preamble = content[:preamble_end]

# All PUBLISHED sections except the last one get archived. Each section runs from
# its own header to the start of the next header (or end of file for the last).
sections = []
for i, m in enumerate(matches):
    start = m.start()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
    sections.append(content[start:end])

sections_to_archive = sections[:-1]
section_to_keep = sections[-1]

# Build the archive file (append-only; if it already exists, add to it rather than
# overwrite, so repeated runs of this script stay safe)
archive_header = (
    "# SEO fixes — archived PUBLISHED entries\n\n"
    "Older `## PUBLISHED` entries moved out of `seo_fixes.md` to keep that file "
    "small enough for the nightly SEO Draft job's context budget (see the "
    "comment block in archive_seo_fixes.py for the full root-cause). Nothing "
    "here was deleted, only relocated — full detail preserved verbatim.\n\n"
)

try:
    with open(ARCHIVE_PATH, "r", encoding="utf-8") as f:
        existing_archive = f.read()
except FileNotFoundError:
    existing_archive = archive_header

new_archive_content = existing_archive.rstrip("\n") + "\n\n" + "\n".join(sections_to_archive)

with open(ARCHIVE_PATH, "w", encoding="utf-8") as f:
    f.write(new_archive_content)

# Build a one-line summary pointer for each archived entry (keyword + date + where
# to find the full detail) so seo_fixes.md still shows history at a glance.
summary_lines = ["## Archived PUBLISHED entries (full detail in seo_fixes_archive.md)\n"]
for sec in sections_to_archive:
    header_line = sec.split("\n", 1)[0]
    # pull the first "GSC Source:" line if present, for a one-line context hint
    gsc_match = re.search(r"^GSC Source: (.+)$", sec, re.MULTILINE)
    gsc_hint = f" — {gsc_match.group(1)[:100]}" if gsc_match else ""
    summary_lines.append(f"- {header_line.replace('## ', '')}{gsc_hint}")
summary_block = "\n".join(summary_lines) + "\n\n"

new_seo_fixes_content = preamble.rstrip("\n") + "\n\n" + summary_block + section_to_keep

with open(PATH, "w", encoding="utf-8") as f:
    f.write(new_seo_fixes_content)

print(f"\nArchived {len(sections_to_archive)} sections to {ARCHIVE_PATH}")
print(f"Kept 1 most-recent section in {PATH}")
print(f"New seo_fixes.md size: {len(new_seo_fixes_content)} bytes (was {len(content)} bytes)")
