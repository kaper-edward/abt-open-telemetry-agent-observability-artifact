from experiments.open_deep_research_base import ResearchScenario


class OpenDeepResearchScenarioCatalog:
    def __init__(self):
        self._scenarios = {
            "short_research": ResearchScenario(
                name="short_research",
                user_id="researcher",
                session_id="odr-session-1",
                question="What is OpenInference?",
                planned_queries=("OpenInference trace spec",),
                retrieved_documents=("doc about OpenInference",),
                compressed_summary="OpenInference defines AI trace semantics.",
                final_report="OpenInference provides semantic conventions for traces.",
            ),
            "multi_source_research": ResearchScenario(
                name="multi_source_research",
                user_id="researcher",
                session_id="odr-session-2",
                question="How do agent traces support debugging?",
                planned_queries=(
                    "agent trace debugging",
                    "OpenTelemetry distributed tracing",
                ),
                retrieved_documents=(
                    "agent trace document",
                    "distributed tracing document",
                ),
                compressed_summary=(
                    "Agent traces expose intermediate behavior and decisions."
                ),
                final_report=(
                    "Agent traces support debugging by exposing tasks, actions, "
                    "tool calls, retrieval, and decisions."
                ),
            ),
            "empty_retrieval_fallback": ResearchScenario(
                name="empty_retrieval_fallback",
                user_id="researcher",
                session_id="odr-session-3",
                question="Find sources about an unavailable topic.",
                planned_queries=("unavailable topic",),
                retrieved_documents=(),
                compressed_summary="No relevant source was found.",
                final_report="The research agent could not find relevant sources.",
            ),
            "broad_market_research": ResearchScenario(
                name="broad_market_research",
                user_id="researcher",
                session_id="odr-session-4",
                question=(
                    "Compare current enterprise adoption patterns for agent "
                    "observability platforms."
                ),
                planned_queries=(
                    "enterprise AI agent observability platforms",
                    "OpenTelemetry AI agent monitoring",
                    "OpenInference trace adoption",
                    "LLM application runtime monitoring",
                ),
                retrieved_documents=(
                    "enterprise observability report",
                    "OpenTelemetry monitoring document",
                    "OpenInference adoption document",
                    "LLM runtime monitoring document",
                    "agent governance document",
                    "production AI operations document",
                ),
                compressed_summary=(
                    "Enterprise agent observability combines tracing, governance, "
                    "runtime monitoring, and model-operation practices."
                ),
                final_report=(
                    "Enterprise adoption of agent observability is driven by "
                    "runtime traceability, operational governance, and the need "
                    "to compare agent behavior across development and production."
                ),
            ),
            "deep_technical_research": ResearchScenario(
                name="deep_technical_research",
                user_id="researcher",
                session_id="odr-session-5",
                question=(
                    "Analyze how standards-compatible traces can support "
                    "behavior modeling for multi-agent systems."
                ),
                planned_queries=(
                    "multi-agent system behavior trace",
                    "process mining from distributed traces",
                    "state model inference from software traces",
                    "OpenTelemetry semantic conventions AI systems",
                    "OpenInference agent trace metadata",
                ),
                retrieved_documents=(
                    "multi-agent trace paper",
                    "distributed process mining paper",
                    "state inference paper",
                    "OpenTelemetry semantic convention document",
                    "OpenInference trace specification",
                    "agent runtime monitoring paper",
                    "AI operations drift detection paper",
                    "multi-agent governance document",
                ),
                compressed_summary=(
                    "Standards-compatible traces can expose action sequences, "
                    "runtime decisions, tool calls, and retrieval behavior for "
                    "subsequent behavior-model construction."
                ),
                final_report=(
                    "Behavior modeling for multi-agent systems can use "
                    "standards-compatible traces as execution records, provided "
                    "that trace structures preserve agent, task, action, and "
                    "decision semantics."
                ),
            ),
        }

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._scenarios))

    def get(self, name: str) -> ResearchScenario:
        try:
            return self._scenarios[name]
        except KeyError as error:
            raise ValueError(f"Unknown Open Deep Research scenario: {name}") from error
