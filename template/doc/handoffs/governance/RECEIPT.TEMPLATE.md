# Receipt: <what this receipt proves>

A receipt holds one run cell for every command the work ran, and one statement cell for every
choice made where the work was silent. Copy this file to the receipt path named in the ticket's
state row, repeat the run cell once per command, and replace every placeholder below before any
gate reads it. A placeholder left in place is a defect.

A `USAGE` cell records the token use of one seat. The control plane appends one per seat, after the
seat returns, below the last cell of the receipt; the evidence gate checks its form and never
requires it, and a `USAGE` cell has no capture, exit, candidate, tool_digest or fence. The block
below is the form of one cell, to be placed under the heading `## USAGE <seat>`; it is not part of
the receipt body, so a receipt that has no seat to record yet simply holds none.

````
cell: USAGE
seat: <seat>
profile: <profile>
model: <model>
effort: <effort>
input_tokens: <input-tokens>
cache_write_tokens: <cache-write-tokens>
cache_read_tokens: <cache-read-tokens>
output_tokens: <output-tokens>
source: <usage-source>
````

The `STATEMENT` cell begins with two lines before any prose: `return:` with one of `COMPLETED`,
`BLOCKED` or `CHANGE_DETECTED`, and `items:` followed by one `- ` line per item, none for
`COMPLETED`. The template shows `return: COMPLETED`; replace the word when the work is not completed.

| Placeholder | Replaced by |
| --- | --- |
| `<cell>` | the cell name, the same text in the heading and in the `cell:` line, unique in the receipt |
| `<candidate-sha>` | the full 40-digit lower-case sha of the committed candidate every cell ran at |
| `<tool-path>` | the repository-relative path of a tool file the cell ran, with forward-slash separators; one line per tool file |
| `<tool-sha256>` | the 64-digit lower-case sha256 of that file's blob at the candidate |
| `<capture-path>` | the capture file's path relative to the evidence root |
| `<exit-codes>` | the exit codes in capture order, comma-separated; each is also a line `exit=N` alone in the capture |
| `<capture-lines>` | the capture file's lines, byte for byte, with LF line ends only |
| `<seat>` | the seat id, `seat:` then the profile, a slash and the run id, the same text in the `USAGE` heading and the `seat:` line, unique in the receipt |
| `<profile>` | the semantic profile reference of the seat, the one `<seat>` names |
| `<model>` | the model the host reports for the seat: one item of `[A-Za-z0-9][A-Za-z0-9._-]*`, or items joined by `,` with no blanks and no repeats |
| `<effort>` | the effort the host reports for the seat, in the same form as `<model>`; the line is optional, and a receipt without it is read as `UNRECORDED` |
| `<input-tokens>` | the seat's input tokens, an integer >= 0 written without a sign or a leading zero |
| `<cache-write-tokens>` | the seat's cache write tokens, an integer in the same form |
| `<cache-read-tokens>` | the seat's cache read tokens, an integer in the same form |
| `<output-tokens>` | the seat's output tokens, an integer in the same form |
| `<usage-source>` | where the numbers come from, one line, for example `host transcript usage, summed per message` |
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
return: COMPLETED
items:

<statement-text>
