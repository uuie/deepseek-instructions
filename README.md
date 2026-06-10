# moe-execution

**MoE-aware coding skill + code-assistant instructions for Mixture-of-Experts models**
(Qwen, GLM, DeepSeek, Mixtral, local MoE).

Most "weak model" coding pain with MoE models isn't low intelligence — it's **unstable
expert routing**. In an MoE model a lightweight router picks a small subset of "experts"
for each token based on your *phrasing*. Paraphrase a concept, mix domains, or drift your
wording, and a *different* set of experts takes over mid-task — so it forgets decisions,
produces locally-correct-but-globally-broken edits, and follows instructions
inconsistently.

This repo gives you three layers that fix that:

1. **Code Assistant Instructions** — an always-on block that re-anchors routing every turn
   (role + canonical vocabulary + one-domain-per-turn + map-before-edit + verify).
2. **`moe-execution` skill** — on-demand depth: routing stabilization, role-anchor table for
   software-dev concerns, state externalization (impact maps, plan files), and a done gate.
3. **`workflow-gate` skill** — workflow bootstrap (`workflow-gate:init`) and mandatory
   interface blast-radius discipline (`workflow-gate:impact-analysis`), then handoff to
   `moe-execution` for execution.

Recommended execution path (non-init):
1. planning (`brainstorming` / `writing-plans`)
2. `workflow-gate:impact-analysis` for interface-level changes
3. `moe-execution` for implementation/refactor/debug

## Why MoE changes the game

| Symptom | MoE root cause | Fix in this repo |
|---|---|---|
| "Lost the plot" mid-task | Wording drift re-routes to different experts | Canonical vocabulary, re-anchoring |
| Locally-right, globally-broken edits | Routing is per-token; no expert sees the whole task | MAP dependents, persist plan to file |
| Inconsistent instruction following | Paraphrasing activates different experts | Stable, structured prompt shape |
| Weaker than expected on a domain | Wrong experts activated | Front-loaded role + tech keywords |

> Works with any MoE model. DeepSeek is a common example, but the same routing dynamics
> apply to Qwen, GLM, Mixtral, Llama-4, and local MoE builds.

## Install

### Claude Code (plugin)

```
/plugin marketplace add uuie/deepseek-instructions
/plugin install moe-execution@moe-instructions
```

> The GitHub repo is currently named `deepseek-instructions`; the marketplace it exposes is
> `moe-instructions`. If you rename the repo, update the `marketplace add` path accordingly.

Then add the always-on layer to your `~/.claude/CLAUDE.md`:

```
@<path-to-clone>/instructions/code-assistant-instructions.md
```

…or copy the block from
[`instructions/code-assistant-instructions.md`](instructions/code-assistant-instructions.md)
directly into your `CLAUDE.md`.

### Any other agent (plain files)

This repo works without the plugin system. Copy the instructions block into your agent's
persistent instruction file and (optionally) the skill into its skills directory:

- Instructions → see the mapping table in
  [`instructions/code-assistant-instructions.md`](instructions/code-assistant-instructions.md)
  (Copilot CLI, Gemini CLI, Codex/`AGENTS.md`, Cursor).
- Skill → copy [`skills/moe-execution/`](skills/moe-execution) into your agent's skills folder
  (e.g. `~/.claude/skills/`).

## What's inside

```
.claude-plugin/
  marketplace.json          # marketplace manifest (for `/plugin marketplace add`)
  plugin.json               # plugin manifest (registers the skill)
skills/
  moe-execution/
    SKILL.md                # on-demand MoE execution skill
  workflow-gate/
    SKILL.md                # init + impact-analysis workflow skill
    scripts/
      init_engineering_workflow.py
instructions/
  code-assistant-instructions.md   # portable always-on block + per-agent mappings
```

## The core idea in one line

> You can't make the experts smarter — but you *can* keep the **right** experts
> consistently active, and write down the global state they can't hold.

## License

MIT — see [LICENSE](LICENSE).
