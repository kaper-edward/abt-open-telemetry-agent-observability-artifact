# Open Deep Research Node-Level Instrumentation Supporting Data

This document records the node-level instrumentation experiment for the Open Deep Research target.

## Purpose

The Open Deep Research experiment executes the original source graph with controlled external dependencies and instruments source graph node execution boundaries directly. This experiment replaces the earlier adapter-level Open Deep Research measurement in the paper because node-level instrumentation better reflects the structure of the public LangGraph agent.

## Instrumentation Variants

| Variant | Package | Purpose |
|---|---|---|
| Direct OI/Otel node-level instrumentation | `src/experiments/open_deep_research_node_oi` | Rebuilds the original source graph with wrapper nodes that create OI/Otel spans around source node execution. |
| ABT node-level instrumentation | `src/experiments/open_deep_research_node_abt` | Rebuilds the original source graph with wrapper nodes that create ABT Task and ToolAction spans around source node execution. |

## Concurrent Child Handling

Open Deep Research can execute delegated researcher subgraphs concurrently. The ABT Framework therefore adds an explicit `allow_concurrent_children` recording option for this experiment. Default ABT recording remains sequential and rejects concurrently open sibling children. When concurrent mode is enabled:

- a TraceStructure may have multiple open child structures;
- parent-child span relationships are still recorded explicitly;
- parent completion still requires all children to be closed;
- metadata records `max_open_child_count` when concurrency occurs.

## Captured Source Graph Nodes

Both node-level variants captured the same source graph node set in the validation scenario.

| Source graph node |
|---|
| `clarify_with_user` |
| `write_research_brief` |
| `supervisor` |
| `supervisor_tools` |
| `researcher` |
| `researcher_tools` |
| `compress_research` |
| `final_report_generation` |

## Verification

| Test | Result |
|---|---|
| `tests/aof_abt/test_abt_concurrent_children.py` | Passed |
| `tests/open_deep_research_node_instrumentation_tests/test_node_oi_open_deep_research.py` | Passed |
| `tests/open_deep_research_node_instrumentation_tests/test_node_abt_open_deep_research.py` | Passed |
| `tests/open_deep_research_node_instrumentation_tests/test_node_level_abt_vs_oi.py` | Passed |

Combined related verification:

`129 passed, 46 warnings`


