# Table 10 Supporting Data: Coverage of OI/Otel-Compatible Trace Generation by Target Agent

This document records supporting data for Table 10, which reports OI/Otel-compatible trace-generation coverage by target agent. The trace-generation coverage target is defined separately in the Table 9 supporting-data document. Detailed instance counts are retained below as supporting data.

## Measurement Command

```powershell
$env:PYTHONPATH='src'
python -X utf8 .\src\experiments\agent_trace_experiments\validation_surface_measurement.py
```

## Counting Rules

Span-kind checks count generated spans by OpenInference span kind. The denominator excludes the fallback `UNKNOWN` value.

Structural comparison counts are retained as supporting data:

- `span identity`: generated spans matched by stable span name and occurrence index.
- `span kind mapping`: spans whose OpenInference span kind was compared.
- `parent-child`: non-root span parent relationships.
- `sibling ordering`: ordered sibling relations under the same parent.

Attribute-key checks count span-kind-specific normalized attribute keys. The span kind is part of the target key, so `TOOL.input.value` and `GUARDRAIL.input.value` are counted as different targets. Numeric indexes are normalized to `*`; for example, `llm.input_messages.0.message.role` is normalized to `llm.input_messages.*.message.role`.

## Attribute-Key Coverage Matrix

The following matrix records which target agent exercised each span-kind-specific attribute-key target. `Y` means that at least one generated span of the target agent contained the corresponding normalized attribute key under the corresponding span kind.

