# Architecture

CRUCIBLE separates seven authorities: task registry, model adapter, agent harness, tool gateway,
environment, ground truth/scorer, and evaluator. `TaskManifest` contains the complete research record;
`TaskContext` is a reduced projection that excludes scoring methods and ground-truth references before
crossing the model boundary.

The orchestrator resolves a versioned task and immutable agent configuration, enforces the task budget,
invokes the adapter, records observable tool events, passes the output to an isolated objective scorer,
and emits a root-hashed evidence package. The model never calls the scorer or evidence writer.

S1 tasks use read-only static fixtures. S2/S3 execution must use a digest-pinned container with no
network, read-only root, non-root user, no capabilities, no-new-privileges, PID/memory/CPU limits, no
host mounts, and no Docker socket. The v0.1 architecture test validates the generated policy; it does
not assert that every possible Docker host is secure.
