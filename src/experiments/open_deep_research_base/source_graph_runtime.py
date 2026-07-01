from __future__ import annotations

import asyncio
from contextlib import contextmanager
from pathlib import Path
import sys
from types import ModuleType
from typing import Any

from langchain_core.messages import AIMessage
from langchain_core.messages import ToolMessage

from experiments.open_deep_research_base.deterministic_runtime import ResearchScenario


class DeterministicOpenDeepResearchRuntime:
    def run(self, scenario: ResearchScenario) -> dict[str, object]:
        deep_researcher_module = self._load_deep_researcher_module()
        recorder = SourceGraphEventRecorder()
        with self._deterministic_dependencies(
            deep_researcher_module, scenario, recorder
        ):
            output = asyncio.run(
                deep_researcher_module.deep_researcher.ainvoke(
                    {"messages": [("user", scenario.question)]},
                    self._config_for(scenario),
                )
            )
        return {
            "execution_mode": "source_graph_with_deterministic_dependencies",
            "question": scenario.question,
            "planned_queries": list(scenario.planned_queries),
            "retrieved_documents": list(scenario.retrieved_documents),
            "compressed_summary": scenario.compressed_summary,
            "final_report": output["final_report"],
            "source_graph_events": recorder.events(),
            "source_graph_output": output,
        }

    @staticmethod
    def _load_deep_researcher_module():
        install_langchain_chat_model_stub()
        install_optional_dependency_stubs()
        source_path = (
            Path(__file__).resolve().parents[1]
            / "_evaluation_resources"
            / "target_agent_references"
            / "open_deep_research"
            / "source"
            / "src"
        )
        source_path_text = str(source_path)
        if source_path_text not in sys.path:
            sys.path.insert(0, source_path_text)
        from open_deep_research import deep_researcher

        return deep_researcher

    @staticmethod
    def _config_for(scenario: ResearchScenario) -> dict[str, object]:
        return {
            "configurable": {
                "allow_clarification": True,
                "max_concurrent_research_units": max(1, len(scenario.planned_queries)),
                "max_researcher_iterations": 3,
                "max_react_tool_calls": 2,
                "search_api": "none",
                "research_model": "deterministic-research-model",
                "compression_model": "deterministic-compression-model",
                "final_report_model": "deterministic-report-model",
            }
        }

    @contextmanager
    def _deterministic_dependencies(
        self,
        deep_researcher_module,
        scenario,
        recorder: "SourceGraphEventRecorder",
    ):
        original_model = deep_researcher_module.configurable_model
        original_get_all_tools = deep_researcher_module.get_all_tools
        deep_researcher_module.configurable_model = DeterministicChatModel(
            scenario,
            recorder=recorder,
        )
        deep_researcher_module.get_all_tools = (
            lambda config: deterministic_research_tools_async(scenario, recorder)
        )
        try:
            yield
        finally:
            deep_researcher_module.configurable_model = original_model
            deep_researcher_module.get_all_tools = original_get_all_tools


class DeterministicChatModel:
    def __init__(
        self,
        scenario: ResearchScenario,
        *,
        recorder: "SourceGraphEventRecorder",
        structured_output_type: type | None = None,
        tool_names: tuple[str, ...] = (),
        configured_model: str | None = None,
    ):
        self._scenario = scenario
        self._recorder = recorder
        self._structured_output_type = structured_output_type
        self._tool_names = tool_names
        self._configured_model = configured_model

    def with_structured_output(self, structured_output_type: type):
        return type(self)(
            self._scenario,
            recorder=self._recorder,
            structured_output_type=structured_output_type,
            tool_names=self._tool_names,
            configured_model=self._configured_model,
        )

    def with_retry(self, *args, **kwargs):
        return self

    def with_config(self, config=None, **kwargs):
        config = config or {}
        return type(self)(
            self._scenario,
            recorder=self._recorder,
            structured_output_type=self._structured_output_type,
            tool_names=self._tool_names,
            configured_model=config.get("model", self._configured_model),
        )

    def bind_tools(self, tools):
        return type(self)(
            self._scenario,
            recorder=self._recorder,
            structured_output_type=self._structured_output_type,
            tool_names=tuple(tool_name(tool) for tool in tools),
            configured_model=self._configured_model,
        )

    async def ainvoke(self, messages):
        if self._structured_output_type is not None:
            return self._structured_output()
        if "ConductResearch" in self._tool_names:
            return self._supervisor_response(messages)
        if "web_search" in self._tool_names:
            return self._researcher_response(messages)
        return self._text_response(messages)

    def _structured_output(self):
        class_name = self._structured_output_type.__name__
        if class_name == "ClarifyWithUser":
            self._recorder.record("clarify_with_user")
            return self._structured_output_type(
                need_clarification=False,
                question="",
                verification="Proceeding with deterministic research.",
            )
        if class_name == "ResearchQuestion":
            self._recorder.record("write_research_brief")
            return self._structured_output_type(
                research_brief=self._scenario.question
            )
        raise ValueError(f"Unsupported structured output: {class_name}")

    def _supervisor_response(self, messages) -> AIMessage:
        if any(isinstance(message, ToolMessage) for message in messages):
            self._recorder.record("supervisor_complete_research")
            return AIMessage(
                content="Research complete.",
                tool_calls=[
                    {
                        "name": "ResearchComplete",
                        "args": {},
                        "id": "supervisor-research-complete",
                    }
                ],
            )
        self._recorder.record("supervisor_delegate_research")
        return AIMessage(
            content="Delegating deterministic research.",
            tool_calls=[
                {
                    "name": "ConductResearch",
                    "args": {"research_topic": query},
                    "id": f"conduct-research-{index}",
                }
                for index, query in enumerate(
                    self._scenario.planned_queries, start=1
                )
            ],
        )

    def _researcher_response(self, messages) -> AIMessage:
        if any(isinstance(message, ToolMessage) for message in messages):
            self._recorder.record("researcher_complete")
            return AIMessage(
                content="Researcher complete.",
                tool_calls=[
                    {
                        "name": "ResearchComplete",
                        "args": {},
                        "id": "researcher-complete",
                    }
                ],
            )
        self._recorder.record("researcher_call_search")
        return AIMessage(
            content="Searching deterministic source set.",
            tool_calls=[
                {
                    "name": "web_search",
                    "args": {"query": self._research_topic(messages)},
                    "id": "web-search",
                }
            ],
        )

    def _text_response(self, messages) -> AIMessage:
        if self._configured_model == "deterministic-compression-model":
            self._recorder.record("compress_research")
            return AIMessage(content=self._scenario.compressed_summary)
        if self._configured_model == "deterministic-report-model":
            self._recorder.record("final_report_generation")
            return AIMessage(content=self._scenario.final_report)
        message_text = "\n".join(str(message.content) for message in messages)
        if "compress" in message_text.lower() or "summary" in message_text.lower():
            self._recorder.record("compress_research")
            return AIMessage(content=self._scenario.compressed_summary)
        self._recorder.record("final_report_generation")
        return AIMessage(content=self._scenario.final_report)

    @staticmethod
    def _research_topic(messages) -> str:
        for message in reversed(messages):
            content = getattr(message, "content", "")
            if content:
                return str(content)
        return "deterministic research topic"


