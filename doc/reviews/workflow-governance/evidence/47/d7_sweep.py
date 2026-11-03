"""D7 (ticket 47 closure revision06): governance-wide sweep for the rules Revision 04 retired, on paragraph-joined units.

Units: a Markdown table row, a list item joined with its indented continuation lines, a heading, or a
paragraph joined across its wrapped lines (fenced code is skipped). Patterns:
  a1  a reviewer who integrates
  a2  a reviewer who submits
  a3  a fixed integrator role (owns guarded integration, 整合負責人)
  b1  a receipt-bound bridge, live descriptor or merge-queue file that is mandatory, required,
      kept, retained, reserved or the default
  b2  a cross-lifetime handoff that requires, keeps or retains controls, or controls required only
      for a cross-lifetime handoff
  c   (Chinese) a reviewer who integrates
  d   (Chinese) a descriptor, bridge or receipt-bound route that is mandatory, the default or the only one
A hit is permitted only when (1) the sentence that contains it (split at '.', ';', '|', '。' and '；') states the Revision 04 rule with a pattern-specific, word-bounded marker, (2) the unit is a dated record row or sits under an Amendments, Revision
Signatures, Approval Record or Revision record heading, (3) the file is a ticket or review record of
this line, or (4) for patterns b1 and b2 only, the file's first 40 lines carry a scope note saying
the route is not the default (R4-1), which marks a document that describes the bridge's own
mechanics. Everything else is LIVE RETIRED RULE. Exit 0 when none; 1 otherwise. Run from the
repository root.
"""
import os, re, sys

ROOTS = ['skills', 'modules/spec', 'Workflow.md', 'CodeReview.md', 'AGENTS.md', 'doc/runbooks', 'template']
B_EXEMPT = (r'\bR4-1\b', r'not the default', r'\bNOT_REQUIRED\b', r'\bnot required\b', r'does not (consume|require)', r'bridge-free',
            r'until (it retires|wave 3)', r'no receipt, descriptor', r'must not halt', r'is `NOT_REQUIRED`', r'needs no bridge')
PATTERNS = {
    'a1 reviewer integrates': (
        re.compile(r'reviewer\b[^.;|]{0,240}\bintegrat\w*|\bintegrat\w*[^.;|]{0,160}\breviewer\b', re.I),
        (r'\bR4-4\b', r'integration script', r'not by the reviewer', r'never the reviewer', r'整合腳本')),
    'a2 reviewer submits': (
        re.compile(r'reviewer\b[^.;|]{0,240}\bsubmi(t|ts|ssion)\b', re.I),
        (r'never submits', r'who is not (that candidate|its reviewer)', r'is not its reviewer', r'differs from', r'not the reviewer')),
    'a3 fixed integrator role': (
        re.compile(r'\b(owns?|owner of|responsible for)\b[^.;|]{0,120}\bguarded integration\b|整合負責人|固定整合者', re.I),
        (r'\bR4-4\b', r'integration script', r'整合腳本', r'不指定固定整合者', r'must not be assumed')),
    'b1 bridge required or default': (
        re.compile(r'(live[- ]descriptor|receipt-bound|PendingDispatchDescriptor|merge-queue file|durable bridge)[^.;|]{0,160}\b(mandatory|required|requires|must|default|keeps?|retains?|reserved|only)\b'
                   r'|\b(mandatory|required|requires|must|default|keeps?|retains?|reserved)\b[^.;|]{0,160}(live[- ]descriptor|receipt-bound|PendingDispatchDescriptor|merge-queue file|durable bridge)', re.I),
        B_EXEMPT),
    'c 審閱者整合 (zh)': (
        re.compile(r'(審閱者|審查者|reviewer)[^。；|]{0,80}整合|整合[^。；|]{0,60}(審閱者|審查者)'),
        (r'整合腳本', r'\bR4-4\b', r'不是|不由|不得', r'integration script')),
    'd 過渡路徑為預設 (zh)': (
        re.compile(r'(descriptor|bridge|受據綁定|receipt-bound)[^。；|]{0,80}(必須|預設|唯一|保留)|(必須|預設|唯一)[^。；|]{0,80}(descriptor|bridge|受據綁定|receipt-bound)'),
        (r'不是預設', r'不再是預設', r'過渡', r'\bR4-1\b', r'退場')),
    'b2 cross-lifetime requires controls': (
        re.compile(r'cross-lifetime[^.|]{0,160}\b(required|requires|mandatory|retains?|keeps?|must)\b|\b(required|requires|mandatory|retains?|keeps?)\b[^.|]{0,160}cross-lifetime', re.I),
        B_EXEMPT),
}
DATED = re.compile(r'^\|\s*20\d\d-\d\d-\d\d\s*\|')
SCOPE_NOTE = re.compile(r'not the default[^\n]{0,120}R4-1|R4-1[^\n]{0,120}not the default')
RECORD_SECTIONS = ('amendments', 'revision signatures', 'approval record', 'revision record')
ITEM = re.compile(r'^\s*([-*]|\d+\.)\s|^\s*\|')

