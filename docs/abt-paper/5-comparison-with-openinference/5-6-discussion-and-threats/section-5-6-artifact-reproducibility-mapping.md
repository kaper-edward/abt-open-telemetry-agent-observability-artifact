# Section 5.6 Artifact and Reproducibility Mapping

This document records how the evaluation artifacts map to the paper sections and tables. It is intended to support reproduction of the Section 5 evaluation.

## Artifact Overview

| Paper location | Artifact type | Workspace location | Purpose |
|---|---|---|---|
| Section 4; Section 5 | ABT Framework source code | `src/aof/abt/` | Implements the ABT recording API, ABT model elements, semantic mapper, trace recorder, and export targets used by the evaluated ABT variants. |
| Section 5.2 | Target-agent source code and controlled evaluation harnesses | `src/experiments/support_agent/customer_support_agent/`, `src/experiments/_evaluation_resources/target_agent_references/*/SOURCE-METADATA.md`, `src/experiments/_evaluation_resources/target_agent_references/open_deep_research/source/`, `src/experiments/open_deep_research_base/`, `src/experiments/crewai_book_flow_base/`, `src/experiments/autogen_group_chat_base/`, `src/experiments/swe_agent_core_base/` | Provides the target behavior sources, public-source metadata or snapshots, controlled source-level evaluation harnesses, and scenario-facing base implementations used by the evaluation. |
| Section 5.2-5.5 | ABT-instrumented target variants | `src/experiments/customer_support_agent_abt/`, `src/experiments/open_deep_research_node_abt/`, `src/experiments/crewai_book_flow_abt/`, `src/experiments/autogen_group_chat_abt/`, `src/experiments/swe_agent_core_abt/` | Provides the ABT Framework instrumentation variant for each evaluated target agent. |
| Section 5.2-5.5 | Direct OI/Otel-instrumented target variants | `src/experiments/customer_support_agent_oi/`, `src/experiments/open_deep_research_node_oi/`, `src/experiments/crewai_book_flow_oi/`, `src/experiments/autogen_group_chat_oi/`, `src/experiments/swe_agent_core_oi/` | Provides the direct OpenInference/OpenTelemetry reference instrumentation variant for each evaluated target agent. |
| Section 5.2; Table 8 | Scenario catalogs | `src/experiments/agent_trace_experiments/scenario_catalog.py`, `src/experiments/agent_trace_experiments/targets/open_deep_research.py`, `src/experiments/crewai_book_flow_base/scenario.py`, `src/experiments/autogen_group_chat_base/scenario.py`, `src/experiments/swe_agent_core_base/scenario.py` | Defines the request-level scenarios used to generate traces for each target. |
| Section 5.3; Tables 9 and 10 | OI/Otel comparison scripts | `src/experiments/agent_trace_experiments/comparison_runner.py`, `src/experiments/agent_trace_experiments/trace_comparison.py`, `src/experiments/agent_trace_experiments/validation_surface_measurement.py` | Runs paired ABT and direct OI/Otel variants and computes trace-generation coverage and compatibility/equivalence checkpoints. |
| Section 5.4; Table 11 | rule/guideline analysis script | `src/experiments/agent_trace_experiments/rule_guideline_analysis.py` | Computes assessment counts for ABT rules and guidelines over generated traces. |
| Section 5.5; Tables 12 and 13 | Instrumentation-effort measurement script | `src/experiments/agent_trace_experiments/instrumentation_effort_measurement.py` | Computes instrumentation LOC, code ratio, instrumentation call-site count, and API argument count. |
| Section 5.2-5.5 | supporting documents | `docs/abt-paper/5-comparison-with-openinference/5-2-target-agents-and-scenarios/`, `5-3-oi-otel-compatible-trace-generation/`, `5-4-abt-rule-guideline-analysis/`, `5-5-instrumentation-effort/` | Stores table-level supporting data and notes with subsection and table numbers in file paths. |

## Supporting Data Folder Mapping

| Folder | Paper mapping | Contents |
|---|---|---|
| `5-2-target-agents-and-scenarios/` | Section 5.2; Tables 7 and 8 | Target-agent characteristics, orchestration indicators, controlled evaluation harness notes, semantic assignment rules, and scenario-scale supporting data. |
| `5-3-oi-otel-compatible-trace-generation/` | Section 5.3; Tables 9 and 10 | Trace-generation coverage targets, per-target coverage data, and validation checkpoint data for OI/Otel-compatible trace generation. |
| `5-4-abt-rule-guideline-analysis/` | Section 5.4; Table 11 | Assessment counts for ABT rules/guidelines. |
| `5-5-instrumentation-effort/` | Section 5.5; Tables 12 and 13 | Automated effort-measurement procedure and per-target effort data. |
| `5-6-discussion-and-threats/` | Section 5.6 | Artifact-to-paper mapping, reproduction notes, and supporting notes for limitations and future validation dimensions. |

## Reproduction Entry Points

The main scripts used to regenerate the evaluation supporting data are:

```text
python .\src\experiments\agent_trace_experiments\validation_surface_measurement.py
python .\src\experiments\agent_trace_experiments\rule_guideline_analysis.py
python .\src\experiments\agent_trace_experiments\instrumentation_effort_measurement.py
```

The comparison runner used by the validation surface measurement is:

```text
src/experiments/agent_trace_experiments/comparison_runner.py
```

The supporting documents record the generated table values and the interpretation notes used in the paper. When a table reports summarized values, the corresponding supporting-data file name includes the table number, such as `table-9-trace-generation-coverage-target-supporting-data.md`, `table-10-oi-otel-trace-generation-coverage-by-target-agent-supporting-data.md`, or `table-12-13-automated-measurement-supporting-data.md`.
