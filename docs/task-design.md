# Task design

Tasks terminate in controlled outcomes: a finding, patch, regression-test result, proof token, timeline,
policy decision, or remediation plan. They never require unrestricted compromise. S0–S3 tasks use
synthetic data, controlled repositories, or deliberately vulnerable local services. S4 is unsupported.

Difficulty is multidimensional: knowledge depth, reasoning depth, tool complexity, environment
uncertainty, step count, state requirements, recovery requirement, and verification difficulty. Public
task manifests declare inputs, tools, prohibitions, budgets, safety class, contamination status, scoring,
and conditions. Ground truth is stored in the scorer authority, not in model-visible context.
