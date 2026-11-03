"""Ticket 48 P9 receipt check (closure revision05).

usage: python receipt_check.py <RETURN.md> <repo>

Reads a seat receipt whose run cells are '## <name>' sections holding the lines 'cell:', 'candidate:',
'tool_digest:' (followed by '- <path>=<sha256>' lines), 'capture:' and 'exit:', then the raw capture in a
four-backtick fence. A section whose 'cell:' value is STATEMENT is informational and skipped. For every
run cell it checks: the three gate scripts are listed in tool_digest and each digest equals the sha256 of
'git show <candidate>:<path>' in <repo>; the capture file named in 'capture:' exists next to the receipt and
holds no CR byte; the fenced block equals the capture byte for byte (the block is the lines between the
fences joined with LF plus a final LF). It also checks that exactly one cell is named F1.
Exit 0 when every check passes; 1 when any check fails (each failure printed); 2 when git cannot serve a
digest query or the receipt or a capture cannot be read; 3 on bad arguments.
"""
import hashlib, os, re, subprocess, sys

SCRIPTS = ('skills/johnny-project-takeover/scripts/dispatch_lint.py',
           'skills/johnny-project-takeover/scripts/receipt_fence_check.py',
           'skills/johnny-project-takeover/scripts/index_pins.py')
FENCE = '````'


class ToolFault(Exception):
    pass


def git_blob_sha256(repo: str, rev: str, path: str) -> str:
    r = subprocess.run(['git', '-C', repo, 'show', f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise ToolFault(f'git show {rev}:{path} failed: {r.stderr.decode("utf-8", "replace").strip()}')
    return hashlib.sha256(r.stdout).hexdigest()


def sections(text: str) -> list[tuple[str, list[str]]]:
    out: list[tuple[str, list[str]]] = []
    name, buf, in_fence = None, [], False
    for line in text.split('\n'):
        if line.strip() == FENCE:
            in_fence = not in_fence
        if line.startswith('## ') and not in_fence:
            if name is not None:
                out.append((name, buf))
            name, buf = line[3:].strip(), []
            continue
        if name is not None:
            buf.append(line)
    if name is not None:
        out.append((name, buf))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: receipt_check.py <RETURN.md> <repo>', file=sys.stderr)
        return 3
    receipt, repo = argv
    try:
        raw = open(receipt, 'rb').read()
    except OSError as e:
        print(f'tool fault: cannot read {receipt}: {e}', file=sys.stderr)
        return 2
    failures: list[str] = []
    if b'\r' in raw:
        failures.append('receipt contains CR bytes')
    text = raw.decode('utf-8', 'replace').replace('\r\n', '\n')
    base = os.path.dirname(os.path.abspath(receipt))
    f1 = 0
    try:
        for name, body in sections(text):
            fields: dict[str, str] = {}
            digests: dict[str, str] = {}
            fence: list[str] | None = None
            collecting = False
            for line in body:
                if line.strip() == FENCE:
                    if fence is None:
                        fence, collecting = [], True
                        continue
                    if collecting:
                        collecting = False
                        continue
                if collecting:
                    fence.append(line)
                    continue
                m = re.match(r'^(cell|candidate|capture|exit):\s*(.*)$', line)
                if m and m.group(1) not in fields:
                    fields[m.group(1)] = m.group(2).strip()
                m = re.match(r'^-\s*(\S+?)=([0-9a-f]{64})\s*$', line)
                if m:
                    digests[m.group(1)] = m.group(2)
            if 'cell' not in fields:
                continue
            cell = fields['cell']
            if cell.upper() == 'STATEMENT':
                print(f'[statement] {name}')
                continue
            if cell == 'F1':
                f1 += 1
            bad: list[str] = []
            for key in ('candidate', 'capture', 'exit'):
                if not fields.get(key):
                    bad.append(f'missing field {key}')
            for path in SCRIPTS:
                if path not in digests:
                    bad.append(f'tool_digest lacks {path}')
                elif fields.get('candidate'):
                    actual = git_blob_sha256(repo, fields['candidate'], path)
                    if actual != digests[path]:
                        bad.append(f'tool_digest of {path} is {digests[path]}, git show gives {actual}')
            if fence is None or collecting:
                bad.append('no closed four-backtick raw block')
            cap_name = fields.get('capture', '').split()[0] if fields.get('capture') else ''
            if cap_name:
                cap_path = os.path.join(base, cap_name)
                try:
                    cap = open(cap_path, 'rb').read()
                except OSError as e:
                    raise ToolFault(f'cannot read capture {cap_path}: {e}')
                if b'\r' in cap:
                    bad.append(f'capture {cap_name} contains {cap.count(chr(13).encode())} CR bytes')
                if fence is not None and not collecting:
                    block = ('\n'.join(fence) + '\n').encode('utf-8')
                    if block != cap:
                        bad.append(f'raw block differs from capture {cap_name} (block {len(block)} bytes, capture {len(cap)} bytes)')
            status = 'ok' if not bad else 'FAIL'
            print(f'[{status}] {name} (cell {cell})' + ''.join(f'\n    - {b}' for b in bad))
            failures += [f'{name}: {b}' for b in bad]
    except ToolFault as e:
        print(f'tool fault: {e}', file=sys.stderr)
        return 2
    if f1 != 1:
        failures.append(f'expected exactly one F1 cell, found {f1}')
        print(f'[FAIL] F1 cells: {f1}')
    print(f'--- receipt defects: {len(failures)}')
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
