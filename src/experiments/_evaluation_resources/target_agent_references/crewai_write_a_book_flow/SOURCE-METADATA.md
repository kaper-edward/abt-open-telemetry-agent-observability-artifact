# CrewAI Write-a-Book Flow Source Metadata

## Public Source

- Repository: https://github.com/crewAIInc/crewAI-examples
- Public source scope used for evaluation: `flows/write_a_book_with_flows`
- Packaged source snapshot: not included in this artifact; the public source scope is recorded as metadata and represented by the controlled evaluation harness below.

## Evaluation Use

CrewAI Write-a-Book Flow is used as a public flow-orchestration target. The experiment does not execute the full upstream CrewAI execution stack. Instead, it uses a controlled source-level evaluation harness derived from the public flow structure: outline generation, chapter generation, review, conditional revision, and final assembly.

Here, controlled evaluation harness means a reproducible experimental program that preserves the public workflow structure while fixing external or generated results as scenario data. LLM outputs, crew execution results, and generated chapter contents are fixed so that ABT and direct OI/Otel variants observe the same behavior sequence.

## Related Artifact Files

- Controlled evaluation harness: `src/experiments/crewai_book_flow_base/`
- ABT instrumentation variant: `src/experiments/crewai_book_flow_abt/`
- Direct OI/Otel instrumentation variant: `src/experiments/crewai_book_flow_oi/`
- Scenario and measurement scripts: `src/experiments/agent_trace_experiments/`
