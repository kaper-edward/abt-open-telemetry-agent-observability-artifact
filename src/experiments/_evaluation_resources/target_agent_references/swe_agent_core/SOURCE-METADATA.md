# SWE-agent Core Execution Source Metadata

## Public Source

- Repository: https://github.com/princeton-nlp/SWE-agent
- Public source scope used for evaluation: core execution behavior corresponding to `sweagent/agent`, `sweagent/tools`, and `sweagent/environment`
- Packaged source snapshot: not included in this artifact; the public source scope is recorded as metadata and represented by the controlled evaluation harness below.

## Evaluation Use

SWE-agent Core Execution is used as a public software-engineering agent target. The experiment uses a controlled source-level evaluation harness modeled after the SWE-agent issue-solving loop: issue parsing, repository exploration, file inspection, patch application, shell command execution, test execution, failure diagnosis, retry, and submission.

Here, controlled evaluation harness means that shell results, test outcomes, patch results, and filesystem side effects are fixed as scenario data. This does not claim to execute the full upstream SWE-agent execution stack; it preserves the source-level operation sequence needed to evaluate trace generation for software-engineering agent behavior.

## Related Artifact Files

- Controlled evaluation harness: `src/experiments/swe_agent_core_base/`
- ABT instrumentation variant: `src/experiments/swe_agent_core_abt/`
- Direct OI/Otel instrumentation variant: `src/experiments/swe_agent_core_oi/`
- Scenario and measurement scripts: `src/experiments/agent_trace_experiments/`
