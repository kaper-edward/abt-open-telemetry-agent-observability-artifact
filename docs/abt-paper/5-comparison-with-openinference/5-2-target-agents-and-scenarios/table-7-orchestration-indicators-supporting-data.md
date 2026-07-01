# Orchestration Complexity Candidate Supporting Data

This document records candidate orchestration-complexity metrics used to strengthen Table 7. The targets use different orchestration forms, so the metrics should be interpreted as representative orchestration indicators rather than as a single comparable complexity score. Terms that correspond to a specific framework concept are named as such, such as LangGraph StateGraph or add_edge. Terms derived from the deterministic source model used in the experiment are labeled as source-model events or steps.

## Measurement Principle

Only values that can be derived from source files or declared scenario catalogs are recorded. Generated trace scale is not repeated here because it is already reported in Table 8.

## Candidate Metrics

| Target agent | Source of measurement | Candidate complexity metrics |
|---|---|---|
| Customer Support Agent | `src/experiments/support_agent/customer_support_agent/support_agent_task_flow_plan.py` | LangGraph workflow nodes: 11; conditional routing points: 9; conditional route labels: 24; explicit add_edge calls: 3 |
| Open Deep Research | `src/experiments/_evaluation_resources/target_agent_references/open_deep_research/source/src/open_deep_research/deep_researcher.py`; `src/experiments/agent_trace_experiments/targets/open_deep_research.py` | LangGraph StateGraph definitions: 3; declared graph nodes: 9; declared explicit edges: 6; scenario planned-query fan-out: 1-5 |
| CrewAI Write-a-Book Flow | `src/experiments/crewai_book_flow_base/source_flow_runtime.py`; `src/experiments/crewai_book_flow_base/scenario.py` | CrewAI-flow event types in source model: 5; chapter fan-out: 3-6; revision branches: 0-2; executed flow events: 8-16 |
| AutoGen Distributed Group Chat | `src/experiments/autogen_group_chat_base/source_group_chat_runtime.py`; `src/experiments/autogen_group_chat_base/scenario.py` | Conversation event types in source model: 6; participating agents: 4-5; review rounds: 1-3; executed conversation events: 5-11 |
| SWE-agent Core Execution | `src/experiments/swe_agent_core_base/source_core_runtime.py`; `src/experiments/swe_agent_core_base/scenario.py` | Core execution step types: 11; scenario step-count range: 5-60; failure/retry scenarios: 10/11; total scenario steps: 288 |

## Interpretation

The values show that the target agents cover different orchestration styles:

- graph-style conditional routing and branching in the Customer Support Agent;
- nested LangGraph source graphs and research delegation in Open Deep Research;
- flow-stage orchestration with chapter fan-out and revision branches in CrewAI;
- multi-agent group-chat routing with optional fact checking in AutoGen;
- iterative software-engineering execution loops with shell/test/retry behavior in SWE-agent.

## Table 7 Decision

The candidate metrics are useful in the main paper when the table explicitly presents them as representative orchestration indicators. A LangGraph node count, a source-model flow-event count, a group-chat participant count, and a SWE-agent step-count range do not measure the same underlying unit. Therefore, Table 7 should not present them as a direct numeric comparison. Instead, each cell should include both the metric name and the value, such as "LangGraph workflow nodes: 11" or "failure/retry scenarios: 10/11", so that the reader understands what each number means for that target agent.

Current recommendation:

- add a "Representative orchestration indicators" column to Table 7;
- keep metric names and values together in each cell;
- avoid aggregating these heterogeneous indicators into a single complexity score;
- keep this document as supporting data for reviewer response or appendix material.


