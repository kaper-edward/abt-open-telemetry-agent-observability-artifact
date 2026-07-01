# Table 9 Validation-Surface Measurement

This document explains how `validation_surface_measurement.py` generates the numbers used in Table 9 of the ABT paper.

## Purpose

The script measures the validation surface for OI/Otel-compatible trace generation. It does not only report whether ABT and direct OI/Otel traces are equivalent. Instead, it reports which compatibility checkpoints were exercised and how many checks were performed for each target agent.

The generated table is used as the supporting data for:

- OpenInference span-kind coverage, and
- span-kind-specific attribute-key coverage.

## Inputs

The script does not read a CSV or JSON file. It uses the experiment code in this repository as its input.

The target agents are defined in `TARGETS`:

- Customer support agent
- Open Deep Research
- CrewAI Write-a-Book Flow
- AutoGen Distributed Group Chat
- SWE-agent Core Execution

For each target agent, `TraceComparisonRunner` loads the corresponding scenario catalog. Each scenario represents one request-level Trace execution.

For each scenario, the runner executes two instrumentation variants:

1. ABT-instrumented agent implementation
2. Direct OI/Otel-instrumented reference implementation

Both variants use the same scenario input and deterministic dependencies.

## Processing Pipeline

For each target agent and scenario, the script performs the following steps.

1. Run the ABT-instrumented agent.

   Output: ABT-generated spans.

2. Run the direct OI/Otel-instrumented agent.

   Output: reference OI/Otel spans.

3. Compare the two span sets using `TraceComparator`.

   The comparator checks:

   - missing spans,
   - unexpected spans, and
   - materialized attribute key/value differences.

4. Count span-kind mapping checks from ABT-generated spans.

   The script counts spans by `openinference.span.kind`, such as:

   - AGENT
   - CHAIN
   - PROMPT
   - LLM
   - TOOL
   - RETRIEVER
   - RERANKER
   - GUARDRAIL
   - EVALUATOR

5. Count structural equivalence checks for the supporting evidence document.

   These detailed counts are retained as execution evidence, but the paper table focuses on span-kind and attribute-key coverage.

6. Count span-kind-specific attribute-key checks.

   The script counts concrete normalized attribute keys together with their OpenInference span kind. The span kind is part of the coverage target. For example, `TOOL.input.value` and `GUARDRAIL.input.value` are counted as different targets, even though both use the low-level key `input.value`. Indexed list attributes are normalized by replacing numeric indexes with `*`; for example, `llm.input_messages.0.message.role` is normalized to `llm.input_messages.*.message.role`.

   The denominator is the set of 79 span-kind-specific attribute-key targets implemented and checked by the evaluated `ABTToOpenInferenceSemanticMapper` with message-content capture enabled. It is not a claim about all possible OpenInference attributes.

7. Aggregate counts across all scenarios for the target agent.

8. Print a Markdown table.

## Output

The script prints a Markdown table with these columns:

- `Target agent`
- `Validation purpose`
- `OpenInference span kinds exercised`
- `Span-kind-specific attribute keys exercised`

The script also prints a summary sentence confirming whether the comparison found missing spans, unexpected spans, or materialized attribute differences.

## Execution Command

Use the repository source tree on `PYTHONPATH` so the script uses the current workspace code rather than an installed package snapshot.

```powershell
$env:PYTHONPATH='src'
python -X utf8 .\src\experiments\agent_trace_experiments\validation_surface_measurement.py
```

## Relation to Table 9

The printed Markdown table is copied into Table 9 of the paper.

The current supporting data copy is stored in:

```text
docs/abt-paper/5-comparison-with-openinference/5-3-oi-otel-compatible-trace-generation/table-9-oi-otel-compatible-trace-generation-supporting-data.md
```

The measurement pipeline can be summarized as:

```text
scenario catalog
  -> ABT-instrumented agent execution
  -> direct OI/Otel-instrumented agent execution
  -> span comparison
  -> validation-surface counting
  -> Markdown table output
  -> Table 9 and supporting data document
```
