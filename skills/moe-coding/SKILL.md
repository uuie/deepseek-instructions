---
name: moe-coding
description: Use for any coding, refactoring, or debugging task when running on a Mixture-of-Experts (MoE) model (Qwen, GLM, DeepSeek, Mixtral, local MoE). Stabilizes expert routing through specific role anchors, consistent vocabulary, keyword anchoring, single-domain turns, and structured prompts, then enforces impact-mapping and per-change verification. Compensates for MoE routing fragility that causes inconsistent instruction-following and locally-correct-but-globally-broken edits.
---

# MoE Coding Discipline

## The root cause (read this first)

Models such as Qwen, GLM, DeepSeek, Mixtral, and many local models are
**Mixture-of-Experts (MoE)**. For each token a lightweight
router activates a small subset of "experts" (sub-networks). The router keys heavily on
**surface phrasing — keywords, tokens, n-grams.**

Two consequences drive everything in this skill:

1. **Routing is phrase-sensitive.** Paraphrasing the same concept, or switching the term
   you use for an entity, activates *different* experts mid-task. The model then behaves as
   if a different assistant took over — this is the real source of "no global sight" and
   inconsistent instruction-following. It is a *routing* problem, not an intelligence
   problem.
2. **Routing is per-token, not global.** No single expert sees the whole task, so the
   model genuinely cannot hold global structure in its head the way a dense frontier model
   can. You must supply that structure externally and keep routing stable.

**Strategy:** make routing *stable and well-targeted*, then externalize global state.
You cannot make the experts smarter; you can keep the *right* experts consistently active.

## Part A — Stabilize routing (the MoE-specific part)

### A1. One canonical name per entity — never paraphrase
Pick ONE name for each function, file, variable, type, and concept, and reuse it verbatim
for the entire task. `parseConfig` stays `parseConfig` — not "the config parser", "that
loader", "the parsing logic". Each synonym re-routes to different experts and desyncs
behavior. Consistency of *tokens* matters more than elegance of prose.

### A2. Front-load domain keywords
Open each request with the concrete technical anchors so the correct experts fire on the
first tokens: language, framework, and the action verb (`refactor`, `debug`, `test`,
`implement`). "In **Go**, **refactor** the `auth` middleware…" routes better than "Could
you take a look at the middleware and clean it up a bit".

### A3. One domain per turn
Keep each turn to a single language / module / concern. Mixing unrelated topics (e.g. SQL
schema + CSS + shell script) in one turn forces the router to spread across many experts
and degrades all of them. Split unrelated work into separate turns.

### A4. Stable, structured instruction shape
Small wording changes change behavior, so keep a fixed structure: **Context → Task →
Constraints → Verify.** Reuse the same headings/phrasing across turns. Predictable input
shape ⇒ predictable routing.

### A5. Re-anchor in long sessions
As context grows, early anchors lose influence and routing drifts. Periodically restate
the canonical names and the current goal in one short line before continuing. If drift is
bad (model contradicts earlier decisions), start a fresh turn and reload state from a file.

### A6. Determinism
Code tasks want low temperature (≈0.0–0.3). If you control sampling, set it low. If you
don't (fixed endpoint), compensate by being more explicit and structured — explicitness
reduces the router's freedom to wander.

### A7. Role anchors — steer routing to the right experts
The router keys strongly on **role/persona tokens**. A precise role pulls in better-targeted
experts than generic "assistant". Rules:
- **Front-load ONE specific role** matching the task's concern, as the first tokens of the
  turn. Specific beats generic: "**Go concurrency engineer**" routes better than "engineer".
- **One role per turn.** Switching roles mid-turn scatters routing (see A3). When the
  concern changes, switch role *and* start a new turn.
- **Stack role + tech + action keywords:** `[role] + [language/framework] + [verb]` →
  e.g. "As a **security reviewer**, audit this **Express** route for **injection**."
