# ABT Journal Paper Artifact Package

This document records the artifact package that should be published with the journal submission or provided as an anonymous review artifact. It is intended to make the empirical results in Section 5 reproducible and to avoid relying only on textual descriptions in the paper.

## Artifact Scope

The artifact should include four groups of materials.

| Group | Contents | Workspace location |
|---|---|---|
| ABT Framework | ABT recording API, model elements, semantic mapper, trace recorder, export targets, and tests | `src/aof/abt/`, `tests/aof_abt/` |
| Target agent sources and harnesses | Customer Support Agent, public-agent source metadata or source snapshots, and controlled evaluation harness implementations | `src/experiments/support_agent/customer_support_agent/`, `src/experiments/_evaluation_resources/target_agent_references/*/SOURCE-METADATA.md`, `src/experiments/_evaluation_resources/target_agent_references/open_deep_research/source/`, `src/experiments/open_deep_research_base/`, `src/experiments/crewai_book_flow_base/`, `src/experiments/autogen_group_chat_base/`, `src/experiments/swe_agent_core_base/` |
| Instrumentation variants | Paired ABT and direct OI/Otel variants for each target agent | `src/experiments/customer_support_agent_abt/`, `src/experiments/customer_support_agent_oi/`, `src/experiments/open_deep_research_node_abt/`, `src/experiments/open_deep_research_node_oi/`, `src/experiments/crewai_book_flow_abt/`, `src/experiments/crewai_book_flow_oi/`, `src/experiments/autogen_group_chat_abt/`, `src/experiments/autogen_group_chat_oi/`, `src/experiments/swe_agent_core_abt/`, `src/experiments/swe_agent_core_oi/` |
| Evaluation scripts and supporting data | Scenario catalogs, trace comparison, rule/guideline analysis, instrumentation-effort measurement, and table-level supporting data | `src/experiments/agent_trace_experiments/`, `docs/abt-paper/5-comparison-with-openinference/` |
| Paper supporting examples | Full instrumentation listings that are abbreviated in the main paper for readability | `docs/abt-paper/4-agent-behavior-trace-framework/section-4-3-full-instrumentation-listings.md` |

## Section 5 Reproduction Map

| Paper result | Script or supporting file | Purpose |
|---|---|---|
| Section 4.3 abbreviated listings | `docs/abt-paper/4-agent-behavior-trace-framework/section-4-3-full-instrumentation-listings.md` | Full ABT-style and direct OI/Otel-style instrumentation listings corresponding to the abbreviated examples in the paper |
| Tables 7 and 8 | `docs/abt-paper/5-comparison-with-openinference/5-2-target-agents-and-scenarios/` | Target-agent characteristics, orchestration indicators, scenario catalog, generated trace scale |
| Table 9 | `docs/abt-paper/5-comparison-with-openinference/5-3-oi-otel-compatible-trace-generation/table-9-trace-generation-coverage-target-supporting-data.md` | OI/Otel-compatible trace-generation coverage target |
| Table 10 | `src/experiments/agent_trace_experiments/validation_surface_measurement.py`; `docs/abt-paper/5-comparison-with-openinference/5-3-oi-otel-compatible-trace-generation/table-10-oi-otel-trace-generation-coverage-by-target-agent-supporting-data.md` | OI/Otel-compatible trace-generation coverage by target agent |
| Representative exported trace | `docs/abt-paper/5-comparison-with-openinference/5-3-oi-otel-compatible-trace-generation/customer-support-shipping-order-success-trace-evidence.md` | Text evidence for one ABT-generated Customer Support trace and Phoenix/OTLP backend verification procedure |
| Table 11 | `src/experiments/agent_trace_experiments/rule_guideline_analysis.py`; `docs/abt-paper/5-comparison-with-openinference/5-4-abt-rule-guideline-analysis/table-11-abt-rule-guideline-assessment-counts-supporting-data.md` | Assessment counts for ABT rules and guidelines |
| Tables 12 and 13 | `src/experiments/agent_trace_experiments/instrumentation_effort_measurement.py`; `docs/abt-paper/5-comparison-with-openinference/5-5-instrumentation-effort/table-12-13-automated-measurement-supporting-data.md` | Static instrumentation-effort measurement |

## Reproduction Commands

The evaluation scripts are expected to be run with `PYTHONPATH=src` from the project root after installing the project dependencies as described in the repository README.

```powershell
$env:PYTHONPATH='src'
python -X utf8 .\src\experiments\agent_trace_experiments\validation_surface_measurement.py
python -X utf8 .\src\experiments\agent_trace_experiments\rule_guideline_analysis.py
python -X utf8 .\src\experiments\agent_trace_experiments\instrumentation_effort_measurement.py
```

## Publication Checklist

- [ ] Decide whether the artifact will be public or anonymous for double-blind review.
- [ ] Add a repository URL or anonymous artifact URL to Section 5.6.
- [x] Include dependency installation instructions.
- [ ] Pin public target-agent source versions or commit hashes where available.
- [x] Verify that generated supporting documents match the values reported in Tables 7-13.
- [ ] Run `git diff --check` before packaging.
- [x] Remove local-only paths from published instructions if the artifact is distributed outside the current workspace.
