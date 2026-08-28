# Frontier-evaluation research context

CRUCIBLE uses public frontier-safety concepts—capability evaluation, tracked thresholds, early-warning
evaluation, model-generation deltas, and mitigation triggers—as research context. Project-specific
threshold labels are `TRACKED`, `ELEVATED`, and `RESEARCH ATTENTION`; they are not Google DeepMind
Critical Capability Levels.

The design supports repeated evaluations across model generations, exact configuration capture,
dimension-level capability deltas, and large-change flags. It does not reproduce Google DeepMind's
internal Frontier Safety Framework, claim equivalence with a frontier laboratory evaluation, or make
deployment decisions for a model provider.

Official reference: [Google DeepMind Frontier Safety Framework 3.1](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/), current public version checked 2026-08-28.
