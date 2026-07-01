# Open Deep Research Evaluation Target

Source repository: https://github.com/langchain-ai/open_deep_research

Pinned commit: `1f24f1142db24f81e29eb88751985a00ec8ed580`

Purpose: External public agent used as an additional evaluation target for ABT-vs-direct-OI/Otel trace-generation experiments.

Local policy:
- The source directory is treated as external code.
- Business behavior must not be rewritten for ABT.
- Instrumentation must be added through local adapter packages under `src/experiments/open_deep_research_node_abt` and `src/experiments/open_deep_research_node_oi`.
