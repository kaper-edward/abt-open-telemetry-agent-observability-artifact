# Open Deep Research Source Metadata

## Public Source

- Repository: https://github.com/langchain-ai/open_deep_research
- Pinned commit: `1f24f1142db24f81e29eb88751985a00ec8ed580`
- Packaged source snapshot: `src/experiments/_evaluation_resources/target_agent_references/open_deep_research/source/`

## Evaluation Use

Open Deep Research is used as a public LangGraph research-agent target. The artifact includes a source snapshot and executes the original source graph with controlled LLM, search, retrieval, and external-service dependencies.

The controlled dependencies do not mean that the source graph is replaced. They mean that nondeterministic or external effects are fixed so that the same graph-node behavior sequence can be reproduced across ABT and direct OI/Otel instrumentation variants.

## Related Artifact Files

- Deterministic execution wrapper: `src/experiments/open_deep_research_base/`
- ABT instrumentation variant: `src/experiments/open_deep_research_node_abt/`
- Direct OI/Otel instrumentation variant: `src/experiments/open_deep_research_node_oi/`
- Scenario and measurement scripts: `src/experiments/agent_trace_experiments/`
