# AutoGen Distributed Group Chat Source Metadata

## Public Source

- Repository: https://github.com/microsoft/autogen
- Public source scope used for evaluation: `python/samples/core_distributed-group-chat`
- Packaged source snapshot: not included in this artifact; the public source scope is recorded as metadata and represented by the controlled evaluation harness below.

## Evaluation Use

AutoGen Distributed Group Chat is used as a public multi-agent conversation and routing target. The experiment does not execute the full upstream AutoGen execution stack. Instead, it uses a controlled source-level evaluation harness derived from the public group-chat sample: manager routing, writer drafting, editor review, optional fact checking, and final response generation.

Here, controlled evaluation harness means that agent messages, review decisions, routing outcomes, and final responses are fixed by scenarios. This keeps the behavior sequence identical for ABT and direct OI/Otel instrumentation while preserving the multi-agent routing structure used for trace generation.

## Related Artifact Files

- Controlled evaluation harness: `src/experiments/autogen_group_chat_base/`
- ABT instrumentation variant: `src/experiments/autogen_group_chat_abt/`
- Direct OI/Otel instrumentation variant: `src/experiments/autogen_group_chat_oi/`
- Scenario and measurement scripts: `src/experiments/agent_trace_experiments/`
