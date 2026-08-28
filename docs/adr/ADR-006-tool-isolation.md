# ADR-006: Narrow tool gateway

Status: Accepted — 2026-08-28

Models receive no arbitrary external shell or internet. Tools are task-authorized, path-canonicalized,
budgeted, and observed. Container execution requires network denial, read-only root, non-root identity,
capability removal, no-new-privileges, resource limits, and digest-pinned task images.
