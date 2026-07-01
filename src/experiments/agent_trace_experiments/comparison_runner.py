from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

from aof.abt import ABT, ExportTargetFactory
import aof.abt.abt_model.agent as abt_agent_module
from experiments.agent_trace_experiments.scenario_catalog import (
    TraceExperimentScenarioCatalog,
)
from experiments.agent_trace_experiments.targets.open_deep_research import (
    OpenDeepResearchScenarioCatalog,
)
from experiments.agent_trace_experiments.trace_comparison import TraceComparator
from experiments.agent_trace_experiments.trace_comparison import TraceComparisonReport
import experiments.customer_support_agent_oi.instrumented_agent as oi_agent_module
from experiments.customer_support_agent_abt import AbtCustomerSupportAgent
from experiments.customer_support_agent_oi import OiCustomerSupportAgent
from experiments.customer_support_agent_oi.telemetry_context import OiTelemetryContext
from experiments.open_deep_research_node_abt import NodeAbtOpenDeepResearchAgent
from experiments.open_deep_research_node_oi import NodeOiOpenDeepResearchAgent
from experiments.crewai_book_flow_abt import AbtCrewAiBookFlowAgent
from experiments.crewai_book_flow_base import CrewAiBookFlowScenarioCatalog
from experiments.crewai_book_flow_oi import OiCrewAiBookFlowAgent
from experiments.autogen_group_chat_abt import AbtAutoGenGroupChatAgent
from experiments.autogen_group_chat_base import AutoGenGroupChatScenarioCatalog
from experiments.autogen_group_chat_oi import OiAutoGenGroupChatAgent
from experiments.swe_agent_core_abt import AbtSweAgentCoreAgent
from experiments.swe_agent_core_base import SweAgentCoreScenarioCatalog
from experiments.swe_agent_core_oi import OiSweAgentCoreAgent
from experiments.support_agent.customer_support_agent.tasks import FallbackResponseTask
from experiments.support_agent.data_models import PolicyDecision
from experiments.support_agent.order_store import InMemoryOrderStore
from experiments.support_agent.policies import SupportPolicy


@dataclass(frozen=True)
class TraceComparisonRunResult:
    scenario_name: str
    abt_span_count: int
    oi_span_count: int
    shape_matches: bool
    attribute_matches: bool
    missing_span_count: int
    unexpected_span_count: int
    attribute_difference_count: int
    report: TraceComparisonReport


