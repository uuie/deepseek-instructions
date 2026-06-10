---
name: workflow-gate
description: Engineering workflow orchestrator. Use `workflow-gate:init` to patch mandatory workflow rules into CLAUDE.md/AGENTS.md/.github/copilot-instructions.md (and AGENT.md if present). Use `workflow-gate:impact-analysis` before changing any public API, interface, shared type, DB schema, exported signature, or symbol with more than 3 call sites. For coding/refactoring/debugging execution, invoke `moe-execution` after planning and impact analysis.
---

# Engineering Workflow

`$ARGUMENTS`:
- `init` — bootstrap/patch engineering workflow rules in project instruction files
- `impact-analysis` — run mandatory blast-radius analysis before interface changes

If `$ARGUMENTS` is empty:
1. Use `init` when user asks to set up workflow guardrails.
2. Use `impact-analysis` when user is about to change interfaces/contracts.
3. For coding/refactor/debug execution requests, keep `workflow-gate` as gatekeeper only, then hand off to `moe-execution` after planning (+ impact-analysis when required).

## Mode: `init`

Run:

```bash
python3 .claude/skills/workflow-gate/scripts/init_engineering_workflow.py
```

Expected behavior:
1. Detect and patch these files when they exist: `CLAUDE.md`, `AGENTS.md`, `AGENT.md`, `.github/copilot-instructions.md`.
2. Insert a managed engineering workflow block if missing.
3. Preserve existing stricter rules.
4. Be idempotent (safe to run repeatedly).
5. Add a handoff rule that routes coding execution to `moe-execution`.

## Mode: execution handoff

After plan + (if needed) impact analysis:
1. Invoke `moe-execution` for implementation/refactor/debug execution.
2. Keep `workflow-gate` responsible for pre-change gates and workflow ordering.
3. Keep `moe-execution` responsible for MoE routing stability and per-change verification discipline.

## Mode: `impact-analysis`

No interface change without blast-radius report first.

### Phase 1: Identify
1. Exact symbol and file path.
2. Exact change type (add/remove/rename/type/return/delete/schema).
3. Backward-compatible path (default/overload/deprecate-migrate/dual-write).

### Phase 2: Map blast radius
Search these layers in order:
1. Text search
2. Semantic references
3. Generated code
4. Late binding
5. External consumers

Project hazard checks (hidden dependencies):

| Hazard | Why it hides callers | Check |
|---|---|---|
| jOOQ generated code | Schema changes break generated classes | `rg "FROM.*table_name" src/` |
| Flyway migrations | Later migrations depend on earlier table shape | `ls -1 src/main/resources/db/migration/ \| sort` |
| Spring bean wiring | `@Qualifier`/bean names wire by string | `rg "Qualifier.*beanName" --type java` |
| Temporal activities | Activity names called by string | Search workflow files for activity name strings |
| Kafka schemas | Producer/consumer drift | Check producer and consumer schema usage |
| TypeScript API mirrors | Frontend DTOs mirror backend manually | `rg "interface.*SameName" frontend/src/` |
| MCAP/ROS message types | Bag/clip format tied to ROS definitions | Check `bagdb-mcap/` and clip format docs |
| OpenSearch mappings | Mapping changes break queries/dashboards | Check OpenSearch query templates |

### Phase 3: Classify + report
Classify dependents:
- d=1 **WILL BREAK**
- d=2 **LIKELY AFFECTED**
- d=3 **MAY NEED TESTING**

Rate risk: LOW / MEDIUM / HIGH / CRITICAL.

Report before code edits:

```text
Blast radius: <symbol>
  d=1 WILL BREAK:      <N> callers
  d=2 LIKELY AFFECTED: <N> consumers
  d=3 TEST:            <N> suites/paths
  Risk: <LOW|MEDIUM|HIGH|CRITICAL>
  BC path: <Yes/No + strategy>
  Plan: <ordered steps>
```
