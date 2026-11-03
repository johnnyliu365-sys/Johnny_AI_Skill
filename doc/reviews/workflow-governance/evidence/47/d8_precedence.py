"""D8 (ticket 47 closure revision08): every SPEC under modules/spec/ other than workflow-governance.md
opens with a blockquote precedence note naming CHG-20261103-043, R4-1 and R4-4 within its first five
non-empty lines. Exit 0 when every such SPEC carries the note; 1 otherwise. Run from the repository root."""
import os, re, sys

NOTE = re.compile(r'^>\s*Precedence note.*CHG-20261103-043.*R4-1.*R4-4', re.I)
missing = 0
for name in sorted(os.listdir('modules/spec')):
    if not name.endswith('.md') or name == 'workflow-governance.md':
        continue
    path = 'modules/spec/' + name
    head = [l for l in open(path, encoding='utf-8', errors='replace').read().replace('\r\n', '\n').split('\n') if l.strip()][:5]
    ok = any(NOTE.match(l) for l in head)
    missing += not ok
    print(f'[{"note present" if ok else "NOTE MISSING"}] {path}')
print(f'--- SPECs without the precedence note: {missing}')
sys.exit(0 if missing == 0 else 1)