| Span kind | Attribute key | Customer support | Open Deep Research | CrewAI | AutoGen | SWE-agent |
|---|---|---:|---:|---:|---:|---:|
| AGENT | `input.mime_type` | Y | Y | Y | Y | Y |
| AGENT | `input.value` | Y | Y | Y | Y | Y |
| AGENT | `metadata` | Y | Y | Y | Y | Y |
| AGENT | `output.mime_type` | Y | Y | Y | Y | Y |
| AGENT | `output.value` | Y | Y | Y | Y | Y |
| AGENT | `session.id` | Y | Y | Y | Y | Y |
| AGENT | `user.id` | Y | Y | Y | Y | Y |
| CHAIN | `input.mime_type` | Y | Y | Y | Y | Y |
| CHAIN | `input.value` | Y | Y | Y | Y | Y |
| CHAIN | `metadata` | Y | Y | Y | Y | Y |
| CHAIN | `output.mime_type` | Y | Y | Y | Y | Y |
| CHAIN | `output.value` | Y | Y | Y | Y | Y |
| EMBEDDING | `embedding.model_name` | Y | - | - | - | - |
| EMBEDDING | `input.mime_type` | Y | - | - | - | - |
| EMBEDDING | `input.value` | Y | - | - | - | - |
| EMBEDDING | `metadata` | Y | - | - | - | - |
| EMBEDDING | `output.mime_type` | Y | - | - | - | - |
| EMBEDDING | `output.value` | Y | - | - | - | - |
| EVALUATOR | `input.mime_type` | Y | - | Y | Y | - |
| EVALUATOR | `input.value` | Y | - | Y | Y | - |
| EVALUATOR | `metadata` | Y | - | Y | Y | - |
| EVALUATOR | `output.mime_type` | Y | - | Y | Y | - |
| EVALUATOR | `output.value` | Y | - | Y | Y | - |
| GUARDRAIL | `input.mime_type` | Y | Y | Y | Y | Y |
| GUARDRAIL | `input.value` | Y | Y | Y | Y | Y |
| GUARDRAIL | `metadata` | Y | Y | Y | Y | Y |
| GUARDRAIL | `output.mime_type` | Y | Y | Y | Y | Y |
| GUARDRAIL | `output.value` | Y | Y | Y | Y | Y |
| LLM | `input.mime_type` | Y | Y | Y | Y | Y |
| LLM | `input.value` | Y | Y | Y | Y | Y |
| LLM | `llm.input_messages.*.message.content` | Y | - | - | - | - |
| LLM | `llm.input_messages.*.message.role` | Y | - | - | - | - |
| LLM | `llm.invocation_parameters` | Y | - | - | - | - |
| LLM | `llm.model_name` | Y | Y | Y | Y | Y |
| LLM | `llm.output_messages.*.message.content` | Y | - | - | - | - |
| LLM | `llm.output_messages.*.message.role` | Y | - | - | - | - |
| LLM | `llm.provider` | Y | - | - | - | - |
| LLM | `llm.system` | Y | - | - | - | - |
| LLM | `metadata` | Y | Y | Y | Y | Y |
| LLM | `output.mime_type` | Y | Y | Y | Y | Y |
| LLM | `output.value` | Y | Y | Y | Y | Y |
| PROMPT | `input.mime_type` | - | Y | Y | Y | Y |
| PROMPT | `input.value` | - | Y | Y | Y | Y |
| PROMPT | `llm.prompt_template.template` | Y | Y | Y | Y | Y |
| PROMPT | `llm.prompt_template.variables` | Y | Y | Y | Y | Y |
| PROMPT | `metadata` | Y | Y | Y | Y | Y |
| PROMPT | `output.mime_type` | Y | Y | Y | Y | Y |
| PROMPT | `output.value` | Y | Y | Y | Y | Y |
| RERANKER | `input.mime_type` | Y | - | - | - | - |
| RERANKER | `input.value` | Y | - | - | - | - |
| RERANKER | `metadata` | Y | - | - | - | - |
| RERANKER | `output.mime_type` | Y | - | - | - | - |
| RERANKER | `output.value` | Y | - | - | - | - |
| RERANKER | `reranker.input_documents.*.document.content` | Y | - | - | - | - |
| RERANKER | `reranker.input_documents.*.document.id` | Y | - | - | - | - |
| RERANKER | `reranker.input_documents.*.document.metadata` | Y | - | - | - | - |
| RERANKER | `reranker.input_documents.*.document.score` | Y | - | - | - | - |
| RERANKER | `reranker.output_documents.*.document.content` | Y | - | - | - | - |
| RERANKER | `reranker.output_documents.*.document.id` | Y | - | - | - | - |
| RERANKER | `reranker.output_documents.*.document.metadata` | Y | - | - | - | - |
| RERANKER | `reranker.output_documents.*.document.score` | Y | - | - | - | - |
| RERANKER | `reranker.query` | Y | - | - | - | - |
| RERANKER | `reranker.top_k` | Y | - | - | - | - |
| RETRIEVER | `input.mime_type` | Y | Y | - | - | Y |
| RETRIEVER | `input.value` | Y | Y | - | - | Y |
| RETRIEVER | `metadata` | Y | Y | - | - | Y |
| RETRIEVER | `output.mime_type` | Y | Y | - | - | Y |
| RETRIEVER | `output.value` | Y | Y | - | - | Y |
| RETRIEVER | `retrieval.documents.*.document.content` | Y | Y | - | - | Y |
| RETRIEVER | `retrieval.documents.*.document.id` | Y | Y | - | - | Y |
| RETRIEVER | `retrieval.documents.*.document.metadata` | Y | Y | - | - | Y |
| RETRIEVER | `retrieval.documents.*.document.score` | Y | Y | - | - | Y |
| TOOL | `input.mime_type` | Y | Y | Y | Y | Y |
| TOOL | `input.value` | Y | Y | Y | Y | Y |
| TOOL | `metadata` | Y | Y | Y | Y | Y |
| TOOL | `output.mime_type` | Y | Y | Y | Y | Y |
| TOOL | `output.value` | Y | Y | Y | Y | Y |
| TOOL | `tool.name` | Y | Y | Y | Y | Y |
| TOOL | `tool.parameters` | Y | - | - | - | - |

The structural checkpoint vocabulary contains four checkpoint types:

```text
span identity, span kind, parent-child, sibling ordering
```

## Paper Table

