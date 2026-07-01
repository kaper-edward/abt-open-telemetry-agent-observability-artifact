# Table 8 Supporting Data: Open Deep Research Scenario Catalog and Generated Trace Scale

This document records the Open Deep Research data used to extend Table 8.

## Source Target

Source repository: https://github.com/langchain-ai/open_deep_research

Pinned commit: `1f24f1142db24f81e29eb88751985a00ec8ed580`

The experiment uses controlled scenarios to avoid external API cost and network instability. The purpose is trace-generation comparison, not answer-quality evaluation. The Open Deep Research target executes the original source LangGraph (`deep_researcher`) with controlled LLM and tool dependencies. Node-level instrumentation wraps the executed source graph nodes while preserving the source graph's control structure. Semantic action instrumentation additionally records natural PromptAction, LLMAction, RetrieverAction, and GuardrailAction spans for source nodes whose roles correspond to prompt construction, model invocation, retrieval, or validation.

## Scenario Catalog Data

| Scenario | Main situation | Generated spans | Major Action span counts |
|---|---|---:|---|
| `short_research` | Single-query research, retrieval, source summarization, compression, and report generation | 59 | Input 1; Prompt 8; LLM 8; Tool 12; Retriever 4; Guardrail 12 |
| `multi_source_research` | Multi-query research with multiple retrieved documents and per-source summarization | 82 | Input 1; Prompt 11; LLM 11; Tool 17; Retriever 6; Guardrail 17 |
| `empty_retrieval_fallback` | Empty retrieval result summarized into a no-source report | 59 | Input 1; Prompt 8; LLM 8; Tool 12; Retriever 4; Guardrail 12 |
| `broad_market_research` | Broad research with four planned queries and six retrieved documents | 128 | Input 1; Prompt 17; LLM 17; Tool 27; Retriever 10; Guardrail 27 |
| `deep_technical_research` | Deeper technical research with five planned queries and eight retrieved documents | 151 | Input 1; Prompt 20; LLM 20; Tool 32; Retriever 12; Guardrail 32 |

## Summary Statistics

| Statistic | Value |
|---|---:|
| Scenario count | 5 |
| Total generated span instances | 479 |
| Average generated span count per scenario | 95.80 |
| Minimum generated span count | 59 |
| Maximum generated span count | 151 |

## Span Kind Breakdown

| Scenario | Total spans | AGENT | CHAIN | PROMPT | LLM | TOOL | RETRIEVER | GUARDRAIL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `short_research` | 59 | 1 | 13 | 8 | 8 | 13 | 4 | 12 |
| `multi_source_research` | 82 | 1 | 18 | 11 | 11 | 18 | 6 | 17 |
| `empty_retrieval_fallback` | 59 | 1 | 13 | 8 | 8 | 13 | 4 | 12 |
| `broad_market_research` | 128 | 1 | 28 | 17 | 17 | 28 | 10 | 27 |
| `deep_technical_research` | 151 | 1 | 33 | 20 | 20 | 33 | 12 | 32 |


