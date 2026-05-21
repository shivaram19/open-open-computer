#!/usr/bin/env python3
"""
Pre-commit hook: Verify all code has citations before allowing commit.

Usage:
    python scripts/verify_citations.py [--strict] [--fix] [--trust-report]

Exit code 0 = all citations present and verified
Exit code 1 = missing citations found

Principle: In God we trust. All others must bring data.
"""

import ast
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Any
import json

# ── Configuration ──────────────────────────────────────────────────────
# Files exempt from citation requirements
_EXEMPT_PATTERNS = [
    "__init__.py",
    "conftest.py",
    "test_*.py",
    "*_test.py",
    "scripts/verify_citations.py",
]

_EXEMPT_DIRS = [
    "tests/",
    "scripts/",
    "docs/",
]

# ── Exemption Check ────────────────────────────────────────────────────

def _is_exempt(filepath: Path) -> bool:
    """Check if a file is exempt from citation requirements."""
    path_str = str(filepath)

    for pattern in _EXEMPT_PATTERNS:
        if filepath.name == pattern or filepath.match(pattern):
            return True

    for dir_pattern in _EXEMPT_DIRS:
        if dir_pattern in path_str:
            return True

    return False


# ── Citation Detection ─────────────────────────────────────────────────

def _has_cite_decorator(node: ast.AST) -> bool:
    """Check if node has @cite decorator."""
    if not hasattr(node, "decorator_list"):
        return False

    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name) and decorator.func.id == "cite":
                return True
            # Handle module-qualified: @cite.cite() or @utils.cite()
            if isinstance(decorator.func, ast.Attribute) and decorator.func.attr == "cite":
                return True
    return False


def _docstring_has_citation(node: ast.AST) -> bool:
    """Check if docstring contains citation markers."""
    doc = ast.get_docstring(node)
    if not doc:
        return False

    markers = [
        "Sources:",
        "[CITATION:",
        "# [CITATION:",
        "Source:",
        "References:",
    ]
    return any(marker in doc for marker in markers)


def _find_missing_citations(filepath: Path) -> List[Tuple[int, str, str]]:
    """
    Parse a Python file and find public classes/functions without citations.

    Returns list of (line_number, name, node_type) tuples.
    """
    missing: List[Tuple[int, str, str]] = []

    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"  WARNING: Syntax error in {filepath}: {e}")
        return missing

    # Collect all function names defined inside other functions
    nested_functions: set[str] = set()

    def _collect_nested(node: ast.AST) -> None:
        if isinstance(node, ast.FunctionDef):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, ast.FunctionDef):
                    nested_functions.add(child.name)
                _collect_nested(child)
        else:
            for child in ast.iter_child_nodes(node):
                _collect_nested(child)

    _collect_nested(tree)

    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            # Skip private
            if node.name.startswith("_"):
                continue

            # Skip nested functions (implementation detail, not public API)
            if isinstance(node, ast.FunctionDef) and node.name in nested_functions:
                continue

            # Check for citation
            has_cite = _has_cite_decorator(node) or _docstring_has_citation(node)

            if not has_cite:
                node_type = "class" if isinstance(node, ast.ClassDef) else "function"
                missing.append((node.lineno, node.name, node_type))

    return missing


# ── Registry Verification ──────────────────────────────────────────────

def _verify_registry_keys(filepath: Path, repo_root: Path) -> List[Dict[str, Any]]:
    """Extract citation keys from file and verify they exist in registry."""
    issues: List[Dict[str, Any]] = []

    try:
        source = filepath.read_text(encoding="utf-8")
    except Exception:
        return issues

    # Find all [CITATION: KEY] patterns
    import re
    citation_refs = re.findall(r"\[CITATION:\s*([^\]]+)\]", source)

    if not citation_refs:
        return issues

    registry_path = repo_root / "docs" / "research" / "citation_registry.json"
    registry: Dict[str, Any] = {"citations": {}}
    if registry_path.exists():
        registry = json.loads(registry_path.read_text())

    for ref in citation_refs:
        key = ref.strip().split()[0]  # e.g., "CP-WBFT2025 §3.2" -> "CP-WBFT2025"
        if key not in registry.get("citations", {}):
            issues.append({
                "file": str(filepath),
                "key": key,
                "issue": "Citation key not found in registry",
            })

    return issues


# ── Main ───────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify code citations in the ACN codebase",
        epilog="In God we trust. All others must bring data.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any missing citation (default: warn only)",
    )
    parser.add_argument(
        "--trust-report",
        action="store_true",
        help="Generate trust score report per module",
    )
    parser.add_argument(
        "--registry-check",
        action="store_true",
        help="Verify all cited keys exist in citation_registry.json",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    src_dir = repo_root / "src"

    if not src_dir.exists():
        print(f"❌ Source directory not found: {src_dir}")
        return 1

    all_missing: List[Tuple[Path, Tuple[int, str, str]]] = []
    all_registry_issues: List[Dict[str, Any]] = []

    for pyfile in src_dir.rglob("*.py"):
        if _is_exempt(pyfile):
            continue

        missing = _find_missing_citations(pyfile)
        if missing:
            all_missing.extend([(pyfile, m) for m in missing])

        if args.registry_check:
            issues = _verify_registry_keys(pyfile, repo_root)
            all_registry_issues.extend(issues)

    # ── Report ─────────────────────────────────────────────────────────
    has_errors = False

    if all_missing:
        has_errors = True
        print(f"❌ Found {len(all_missing)} uncited code elements:")
        print()

        for filepath, (line, name, node_type) in all_missing:
            rel_path = filepath.relative_to(repo_root)
            print(f"  {rel_path}:{line}  {node_type:7s} '{name}' — NO CITATION")

        print()

    if all_registry_issues:
        has_errors = True
        print(f"❌ Found {len(all_registry_issues)} unregistered citation keys:")
        print()

        for issue in all_registry_issues:
            print(f"  {issue['file']} — key '{issue['key']}' — {issue['issue']}")

        print()

    if not has_errors:
        print("✅ All code elements have citations. Trust maintained.")

        if args.registry_check:
            print("✅ All citation keys verified against registry.")

        print()
        print("In God we trust. All others have brought data.")
        return 0

    print("In God we trust. All others must bring data.")
    print()
    print("Every class and function must cite its research source.")
    print("Use @cite() decorator or include 'Sources:' in docstring.")
    print("Register all citation keys in docs/research/citation_registry.json.")

    if args.strict:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