| Target agent | Validation purpose | OpenInference span kinds exercised | Span-kind-specific attribute keys exercised |
|---|---|---|---|
| Customer Support Agent | Broad ABT Action-type and span-kind exercise | 10/10: AGENT, CHAIN, EMBEDDING, EVALUATOR, GUARDRAIL, LLM, PROMPT, RERANKER, RETRIEVER, TOOL | 77/79 |
| Open Deep Research | Public LangGraph graph and research-action validation | 7/10: AGENT, CHAIN, GUARDRAIL, LLM, PROMPT, RETRIEVER, TOOL | 45/79 |
| CrewAI Write-a-Book Flow | Public CrewAI flow-orchestration validation | 7/10: AGENT, CHAIN, EVALUATOR, GUARDRAIL, LLM, PROMPT, TOOL | 41/79 |
| AutoGen Distributed Group Chat | Public AutoGen multi-agent conversation validation | 7/10: AGENT, CHAIN, EVALUATOR, GUARDRAIL, LLM, PROMPT, TOOL | 41/79 |
| SWE-agent Core Execution | Public software-engineering execution-loop validation | 7/10: AGENT, CHAIN, GUARDRAIL, LLM, PROMPT, RETRIEVER, TOOL | 45/79 |
| Overall evaluated scope | Union across all target agents | 10/10: AGENT, CHAIN, EMBEDDING, EVALUATOR, GUARDRAIL, LLM, PROMPT, RERANKER, RETRIEVER, TOOL | 79/79 |

## Detailed Instance Counts

