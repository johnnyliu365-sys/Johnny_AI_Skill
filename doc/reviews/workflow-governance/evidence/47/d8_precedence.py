"""D8 (ticket 47 closure revision09): every historical SPEC under modules/spec/ (every .md except
workflow-governance.md, the SPEC template TEMPLATE.md and the index README.md) and every dated handover
runbook doc/runbooks/handover-*.md opens with a blockquote precedence note naming CHG-20261103-043, R4-1
and R4-4 within its first five non-empty lines; the template and the index carry no such note.
Exit 0 when every covered file carries the note and the two excluded files do not; 1 otherwise.
Run from the repository root."""
import glob, os, re, sys

NOTE = re.compile(r'^>\s*Precedence note.*CHG-20261103-043.*R4-1.*R4-4', re.I)
EXCLUDED = ('modules/spec/workflow-governance.md', 'modules/spec/TEMPLATE.md', 'modules/spec/README.md')

def has_note(path):
    text = open(path, encoding='utf-8', errors='replace').read().replace('\r\n', '\n')
    head = [l for l in text.split('\n') if l.strip()][:5]
    return any(NOTE.match(l) for l in head), 'Precedence note (`CHG-20261103-043`)' in text

covered = sorted(p.replace('\\', '/') for p in glob.glob('modules/spec/*.md') if p.replace('\\', '/') not in EXCLUDED)
covered += sorted(p.replace('\\', '/') for p in glob.glob('doc/runbooks/handover-*.md'))
bad = 0
for path in covered:
    ok, _ = has_note(path)
    bad += not ok
    print(f'[{"note present" if ok else "NOTE MISSING"}] {path}')
for path in ('modules/spec/TEMPLATE.md', 'modules/spec/README.md'):
    _, anywhere = has_note(path)
    bad += anywhere
    print(f'[{"no note, as required" if not anywhere else "NOTE PRESENT BUT EXCLUDED"}] {path}')
print(f'--- defects: {bad} (covered files: {len(covered)})')
sys.exit(0 if bad == 0 else 1)
