from __future__ import annotations

from pathlib import Path

from radon.complexity import cc_visit


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = (
    "nextgen_dashboard",
    "fivetran_simulator",
    "mcp_tools",
    "pipeline_runtime",
    "scripts",
)
MAX_MODULE_LINES = 1900
DEFAULT_MAX_COMPLEXITY = 30
COMPLEXITY_BUDGETS = {
    # The dashboard audit is intentionally independent from production metrics.
    # It is tracked here until its page-specific checks are split into strategies.
    "nextgen_dashboard/backend/dashboard_audit.py:_audit_page": 55,
}


def main() -> int:
    violations = [*module_size_violations(), *complexity_violations()]
    if violations:
        print("Quality budget violations:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print(
        "Quality budgets passed: "
        f"modules <= {MAX_MODULE_LINES} lines and functions <= "
        f"{DEFAULT_MAX_COMPLEXITY} cyclomatic complexity by default."
    )
    return 0


def module_size_violations() -> list[str]:
    violations: list[str] = []
    for path in python_files():
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        if line_count > MAX_MODULE_LINES:
            violations.append(
                f"{relative(path)} has {line_count} lines (budget {MAX_MODULE_LINES})"
            )
    return violations


def complexity_violations() -> list[str]:
    violations: list[str] = []
    for path in python_files():
        relative_path = relative(path)
        for block in cc_visit(path.read_text(encoding="utf-8")):
            block_key = f"{relative_path}:{block.fullname}"
            budget = COMPLEXITY_BUDGETS.get(block_key, DEFAULT_MAX_COMPLEXITY)
            if block.complexity > budget:
                violations.append(
                    f"{block_key} has CC {block.complexity} (budget {budget})"
                )
    return violations


def python_files() -> list[Path]:
    return [
        path
        for source_root in SOURCE_ROOTS
        for path in (ROOT / source_root).rglob("*.py")
        if "__pycache__" not in path.parts
    ]


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