| Target agent | Validation purpose | Span-kind instance counts | Structural instance counts | Attribute-key instance counts |
|---|---|---|---|---|
| Customer support agent | Broad ABT Action-type and span-kind exercise | AGENT 8; CHAIN 59; EMBEDDING 3; EVALUATOR 2; GUARDRAIL 37; LLM 13; PROMPT 13; RERANKER 3; RETRIEVER 3; TOOL 23 | parent-child 156; sibling ordering 89; span identity 164; span kind mapping 164 | AGENT.input.mime_type 8; AGENT.input.value 8; AGENT.metadata 8; AGENT.output.mime_type 8; AGENT.output.value 8; AGENT.session.id 8; AGENT.user.id 8; CHAIN.input.mime_type 59; CHAIN.input.value 59; CHAIN.metadata 59; CHAIN.output.mime_type 59; CHAIN.output.value 59; EMBEDDING.embedding.model_name 3; EMBEDDING.input.mime_type 3; EMBEDDING.input.value 3; EMBEDDING.metadata 3; EMBEDDING.output.mime_type 3; EMBEDDING.output.value 3; EVALUATOR.input.mime_type 2; EVALUATOR.input.value 2; EVALUATOR.metadata 2; EVALUATOR.output.mime_type 2; EVALUATOR.output.value 2; GUARDRAIL.input.mime_type 37; GUARDRAIL.input.value 37; GUARDRAIL.metadata 37; GUARDRAIL.output.mime_type 37; GUARDRAIL.output.value 37; LLM.input.mime_type 13; LLM.input.value 13; LLM.llm.input_messages.*.message.content 13; LLM.llm.input_messages.*.message.role 13; LLM.llm.invocation_parameters 13; LLM.llm.model_name 13; LLM.llm.output_messages.*.message.content 13; LLM.llm.output_messages.*.message.role 13; LLM.llm.provider 13; LLM.llm.system 13; LLM.metadata 13; LLM.output.mime_type 13; LLM.output.value 13; PROMPT.llm.prompt_template.template 13; PROMPT.llm.prompt_template.variables 13; PROMPT.metadata 13; PROMPT.output.mime_type 13; PROMPT.output.value 13; RERANKER.input.mime_type 3; RERANKER.input.value 3; RERANKER.metadata 3; RERANKER.output.mime_type 3; RERANKER.output.value 3; RERANKER.reranker.input_documents.*.document.content 2; RERANKER.reranker.input_documents.*.document.id 2; RERANKER.reranker.input_documents.*.document.metadata 2; RERANKER.reranker.input_documents.*.document.score 2; RERANKER.reranker.output_documents.*.document.content 2; RERANKER.reranker.output_documents.*.document.id 2; RERANKER.reranker.output_documents.*.document.metadata 2; RERANKER.reranker.output_documents.*.document.score 2; RERANKER.reranker.query 3; RERANKER.reranker.top_k 3; RETRIEVER.input.mime_type 3; RETRIEVER.input.value 3; RETRIEVER.metadata 3; RETRIEVER.output.mime_type 3; RETRIEVER.output.value 3; RETRIEVER.retrieval.documents.*.document.content 2; RETRIEVER.retrieval.documents.*.document.id 2; RETRIEVER.retrieval.documents.*.document.metadata 2; RETRIEVER.retrieval.documents.*.document.score 2; TOOL.input.mime_type 15; TOOL.input.value 15; TOOL.metadata 23; TOOL.output.mime_type 23; TOOL.output.value 23; TOOL.tool.name 23; TOOL.tool.parameters 7 |
| Open Deep Research | Public LangGraph graph and research-action validation | AGENT 5; CHAIN 105; GUARDRAIL 100; LLM 64; PROMPT 64; RETRIEVER 36; TOOL 105 | parent-child 474; sibling ordering 364; span identity 479; span kind mapping 479 | AGENT.input.mime_type 5; AGENT.input.value 5; AGENT.metadata 5; AGENT.output.mime_type 5; AGENT.output.value 5; AGENT.session.id 5; AGENT.user.id 5; CHAIN.input.mime_type 105; CHAIN.input.value 105; CHAIN.metadata 105; CHAIN.output.mime_type 105; CHAIN.output.value 105; GUARDRAIL.input.mime_type 100; GUARDRAIL.input.value 100; GUARDRAIL.metadata 100; GUARDRAIL.output.mime_type 100; GUARDRAIL.output.value 100; LLM.input.mime_type 64; LLM.input.value 64; LLM.llm.model_name 64; LLM.metadata 64; LLM.output.mime_type 64; LLM.output.value 64; PROMPT.input.mime_type 64; PROMPT.input.value 64; PROMPT.llm.prompt_template.template 64; PROMPT.llm.prompt_template.variables 64; PROMPT.metadata 64; PROMPT.output.mime_type 64; PROMPT.output.value 64; RETRIEVER.input.mime_type 36; RETRIEVER.input.value 36; RETRIEVER.metadata 36; RETRIEVER.output.mime_type 36; RETRIEVER.output.value 36; RETRIEVER.retrieval.documents.*.document.content 36; RETRIEVER.retrieval.documents.*.document.id 36; RETRIEVER.retrieval.documents.*.document.metadata 36; RETRIEVER.retrieval.documents.*.document.score 36; TOOL.input.mime_type 100; TOOL.input.value 100; TOOL.metadata 105; TOOL.output.mime_type 105; TOOL.output.value 105; TOOL.tool.name 105 |
| CrewAI Write-a-Book Flow | Public CrewAI flow-orchestration validation | AGENT 3; CHAIN 38; EVALUATOR 16; GUARDRAIL 19; LLM 32; PROMPT 32; TOOL 38 | parent-child 175; sibling ordering 134; span identity 178; span kind mapping 178 | AGENT.input.mime_type 3; AGENT.input.value 3; AGENT.metadata 3; AGENT.output.mime_type 3; AGENT.output.value 3; AGENT.session.id 3; AGENT.user.id 3; CHAIN.input.mime_type 38; CHAIN.input.value 38; CHAIN.metadata 38; CHAIN.output.mime_type 38; CHAIN.output.value 38; EVALUATOR.input.mime_type 16; EVALUATOR.input.value 16; EVALUATOR.metadata 16; EVALUATOR.output.mime_type 16; EVALUATOR.output.value 16; GUARDRAIL.input.mime_type 19; GUARDRAIL.input.value 19; GUARDRAIL.metadata 19; GUARDRAIL.output.mime_type 19; GUARDRAIL.output.value 19; LLM.input.mime_type 32; LLM.input.value 32; LLM.llm.model_name 32; LLM.metadata 32; LLM.output.mime_type 32; LLM.output.value 32; PROMPT.input.mime_type 32; PROMPT.input.value 32; PROMPT.llm.prompt_template.template 32; PROMPT.llm.prompt_template.variables 32; PROMPT.metadata 32; PROMPT.output.mime_type 32; PROMPT.output.value 32; TOOL.input.mime_type 35; TOOL.input.value 35; TOOL.metadata 38; TOOL.output.mime_type 38; TOOL.output.value 38; TOOL.tool.name 38 |
| AutoGen Distributed Group Chat | Public AutoGen multi-agent conversation validation | AGENT 3; CHAIN 29; EVALUATOR 8; GUARDRAIL 18; LLM 26; PROMPT 26; TOOL 29 | parent-child 136; sibling ordering 104; span identity 139; span kind mapping 139 | AGENT.input.mime_type 3; AGENT.input.value 3; AGENT.metadata 3; AGENT.output.mime_type 3; AGENT.output.value 3; AGENT.session.id 3; AGENT.user.id 3; CHAIN.input.mime_type 29; CHAIN.input.value 29; CHAIN.metadata 29; CHAIN.output.mime_type 29; CHAIN.output.value 29; EVALUATOR.input.mime_type 8; EVALUATOR.input.value 8; EVALUATOR.metadata 8; EVALUATOR.output.mime_type 8; EVALUATOR.output.value 8; GUARDRAIL.input.mime_type 18; GUARDRAIL.input.value 18; GUARDRAIL.metadata 18; GUARDRAIL.output.mime_type 18; GUARDRAIL.output.value 18; LLM.input.mime_type 26; LLM.input.value 26; LLM.llm.model_name 26; LLM.metadata 26; LLM.output.mime_type 26; LLM.output.value 26; PROMPT.input.mime_type 26; PROMPT.input.value 26; PROMPT.llm.prompt_template.template 26; PROMPT.llm.prompt_template.variables 26; PROMPT.metadata 26; PROMPT.output.mime_type 26; PROMPT.output.value 26; TOOL.input.mime_type 26; TOOL.input.value 26; TOOL.metadata 29; TOOL.output.mime_type 29; TOOL.output.value 29; TOOL.tool.name 29 |
| SWE-agent Core Execution | Public software-engineering execution-loop validation | AGENT 11; CHAIN 299; GUARDRAIL 288; LLM 80; PROMPT 80; RETRIEVER 39; TOOL 299 | parent-child 1085; sibling ordering 775; span identity 1096; span kind mapping 1096 | AGENT.input.mime_type 11; AGENT.input.value 11; AGENT.metadata 11; AGENT.output.mime_type 11; AGENT.output.value 11; AGENT.session.id 11; AGENT.user.id 11; CHAIN.input.mime_type 299; CHAIN.input.value 299; CHAIN.metadata 299; CHAIN.output.mime_type 299; CHAIN.output.value 299; GUARDRAIL.input.mime_type 288; GUARDRAIL.input.value 288; GUARDRAIL.metadata 288; GUARDRAIL.output.mime_type 288; GUARDRAIL.output.value 288; LLM.input.mime_type 80; LLM.input.value 80; LLM.llm.model_name 80; LLM.metadata 80; LLM.output.mime_type 80; LLM.output.value 80; PROMPT.input.mime_type 80; PROMPT.input.value 80; PROMPT.llm.prompt_template.template 80; PROMPT.llm.prompt_template.variables 80; PROMPT.metadata 80; PROMPT.output.mime_type 80; PROMPT.output.value 80; RETRIEVER.input.mime_type 39; RETRIEVER.input.value 39; RETRIEVER.metadata 39; RETRIEVER.output.mime_type 39; RETRIEVER.output.value 39; RETRIEVER.retrieval.documents.*.document.content 39; RETRIEVER.retrieval.documents.*.document.id 39; RETRIEVER.retrieval.documents.*.document.metadata 39; RETRIEVER.retrieval.documents.*.document.score 39; TOOL.input.mime_type 288; TOOL.input.value 288; TOOL.metadata 299; TOOL.output.mime_type 299; TOOL.output.value 299; TOOL.tool.name 299 |

All validation runs reported zero missing spans, zero unexpected spans, and zero generated-attribute differences.


