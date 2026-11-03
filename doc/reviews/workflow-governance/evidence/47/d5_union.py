"""D5: every path in a1cb6c1..HEAD tagged with the tickets whose johnny-boundary covers it (read from the tickets at HEAD)."""
import re, subprocess, os, sys
# run from the repository root
def boundary(ticket):
    text = open(f'modules/tickets/workflow-governance/{ticket}', encoding='utf-8').read()
    block = text.split('```johnny-boundary', 1)[1].split('```', 1)[0]
    rules = {'modify': [], 'create': [], 'forbid': []}
    for line in block.splitlines():
        m = re.match(r'\s*(modify|create|delete|forbid)\s*=\s*(\S+)', line)
        if m and m.group(1) in rules: rules[m.group(1)].append(m.group(2))
    return rules
def matches(path, rule):
    if rule.endswith('/'): return path.startswith(rule)
    if '*' in rule:
        pat = '^' + re.escape(rule).replace(r'\*', '[^/]*') + '$'
        return re.match(pat, path) is not None
    return path == rule
T = {'47': boundary('47-gates-first-governance-rewrite.md'), '48': boundary('48-port-gate-scripts.md'), '49': boundary('49-wording-drift-and-vendor-names.md')}
paths = subprocess.run(['git', 'diff', '--name-only', 'a1cb6c1..HEAD'], capture_output=True, text=True).stdout.split()
outside = 0
for p in paths:
    tags = [t for t, r in T.items() if any(matches(p, x) for x in r['modify'] + r['create']) and not any(matches(p, x) for x in r['forbid'])]
    tag = '+'.join(tags) if tags else 'NONE'
    outside += not tags
    print(f'[{tag}] {p}')
print(f'--- paths: {len(paths)}; outside every boundary: {outside}')
sys.exit(0 if outside == 0 else 1)
