# Agent Behavior Trace Artifact

This repository contains the research artifact for the paper
**Agent Behavior Trace: A Behavior-Level Model and Framework for OpenTelemetry-Compatible AI Agent Observability**.

The artifact includes:

- the Agent Behavior Trace (ABT) framework implementation,
- target agent source and controlled evaluation harness implementations,
- paired ABT and direct OI/Otel instrumentation variants,
- scenario catalogs and evaluation scripts, and
- supporting data for the tables reported in the paper.

## Repository Layout

| Path | Contents |
|---|---|
| `src/aof/abt/` | ABT framework source code: Trace Recording API, ABT Model, Semantic Mapping, Telemetry Recording, and Export Target layers |
| `tests/aof_abt/` | ABT framework tests |
| `src/experiments/support_agent/customer_support_agent/` | Customer Support Agent target implementation |
| `src/experiments/_evaluation_resources/target_agent_references/*/SOURCE-METADATA.md` | Public target-agent source references, source scopes, and evaluation-use notes |
| `src/experiments/_evaluation_resources/target_agent_references/open_deep_research/source/` | Packaged Open Deep Research source snapshot used for source-graph execution |
| `src/experiments/open_deep_research_base/` | Controlled evaluation harness for Open Deep Research scenarios |
| `src/experiments/crewai_book_flow_base/` | Controlled evaluation harness for CrewAI Write-a-Book Flow scenarios |
| `src/experiments/autogen_group_chat_base/` | Controlled evaluation harness for AutoGen Distributed Group Chat scenarios |
| `src/experiments/swe_agent_core_base/` | Controlled evaluation harness for SWE-agent Core Execution scenarios |
| `src/experiments/*_abt/` | ABT-instrumented variants |
| `src/experiments/*_oi/` | Direct OI/Otel-instrumented variants |
| `src/experiments/agent_trace_experiments/` | Evaluation scripts and scenario orchestration |
| `docs/abt-paper/ARTIFACT-PACKAGE.md` | Mapping between paper results, reproduction scripts, and supporting data |
| `docs/abt-paper/5-comparison-with-openinference/` | Table-level supporting data for Section 5 |

## Environment Setup

Python 3.11 or later is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The pinned package versions used in the local evaluation are recorded in
`requirements.lock`. To install the exact locked package set instead of using
the version ranges in `pyproject.toml`, run:

```powershell
python -m pip install -r requirements.lock
python -m pip install -e . --no-deps
```

## Running Tests

```powershell
python -m pytest -q
```

The default pytest configuration excludes integration tests.

## Reproducing Section 5 Measurements

Run the following commands from the repository root.

```powershell
$env:PYTHONPATH='src'
python -X utf8 .\src\experiments\agent_trace_experiments\validation_surface_measurement.py
python -X utf8 .\src\experiments\agent_trace_experiments\rule_guideline_analysis.py
python -X utf8 .\src\experiments\agent_trace_experiments\instrumentation_effort_measurement.py
```

The scripts generate or check the values reported in:

- Table 9: OI/Otel-compatible trace-generation coverage target,
- Table 10: OI/Otel-compatible trace-generation coverage by target agent,
- Table 11: ABT rule/guideline assessment counts, and
- Tables 12 and 13: static instrumentation-effort measurements.

Supporting documents for Tables 7-13 are stored under:

```text
docs/abt-paper/5-comparison-with-openinference/
```

See `docs/abt-paper/ARTIFACT-PACKAGE.md` for the detailed mapping between paper
results, scripts, and supporting files.

## Notes on Target Agents

The public-agent targets are evaluated through controlled evaluation harnesses.
In this artifact, a controlled evaluation harness is an experimental program
that preserves the source-level behavior structure relevant to trace generation
while fixing nondeterministic or external effects such as LLM responses,
tool-service results, search outputs, shell results, and filesystem side
effects. This ensures that ABT and direct OI/Otel variants observe the same
behavior sequence. It does not mean that every target executes the full
upstream framework execution stack.

Open Deep Research includes a packaged public source snapshot and executes the
original LangGraph source graph with controlled external dependencies.
CrewAI Write-a-Book Flow, AutoGen Distributed Group Chat, and SWE-agent Core
Execution use controlled source-level evaluation harnesses derived from the
public source scopes recorded under `src/experiments/_evaluation_resources/target_agent_references/*/SOURCE-METADATA.md`.

## Current Artifact Status

The artifact is prepared for public or anonymous review packaging. Before final
publication, add the repository URL or DOI to the paper and pin any external
source snapshot commit hashes that are required by the final submission policy.
