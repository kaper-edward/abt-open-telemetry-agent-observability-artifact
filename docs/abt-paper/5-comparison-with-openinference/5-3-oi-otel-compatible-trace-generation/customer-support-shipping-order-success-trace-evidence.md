# Customer Support Trace Evidence: Shipping Order Success

This document records a representative ABT-generated OI/Otel trace for one Customer Support Agent scenario. It complements the aggregate coverage results in Tables 9 and 10 by showing an actual trace hierarchy and the backend-export verification procedure for a single scenario.

## Scope

| Item | Value |
|---|---|
| Target agent | Customer Support Agent |
| Instrumentation variant | ABT Framework |
| Scenario | `shipping_order_success` |
| User message | `Where is order O1001?` |
| Customer ID | `C001` |
| Session ID | `S-shipping` |
| Export mode used for text evidence | `MemoryExportTarget` |
| Generated span count | 22 |
| Observed span kinds | AGENT, CHAIN, TOOL, PROMPT, LLM, GUARDRAIL, EVALUATOR |

## Reproduction Command for Text Trace

Run from the project root:

```powershell
$env:PYTHONPATH='src'
@'
from experiments.agent_trace_experiments.comparison_runner import TraceComparisonRunner

spans = TraceComparisonRunner()._run_abt_for_comparison("shipping_order_success")
children = {}
for span in spans:
    parent_id = span.parent.span_id if span.parent else None
    children.setdefault(parent_id, []).append(span)
for sibling_spans in children.values():
    sibling_spans.sort(key=lambda span: span.start_time)

def kind(span):
    return span.attributes.get("openinference.span.kind")

def render(span, depth=0):
    attrs = span.attributes
    fields = [f"kind={kind(span)}"]
    if "metadata" in attrs:
        fields.append("metadata=yes")
    for key in ("input.value", "output.value", "llm.model_name"):
        if key in attrs:
            value = str(attrs[key]).replace("\n", " ")[:80]
            fields.append(f"{key}={value}")
    print("  " * depth + f"- {span.name} ({'; '.join(fields)})")
    for child in children.get(span.context.span_id, []):
        render(child, depth + 1)

print(f"span_count={len(spans)}")
for root in children.get(None, []):
    render(root)
'@ | .\.venv\Scripts\python.exe -
```

## Generated Trace Summary

```text
span_count=22
- agent.customer_support_agent (kind=AGENT; metadata=yes; input.value=Where is order O1001?; output.value=Order O1001 is shipped.)
  - trace.request (kind=CHAIN; metadata=yes; input.value=Where is order O1001?; output.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001)
    - input.initial (kind=TOOL; metadata=yes; output.value=Where is order O1001?)
    - task.classify_and_extract (kind=CHAIN; metadata=yes; input.value=Prompt(role='Customer-support intent classifier and order ID extractor.', policy; output.value={"intent_prompt":"Prompt(role='Customer-support intent classifier and order ID e)
      - prompt.intent_extraction (kind=PROMPT; metadata=yes; output.value=Prompt(role='Customer-support intent classifier and order ID extractor.', policy)
      - llm.intent_extraction (kind=LLM; metadata=yes; input.value=Prompt(role='Customer-support intent classifier and order ID extractor.', policy; output.value={"intent":"shipping","order_id":"O1001"}; llm.model_name=qwen3:4b)
      - guardrail.validate_intent_output (kind=GUARDRAIL; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"intent_valid":true})
    - task.route_request (kind=CHAIN; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"route":"order"})
      - guardrail.route_decision (kind=GUARDRAIL; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"route":"order"})
    - task.order_lookup_branch (kind=CHAIN; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"order":"Order(id='O1001', customer_id='C001', status='shipped', product='Wirel)
      - tool.lookup_order (kind=TOOL; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"order":"Order(id='O1001', customer_id='C001', status='shipped', product='Wirel)
      - guardrail.validate_order_result (kind=GUARDRAIL; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"order_result_route":"policy_decision_branch","order_result_valid":true})
    - task.policy_decision_branch (kind=CHAIN; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"decision":"PolicyDecision(outcome='not_applicable', reason_code='informational)
      - guardrail.policy_decision (kind=GUARDRAIL; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"policy_decision_route":"response_generation_branch"})
    - task.response_generation_branch (kind=CHAIN; metadata=yes; input.value=Prompt(role='Concise customer-support agent.', policy='Use only supplied order f; output.value={"response_prompt":"Prompt(role='Concise customer-support agent.', policy='Use o)
      - prompt.response_generation (kind=PROMPT; metadata=yes; output.value=Prompt(role='Concise customer-support agent.', policy='Use only supplied order f)
      - llm.response_generation (kind=LLM; metadata=yes; input.value=Prompt(role='Concise customer-support agent.', policy='Use only supplied order f; output.value={"response":"Order O1001 is shipped."}; llm.model_name=qwen3:4b)
      - guardrail.response_grounding (kind=GUARDRAIL; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"response_grounded":true,"response_grounding_route":"pass"})
    - task.answer_evaluation_branch (kind=CHAIN; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"answer_quality_route":"finalize_branch"})
      - evaluator.answer_quality (kind=EVALUATOR; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"answer_quality_route":"finalize_branch"})
    - task.finalize_branch (kind=CHAIN; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"tool_calls":[{"name":"lookup_order","arguments":{"customer_id":"C001","order_i)
      - tool.finalize_response (kind=TOOL; metadata=yes; input.value={"message":"Where is order O1001?","session_id":"S-shipping","customer_id":"C001; output.value={"tool_calls":[{"name":"lookup_order","arguments":{"customer_id":"C001","order_i)
```

## Phoenix Export Verification Procedure

The same scenario can be exported to a Phoenix backend through the ABT `NetworkExportTarget`, because Phoenix receives OpenTelemetry traces through an OTLP HTTP endpoint.

1. Start Phoenix locally.

```powershell
python -m phoenix.server.main serve
```

2. In another terminal, set the OTLP endpoint.

```powershell
$env:PYTHONPATH='src'
$env:OTLP_ENDPOINT='http://127.0.0.1:6006/v1/traces'
```

3. Run the Customer Support Agent in ABT mode with network export enabled, or adapt the command above to use `ExportTargetFactory().create_network_export_target(...)` instead of `create_memory_export_target(...)`.

4. Open Phoenix at `http://127.0.0.1:6006` and confirm that the trace contains:

| Expected item | Verification criterion |
|---|---|
| Service name | ABT Customer Support service name is visible in Phoenix. |
| Root span | `agent.customer_support_agent` appears as the root AGENT span. |
| Request trace | `trace.request` appears as a CHAIN child of the root span. |
| Task spans | CHAIN spans such as `task.classify_and_extract`, `task.order_lookup_branch`, and `task.response_generation_branch` are present. |
| Action spans | PROMPT, LLM, TOOL, GUARDRAIL, and EVALUATOR spans are visible under their corresponding task spans. |
| Attributes | `openinference.span.kind`, `input.value`, `output.value`, `metadata`, and LLM attributes are visible on corresponding spans. |

## Optional Screenshot Evidence

If Phoenix is used during artifact verification, save a screenshot of the trace tree to:

```text
docs/abt-paper/5-comparison-with-openinference/5-3-oi-otel-compatible-trace-generation/phoenix-customer-support-shipping-order-success.png
```

The screenshot should show the root `agent.customer_support_agent` span and at least the `trace.request`, `task.classify_and_extract`, `llm.intent_extraction`, `tool.lookup_order`, and `guardrail.response_grounding` spans.