class DeterministicSearchTool:
    name = "web_search"

    def __init__(
        self,
        scenario: ResearchScenario,
        recorder: "SourceGraphEventRecorder",
    ):
        self._scenario = scenario
        self._recorder = recorder

    async def ainvoke(self, args: dict[str, Any], config: Any = None) -> str:
        self._recorder.record("execute_web_search")
        query = args.get("query", "")
        documents = "\n".join(self._scenario.retrieved_documents)
        return f"Results for {query}:\n{documents}"


class DeterministicResearchCompleteTool:
    name = "ResearchComplete"

    async def ainvoke(self, args: dict[str, Any], config: Any = None) -> str:
        return "Research complete."


def deterministic_research_tools(
    scenario: ResearchScenario,
    recorder: "SourceGraphEventRecorder",
) -> list[object]:
    return [
        DeterministicResearchCompleteTool(),
        DeterministicSearchTool(scenario, recorder),
    ]


async def deterministic_research_tools_async(
    scenario: ResearchScenario,
    recorder: "SourceGraphEventRecorder",
) -> list[object]:
    return deterministic_research_tools(scenario, recorder)


def tool_name(tool: object) -> str:
    if isinstance(tool, type):
        return tool.__name__
    if hasattr(tool, "name"):
        return str(tool.name)
    if hasattr(tool, "__name__"):
        return str(tool.__name__)
    return type(tool).__name__


def install_langchain_chat_model_stub() -> None:
    if "langchain.chat_models" in sys.modules:
        return
    langchain_module = sys.modules.setdefault("langchain", ModuleType("langchain"))
    chat_models_module = ModuleType("langchain.chat_models")
    chat_models_module.init_chat_model = lambda *args, **kwargs: (
        DeterministicChatModel(
            ResearchScenario(
                name="import_stub",
                user_id="import_stub",
                session_id="import_stub",
                question="import stub",
                planned_queries=("import stub",),
                retrieved_documents=(),
                compressed_summary="import stub",
                final_report="import stub",
            ),
            recorder=SourceGraphEventRecorder(),
        )
    )
    langchain_module.chat_models = chat_models_module
    sys.modules["langchain.chat_models"] = chat_models_module


def install_optional_dependency_stubs() -> None:
    sys.modules.setdefault("aiohttp", ModuleType("aiohttp"))

    tavily_module = sys.modules.setdefault("tavily", ModuleType("tavily"))
    if not hasattr(tavily_module, "AsyncTavilyClient"):
        tavily_module.AsyncTavilyClient = DeterministicAsyncTavilyClient

    mcp_module = sys.modules.setdefault("mcp", ModuleType("mcp"))
    if not hasattr(mcp_module, "McpError"):
        mcp_module.McpError = RuntimeError

    adapter_module = sys.modules.setdefault(
        "langchain_mcp_adapters", ModuleType("langchain_mcp_adapters")
    )
    client_module = ModuleType("langchain_mcp_adapters.client")
    client_module.MultiServerMCPClient = DeterministicMCPClient
    adapter_module.client = client_module
    sys.modules["langchain_mcp_adapters.client"] = client_module


class DeterministicAsyncTavilyClient:
    async def search(self, *args, **kwargs) -> dict[str, object]:
        return {"results": []}


class DeterministicMCPClient:
    def __init__(self, *args, **kwargs):
        pass

    async def get_tools(self):
        return []


class SourceGraphEventRecorder:
    def __init__(self):
        self._events: list[str] = []

    def record(self, event_name: str) -> None:
        self._events.append(event_name)

    def events(self) -> list[str]:
        return list(self._events)
