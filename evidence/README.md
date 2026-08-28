# Release evidence

The fourteen checked-in `RUN-20260828T02064*` packages are the v0.1 deterministic harness-validation
experiment: seven A0 model-only runs and seven A2 bounded-agent runs across CRUCIBLE // BLUE. Each
package contains its own `evidence-root.json`; verify all packages with:

```bash
crucible evidence verify-all
```

New `RUN-*` directories remain ignored by default so ad hoc transcripts, provider-policy-sensitive
content, and sequestered answers are never published accidentally. Only deliberately reviewed public
development evidence should be force-added to a release.
