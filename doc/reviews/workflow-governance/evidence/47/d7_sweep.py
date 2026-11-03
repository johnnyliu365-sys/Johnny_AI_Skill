"""D7 (ticket 47 closure revision07): governance-wide sweep for the rules Revision 04 retired, on paragraph-joined units.

Units: a Markdown table row, a list item joined with its indented continuation lines, a heading, a
line inside a fenced block (code and diagrams are scanned, not skipped), or a paragraph joined
across its wrapped lines. Patterns (every match in a unit is classified, not only the first):
  a1  a reviewer who integrates
  a2  a reviewer who submits
  a3  a fixed integrator role (owns guarded integration, 整合負責人)
  b1  a receipt-bound bridge, live or pending descriptor or merge-queue file that is mandatory, required, kept,
      retained, reserved, bound, the only source or the default
  b2  a cross-lifetime handoff that requires, keeps, retains, binds or is only served by controls
  c   (Chinese) a reviewer who integrates
  d   (Chinese) a descriptor, bridge or receipt-bound route that is mandatory, the default or the only one
  e   a dispatch described as carrying or bound to a descriptor
A match is permitted only when (1) the sentence that contains it (split at '.', ';', '|', '。' and
'；') states the Revision 04 rule with a pattern-specific, word-bounded marker, (2) the unit is a
dated record row or sits under an Amendments, Revision Signatures, Approval Record or Revision
record heading, (3) the file is a ticket or review record of this line, or (4) for patterns b1, b2,
d and e only, the file opens with a blockquote scope note ("> Scope note") within its first five
non-empty lines saying the route is not the default (R4-1), which marks a document that describes
the bridge's own mechanics. Everything else is LIVE RETIRED RULE. Exit 0 when none; 1 otherwise.
Run from the repository root with `python -I -X utf8`.
"""
import os, re, sys

ROOTS = ['skills', 'modules/spec', 'Workflow.md', 'CodeReview.md', 'AGENTS.md', 'doc/runbooks', 'template']
NOUN = r'(live[- ]descriptor|pending descriptor|dispatch descriptor|its descriptor|receipt-bound|PendingDispatchDescriptor|merge-queue file|durable bridge|the bridge\b)'
VERB = r'\b(mandatory|required|requires?|must|default|keeps?|retains?|reserved|bound|only)\b'
B_EXEMPT = (r'\bR4-1\b', r'not the default', r'\bNOT_REQUIRED\b', r'\bnot required\b', r'does not (consume|require)', r'bridge-free',
            r'until (it retires|wave 3)', r'no receipt, descriptor', r'must not halt', r'is `NOT_REQUIRED`', r'needs no bridge',
            r'bridge (route|path)', r'transitional', r'過渡', r'\bneither\b', r'requires? no\b', r'nor requires?', r'must not\b', r'\boptional\b')
PATTERNS = {
    'a1 reviewer integrates': (
        re.compile(r'reviewers?\b[^.;|]{0,240}\bintegrat\w*|\bintegrat\w*[^.;|]{0,160}\breviewers?\b', re.I),
        (r'\bR4-4\b', r'integration script', r'not by the reviewer', r'never the reviewer', r'整合腳本')),
    'a2 reviewer submits': (
        re.compile(r'reviewers?\b[^.;|]{0,240}\bsubmi(t|ts|ssion)\b', re.I),
        (r'never submits', r'who is not (that candidate|its reviewer)', r'is not its reviewer', r'differs from', r'not the reviewer', r'superseded')),
    'a3 fixed integrator role': (
        re.compile(r'\b(owns?|owner of|responsible for)\b[^.;|]{0,120}\bguarded integration\b|整合負責人|固定整合者', re.I),
        (r'integration script', r'整合腳本', r'不指定固定整合者', r'must not be assumed', r'no fixed integrator', r'by whoever holds budget')),
    'b1 bridge required or default': (
        re.compile(NOUN + r'[^.;|]{0,160}' + VERB + r'|' + VERB + r'[^.;|]{0,160}' + NOUN, re.I),
        B_EXEMPT),
    'b2 cross-lifetime requires controls': (
        re.compile(r'cross-lifetime[^.;|]{0,160}' + VERB + r'|' + VERB + r'[^.;|]{0,160}cross-lifetime', re.I),
        B_EXEMPT),
    'c 審閱者整合 (zh)': (
        re.compile(r'(審閱者|審查者|reviewer)[^。；|]{0,80}整合|整合[^。；|]{0,60}(審閱者|審查者)'),
        (r'整合腳本', r'\bR4-4\b', r'不是|不由|不得', r'integration script')),
    'd 過渡路徑為預設 (zh)': (
        re.compile(r'(descriptor|bridge|受據綁定|receipt-bound)[^。；|]{0,80}(必須|預設|唯一|保留|僅)|(必須|預設|唯一)[^。；|]{0,80}(descriptor|bridge|受據綁定|receipt-bound)'),
        (r'不是預設', r'不再是預設', r'過渡', r'\bR4-1\b', r'退場', r'僅限過渡')),
    'e dispatch carries a descriptor': (
        re.compile(r'dispatch[^.;。；]{0,100}\bdescriptor\b|\bdescriptor\b[^.;。；]{0,100}dispatch', re.I),
        B_EXEMPT + (r'live descriptor 是', r'僅限')),
}
DATED = re.compile(r'^\|\s*20\d\d-\d\d-\d\d\s*\|')
SCOPE_NOTE = re.compile(r'^>\s*Scope note.*(not the default[^\n]{0,160}R4-1|R4-1[^\n]{0,160}not the default)', re.I)
RECORD_SECTIONS = ('amendments', 'revision signatures', 'approval record', 'revision record')
ITEM = re.compile(r'^\s*([-*]|\d+\.)\s|^\s*\|')
SEPS = '.;|。；'

def read(path):
    return open(path, encoding='utf-8', errors='replace').read().replace('\r\n', '\n')

def scoped(text):
    head = [l for l in text.split('\n') if l.strip()][:5]
    return any(SCOPE_NOTE.match(l) for l in head)

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
            flush(); out.append((n, line.strip(), section)); continue
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

def sentence_of(unit, m):
    lo = max([unit.rfind(c, 0, m.start()) for c in SEPS] + [-1]) + 1
    hi = min([i for i in (unit.find(c, m.end()) for c in SEPS) if i != -1] + [len(unit)])
    return unit[lo:hi]

live = 0
for path in sorted(files()):
    text = read(path)
    record = path.startswith('modules/tickets/') or path.startswith('doc/reviews/')
    bridge_doc = scoped(text)
    for start, unit, section in units(text):
        for name, (pat, exempt) in PATTERNS.items():
            seen = set()
            for m in pat.finditer(unit):
                sentence = sentence_of(unit, m)
                if sentence in seen:
                    continue
                seen.add(sentence)
                if record:
                    cls = 'ticket or review record of this line'
                elif DATED.match(unit):
                    cls = 'dated signature, approval or revision record'
                elif section.lower().startswith(RECORD_SECTIONS):
                    cls = 'amendments or signature table'
                elif any(re.search(e, sentence, re.I) for e in exempt):
                    cls = 'states the Revision 04 rule'
                elif name[0] in 'bde' and bridge_doc:
                    cls = 'bridge-internal document with a header scope note (R4-1)'
                else:
                    cls = 'LIVE RETIRED RULE'
                live += cls == 'LIVE RETIRED RULE'
                print(f'[{cls}] ({name}) {path}:{start}: {sentence.strip()[:220]}')
print(f'--- live retired-rule hits: {live}')
sys.exit(0 if live == 0 else 1)
