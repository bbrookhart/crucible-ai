# CRUCIBLE: Measuring Cybersecurity Capability and Defensive Uplift in Advanced AI Systems

## Abstract

Cybersecurity evaluations of advanced AI systems are confounded by agent scaffolds, tools, budgets,
environmental feedback, stochasticity, benchmark exposure, and ambiguous ground truth. CRUCIBLE is a
defensive TEVV architecture that makes those conditions explicit, separates model authority from
scoring authority, and produces traceable evidence. Version 0.1 validates the architecture using a
deterministic mock adapter and seven public static tasks; it makes no frontier-model capability claim.

## Motivation and related work

NIST's initial-draft TEVV-Athlon emphasizes customized assessment across diverse AI systems. NIST AI
RMF provides GOVERN, MAP, MEASURE, and MANAGE functions. Public frontier-safety frameworks motivate
tracked capability and early-warning evaluation. CRUCIBLE applies these ideas to defensive cyber tasks
without claiming endorsement, compliance, or replication of any internal laboratory process.

## Threat and safety model

All tasks are synthetic/local and S0–S3. The platform excludes public targets, real credentials,
malware, persistence, destructive actions, phishing, unrestricted shell, and external scanning. Models
are treated as potentially compromised. Ground truth, scorers, sequestered material, and budgets remain
outside model authority.

## Evaluation architecture

Typed registries resolve tasks, models, agents, and tools. A CRUCIBLE-owned orchestrator applies budgets
and calls a reduced model context. Tool events are allowlisted and observed. An independent scorer
evaluates output against predeclared truth, then an evidence writer hashes configuration, transcript,
tool events, scores, metrics, and verification.

## Task taxonomy and agent/resource model

The broader taxonomy includes knowledge, code review, patching, vulnerability triage, configuration,
detection, incident analysis, campaign reconstruction, OT/ICS reasoning, agent security, supply chain,
and cryptographic migration. v0.1 implements seven S1 domains. A0 model-only and A2 bounded-agent
conditions are executable. Every result binds step, tool, token, wall-time, and cost budgets.

## Measurement methodology

Objective ground truth is preferred. Pass@1, task success, partial credit, tool quality, planning,
recovery, verification, calibration, efficiency, failure stage, and safe capability remain separate.
Stochastic comparisons require repeated trials and uncertainty. The system records refusal distinctly
and never jailbreaks a provider to raise completion.

## Contamination and sequestered evaluation

Public development tasks are separated from private and sequestered claims. BLACKBOX encrypts local
task payloads, commits task/environment/scorer hashes, reveals ephemerally, and verifies afterward.
Procedural variants, canaries, and leakage audits reduce contamination risk but do not prove absence.

## Experimental design and v0.1 results

The v0.1 experiment compares a deterministic mock adapter with no artifact tools against the same
adapter with task-scoped read access and bounded verification. A0 completes 0/7; A2 completes 7/7 with
7/7 safe completions and verification. This expected contrast verifies condition separation, tool
accounting, scoring, and evidence. It cannot estimate AI cyber capability.

## Failure analysis and human uplift

CRUCIBLE attributes the earliest defensible failure stage from knowledge through safety/refusal. Human
uplift will compare success, time, quality, critical errors, and calibration and will explicitly measure
negative uplift. No human data or population claim exists in v0.1.

## Limitations, implications, and future work

The public pack is small and transparent; dynamic S3 tasks, long-horizon recovery, external models,
sequestered generalization, signed evidence, cross-project fixtures, and independent reproduction remain
future work. CRUCIBLE demonstrates that a useful cyber-capability claim is inseparable from its system
configuration, budget, task distribution, scorer, evidence, and limitations.
