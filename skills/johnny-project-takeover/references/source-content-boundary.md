# Source content boundary

Read during implementation and review, including work delegated to a child Agent.
Source code carries product behavior and necessary technical explanation, not the work order.

## Forbidden content

Do not paste or paraphrase owner instructions, dispatch prompts, conversation transcripts,
ticket bodies, acceptance checklists, correction history or workflow directives into source
comments, docstrings, unused constants or string literals. Moving that text to another code
file or encoding it does not make it product source. Tests and temporary review code have
the same boundary; documentation belongs in its target-owned indexed artifact.

Keep necessary technical comments: invariants, algorithm rationale, compatibility limits,
units, concurrency/ownership reasoning and public API documentation. Explain what the code
does and why the technical constraint exists, not who instructed the Agent to write it.
Preserve required license notices. Ordinary domain names containing words such as owner,
ticket or prompt are not themselves violations.

Work instructions are distinct from a product whose explicit behavior processes prompts
or tickets. Such product data needs an approved, dedicated responsibility and location;
it must not be smuggled into unrelated implementation as a comment or incidental string.
Synthetic rejection fixtures must be explicitly scoped test data, never copied live owner
messages or secrets. There is no blanket exception for every string in a test file.

## Admission and review

Implementers inspect the changed source before returning it. Reviewers reject a candidate
that mixes work instructions into source; move the record to its canonical artifact and
retain only the technical explanation needed by future maintainers. Do not erase useful
comments simply to pass a text scan.

An available source-content checker checks the actual candidate diff at its declared
language seam, including comments, docstrings and string literals, and names its violated
rule and location. Its executable predicates and supported languages must be explicit.
Keyword absence cannot prove semantic cleanliness, and arbitrary paraphrases are not
reliably recognized by a finite denylist. Record mechanical coverage separately from the
reviewer's semantic assessment. Until the checker and its integration/host paths are
implemented and qualified, this rule is **review policy**, not a claim of hard enforcement.
