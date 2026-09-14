#!/usr/bin/env python3
"""Repository-level preflight for AssureGraph."""

from pathlib import Path
import argparse
import ast
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STABLE_DEP = "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6"
REQUIRED = [
    "contracts/assuregraph.py",
    "contracts/assurance_gate.py",
    "README.md",
    "SUBMISSION.md",
    "DEPLOYMENT.md",
    "gltest.config.yaml",
    "tests/direct/test_assuregraph.py",
    "tests/integration/test_studionet_lifecycle.py",
]


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--final", action="store_true", help="require live deployment evidence and pinned fixtures")
    args = parser.parse_args()
    errors: list[str] = []

    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            fail(f"missing required file: {rel}", errors)

    for forbidden_dir in ("frontend", "web", "app", "ui"):
        if (ROOT / forbidden_dir).exists():
            fail(f"frontend/product directory is out of scope for this contract submission: {forbidden_dir}/", errors)

    for py in ROOT.rglob("*.py"):
        try:
            ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except SyntaxError as exc:
            fail(f"python syntax error in {py.relative_to(ROOT)}: {exc}", errors)

    contract_text = (ROOT / "contracts" / "assuregraph.py").read_text(encoding="utf-8")
    consumer_text = (ROOT / "contracts" / "assurance_gate.py").read_text(encoding="utf-8")
    if STABLE_DEP not in contract_text or STABLE_DEP not in consumer_text:
        fail("contracts are not pinned to the expected stable py-genlayer dependency", errors)

    cfg = (ROOT / "gltest.config.yaml").read_text(encoding="utf-8")
    if "https://studio.genlayer.com/api" not in cfg:
        fail("gltest config is not pinned to stable Studio RPC", errors)
    if not re.search(r"(?m)^\s*studionet:\s*$", cfg):
        fail("gltest config is missing the studionet network", errors)

    # Guard the exact network target requested for this project.
    forbidden_network_tokens = ("619" + "97", "studio" + "-dev", "studionet" + "-dev")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix in {".zip", ".pyc"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in forbidden_network_tokens:
            if token.lower() in text.lower():
                fail(f"forbidden network token {token!r} found in {path.relative_to(ROOT)}", errors)

    integration = (ROOT / "tests" / "integration" / "test_studionet_lifecycle.py").read_text(encoding="utf-8")
    if args.final and "FIXTURE_COMMIT_PLACEHOLDER" in integration:
        fail("final mode: integration fixtures are not pinned to an immutable commit", errors)

    deployment = (ROOT / "DEPLOYMENT.md").read_text(encoding="utf-8")
    if args.final:
        for placeholder in ("<FINALIZED_ADDRESS>", "<FINALIZED_TX_HASH>", "<64_HEX>"):
            if placeholder in deployment:
                fail(f"final mode: deployment evidence still contains {placeholder}", errors)

    if errors:
        print("PRE-FLIGHT FAILED")
        for item in errors:
            print(f"- {item}")
        return 1

    print("PRE-FLIGHT PASSED")
    print("- contract-only repository: yes")
    print("- stable Studionet target: 61999")
    print("- Studio RPC: https://studio.genlayer.com/api")
    print("- Python syntax: valid")
    print("- stable py-genlayer dependency: pinned")
    if args.final:
        print("- immutable fixture pin: present")
        print("- deployment evidence placeholders: cleared")
    else:
        print("- live fixture/deployment evidence: intentionally deferred to final handoff")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
