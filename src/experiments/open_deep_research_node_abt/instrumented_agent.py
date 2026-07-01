from __future__ import annotations

import asyncio
from contextlib import contextmanager
from typing import Any

from langgraph.graph import END, START, StateGraph

from aof.abt import ActionInvocationProtocol
from aof.abt import ActionTargetLocation
from aof.abt import ActionTargetType
from aof.abt import InputSourceType
from experiments.agent_trace_experiments.semantic_node_instrumentation import (
    record_abt_semantic_actions,
)
from experiments.open_deep_research_base import ResearchScenario
from experiments.open_deep_research_base.source_graph_runtime import (
    DeterministicOpenDeepResearchRuntime,
    SourceGraphEventRecorder,
)


class NodeAbtOpenDeepResearchAgent:
    """Runs the original Open Deep Research source graph with node-level ABT spans."""

    def __init__(self, *, abt):
        self._abt = abt
        self._runtime = DeterministicOpenDeepResearchRuntime()

    def run(self, scenario: ResearchScenario) -> dict[str, object]:
        deep_researcher_module = self._runtime._load_deep_researcher_module()
        event_recorder = SourceGraphEventRecorder()
        agent = self._abt.agent("open_deep_research_node_level", user_id=scenario.user_id)
        trace = agent.trace(
            "research_request",
            input_value=scenario.question,
            input_source_type=InputSourceType.USER,
            input_channel="experiment",
        )
        try:
            with self._runtime._deterministic_dependencies(
                deep_researcher_module,
                scenario,
                event_recorder,
            ):
                with self._instrumented_researcher_subgraph(
                    deep_researcher_module,
                    trace,
                ):
                    source_graph = self._build_instrumented_source_graph(
                        deep_researcher_module,
                        trace,
                    )
                    output = asyncio.run(
                        source_graph.ainvoke(
                            {"messages": [("user", scenario.question)]},
                            self._runtime._config_for(scenario),
                        )
                    )
            trace.complete(output=output["final_report"])
            agent.complete(output=output["final_report"])
            return {
                "execution_mode": "source_graph_node_level_abt_instrumentation",
                "question": scenario.question,
                "planned_queries": list(scenario.planned_queries),
                "retrieved_documents": list(scenario.retrieved_documents),
                "compressed_summary": scenario.compressed_summary,
                "final_report": output["final_report"],
                "source_graph_events": event_recorder.events(),
                "source_graph_output": output,
            }
        except Exception as error:
            agent.fail(error)
            raise

    @contextmanager
    def _instrumented_researcher_subgraph(self, deep_researcher_module, trace):
        original_researcher_subgraph = deep_researcher_module.researcher_subgraph
        instrumented_researcher_subgraph = self._build_instrumented_researcher_subgraph(
            deep_researcher_module,
            trace,
        )
        deep_researcher_module.researcher_subgraph = instrumented_researcher_subgraph
        try:
            yield
        finally:
            deep_researcher_module.researcher_subgraph = original_researcher_subgraph

    def _build_instrumented_source_graph(self, deep_researcher_module, trace):
        supervisor_subgraph = self._build_instrumented_supervisor_subgraph(
            deep_researcher_module,
            trace,
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
                trace,
            ),
        )
        builder.add_node(
            "write_research_brief",
            self._instrument_node(
                "write_research_brief",
                deep_researcher_module.write_research_brief,
                trace,
            ),
        )
        builder.add_node("research_supervisor", supervisor_subgraph)
        builder.add_node(
            "final_report_generation",
            self._instrument_node(
                "final_report_generation",
                deep_researcher_module.final_report_generation,
                trace,
            ),
        )
        builder.add_edge(START, "clarify_with_user")
        builder.add_edge("research_supervisor", "final_report_generation")
        builder.add_edge("final_report_generation", END)
        return builder.compile()

    def _build_instrumented_supervisor_subgraph(self, deep_researcher_module, trace):
        builder = StateGraph(
            deep_researcher_module.SupervisorState,
            config_schema=deep_researcher_module.Configuration,
        )
        builder.add_node(
            "supervisor",
            self._instrument_node("supervisor", deep_researcher_module.supervisor, trace),
        )
        builder.add_node(
            "supervisor_tools",
            self._instrument_node(
                "supervisor_tools",
                deep_researcher_module.supervisor_tools,
                trace,
            ),
        )
        builder.add_edge(START, "supervisor")
        return builder.compile()

    def _build_instrumented_researcher_subgraph(self, deep_researcher_module, trace):
        builder = StateGraph(
            deep_researcher_module.ResearcherState,
            output=deep_researcher_module.ResearcherOutputState,
            config_schema=deep_researcher_module.Configuration,
        )
        builder.add_node(
            "researcher",
            self._instrument_node("researcher", deep_researcher_module.researcher, trace),
        )
        builder.add_node(
            "researcher_tools",
            self._instrument_node(
                "researcher_tools",
                deep_researcher_module.researcher_tools,
                trace,
            ),
        )
        builder.add_node(
            "compress_research",
            self._instrument_node(
                "compress_research",
                deep_researcher_module.compress_research,
                trace,
            ),
        )
        builder.add_edge(START, "researcher")
        builder.add_edge("compress_research", END)
        return builder.compile()

    def _instrument_node(self, node_name: str, node_function, trace):
        async def instrumented_node(state, config):
            task = trace.task(f"source_node_{node_name}")
            state_summary = self._state_summary(state)
            record_abt_semantic_actions(task, node_name, state_summary)
            action = task.tool(f"execute_source_graph_node_{node_name}")
            action.target(
                location=ActionTargetLocation.IN_PROCESS,
                target_type=ActionTargetType.FUNCTION,
                target_name=node_name,
                invocation_protocol=ActionInvocationProtocol.FUNCTION_CALL,
            )
            action.input(state_summary)
            try:
                result = await node_function(state, config)
            except Exception as error:
                task.fail(error)
                raise
            result_summary = self._result_summary(result)
            action.complete(output=result_summary)
            task.complete(output=result_summary)
            return result

        return instrumented_node

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
                "update": NodeAbtOpenDeepResearchAgent._state_summary(update or {}),
            }
        return NodeAbtOpenDeepResearchAgent._state_summary(result)
