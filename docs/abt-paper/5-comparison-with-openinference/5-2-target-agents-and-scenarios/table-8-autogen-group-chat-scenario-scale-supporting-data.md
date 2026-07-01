# Table 8 Supporting Data: AutoGen Distributed Group Chat Scenario Scale

This document records the AutoGen Distributed Group Chat data used to extend Table 8.

## Source Target

Source repository: https://github.com/microsoft/autogen

Evaluated example: `python/samples/core_distributed-group-chat`

Measured source LOC: 579 non-empty, non-comment LOC.

The experiment uses controlled source-level scenarios modeled after the public AutoGen distributed group chat sample. The purpose is trace-generation comparison across multi-agent routing and communication behavior, not answer-quality evaluation. Semantic action instrumentation records PromptAction and LLMAction spans for message-producing nodes, EvaluatorAction spans for review/fact-checking nodes, and GuardrailAction spans for routing or validation-oriented nodes.

## Scenario Catalog Data

| Scenario | Main situation | Generated spans | Major Action span counts |
|---|---|---:|---|
| `single_review` | One telemetry_recording/editor review round | 28 | Input 1; Prompt 5; LLM 5; Tool 5; Guardrail 4; Evaluator 1 |
| `multi_round_review` | Three telemetry_recording/editor review rounds with repeated routing | 58 | Input 1; Prompt 11; LLM 11; Tool 11; Guardrail 8; Evaluator 3 |
| `fact_checked_review` | Two review rounds with additional fact-checker agent review | 53 | Input 1; Prompt 10; LLM 10; Tool 10; Guardrail 6; Evaluator 4 |

## Summary Statistics

| Statistic | Value |
|---|---:|
| Scenario count | 3 |
| Total generated span instances | 139 |
| Average generated span count per scenario | 46.33 |
| Minimum generated span count | 28 |
| Maximum generated span count | 58 |

## Span Kind Breakdown

| Scenario | Total spans | AGENT | CHAIN | PROMPT | LLM | TOOL | GUARDRAIL | EVALUATOR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `single_review` | 28 | 1 | 6 | 5 | 5 | 6 | 4 | 1 |
| `multi_round_review` | 58 | 1 | 12 | 11 | 11 | 12 | 8 | 3 |
| `fact_checked_review` | 53 | 1 | 11 | 10 | 10 | 11 | 6 | 4 |


