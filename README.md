# Johnny AI Skill

Johnny AI Skill is a detachable, user-scoped workflow plugin for taking over a new, inherited, or in-progress software project. It supplies the same two skills to Codex and Claude Code while keeping the target project independent.

It is not a runtime service, MCP server, hook, CI dependency, Git submodule, symlink, package dependency, or source-code import. Removing it therefore never changes how a company project builds, tests, deploys, or runs.

## What is installed

| Skill | Purpose |
| --- | --- |
| `johnny-project-takeover` | Enter Wayfinder, follow the router and workflow, then use the target project's own rules and evidence. |
| `apply-reusable-modules` | Select the smallest suitable `READY` module from `library/MODULE_CATALOG.md`; never copy it automatically. |

The skills share the repository's `Workflow.md`, `Defined_wayfinder.md`, router POC, and module catalog. Only the platform-specific plugin manifests differ; there is one shared `skills/` source of truth.

## Before using it at a company

Install this plugin in your personal Codex or Claude Code user scope, outside the company repository. Then open the company repository normally and invoke the skill in that task.

The target repository remains the authority for its own `AGENTS.md`, `Workflow.md`, security rules, tests, and Git policy. Johnny AI Skill is an external control plane: it helps the agent choose the next safe step, but does not overwrite or add a dependency to the target project.

You need GitHub access that can clone the private repository. Authenticate Git/SSH before installing; do not place a personal access token in a command, config file, or project repository.

## Codex

### Install once

In a personal terminal, not inside the company project:

```powershell
codex plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill --ref main
```

Restart Codex (or refresh its Plugins Directory), find **Johnny AI Skill**, and install `johnny-ai-skill` from the marketplace. No files are copied to the company repository.

### Use in a company project

1. Open the company repository in a new Codex task.
2. Give the takeover instruction:

   ```text
   Use $johnny-project-takeover to take over this project safely.
   ```

3. When implementation could reuse a catalogued capability, give:

   ```text
   Use $apply-reusable-modules to select the smallest safe module set.
   ```

The first skill reads the target project's local instructions first. If they do not establish a workflow, it uses this plugin's workflow as the fallback process.

### Update or remove

```powershell
codex plugin marketplace upgrade johnny-ai-skill
codex plugin marketplace remove johnny-ai-skill
```

Removing the marketplace/plugin removes only the skills and their guidance from your Codex environment. It leaves every company repository untouched.

## Claude Code

Claude Code reads the same root `skills/` directory through `.claude-plugin/plugin.json`; the skills appear under the `johnny-ai-skill` namespace.

### Install once

In a personal terminal, not inside the company project:

```powershell
claude plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill
claude plugin install johnny-ai-skill@johnny-ai-skill --scope user
```

If the private repository cannot be read, first ensure the same user can clone it with Git or SSH. For GitHub CLI authentication, a safe setup is:

```powershell
gh auth login
gh auth setup-git
```

Start a new Claude Code session, or run `/reload-plugins` in an active one.

### Use in a company project

1. Open the company repository with Claude Code as usual.
2. Invoke the project takeover skill:

   ```text
   /johnny-ai-skill:johnny-project-takeover
   ```

3. Invoke module selection only when it is relevant:

   ```text
   /johnny-ai-skill:apply-reusable-modules
   ```

You can add the project goal after either command. Claude Code receives the shared skill instructions, then must respect the company repository's own rules before acting.

### Update, test, or remove

```powershell
claude plugin marketplace update johnny-ai-skill
claude plugin update johnny-ai-skill@johnny-ai-skill
claude plugin uninstall johnny-ai-skill@johnny-ai-skill --scope user
claude plugin marketplace remove johnny-ai-skill --scope user
```

For a local smoke test of a clone of this repository, run:

```powershell
claude plugin validate .
claude --plugin-dir .
```

`plugin.json` deliberately has no Claude version field. Claude Code can therefore use the Git commit SHA as the installed version, so a new commit is visible as an update without a duplicate version change.

## Detach guarantee

The plugin is installed per user, not committed into the target project. To detach completely, run the relevant removal command above and close/reopen the agent session. The company project keeps its exact checkout, source, dependencies, CI, deployment configuration, and Git history; only the optional workflow skills are gone.
