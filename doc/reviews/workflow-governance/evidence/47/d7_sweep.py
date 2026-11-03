"""D7: governance-wide sweep for the two rules Revision 04 retired, every hit classified.

(a) a reviewer who integrates or alone submits; (b) a receipt-bound bridge, live descriptor or
merge-queue file that is mandatory, required or the default for a cross-lifetime handoff.
Exit 0 when no hit is classified LIVE RETIRED RULE; exit 1 otherwise. Run from the repository root.
"""
import re, subprocess, sys

ROOTS = ['skills/', 'modules/spec/', 'Workflow.md', 'CodeReview.md', 'AGENTS.md', 'doc/runbooks/']
PAT_A = r'reviewer[^.|]{0,100}(integrat|submits? (it|the candidate) to)|integrat[^.|]{0,80}reviewer|(only|sole) role that submits'
PAT_B = r'(live descriptor|receipt-bound|PendingDispatchDescriptor|merge-queue file)[^.|]{0,120}(mandatory|required|must|default)|(mandatory|required|must|default)[^.|]{0,120}(live descriptor|receipt-bound|PendingDispatchDescriptor|merge-queue file)'
STATES_RULE = ('integration script', 'R4-4', 'its admission', 'not by the reviewer', 'not the default', 'not required', 'NOT_REQUIRED',
               'until wave 3', 'transitional', 'who is not that candidate', 'never submits', 'is not its reviewer', 'script-run', 'runs by the versioned',
               'run by the versioned', 'R4-1', 'bridge-free', 'never replaced', 'does not require')
DATED = re.compile(r'^\|\s*20\d\d-\d\d-\d\d\s*\|')
QUOTED = ('amended', 'Amendments', 'ARA-01', 'retired', 'said the reviewer', 'earlier wording', 'superseded', 'historical')

def classify(path, text):
    if path.startswith('modules/tickets/') or path.startswith('doc/reviews/'):
        return 'ticket or review record of this line'
    if DATED.match(text.strip()):
        return 'dated signature, approval or revision record'
    if any(q in text for q in QUOTED):
        return 'quoted finding or retired-rule citation'
    if any(k in text for k in STATES_RULE):
        return 'states the Revision 04 rule'
    return 'LIVE RETIRED RULE'

def run(pat):
    r = subprocess.run(['grep', '-rniE', pat] + ROOTS, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return [l for l in r.stdout.splitlines() if l.strip()]

live = 0
for tag, pat in (('a', PAT_A), ('b', PAT_B)):
    print(f'--- pattern ({tag})')
    for l in run(pat):
        m = re.match(r'^([^:]+):(\d+):(.*)$', l)
        if not m:
            continue
        c = classify(m.group(1), m.group(3))
        live += c == 'LIVE RETIRED RULE'
        print(f'[{c}] {l[:220]}')
print(f'--- live retired-rule hits: {live}')
sys.exit(0 if live == 0 else 1)
