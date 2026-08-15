# Environment Capability Bootstrap Context

| Field | Value |
| --- | --- |
| State | `SEALED / REVISION_01_APPROVED / REVISION_02_OWNER_REVIEW_REQUIRED` |
| Requirement / ADR | `PRD-20260815-024`, `CHG-20260815-024`, `PRD-20260816-025`, `CHG-20260816-025` / `ADR-20260815-013`, `ADR-20260816-014` |
| SPEC | `SPEC-AI-WORKFLOW-ENVIRONMENT-CAPABILITY-BOOTSTRAP-20260815-01M0E2C4B6S8T0R2A4P6D8F0H2` |
| Prior shared Context | `main@2701ed563f26e116db69e8e4fcb84024754c9498` |
| Control owner | Architecture owner / current `main` |

## Confirmed facts

- Johnny and each controlled project are parallel systems. Project-owned Context, PRD, change,
  SPEC, ticket, source, tests, reviews and handoffs remain in the project; control runtime,
  environments, caches, grants and capability evidence remain outside it.
- Git is a core control capability. Docker and build/deploy tools are conditional capabilities
  required only when the current project or ticket needs them.
- Compatible user/project tool versions are preferred. Johnny never silently upgrades,
  downgrades, replaces or globally configures them.
- `CONTROL_PYTHON` is a Johnny-owned pinned Python 3.11 environment with locked control-plane
  dependencies and `mypy --strict`. It is distinct from every project's `PROJECT_PYTHON`.
- Johnny may automatically install only per-user, reversible, Johnny-owned artifacts. Admin,
  global/system changes, EULA acceptance, reboot, login, credential and external-effect work is
  guided and separately approved.
- Side-by-side environments are immutable and keyed by opaque project identity, capability and
  dependency-lock digest. Read-only caches may be shared; writable state is isolated per
  ticket/worktree. Docker names and resources are namespaced.
- Every Johnny-launched process is hard-limited. Windows uses a proved Job Object boundary;
  containers use native Docker limits; build workers receive bounded flags. If the required
  enforcement cannot be proved, launch halts.
- A `LIGHT` plan is capped at the lower of 25% CPU or one core-equivalent, the lower of 25% of
  currently available RAM or 2 GiB, 1 GiB disk/temp, eight processes, zero containers, one
  worker and one lane; it halts when less than 1 GiB RAM is available. `STANDARD` uses the lower
  of 50% CPU or two core-equivalents, the lower of 50% available RAM or 4 GiB, 5 GiB disk/temp,
  24 processes, zero containers, two workers and one lane; it halts below 2 GiB available RAM.
  Only an exact Docker ticket may request a nonzero container count. `HEAVY_APPROVAL` has no
  default values.
- Resource plans are one-shot immutable ticket evidence and do not reset on retry, correction or
  role replacement. Local inference reserves CPU/RAM/GPU/VRAM first. Local training is a
  separately approved heavy mode and cannot run concurrently with Docker, full-suite or other
  heavy ticket work.
- Environment admission has three boundaries: `CONTROL_BOOTSTRAP`, `PROJECT_BASELINE` and
  `TICKET_OVERLAY`. Implementation never installs or changes tools. Drift blocks the affected
  stage and returns to environment planning.
- Install approval and ticket execution authority are different. An event-based `InstallGrant`
  may remain valid for one exact signed/hashed tool artifact with no fixed expiry. Each ticket
  still has one Router receipt at a time; its execution-environment binding uses that same
  receipt and does not create a second receipt.
- Capability evidence is produced and revalidated only at declared boundaries. There is no
  background updater, retry loop, device fingerprint, heartbeat, cron, watchdog or recurring
  environment polling.
- `PROJECT_DETACH` removes only the exact Johnny-owned mapping/state for that project.
  `PLUGIN_UNINSTALL` removes all exact Johnny-owned runtime, tools, cache, grants, evidence and
  receipt bindings. Target projects and foreign/user tools remain untouched.
- Contracts are platform-neutral. Version one supports Windows 10/11 x64 hosts and may use
  Linux Docker containers. Unsupported macOS/Linux host control halts rather than inventing a
  partial compatibility claim.
- This revision provides only a compatibility/resource-reservation adapter for local models. It
  does not download models, train weights, manage datasets or govern model artifacts.

## Boundaries

- No target-project `.johnny`, `.johnny-router`, plugin-specific environment manifest, hook,
  runtime import, CI dependency, submodule, symlink or hidden worktree root.
- No Secret in Router state, receipts, logs or capability evidence. Login uses an official UI,
  device-code or OS credential-store flow and stores only an opaque credential alias.
- No ticket, implementation, installer download, system mutation, login, deployment or other
  external effect is authorized by this draft.
- The root README must explain reuse, guided setup, project detach, plugin uninstall and
  successor freedom before the feature can be considered complete.
