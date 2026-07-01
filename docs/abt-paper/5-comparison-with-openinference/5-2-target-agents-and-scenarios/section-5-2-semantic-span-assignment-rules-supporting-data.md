# Semantic Span Assignment Rules Supporting Data

This document records the semantic span assignment rules used for the four public-agent targets in Section 5.

## Purpose

The public-agent experiments combine two observation levels:

1. source-node execution, represented as `Task` + `ToolAction`
2. behavior-semantic actions, represented as `PromptAction`, `LLMAction`, `RetrieverAction`, `GuardrailAction`, or `EvaluatorAction` when those actions are natural for the source node role

This avoids reducing public-agent traces to only source-node TOOL spans while keeping the instrumentation controlled and reproducible.

## Assignment Rules

The implementation is centralized in:

```text
src/experiments/agent_trace_experiments/semantic_node_instrumentation.py
```

| Source node role | Assigned semantic actions | Rationale |
|---|---|---|
| Research planning, supervision, report generation, compression, writing, revision, finalization, issue parsing | `PromptAction`, `LLMAction`, `GuardrailAction` | These nodes represent prompt construction, model-mediated generation or interpretation, and validation of the generated result. |
| Research tool nodes | `RetrieverAction`, `GuardrailAction` | These nodes represent retrieval of external or contextual information followed by validation of retrieved content. |
| File inspection in SWE-agent | `RetrieverAction`, `GuardrailAction` | File inspection retrieves repository context and validates whether the retrieved file information is useful for subsequent repair. |
| Patch generation, direct file editing, test-failure diagnosis in SWE-agent | `PromptAction`, `LLMAction`, `GuardrailAction` | These nodes represent model-mediated repair reasoning or code generation followed by validation. |
| Review, fact checking, or evaluation nodes | `PromptAction`, `LLMAction`, `EvaluatorAction` | These nodes produce or apply judgment over generated content, so the result is represented as an evaluator action rather than only a guardrail. |
| Shell execution, test execution, patch submission, command execution | `GuardrailAction` | These nodes validate execution results, test outcomes, command status, or submission status. The actual source-node execution remains represented by `ToolAction`. |

## Target-Specific Effect

| Target agent | Additional non-TOOL semantic span kinds |
|---|---|
| Open Deep Research | `PROMPT`, `LLM`, `RETRIEVER`, `GUARDRAIL` |
| CrewAI Write-a-Book Flow | `PROMPT`, `LLM`, `GUARDRAIL`, `EVALUATOR` |
| AutoGen Distributed Group Chat | `PROMPT`, `LLM`, `GUARDRAIL`, `EVALUATOR` |
| SWE-agent Core Execution | `PROMPT`, `LLM`, `RETRIEVER`, `GUARDRAIL` |

## Reproducibility Note

The same assignment rule is applied to both instrumentation variants:

- ABT variant: `record_abt_semantic_actions`
- Direct OI/Otel variant: `record_oi_semantic_actions`

Therefore, semantic span assignment does not favor either variant in the equivalence comparison. The comparison still checks that ABT trace generation and direct OI/Otel trace generation produce the same span structure and attributes for the assigned semantic actions.


