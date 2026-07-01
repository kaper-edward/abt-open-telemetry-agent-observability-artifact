# Table 8 Supporting Data: CrewAI Write-a-Book Flow Scenario Scale

This document records the CrewAI Write-a-Book Flow data used to extend Table 8.

## Source Target

Source repository: https://github.com/crewAIInc/crewAI-examples

Evaluated example: `flows/write_a_book_with_flows`

Measured source LOC: 1,598 non-empty, non-comment LOC.

The experiment uses controlled source-level scenarios modeled after the public CrewAI flow structure. The purpose is trace-generation comparison across framework styles, not book-quality evaluation. Semantic action instrumentation records PromptAction and LLMAction spans for generation-oriented nodes, EvaluatorAction spans for review nodes, and GuardrailAction spans for validation-oriented nodes.

## Scenario Catalog Data

| Scenario | Main situation | Generated spans | Major Action span counts |
|---|---|---:|---|
| `short_book` | Outline and write a three-chapter book without revision | 41 | Input 1; Prompt 7; LLM 7; Tool 8; Guardrail 4; Evaluator 4 |
| `revision_book` | Four-chapter book with one chapter revision | 56 | Input 1; Prompt 10; LLM 10; Tool 11; Guardrail 6; Evaluator 5 |
| `large_book` | Six-chapter book with two chapter revisions | 81 | Input 1; Prompt 15; LLM 15; Tool 16; Guardrail 9; Evaluator 7 |

## Summary Statistics

| Statistic | Value |
|---|---:|
| Scenario count | 3 |
| Total generated span instances | 178 |
| Average generated span count per scenario | 59.33 |
| Minimum generated span count | 41 |
| Maximum generated span count | 81 |

## Span Kind Breakdown

| Scenario | Total spans | AGENT | CHAIN | PROMPT | LLM | TOOL | GUARDRAIL | EVALUATOR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `short_book` | 41 | 1 | 9 | 7 | 7 | 9 | 4 | 4 |
| `revision_book` | 56 | 1 | 12 | 10 | 10 | 12 | 6 | 5 |
| `large_book` | 81 | 1 | 17 | 15 | 15 | 17 | 9 | 7 |


