#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

MANAGED_START = "<!-- workflow-gate:init:start -->"
MANAGED_END = "<!-- workflow-gate:init:end -->"

MANAGED_BLOCK = f"""{MANAGED_START}
### workflow-gate bootstrap (managed)

- Use `workflow-gate:init` to keep this workflow block present and consistent.
- **Rule 1 (Plan Before Building):** new feature / non-trivial change / design change / touching >2 files → invoke planning skill before code.
- **Rule 2 (Impact Analysis Before Interface Changes):** public API/interface/shared type/DB schema/exported signature/symbol with >3 call sites → invoke `workflow-gate:impact-analysis` before code changes.
- **Rule 3 (Verify Before Done):** task completion / claiming done / handoff → run verification command and show passing output.
- **Rule 4 (Root-Cause Debugging):** any bug/test failure/unexpected behavior → invoke debugging workflow before fix; hypothesis → evidence → test → fix.
- **Rule 5 (MoE Execution Discipline):** after planning and required impact analysis, invoke `moe-execution` for coding/refactoring/debugging execution.
{MANAGED_END}
"""

SECTION_HEADER = "## Engineering Workflow (MANDATORY)"

SECTION_FALLBACK = f"""
## Engineering Workflow (MANDATORY)

Every rule is trigger-based. When the trigger fires, the action is NON-NEGOTIABLE.

{MANAGED_BLOCK}
""".strip() + "\n"


def _inject_managed_block(content: str) -> tuple[str, bool]:
    if MANAGED_START in content and MANAGED_END in content:
        return content, False

    if SECTION_HEADER in content:
        anchor = content.index(SECTION_HEADER) + len(SECTION_HEADER)
        updated = content[:anchor] + "\n\n" + MANAGED_BLOCK + content[anchor:]
        return updated, True

    sep = "\n" if content.endswith("\n") else "\n\n"
    updated = content + sep + SECTION_FALLBACK
    return updated, True


def patch_file(path: Path) -> str:
    if not path.exists():
        return f"SKIP {path} (missing)"

    content = path.read_text(encoding="utf-8")
    updated, changed = _inject_managed_block(content)
    if not changed:
        return f"SKIP {path} (already initialized)"

    path.write_text(updated, encoding="utf-8")
    return f"PATCH {path}"


def main() -> int:
    repo_root = Path.cwd()
    targets = [
        repo_root / "CLAUDE.md",
        repo_root / "AGENTS.md",
        repo_root / "AGENT.md",
        repo_root / ".github" / "copilot-instructions.md",
    ]

    for target in targets:
        print(patch_file(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
