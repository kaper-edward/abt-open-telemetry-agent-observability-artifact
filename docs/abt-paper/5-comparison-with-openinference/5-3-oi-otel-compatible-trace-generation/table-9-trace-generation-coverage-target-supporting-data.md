# Table 9 Supporting Data: Coverage Target for OI/Otel-Compatible Trace Generation

This document records the coverage target used in Table 9, "Coverage target for OI/Otel-compatible trace generation."

## Counting Rules

The OpenInference span-kind vocabulary used for Table 9 contains ten semantic span kinds. The fallback `UNKNOWN` enum value is excluded because it is not an evaluated semantic span kind.

```text
AGENT, CHAIN, EMBEDDING, EVALUATOR, GUARDRAIL, LLM, PROMPT, RERANKER, RETRIEVER, TOOL
```

Attribute-key coverage is counted over span-kind-specific normalized attribute keys. The span kind is part of the target key, so `TOOL.input.value` and `GUARDRAIL.input.value` are counted as different targets. Numeric indexes are normalized to `*`; for example, `llm.input_messages.0.message.role` is normalized to `llm.input_messages.*.message.role`.

The span-kind-specific attribute-key target universe contains 79 normalized targets. This universe is the set of concrete OpenInference-compatible attribute keys implemented and checked by the evaluated `ABTToOpenInferenceSemanticMapper` under `capture_message_content=True`; it is not a claim about all possible OpenInference attributes.

## Span-Kind-Specific Attribute-Key Targets

| Span kind | Attribute-key target count | Attribute-key targets |
|---|---:|---|
| AGENT | 7 | `input.mime_type`; `input.value`; `metadata`; `output.mime_type`; `output.value`; `session.id`; `user.id` |
| CHAIN | 5 | `input.mime_type`; `input.value`; `metadata`; `output.mime_type`; `output.value` |
| EMBEDDING | 6 | `embedding.model_name`; `input.mime_type`; `input.value`; `metadata`; `output.mime_type`; `output.value` |
| EVALUATOR | 5 | `input.mime_type`; `input.value`; `metadata`; `output.mime_type`; `output.value` |
| GUARDRAIL | 5 | `input.mime_type`; `input.value`; `metadata`; `output.mime_type`; `output.value` |
| LLM | 13 | `input.mime_type`; `input.value`; `llm.input_messages.*.message.content`; `llm.input_messages.*.message.role`; `llm.invocation_parameters`; `llm.model_name`; `llm.output_messages.*.message.content`; `llm.output_messages.*.message.role`; `llm.provider`; `llm.system`; `metadata`; `output.mime_type`; `output.value` |
| PROMPT | 7 | `input.mime_type`; `input.value`; `llm.prompt_template.template`; `llm.prompt_template.variables`; `metadata`; `output.mime_type`; `output.value` |
| RERANKER | 15 | `input.mime_type`; `input.value`; `metadata`; `output.mime_type`; `output.value`; `reranker.input_documents.*.document.content`; `reranker.input_documents.*.document.id`; `reranker.input_documents.*.document.metadata`; `reranker.input_documents.*.document.score`; `reranker.output_documents.*.document.content`; `reranker.output_documents.*.document.id`; `reranker.output_documents.*.document.metadata`; `reranker.output_documents.*.document.score`; `reranker.query`; `reranker.top_k` |
| RETRIEVER | 9 | `input.mime_type`; `input.value`; `metadata`; `output.mime_type`; `output.value`; `retrieval.documents.*.document.content`; `retrieval.documents.*.document.id`; `retrieval.documents.*.document.metadata`; `retrieval.documents.*.document.score` |
| TOOL | 7 | `input.mime_type`; `input.value`; `metadata`; `output.mime_type`; `output.value`; `tool.name`; `tool.parameters` |
| Total | 79 | Span-kind-specific concrete attribute-key targets |
