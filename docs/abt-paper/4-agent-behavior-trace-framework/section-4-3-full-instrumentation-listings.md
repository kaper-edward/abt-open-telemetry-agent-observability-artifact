# Section 4.3 Supporting Data: Full Instrumentation Listings

This document preserves the full ABT-style and direct OI/Otel-style instrumentation listings from Section 4.3. The main paper uses abbreviated excerpts for readability.

## 4.3 Agent Behavior Trace Instrumentation Example

This section uses a simplified Customer Support Agent behavior as a running example. The agent receives a shipping-related user request, classifies the request, invokes another agent to obtain order information, validates the order result through an MCP tool, retrieves shipping-policy information through an MCP resource, and generates a grounded response. The example includes the key ABT Model elements described in Section 3: Agent, Trace, Task, Block, concrete TraceAction types, and TraceAction target context. Listing 4.3 shows the behavior using ABT-style instrumentation.

*Listing 4.3. ABT-style behavior instrumentation.*

```python
with abt.agent("customer_support_agent", user_id=user_id) as agent:
    # ABT represents the Agent -> Trace -> Task -> Block hierarchy in code.
    with agent.trace("request_trace", input_value=message) as trace:
        with trace.task("handle_shipping_request") as task:
            with task.block("classify_and_extract") as classification:
                prompt = classification.prompt("intent_extraction_prompt")
                prompt.template("Classify request: {message}")
                prompt.variables({"message": message})
                # prompt_text is returned by the agent's prompt-construction logic.
                prompt.complete(output=prompt_text)

                llm = classification.llm("intent_extraction")
                # Action-level methods record behavior semantics without OI attribute keys.
                llm.model_name("qwen3:4b")
                llm.target(
                    location=ActionTargetLocation.REMOTE,
                    target_type=ActionTargetType.MODEL_PROVIDER,
                    target_subtype=ActionTargetSubtype.REMOTE_LLM_API,
                    target_name="qwen3:4b",
                    invocation_protocol=ActionInvocationProtocol.HTTPS,
                )
                llm.input(prompt_text)
                # intent_result is the actual result returned by the LLM invocation.
                llm.complete(output=intent_result)

                guardrail = classification.guardrail("validate_intent")
                guardrail.input(intent_result)
                guardrail.decision(GuardrailDecision.PASS)
                # The guardrail output records the validated result.
                guardrail.complete(output=intent_result)

            with task.block("order_lookup") as lookup:
                tool = lookup.tool("consult_order_agent")
                tool.target(
                    location=ActionTargetLocation.REMOTE,
                    target_type=ActionTargetType.AGENT,
                    target_name="order_status_agent",
                    invocation_protocol=ActionInvocationProtocol.A2A,
                )
                tool.input({"customer_id": customer_id, "order_id": order_id})
                # order is the actual result returned by the remote order agent.
                tool.complete(output=order)

                guardrail = lookup.guardrail("validate_order_result")
                guardrail.target(
                    location=ActionTargetLocation.REMOTE,
                    target_type=ActionTargetType.MCP_PROVIDER,
                    target_subtype=ActionTargetSubtype.MCP_TOOL,
                    target_name="order_policy_checker",
                    invocation_protocol=ActionInvocationProtocol.MCP,
                )
                guardrail.input(order)
                guardrail.decision(GuardrailDecision.PASS)
                # The guardrail output records the validated tool result.
                guardrail.complete(output=order)

            with task.block("policy_retrieval") as policy:
                retriever = policy.retriever("retrieve_shipping_policy")
                retriever.target(
                    location=ActionTargetLocation.REMOTE,
                    target_type=ActionTargetType.MCP_PROVIDER,
                    target_subtype=ActionTargetSubtype.MCP_RESOURCE,
                    target_name="shipping_policy_docs",
                    invocation_protocol=ActionInvocationProtocol.MCP,
                )
                retriever.query(policy_query)
                retriever.documents(policy_docs)
                # policy_docs is the actual set of retrieved policy documents.
                retriever.complete(output=policy_docs)

            with task.block("response_generation") as response_block:
                prompt = response_block.prompt("response_generation_prompt")
                prompt.template("Answer with order and policy context: {context}")
                prompt.variables({"context": response_context})
                # response_prompt_text is returned by the prompt-construction logic.
                prompt.complete(output=response_prompt_text)

                llm = response_block.llm("response_generation")
                llm.model_name("qwen3:4b")
                llm.target(
                    location=ActionTargetLocation.REMOTE,
                    target_type=ActionTargetType.MODEL_PROVIDER,
                    target_subtype=ActionTargetSubtype.REMOTE_LLM_API,
                    target_name="qwen3:4b",
                    invocation_protocol=ActionInvocationProtocol.HTTPS,
                )
                llm.input(response_prompt_text)
                # response is the actual result returned by the LLM invocation.
                llm.complete(output=response)

                guardrail = response_block.guardrail("response_grounding")
                guardrail.input(response)
                guardrail.decision(GuardrailDecision.PASS)
                # grounded_response is the validated final answer.
                guardrail.complete(output=grounded_response)

            # The outputs of enclosing Block, Task, Trace, and Agent elements
            # can be derived from completed child actions.
```

