# Table 8 Supporting Data: Customer Support Scenario Catalog and Generated Trace Scale

This document records the customer support data used in Table 8, "Scenario catalog and generated trace scale used for framework evaluation."

## Measurement Scope

The table summarizes the scenario catalog used to evaluate ABT trace generation against the direct OI/Otel reference implementation. Each scenario corresponds to one request-level Trace.

## Scenario Catalog Data

| Scenario | Main situation | Generated spans | Major Action span counts |
|---|---|---:|---|
| `combined_policy_retry_success` | Combined order-policy handling with response retry and final success | 30 | Input 1; Prompt 3; LLM 3; Embedding 1; Tool 2; Retriever 1; Reranker 1; Guardrail 6; Evaluator 1 |
| `fallback_handoff` | Unsupported request leading to fallback failure and handoff | 15 | Input 1; Prompt 1; LLM 1; Tool 2; Guardrail 3 |
| `missing_order_fallback` | Order lookup failure followed by fallback response | 16 | Input 1; Prompt 1; LLM 1; Tool 2; Guardrail 4 |
| `policy_decision_fallback` | Policy decision requiring fallback handling | 22 | Input 1; Prompt 1; LLM 1; Embedding 1; Tool 2; Retriever 1; Reranker 1; Guardrail 5 |
| `policy_retrieval_failure_fallback` | Policy retrieval failure followed by fallback response | 20 | Input 1; Prompt 1; LLM 1; Embedding 1; Tool 2; Retriever 1; Reranker 1; Guardrail 4 |
| `response_retry_exhaustion_fallback` | Response grounding failure, retry exhaustion, and fallback | 26 | Input 1; Prompt 3; LLM 3; Tool 2; Guardrail 7 |
| `shipping_order_success` | Normal shipping-order lookup and response generation | 22 | Input 1; Prompt 2; LLM 2; Tool 2; Guardrail 5; Evaluator 1 |
| `unsupported_fallback` | Unsupported request routed directly to fallback | 13 | Input 1; Prompt 1; LLM 1; Tool 1; Guardrail 3 |

## Summary Statistics

| Statistic | Value |
|---|---:|
| Scenario count | 8 |
| Average generated span count per scenario | 20.50 |
| Minimum generated span count | 13 |
| Maximum generated span count | 30 |

## TraceAction Span Breakdown

The following table decomposes the generated span count by TraceAction subtype. The total span count also includes structural spans such as Agent, Trace, and Task spans, while the action subtotal includes only TraceAction spans.

| Scenario | Total spans | Action subtotal | Input | Prompt | LLM | Embedding | Tool | Retriever | Reranker | Guardrail | Evaluator |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `combined_policy_retry_success` | 30 | 19 | 1 | 3 | 3 | 1 | 2 | 1 | 1 | 6 | 1 |
| `fallback_handoff` | 15 | 8 | 1 | 1 | 1 | 0 | 2 | 0 | 0 | 3 | 0 |
| `missing_order_fallback` | 16 | 9 | 1 | 1 | 1 | 0 | 2 | 0 | 0 | 4 | 0 |
| `policy_decision_fallback` | 22 | 13 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 5 | 0 |
| `policy_retrieval_failure_fallback` | 20 | 12 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 4 | 0 |
| `response_retry_exhaustion_fallback` | 26 | 16 | 1 | 3 | 3 | 0 | 2 | 0 | 0 | 7 | 0 |
| `shipping_order_success` | 22 | 13 | 1 | 2 | 2 | 0 | 2 | 0 | 0 | 5 | 1 |
| `unsupported_fallback` | 13 | 7 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 3 | 0 |