- Re-state the role when re-anchoring a long session (A5).

Canonical roles for software-dev concerns (use the name verbatim, per A1):

| Concern | Role anchor | Stack with |
|---|---|---|
| System/architecture design | senior software architect | the domain + "design", "tradeoffs" |
| Feature implementation | senior <language> engineer | framework + "implement" |
| Refactoring | refactoring engineer | language + target symbol name |
| Debugging | debugging engineer | error text + "root cause" |
| Testing | test engineer (TDD) | framework + "failing test first" |
| Code review | staff code reviewer | "bugs, correctness only" |
| Security | application security reviewer | "injection / authz / secrets" |
| Performance | performance engineer | "profile", "hot path", complexity |
| Concurrency | concurrency engineer | "races", "locks", "goroutines/async" |
| API design | API designer | "REST/gRPC", "contract", "versioning" |
| Database / SQL | database engineer | engine (Postgres…) + "query/schema/index" |
| Frontend / UI | frontend engineer | framework + "accessibility/responsive" |
| DevOps / CI | platform/DevOps engineer | tool (Docker, CI) + "pipeline" |
| Types/generics | type-system engineer | language + "generics/inference" |

Don't invent elaborate personas — a 2–4 word precise role is the sweet spot. Longer
backstories add noise tokens that can mis-route.

## Part B — Externalize global state (compensate for per-token routing)

### B1. MAP before any edit
Before changing a symbol, list **every dependent** — callers, imports, exports, tests,
type/interface definitions, config, fixtures, docs. Use LSP "find references" (gopls,
typescript-lsp, etc.) when available, else `grep` the canonical name across the whole repo,
not just the open file. Write the list down (response, TodoWrite, or the SQL `todos`
table). Editing a symbol without this list produces a local-only fix — the #1 failure.

### B2. Persist the plan to a file
For multi-file work, write the impact MAP + an ordered list of tiny steps to `plan.md`
(session folder) or `todos`. The file is the global memory the model cannot hold itself.
Each step should name exactly one change and its verify command.

### B3. Offload heavy discovery to a subagent
The MAP and wide searches are token-heavy and pollute the main context (which then drifts
routing). Dispatch them to a subagent and take back only the distilled dependent list.
Small, focused context = stable routing.

## Part C — Verify every change (never self-declare done)

- After each step run the project's real check for the changed area — lint, type-check, the
  targeted test, build. Smallest command that covers the change; full suite at the end.
- Red baseline? Fix before the next step. Never stack changes on a failing state.
- Bugfix? Write the failing test FIRST — the test is the external spec the model can't hold
  in its head.
- After editing, re-read the **whole** changed region (not just the diff) and re-open each
  dependent from the MAP to confirm it still compiles/type-checks against your change.

## Done gate — all must hold
- [ ] Single canonical name was used for each entity throughout.
- [ ] Every dependent in the MAP was updated and checked.
- [ ] Each step verified green; full lint + test + build pass at the end.
- [ ] No scope creep beyond the request.

## Works with existing skills
This skill adds the MoE-routing layer on top of, and defers detailed procedure to:
`brainstorming`, `writing-plans`, `executing-plans`, `subagent-driven-development`,
`test-driven-development`, `systematic-debugging`, `verification-before-completion`,
`karpathy-guidelines`.

## Red flags — STOP if you think these
| Thought | Reality |
|---|---|
| "I'll call it 'the parser' here, clearer" | Synonyms re-route experts. Use the one canonical name. |
| "I'll batch these unrelated fixes in one turn" | Mixed domains scatter routing. One domain per turn. |
| "I'll just edit this function" | Did you MAP its callers? If not, stop — local-only fix incoming. |
| "It's obviously right" | MoE is confidently wrong under routing drift. Run the test. |
| "The session's long but I remember the plan" | Anchors decayed. Re-anchor or reload from file. |
| "Close enough, done" | Run the done gate. All boxes or not done. |
