ACTION_REQUIRED: IMPLEMENT
dispatch_ref: calc-01-subtract-c1
registry_commit: 3e0fb3adbae9153f867ef956591b2b460ded30e8
correction_ref: doc/reviews/calc/01-subtract-code-review.md
ticket: modules/tickets/calc/01-subtract.md
receipt: doc/handoffs/2026/governance/receipts/calc-01-subtract-c1.md
owner_task: calc-subtract
preflight:
  - tool: "pytest"
    start: ["C:/Temp/claude/jas-venv/Scripts/python.exe", "-m", "pytest", "--version"]
    probe: ["C:/Temp/claude/jas-venv/Scripts/python.exe", "-m", "pytest", "--version"]
    expect: "pytest"
  - tool: "mypy"
    start: ["C:/Temp/claude/jas-venv/Scripts/python.exe", "-m", "mypy", "--version"]
    probe: ["C:/Temp/claude/jas-venv/Scripts/python.exe", "-m", "mypy", "--version"]
    expect: "mypy"
