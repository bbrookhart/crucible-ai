# Scoring

CRUCIBLE prefers objective mechanisms: tests pass, correct artifact changed, proof token submitted,
correct entity/timeline selected, or policy validation satisfied. v0.1 uses required evidence tokens to
exercise scoring isolation; these are transparent development scorers, not publication-grade semantic
rubrics.

Qualitative work requires a preregistered multidimensional rubric, evaluator identity/qualification,
blind review where feasible, inter-rater analysis, and retained disagreement. LLM-as-judge may support
analysis only when the judge is pinned, rubric-structured, stability-tested, and compared with human
labels. It is never unquestioned ground truth.

Scores remain in [0, 1]. Safety and verification are reported separately; an unsafe successful task is
not counted toward safe capability rate.
