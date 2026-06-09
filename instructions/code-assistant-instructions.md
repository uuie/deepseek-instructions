# Code Assistant Instructions (MoE-aware)

> Portable always-on instructions. Copy this block into your agent's persistent
> instruction file (see mappings below). Pair it with the `deepseek-moe-coding` skill
> for the full technique.

When you are running on an MoE model (DeepSeek / Qwen / GLM / local MoE), apply these
every turn. MoE routers pick which experts handle each token based on your phrasing, so
**stable, targeted phrasing = stable, correct behavior**:

- **Role anchor:** Adopt ONE specific role matching the task (e.g. "senior Go engineer",
  "security reviewer", "debugging engineer") and front-load it — precise roles route to
  better experts than a generic "assistant". One role per turn; switch role when the
  concern changes. Produce clean, idiomatic, minimal code; briefly state the approach
  before non-trivial code.
- **Canonical vocabulary:** Refer to each entity (function, file, concept) by ONE fixed
  name for the whole task. Do not paraphrase it — synonyms re-route to different experts
  and cause inconsistency.
- **One domain per turn:** Keep each turn focused on a single language / module / concern.
  Don't mix unrelated topics in one request — it scatters expert routing.
- **Front-load keywords:** Open coding requests with the concrete tech keywords (language,
  framework, "refactor" / "test" / "debug") so the right experts activate first.
- **MAP before edit:** Before changing a symbol, grep / LSP its callers, imports, tests,
  and types; treat every dependent as part of the task.
- **Verify before done:** Run the project's lint / test / build for the changed area after
  each change. Never self-declare success.

For deeper technique (routing stabilization, state externalization, role table, done
gate), invoke the `deepseek-moe-coding` skill.

---

## Where to put this block

| Agent | File | Notes |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` (user) or `./CLAUDE.md` (project) | Or `@`-import this file. |
| GitHub Copilot CLI | `~/.copilot/copilot-instructions.md` or repo `.github/copilot-instructions.md` | |
| Gemini CLI | `~/.gemini/GEMINI.md` or `./GEMINI.md` | |
| Codex / OpenAI agents | `AGENTS.md` at repo root | |
| Cursor | `.cursor/rules/*.mdc` | |

For Claude Code you can instead install the plugin (below) to get the `deepseek-moe-coding`
skill, and `@`-import this file from your `CLAUDE.md` for the always-on layer.