In Listing 4.3, the trace hierarchy is expressed as containment among ABT elements rather than as direct span-construction code. The call agent.trace() creates a request-level Trace under the Agent, trace.task() creates a processing unit under the Trace, and task.block() represents a logical behavior scope inside the Task. Action-specific operations such as prompt.template(), llm.model_name(), tool.target(), retriever.documents(), and guardrail.decision() express concrete agent behavior directly at the API level. The target() calls also show that ABT can record whether an action invokes a remote model provider, another agent through A2A, an MCP tool, or an MCP resource without changing the Agent-Trace-Task-Block hierarchy.

Listing 4.4 shows an abbreviated direct OI/Otel-style instrumentation for the same behavior. The listing keeps the same behavior sequence as Listing 4.3 and illustrates the additional span-kind, attribute, metadata, and structural-output assignments that must be represented directly when the ABT Framework is not used.

*Listing 4.4. Direct OI/Otel-style instrumentation of the same behavior.*

```python
with tracer.start_as_current_span("agent.customer_support_agent") as agent_span:
    # Direct OI/Otel instrumentation reconstructs the hierarchy using nested spans.
    agent_span.set_attribute("openinference.span.kind", "AGENT")
    agent_span.set_attribute("user.id", "C001")

    with tracer.start_as_current_span("trace.request") as trace_span:
        # Span kinds and attributes must be specified explicitly.
        trace_span.set_attribute("openinference.span.kind", "CHAIN")
        trace_span.set_attribute("input.value", message)

        with tracer.start_as_current_span("task.handle_shipping_request") as task_span:
            task_span.set_attribute("openinference.span.kind", "CHAIN")
            task_span.set_attribute("input.value", message)

            with tracer.start_as_current_span("block.classify_and_extract") as block_span:
                block_span.set_attribute("openinference.span.kind", "CHAIN")

                with tracer.start_as_current_span("prompt.intent_extraction_prompt") as prompt_span:
                    prompt_span.set_attribute("openinference.span.kind", "PROMPT")
                    prompt_span.set_attribute("input.value", {"message": message})
                    prompt_span.set_attribute("output.value", prompt_text)

                with tracer.start_as_current_span("llm.intent_extraction") as model_span:
                    model_span.set_attribute("openinference.span.kind", "LLM")
                    # Behavior semantics are recorded through OpenInference attribute keys.
                    model_span.set_attribute("llm.model_name", "qwen3:4b")
                    model_span.set_attribute("metadata", {
                        "abt": {
                            "target": {"location": "remote", "type": "model_provider", "subtype": "remote_llm_api", "name": "qwen3:4b"},
                            "invocation": {"protocol": "https"},
                        }
                    })
                    model_span.set_attribute("input.value", prompt_text)
                    model_span.set_attribute("output.value", intent_result)

                with tracer.start_as_current_span("guardrail.validate_intent") as guardrail_span:
                    guardrail_span.set_attribute("openinference.span.kind", "GUARDRAIL")
                    guardrail_span.set_attribute("input.value", intent_result)
                    # ABT-level additional information must be constructed as metadata.
                    guardrail_span.set_attribute("metadata", {
                        "abt": {"guardrail": {"decision": "pass"}}
                    })
                    guardrail_span.set_attribute("output.value", intent_result)

                # Structural output must be explicitly copied to enclosing spans.
                block_span.set_attribute("output.value", intent_result)

            with tracer.start_as_current_span("block.order_lookup") as block_span:
                block_span.set_attribute("openinference.span.kind", "CHAIN")

                with tracer.start_as_current_span("tool.consult_order_agent") as tool_span:
                    tool_span.set_attribute("openinference.span.kind", "TOOL")
                    tool_span.set_attribute(
                        "input.value",
                        {"customer_id": customer_id, "order_id": order_id},
                    )
                    tool_span.set_attribute("metadata", {
                        "abt": {
                            "target": {"location": "remote", "type": "agent", "name": "order_status_agent"},
                            "invocation": {"protocol": "a2a"},
                        }
                    })
                    tool_span.set_attribute("output.value", order)

                with tracer.start_as_current_span("guardrail.validate_order_result") as guardrail_span:
                    guardrail_span.set_attribute("openinference.span.kind", "GUARDRAIL")
                    guardrail_span.set_attribute("input.value", order)
                    guardrail_span.set_attribute("metadata", {
                        "abt": {
                            "target": {"location": "remote", "type": "mcp_provider", "subtype": "mcp_tool", "name": "order_policy_checker"},
                            "invocation": {"protocol": "mcp"},
                            "guardrail": {"decision": "pass"},
                        }
                    })
                    guardrail_span.set_attribute("output.value", order)

                block_span.set_attribute("output.value", order)

            with tracer.start_as_current_span("block.policy_retrieval") as block_span:
                block_span.set_attribute("openinference.span.kind", "CHAIN")

                with tracer.start_as_current_span("retriever.retrieve_shipping_policy") as retriever_span:
                    retriever_span.set_attribute("openinference.span.kind", "RETRIEVER")
                    retriever_span.set_attribute("input.value", policy_query)
                    retriever_span.set_attribute("metadata", {
                        "abt": {
                            "target": {"location": "remote", "type": "mcp_provider", "subtype": "mcp_resource", "name": "shipping_policy_docs"},
                            "invocation": {"protocol": "mcp"},
                        }
                    })
                    retriever_span.set_attribute("output.value", policy_docs)

                block_span.set_attribute("output.value", policy_docs)

            with tracer.start_as_current_span("block.response_generation") as block_span:
                block_span.set_attribute("openinference.span.kind", "CHAIN")

                with tracer.start_as_current_span("prompt.response_generation_prompt") as prompt_span:
                    prompt_span.set_attribute("openinference.span.kind", "PROMPT")
                    prompt_span.set_attribute("input.value", {"context": response_context})
                    prompt_span.set_attribute("output.value", response_prompt_text)

                with tracer.start_as_current_span("llm.response_generation") as model_span:
                    model_span.set_attribute("openinference.span.kind", "LLM")
                    model_span.set_attribute("llm.model_name", "qwen3:4b")
                    model_span.set_attribute("metadata", {
                        "abt": {
                            "target": {"location": "remote", "type": "model_provider", "subtype": "remote_llm_api", "name": "qwen3:4b"},
                            "invocation": {"protocol": "https"},
                        }
                    })
                    model_span.set_attribute("input.value", response_prompt_text)
                    model_span.set_attribute("output.value", response)

                with tracer.start_as_current_span("guardrail.response_grounding") as guardrail_span:
                    guardrail_span.set_attribute("openinference.span.kind", "GUARDRAIL")
                    guardrail_span.set_attribute("input.value", response)
                    guardrail_span.set_attribute("metadata", {
                        "abt": {"guardrail": {"decision": "pass"}}
                    })
                    guardrail_span.set_attribute("output.value", grounded_response)

                block_span.set_attribute("output.value", grounded_response)

            task_span.set_attribute("output.value", grounded_response)
        trace_span.set_attribute("output.value", grounded_response)
    agent_span.set_attribute("output.value", grounded_response)
```

The difference between the two listings illustrates the role of the ABT Framework. In Listing 4.3, the hierarchy of agent behavior is represented directly through Agent, Trace, Task, Block, and TraceAction. In Listing 4.4, the same hierarchy must be reconstructed using nested span scopes and repeated CHAIN span kind assignments. In Listing 4.3, structural input and output can be derived from completed child actions. In Listing 4.4, output values must be explicitly copied to enclosing spans. Finally, Listing 4.3 uses behavior-level operations such as llm.model_name(), tool.target(), retriever.target(), and guardrail.decision(), whereas Listing 4.4 requires model-provider calls, A2A agent calls, MCP tool invocations, MCP resource access, and guardrail decisions to be translated directly into OpenInference attribute keys and ABT metadata structures.