def read(path):
    return open(path, encoding='utf-8', errors='replace').read().replace('\r\n', '\n')

def units(text):
    out, buf, start, kind, in_fence, section = [], [], 0, '', False, ''
    def flush():
        nonlocal buf, kind
        if buf:
            out.append((start, ' '.join(l.strip() for l in buf), section))
        buf, kind = [], ''
    for n, line in enumerate(text.split('\n'), 1):
        if line.strip().startswith('```'):
            flush(); in_fence = not in_fence; continue
        if in_fence:
            continue
        if line.startswith('#'):
            flush(); section = line.strip('# ').strip(); out.append((n, line.strip(), section)); continue
        if not line.strip():
            flush(); continue
        if ITEM.match(line):
            flush(); buf, start, kind = [line], n, 'item'; continue
        if kind == 'item' and line[:1].isspace():
            buf.append(line); continue
        if kind == 'item':
            flush()
        if not buf:
            start, kind = n, 'para'
        buf.append(line)
    flush()
    return out

def files():
    for root in ROOTS:
        if os.path.isfile(root):
            yield root
        else:
            for d, _, fs in os.walk(root):
                for f in fs:
                    if f.endswith('.md'):
                        yield os.path.join(d, f).replace('\\', '/')

live = 0
for path in sorted(files()):
    text = read(path)
    record = path.startswith('modules/tickets/') or path.startswith('doc/reviews/')
    scoped = bool(SCOPE_NOTE.search('\n'.join(text.split('\n')[:40])))
    for start, unit, section in units(text):
        for name, (pat, exempt) in PATTERNS.items():
            m = pat.search(unit)
            if not m:
                continue
            seps = '.;|。；'
            lo = max([unit.rfind(c, 0, m.start()) for c in seps] + [-1]) + 1
            hi = min([i for i in (unit.find(c, m.end()) for c in seps) if i != -1] + [len(unit)])
            sentence = unit[lo:hi]
            if record:
                cls = 'ticket or review record of this line'
            elif DATED.match(unit):
                cls = 'dated signature, approval or revision record'
            elif section.lower().startswith(RECORD_SECTIONS):
                cls = 'amendments or signature table'
            elif any(re.search(e, sentence, re.I) for e in exempt):
                cls = 'states the Revision 04 rule'
            elif name[0] in 'bd' and scoped:
                cls = 'bridge-internal document scoped by its header note (R4-1)'
            else:
                cls = 'LIVE RETIRED RULE'
            live += cls == 'LIVE RETIRED RULE'
            print(f'[{cls}] ({name}) {path}:{start}: {unit[:200]}')
print(f'--- live retired-rule hits: {live}')
sys.exit(0 if live == 0 else 1)