class TraceComparisonRunner:
    def __init__(
        self,
        *,
        target_name: str = "customer_support",
        scenario_catalog: TraceExperimentScenarioCatalog | None = None,
        comparator: TraceComparator | None = None,
    ):
        self._target_name = target_name
        if scenario_catalog is not None:
            self._scenario_catalog = scenario_catalog
        elif target_name == "open_deep_research":
            self._scenario_catalog = OpenDeepResearchScenarioCatalog()
        elif target_name == "crewai_book_flow":
            self._scenario_catalog = CrewAiBookFlowScenarioCatalog()
        elif target_name == "autogen_group_chat":
            self._scenario_catalog = AutoGenGroupChatScenarioCatalog()
        elif target_name == "swe_agent_core":
            self._scenario_catalog = SweAgentCoreScenarioCatalog()
        else:
            self._scenario_catalog = TraceExperimentScenarioCatalog()
        self._comparator = comparator or TraceComparator()

    def run(self, scenario_name: str) -> TraceComparisonRunResult:
        scenario = self._scenario_catalog.get(scenario_name)
        with comparison_session_id(f"trace-comparison-{scenario.name}"):
            abt_spans = self._run_abt(scenario)
            oi_spans = self._run_oi(scenario)
        report = self._comparator.compare(abt_spans, oi_spans)
        return TraceComparisonRunResult(
            scenario_name=scenario.name,
            abt_span_count=len(abt_spans),
            oi_span_count=len(oi_spans),
            shape_matches=report.shape.matches,
            attribute_matches=report.attributes.matches,
            missing_span_count=len(report.shape.missing_spans),
            unexpected_span_count=len(report.shape.unexpected_spans),
            attribute_difference_count=len(report.attributes.differences),
            report=report,
        )

    def run_all(self) -> tuple[TraceComparisonRunResult, ...]:
        return tuple(
            self.run(scenario_name)
            for scenario_name in self._scenario_catalog.names()
        )

    def _run_abt_for_comparison(self, scenario_name: str) -> tuple[Any, ...]:
        scenario = self._scenario_catalog.get(scenario_name)
        with comparison_session_id(f"trace-comparison-{scenario.name}"):
            return self._run_abt(scenario)

    def _run_abt(self, scenario) -> tuple[Any, ...]:
        if self._target_name == "open_deep_research":
            return self._run_open_deep_research_abt(scenario)
        if self._target_name == "crewai_book_flow":
            return self._run_crewai_book_flow_abt(scenario)
        if self._target_name == "autogen_group_chat":
            return self._run_autogen_group_chat_abt(scenario)
        if self._target_name == "swe_agent_core":
            return self._run_swe_agent_core_abt(scenario)
        memory_export_target = ExportTargetFactory().create_memory_export_target(
            service_name="trace-comparison-abt",
        )
        abt = ABT.start_recording(
            export_target=memory_export_target,
            capture_message_content=True,
        )
        try:
            with scenario_runtime(scenario):
                AbtCustomerSupportAgent(
                    gateway_for_customer_support_agent=Gateway(
                        scenario.gateway_outputs
                    ),
                    abt=abt,
                ).run(scenario.customer_id, scenario.message, scenario.session_id)
            abt.export_recorded_traces()
            return memory_export_target.spans()
        finally:
            abt.close_recording()

    def _run_oi(self, scenario) -> tuple[Any, ...]:
        if self._target_name == "open_deep_research":
            return self._run_open_deep_research_oi(scenario)
        if self._target_name == "crewai_book_flow":
            return self._run_crewai_book_flow_oi(scenario)
        if self._target_name == "autogen_group_chat":
            return self._run_autogen_group_chat_oi(scenario)
        if self._target_name == "swe_agent_core":
            return self._run_swe_agent_core_oi(scenario)
        span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider(
            resource=Resource.create({"service.name": "trace-comparison-oi"})
        )
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        OiTelemetryContext.configure(
            tracer_provider.get_tracer("trace_comparison.direct_oi")
        )
        try:
            with scenario_runtime(scenario):
                OiCustomerSupportAgent(
                    gateway_for_customer_support_agent=Gateway(
                        scenario.gateway_outputs
                    ),
                ).run(scenario.customer_id, scenario.message, scenario.session_id)
            tracer_provider.force_flush()
            return tuple(span_exporter.get_finished_spans())
        finally:
            OiTelemetryContext.clear()
            tracer_provider.shutdown()

    def _run_open_deep_research_abt(self, scenario) -> tuple[Any, ...]:
        memory_export_target = ExportTargetFactory().create_memory_export_target(
            service_name="trace-comparison-open-deep-research-abt",
        )
        abt = ABT.start_recording(
            export_target=memory_export_target,
            capture_message_content=True,
            allow_concurrent_children=True,
        )
        try:
            NodeAbtOpenDeepResearchAgent(abt=abt).run(scenario)
            abt.export_recorded_traces()
            return memory_export_target.spans()
        finally:
            abt.close_recording()

    def _run_open_deep_research_oi(self, scenario) -> tuple[Any, ...]:
        span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider(
            resource=Resource.create(
                {"service.name": "trace-comparison-open-deep-research-oi"}
            )
        )
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        try:
            NodeOiOpenDeepResearchAgent(
                tracer=tracer_provider.get_tracer(
                    "trace_comparison.open_deep_research.node_level_direct_oi"
                )
            ).run(scenario)
            tracer_provider.force_flush()
            return tuple(span_exporter.get_finished_spans())
        finally:
            tracer_provider.shutdown()

    def _run_crewai_book_flow_abt(self, scenario) -> tuple[Any, ...]:
        memory_export_target = ExportTargetFactory().create_memory_export_target(
            service_name="trace-comparison-crewai-book-flow-abt",
        )
        abt = ABT.start_recording(
            export_target=memory_export_target,
            capture_message_content=True,
        )
        try:
            AbtCrewAiBookFlowAgent(abt=abt).run(scenario)
            abt.export_recorded_traces()
            return memory_export_target.spans()
        finally:
            abt.close_recording()

    def _run_crewai_book_flow_oi(self, scenario) -> tuple[Any, ...]:
        span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider(
            resource=Resource.create({"service.name": "trace-comparison-crewai-oi"})
        )
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        try:
            OiCrewAiBookFlowAgent(
                tracer=tracer_provider.get_tracer(
                    "trace_comparison.crewai_book_flow.direct_oi"
                )
            ).run(scenario)
            tracer_provider.force_flush()
            return tuple(span_exporter.get_finished_spans())
        finally:
            tracer_provider.shutdown()

    def _run_autogen_group_chat_abt(self, scenario) -> tuple[Any, ...]:
        memory_export_target = ExportTargetFactory().create_memory_export_target(
            service_name="trace-comparison-autogen-group-chat-abt",
        )
        abt = ABT.start_recording(
            export_target=memory_export_target,
            capture_message_content=True,
        )
        try:
            AbtAutoGenGroupChatAgent(abt=abt).run(scenario)
            abt.export_recorded_traces()
            return memory_export_target.spans()
        finally:
            abt.close_recording()

    def _run_autogen_group_chat_oi(self, scenario) -> tuple[Any, ...]:
        span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider(
            resource=Resource.create({"service.name": "trace-comparison-autogen-oi"})
        )
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        try:
            OiAutoGenGroupChatAgent(
                tracer=tracer_provider.get_tracer(
                    "trace_comparison.autogen_group_chat.direct_oi"
                )
            ).run(scenario)
            tracer_provider.force_flush()
            return tuple(span_exporter.get_finished_spans())
        finally:
            tracer_provider.shutdown()

    def _run_swe_agent_core_abt(self, scenario) -> tuple[Any, ...]:
        memory_export_target = ExportTargetFactory().create_memory_export_target(
            service_name="trace-comparison-swe-agent-core-abt",
        )
        abt = ABT.start_recording(
            export_target=memory_export_target,
            capture_message_content=True,
        )
        try:
            AbtSweAgentCoreAgent(abt=abt).run(scenario)
            abt.export_recorded_traces()
            return memory_export_target.spans()
        finally:
            abt.close_recording()

    def _run_swe_agent_core_oi(self, scenario) -> tuple[Any, ...]:
        span_exporter = InMemorySpanExporter()
        tracer_provider = TracerProvider(
            resource=Resource.create(
                {"service.name": "trace-comparison-swe-agent-core-oi"}
            )
        )
        tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        try:
            OiSweAgentCoreAgent(
                tracer=tracer_provider.get_tracer(
                    "trace_comparison.swe_agent_core.direct_oi"
                )
            ).run(scenario)
            tracer_provider.force_flush()
            return tuple(span_exporter.get_finished_spans())
        finally:
            tracer_provider.shutdown()


