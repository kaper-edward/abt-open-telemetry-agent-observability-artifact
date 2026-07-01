from experiments.open_deep_research_base.deterministic_runtime import ResearchScenario
from experiments.open_deep_research_base.source_graph_runtime import (
    DeterministicOpenDeepResearchRuntime,
)


class OpenDeepResearchAgent:
    def __init__(
        self,
        runtime: DeterministicOpenDeepResearchRuntime | None = None,
    ):
        self._runtime = runtime or DeterministicOpenDeepResearchRuntime()

    def run(self, scenario: ResearchScenario) -> dict[str, object]:
        return self._runtime.run(scenario)
