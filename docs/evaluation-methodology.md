# Evaluation methodology

1. Pre-register the research question, task set/version, model endpoint/version, agent, tools, resource
   budget, sampling parameters, scoring method, trial count, exclusions, and analysis.
2. For sequestered sets, commit hashes for task payload, environment, and scorer before inference.
3. Create a fresh local environment and expose only the declared `TaskContext` and authorized tools.
4. Record observable inputs, outputs, tool events, latency, resource use, refusals, and policy attempts.
5. Score outside model authority using predeclared machine-verifiable truth or a dimensioned rubric.
6. Preserve pass@1, all trials, failures, abstentions, and negative results.
7. Produce and verify the evidence root before analysis.
8. Report N, distributions, uncertainty, effect size where justified, and limitations.

Model-only, agent, human, and human-plus-AI conditions are not pooled. The same logical model with a
different agent scaffold is a different evaluated system. Best-of-many outputs cannot substitute for
pass@1. Formal claims require repeated trials for stochastic systems.
