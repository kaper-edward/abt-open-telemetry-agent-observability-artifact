from __future__ import annotations

import asyncio
import json
from contextlib import contextmanager
from typing import Any

from langgraph.graph import END, START, StateGraph
from opentelemetry import trace as otel_trace
from openinference.semconv.trace import OpenInferenceSpanKindValues
from openinference.semconv.trace import SpanAttributes

from experiments.agent_trace_experiments.direct_oi_node_recorder import DirectOiNodeRecorder
from experiments.agent_trace_experiments.semantic_node_instrumentation import (
    record_oi_semantic_actions,
)
from experiments.agent_trace_experiments.semantic_node_instrumentation import (
    semantic_profile_for_node,
)
from experiments.agent_trace_experiments.semantic_node_instrumentation import task_input_for_node
from experiments.open_deep_research_base import ResearchScenario
from experiments.open_deep_research_base.source_graph_runtime import (
    DeterministicOpenDeepResearchRuntime,
    SourceGraphEventRecorder,
)


class NodeOiOpenDeepResearchAgent:
    """Runs the original Open Deep Research source graph with node-level OI spans."""

    JSON_MIME_TYPE = "application/json"
    TEXT_MIME_TYPE = "text/plain"

    def __init__(self, *, tracer):
        self._tracer = tracer
        self._recorder = DirectOiNodeRecorder(
            tracer,
            agent_name="open_deep_research_node_level",
            trace_name="research_request",
        )
        self._runtime = DeterministicOpenDeepResearchRuntime()

    def run(self, scenario: ResearchScenario) -> dict[str, object]:
        deep_researcher_module = self._runtime._load_deep_researcher_module()
        event_recorder = SourceGraphEventRecorder()
        trace_counter = {"task_count": 0, "open_task_count": 0, "max_open_task_count": 0}
        with self._span(
            "agent.open_deep_research_node_level",
            "agent",
            OpenInferenceSpanKindValues.AGENT.value,
            metadata={"name": "open_deep_research_node_level"},
            attributes={
                SpanAttributes.SESSION_ID: f"trace-comparison-{scenario.name}",
                SpanAttributes.USER_ID: scenario.user_id,
            },
        ) as agent_span:
            self._set_input(agent_span, scenario.question)
            with self._span(
                "trace.research_request",
                "trace",
                OpenInferenceSpanKindValues.CHAIN.value,
                metadata={"name": "research_request"},
            ) as trace_span:
                self._trace_span = trace_span
                self._set_input(trace_span, scenario.question)
                self._input_initial(scenario.question)
                with self._runtime._deterministic_dependencies(
                    deep_researcher_module,
                    scenario,
                    event_recorder,
                ):
                    with self._instrumented_researcher_subgraph(
                        deep_researcher_module,
                        trace_counter,
                    ):
                        source_graph = self._build_instrumented_source_graph(
                            deep_researcher_module,
                            trace_counter,
                        )
                        output = asyncio.run(
                            source_graph.ainvoke(
                                {"messages": [("user", scenario.question)]},
                                self._runtime._config_for(scenario),
                            )
                        )
                self._merge_abt_metadata(
                    trace_span,
                    self._trace_metadata(trace_counter),
                )
                self._set_output(trace_span, output["final_report"])
            self._merge_abt_metadata(agent_span, {"trace_count": 1})
            self._set_output(agent_span, output["final_report"])
            return {
                "execution_mode": "source_graph_node_level_oi_instrumentation",
                "question": scenario.question,
                "planned_queries": list(scenario.planned_queries),
                "retrieved_documents": list(scenario.retrieved_documents),
                "compressed_summary": scenario.compressed_summary,
                "final_report": output["final_report"],
                "source_graph_events": event_recorder.events(),
                "source_graph_output": output,
            }

    @contextmanager
    def _instrumented_researcher_subgraph(
        self,
        deep_researcher_module,
        trace_counter: dict[str, int],
    ):
        original_researcher_subgraph = deep_researcher_module.researcher_subgraph
        instrumented_researcher_subgraph = self._build_instrumented_researcher_subgraph(
            deep_researcher_module,
            trace_counter,
        )
        deep_researcher_module.researcher_subgraph = instrumented_researcher_subgraph
        try:
            yield
        finally:
            deep_researcher_module.researcher_subgraph = original_researcher_subgraph

    def _build_instrumented_source_graph(
        self,
        deep_researcher_module,
        trace_counter: dict[str, int],
    ):
        supervisor_subgraph = self._build_instrumented_supervisor_subgraph(
            deep_researcher_module,
            trace_counter,
        )
        builder = StateGraph(
            deep_researcher_module.AgentState,
            input=deep_researcher_module.AgentInputState,
            config_schema=deep_researcher_module.Configuration,
        )
        builder.add_node(
            "clarify_with_user",
            self._instrument_node(
                "clarify_with_user",
                deep_researcher_module.clarify_with_user,
                trace_counter,
            ),
        )
        builder.add_node(
            "write_research_brief",
            self._instrument_node(
                "write_research_brief",
                deep_researcher_module.write_research_brief,
                trace_counter,
            ),
        )
        builder.add_node("research_supervisor", supervisor_subgraph)
        builder.add_node(
            "final_report_generation",
            self._instrument_node(
                "final_report_generation",
                deep_researcher_module.final_report_generation,
                trace_counter,
            ),
        )
        builder.add_edge(START, "clarify_with_user")
        builder.add_edge("research_supervisor", "final_report_generation")
        builder.add_edge("final_report_generation", END)
        return builder.compile()

    def _build_instrumented_supervisor_subgraph(
        self,
        deep_researcher_module,
        trace_counter: dict[str, int],
    ):
        builder = StateGraph(
            deep_researcher_module.SupervisorState,
            config_schema=deep_researcher_module.Configuration,
        )
        builder.add_node(
            "supervisor",
            self._instrument_node(
                "supervisor",
                deep_researcher_module.supervisor,
                trace_counter,
            ),
        )
        builder.add_node(
            "supervisor_tools",
            self._instrument_node(
                "supervisor_tools",
                deep_researcher_module.supervisor_tools,
                trace_counter,
            ),
        )
        builder.add_edge(START, "supervisor")
        return builder.compile()

    def _build_instrumented_researcher_subgraph(
        self,
        deep_researcher_module,
        trace_counter: dict[str, int],
    ):
        builder = StateGraph(
            deep_researcher_module.ResearcherState,
            output=deep_researcher_module.ResearcherOutputState,
            config_schema=deep_researcher_module.Configuration,
        )
        builder.add_node(
            "researcher",
            self._instrument_node(
                "researcher",
                deep_researcher_module.researcher,
                trace_counter,
            ),
        )
        builder.add_node(
            "researcher_tools",
            self._instrument_node(
                "researcher_tools",
                deep_researcher_module.researcher_tools,
                trace_counter,
            ),
        )
        builder.add_node(
            "compress_research",
            self._instrument_node(
                "compress_research",
                deep_researcher_module.compress_research,
                trace_counter,
            ),
        )
        builder.add_edge(START, "researcher")
        builder.add_edge("compress_research", END)
        return builder.compile()

    def _instrument_node(
        self,
        node_name: str,
        node_function,
        trace_counter: dict[str, int],
    ):
        async def instrumented_node(state, config):
            trace_counter["task_count"] += 1
            trace_counter["open_task_count"] += 1
            trace_counter["max_open_task_count"] = max(
                trace_counter["max_open_task_count"],
                trace_counter["open_task_count"],
            )
            with self._span(
                f"task.source_node_{node_name}",
                "task",
                OpenInferenceSpanKindValues.CHAIN.value,
                metadata={"name": f"source_node_{node_name}"},
                parent=self._trace_span,
            ) as task_span:
                state_summary = self._state_summary(state)
                self._set_input(
                    task_span,
                    task_input_for_node(node_name, state_summary),
                )
                record_oi_semantic_actions(self._recorder, node_name, state_summary)
                with self._span(
                    f"tool.execute_source_graph_node_{node_name}",
                    "tool",
                    OpenInferenceSpanKindValues.TOOL.value,
                    metadata={
                        "target": {
                            "location": "in_process",
                            "type": "function",
                            "name": node_name,
                        },
                        "invocation": {"protocol": "function_call"},
                    },
                    attributes={SpanAttributes.TOOL_NAME: node_name},
                ) as span:
                    self._set_input(span, state_summary)
                    try:
                        result = await node_function(state, config)
                    except Exception as error:
                        span.record_exception(error)
                        span.set_status(type(error).__name__)
                        raise
                    result_summary = self._result_summary(result)
                    self._set_output(span, result_summary)
                self._merge_abt_metadata(
                    task_span,
                    {
                        "block_count": 0,
                        "action_count": 1 + len(semantic_profile_for_node(node_name)),
                    },
                )
                self._set_output(task_span, result_summary)
                trace_counter["open_task_count"] -= 1
                return result

        return instrumented_node

    def _input_initial(self, question: str) -> None:
        with self._span(
            "input.initial",
            "input",
            OpenInferenceSpanKindValues.TOOL.value,
            metadata={"input": {"source_type": "user", "channel": "experiment"}},
            attributes={SpanAttributes.TOOL_NAME: "receive_input"},
        ) as span:
            self._set_output(span, question)

    def _span(
        self,
        name: str,
        element_type: str,
        span_kind: str,
        *,
        metadata: dict[str, object] | None = None,
        attributes: dict[str, object] | None = None,
        parent=None,
    ):
        span_attributes = {
            SpanAttributes.OPENINFERENCE_SPAN_KIND: span_kind,
            SpanAttributes.METADATA: self._metadata(
                {"element_type": element_type, **dict(metadata or {})}
            ),
        }
        span_attributes.update(attributes or {})
        parent_context = None
        if parent is not None:
            parent_context = otel_trace.set_span_in_context(parent)
        return self._tracer.start_as_current_span(
            name,
            attributes=span_attributes,
            context=parent_context,
        )

    def _set_input(self, span, value: object) -> None:
        self._set_io(span, "input", value)

    def _set_output(self, span, value: object) -> None:
        self._set_io(span, "output", value)

    def _set_io(self, span, prefix: str, value: object) -> None:
        if isinstance(value, str):
            span.set_attribute(f"{prefix}.mime_type", self.TEXT_MIME_TYPE)
            span.set_attribute(f"{prefix}.value", value)
            return
        span.set_attribute(f"{prefix}.mime_type", self.JSON_MIME_TYPE)
        span.set_attribute(f"{prefix}.value", self._json(value))

    @classmethod
    def _metadata(cls, value: dict[str, object]) -> str:
        return cls._json({"abt": value})

    def _merge_abt_metadata(self, span, value: dict[str, object]) -> None:
        metadata = json.loads(span.attributes[SpanAttributes.METADATA])
        abt_metadata = metadata.setdefault("abt", {})
        if not isinstance(abt_metadata, dict):
            abt_metadata = {}
            metadata["abt"] = abt_metadata
        abt_metadata.update(value)
        span.set_attribute(SpanAttributes.METADATA, self._json(metadata))

    @staticmethod
    def _trace_metadata(trace_counter: dict[str, int]) -> dict[str, object]:
        metadata: dict[str, object] = {
            "initial_input_count": 1,
            "task_count": trace_counter["task_count"],
        }
        if trace_counter["max_open_task_count"] > 1:
            metadata.update(
                {
                    "allows_concurrent_children": True,
                    "max_open_child_count": trace_counter["max_open_task_count"],
                }
            )
        return metadata

    @staticmethod
    def _state_summary(state: Any) -> dict[str, object]:
        if not isinstance(state, dict):
            return {"type": type(state).__name__}
        summary: dict[str, object] = {}
        for key, value in state.items():
            if isinstance(value, list):
                summary[key] = {"type": "list", "length": len(value)}
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                summary[key] = value
                continue
            summary[key] = {"type": type(value).__name__}
        return summary

    @staticmethod
    def _result_summary(result: Any) -> dict[str, object]:
        goto = getattr(result, "goto", None)
        update = getattr(result, "update", None)
        if goto is not None or update is not None:
            return {
                "type": type(result).__name__,
                "goto": str(goto),
                "update": NodeOiOpenDeepResearchAgent._state_summary(update or {}),
            }
        return NodeOiOpenDeepResearchAgent._state_summary(result)

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), default=str)
