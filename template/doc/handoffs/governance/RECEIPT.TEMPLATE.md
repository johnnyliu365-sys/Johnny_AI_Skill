# Receipt: <what this receipt proves>

A receipt holds one run cell for every command the work ran, and one statement cell for every
choice made where the work was silent. Copy this file to the receipt path named in the ticket's
state row, repeat the run cell once per command, and replace every placeholder below before any
gate reads it. A placeholder left in place is a defect.

| Placeholder | Replaced by |
| --- | --- |
| `<cell>` | the cell name, the same text in the heading and in the `cell:` line, unique in the receipt |
| `<candidate-sha>` | the full 40-digit lower-case sha of the committed candidate every cell ran at |
| `<tool-path>` | the repository-relative path of a tool file the cell ran, with forward-slash separators; one line per tool file |
| `<tool-sha256>` | the 64-digit lower-case sha256 of that file's blob at the candidate |
| `<capture-path>` | the capture file's path relative to the evidence root |
| `<exit-codes>` | the exit codes in capture order, comma-separated; each is also a line `exit=N` alone in the capture |
| `<capture-lines>` | the capture file's lines, byte for byte, with LF line ends only |
| `<statement-text>` | one or more lines saying what was chosen or left undone; no `capture:`, `exit:` or fenced block |

## <cell>
cell: <cell>
candidate: <candidate-sha>
tool_digest:
- <tool-path>=<tool-sha256>
capture: <capture-path>
exit: <exit-codes>

````
<capture-lines>
````

## STATEMENT
cell: STATEMENT

<statement-text>
