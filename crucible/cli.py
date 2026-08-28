"""Dependency-light CRUCIBLE command-line interface."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from crucible import __version__
from crucible.analysis import compare_summaries, summarize
from crucible.blackbox import (
    BlackboxError,
    commit,
    ephemeral_reveal,
    keygen,
    reveal,
    seal,
    verify,
)
from crucible.contamination import audit, audit_ground_truth_references
from crucible.evidence import sha256_file, verify_evidence
from crucible.models import DeterministicMockAdapter, LocalOpenAIAdapter, ModelAdapter
from crucible.orchestrator import EvaluationOrchestrator
from crucible.registry import AGENTS, PROJECT_ROOT, TaskRegistry

EVIDENCE_ROOT = PROJECT_ROOT / "evidence"
BLACKBOX_ROOT = PROJECT_ROOT / ".crucible" / "blackbox"


def _model(name: str) -> ModelAdapter:
    if name == "mock":
        return DeterministicMockAdapter()
    if name == "local":
        return LocalOpenAIAdapter()
    raise ValueError(f"unsupported model: {name}")


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, default=str))


async def _run_one(task_id: str, model: str, agent: str) -> dict[str, Any]:
    result = await EvaluationOrchestrator(_model(model)).run(task_id, agent)
    return {
        "evaluation_id": result.manifest.evaluation_id,
        "model": result.manifest.model.model_id,
        "agent": result.manifest.agent.agent_id,
        "task_set": result.manifest.task_set,
        "resource_budget": result.manifest.budget.model_dump(mode="json"),
        "task_completion": result.score.success,
        "partial_credit": result.score.score,
        "tool_use": result.usage.tool_calls,
        "planning": result.manifest.agent.planner,
        "recovery": "NOT_TRIGGERED",
        "verification": result.score.verified,
        "safety": result.score.safe,
        "evidence_path": result.evidence_path,
    }


def _suite_tasks(name: str) -> list[str]:
    registry = TaskRegistry()
    tasks = registry.list()
    aliases = {
        "blue": None,
        "secure-code": "secure-code-review",
        "detection": "detection-engineering",
        "incident-response": "incident-analysis",
        "agent-security": "agent-security",
    }
    if name not in aliases:
        raise ValueError(f"unknown suite: {name}")
    domain = aliases[name]
    selected = [task.task_id for task in tasks if domain is None or task.domain == domain]
    if not selected:
        raise ValueError(f"suite contains no tasks: {name}")
    return selected


async def _run_suite(name: str, model: str, agent: str) -> list[dict[str, Any]]:
    return [await _run_one(task_id, model, agent) for task_id in _suite_tasks(name)]


def _condition_agent(condition: str) -> str:
    mapping = {"model-only": "model-only", "bounded-agent": "bounded", "bounded": "bounded"}
    if condition not in mapping:
        raise ValueError(f"unsupported condition: {condition}")
    return mapping[condition]


async def _compare(conditions: list[str], suite: str, model: str) -> dict[str, object]:
    if len(conditions) != 2:
        raise ValueError("compare requires exactly two --condition values")
    paths_by_condition: list[list[Path]] = []
    for condition in conditions:
        results = await _run_suite(suite, model, _condition_agent(condition))
        paths_by_condition.append([Path(str(item["evidence_path"])) for item in results])
    baseline = summarize(conditions[0], paths_by_condition[0])
    treatment = summarize(conditions[1], paths_by_condition[1])
    return compare_summaries(baseline, treatment)


def _blackbox_hashes() -> tuple[str, str]:
    environment_hash = sha256_file(PROJECT_ROOT / "docker-compose.yml")
    scoring_hash = sha256_file(PROJECT_ROOT / "crucible" / "scoring.py")
    return environment_hash, scoring_hash


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="crucible", description="Frontier AI cyber TEVV")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("status")

    models = commands.add_parser("models")
    models.add_subparsers(dest="action", required=True).add_parser("list")
    agents = commands.add_parser("agents")
    agents.add_subparsers(dest="action", required=True).add_parser("list")
    tasks = commands.add_parser("tasks")
    tasks.add_subparsers(dest="action", required=True).add_parser("list")
    task = commands.add_parser("task")
    task_actions = task.add_subparsers(dest="action", required=True)
    inspect = task_actions.add_parser("inspect")
    inspect.add_argument("task_id")

    evaluate = commands.add_parser("eval")
    eval_actions = evaluate.add_subparsers(dest="action", required=True)
    run = eval_actions.add_parser("run")
    run.add_argument("task_id")
    run.add_argument("--model", default="mock", choices=["mock", "local"])
    run.add_argument("--agent", default="bounded", choices=list(AGENTS))
    suite = eval_actions.add_parser("suite")
    suite.add_argument("suite")
    suite.add_argument("--model", default="mock", choices=["mock", "local"])
    suite.add_argument("--agent", default="bounded", choices=list(AGENTS))

    compare = commands.add_parser("compare")
    compare.add_argument("--condition", action="append", required=True)
    compare.add_argument("--suite", default="blue")
    compare.add_argument("--model", default="mock", choices=["mock", "local"])

    analyze = commands.add_parser("analyze")
    analyze.add_argument("run_id")
    evidence = commands.add_parser("evidence")
    evidence_actions = evidence.add_subparsers(dest="action", required=True)
    evidence_verify = evidence_actions.add_parser("verify")
    evidence_verify.add_argument("run_id")
    evidence_actions.add_parser("verify-all")

    contamination = commands.add_parser("contamination")
    contamination_actions = contamination.add_subparsers(dest="action", required=True)
    contamination_audit = contamination_actions.add_parser("audit")
    contamination_audit.add_argument("--canary", action="append", default=[])

    blackbox = commands.add_parser("blackbox")
    bb = blackbox.add_subparsers(dest="action", required=True)
    bb.add_parser("keygen")
    bb_seal = bb.add_parser("seal")
    bb_seal.add_argument("source", type=Path)
    bb_seal.add_argument("--vault", type=Path, default=BLACKBOX_ROOT / "vault.enc")
    bb.add_parser("commit")
    bb.add_parser("run")
    bb_reveal = bb.add_parser("reveal")
    bb_reveal.add_argument("--destination", type=Path, default=BLACKBOX_ROOT / "revealed")
    bb_verify = bb.add_parser("verify")
    bb_verify.add_argument(
        "commitment", nargs="?", type=Path, default=BLACKBOX_ROOT / "commitment.json"
    )
    return parser


def dispatch(args: argparse.Namespace) -> int:
    if args.command == "status":
        _print(
            {
                "name": "CRUCIBLE",
                "version": __version__,
                "safety_classes": ["S0", "S1", "S2", "S3"],
                "external_targets": "PROHIBITED",
                "public_tasks": len(TaskRegistry().list()),
                "blackbox_vault": (BLACKBOX_ROOT / "vault.enc").exists(),
            }
        )
        return 0
    if args.command == "models":
        _print({"models": ["mock", "local"], "provider_api_required": False})
        return 0
    if args.command == "agents":
        _print({name: config.model_dump(mode="json") for name, config in AGENTS.items()})
        return 0
    if args.command == "tasks":
        _print([task.model_dump(mode="json") for task in TaskRegistry().list()])
        return 0
    if args.command == "task":
        _print(TaskRegistry().get(args.task_id).model_dump(mode="json"))
        return 0
    if args.command == "eval" and args.action == "run":
        _print(asyncio.run(_run_one(args.task_id, args.model, args.agent)))
        return 0
    if args.command == "eval" and args.action == "suite":
        _print(asyncio.run(_run_suite(args.suite, args.model, args.agent)))
        return 0
    if args.command == "compare":
        _print(asyncio.run(_compare(args.condition, args.suite, args.model)))
        return 0
    if args.command == "analyze":
        path = EVIDENCE_ROOT / args.run_id
        _print(
            {
                "manifest": json.loads((path / "manifest.json").read_text()),
                "score": json.loads((path / "scores.json").read_text()),
                "metrics": json.loads((path / "metrics.json").read_text()),
            }
        )
        return 0
    if args.command == "evidence":
        if args.action == "verify":
            valid, errors = verify_evidence(EVIDENCE_ROOT / args.run_id)
            _print({"valid": valid, "errors": errors})
            return 0 if valid else 1
        failures = {}
        for path in sorted(EVIDENCE_ROOT.glob("RUN-*")):
            valid, errors = verify_evidence(path)
            if not valid:
                failures[path.name] = errors
        _print({"valid": not failures, "failures": failures})
        return 0 if not failures else 1
    if args.command == "contamination":
        leaks = audit(PROJECT_ROOT, args.canary) if args.canary else []
        reference_leaks = audit_ground_truth_references(PROJECT_ROOT)
        _print(
            {
                "classification": "LOW" if not leaks and not reference_leaks else "ELEVATED",
                "canary_findings": [finding.__dict__ for finding in leaks],
                "sequestered_reference_findings": reference_leaks,
                "claim": "risk classification, not proof of absence",
            }
        )
        return 0 if not leaks and not reference_leaks else 1
    if args.command == "blackbox":
        vault = BLACKBOX_ROOT / "vault.enc"
        commitment = BLACKBOX_ROOT / "commitment.json"
        environment_hash, scoring_hash = _blackbox_hashes()
        if args.action == "keygen":
            print(keygen())
        elif args.action == "seal":
            _print({"task_set_hash": seal(args.source, args.vault), "vault": str(args.vault)})
        elif args.action == "commit":
            _print(
                commit(
                    vault,
                    commitment,
                    environment_hash=environment_hash,
                    scoring_hash=scoring_hash,
                ).model_dump(mode="json")
            )
        elif args.action == "run":
            temporary, path = ephemeral_reveal(vault)
            file_count = sum(1 for item in path.rglob("*") if item.is_file())
            temporary.cleanup()
            _print(
                {
                    "ephemeral_files": file_count,
                    "destroyed": not path.exists(),
                    "evaluation": "READY",
                }
            )
        elif args.action == "reveal":
            _print(
                {
                    "task_set_hash": reveal(vault, args.destination),
                    "destination": str(args.destination),
                }
            )
        else:
            valid, errors = verify(
                vault,
                args.commitment,
                environment_hash=environment_hash,
                scoring_hash=scoring_hash,
            )
            _print({"valid": valid, "errors": errors})
            return 0 if valid else 1
        return 0
    raise ValueError("unhandled command")


def main() -> None:
    parser = build_parser()
    try:
        code = dispatch(parser.parse_args())
    except (BlackboxError, KeyError, ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        code = 2
    raise SystemExit(code)


if __name__ == "__main__":
    main()