class Gateway:
    model_name = "qwen3:4b"

    def __init__(self, outputs):
        self._outputs = iter(outputs)

    def invoke(self, prompt):
        return next(self._outputs)


@contextmanager
def scenario_runtime(scenario):
    original_store_default = InMemoryOrderStore.default
    original_policy_decide = SupportPolicy.decide
    original_fallback_response = FallbackResponseTask._fallback_response
    try:
        if scenario.store_behavior == "policy_lookup_failure":
            base_store = original_store_default()
            InMemoryOrderStore.default = classmethod(
                lambda cls: PolicyLookupFailingStore(base_store)
            )
        if scenario.policy_behavior == "needs_information":
            SupportPolicy.decide = needs_information_policy_decision
        if scenario.fallback_response_behavior == "empty":
            FallbackResponseTask._fallback_response = staticmethod(
                lambda workspace: ""
            )
        yield
    finally:
        InMemoryOrderStore.default = original_store_default
        SupportPolicy.decide = original_policy_decide
        FallbackResponseTask._fallback_response = staticmethod(
            original_fallback_response
        )


class PolicyLookupFailingStore:
    def __init__(self, store):
        self._store = store

    def get_order(self, customer_id: str, order_id: str):
        return self._store.get_order(customer_id, order_id)

    def get_policy(self, intent: str):
        raise RuntimeError("policy lookup failed")


def needs_information_policy_decision(self, intent, order, today):
    return PolicyDecision(
        "needs_information",
        "scenario_forced_policy_decision_fallback",
        "More information is required for this scenario.",
    )


@contextmanager
def comparison_session_id(session_id: str):
    original_abt_uuid4 = abt_agent_module.uuid4
    original_oi_uuid4 = oi_agent_module.uuid4
    fixed_uuid = FixedUuid(session_id)
    try:
        abt_agent_module.uuid4 = lambda: fixed_uuid
        oi_agent_module.uuid4 = lambda: fixed_uuid
        yield
    finally:
        abt_agent_module.uuid4 = original_abt_uuid4
        oi_agent_module.uuid4 = original_oi_uuid4


class FixedUuid:
    def __init__(self, hex_value: str):
        self.hex = hex_value
