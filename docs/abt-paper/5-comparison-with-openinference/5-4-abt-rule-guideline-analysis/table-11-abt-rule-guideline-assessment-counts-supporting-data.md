# Table 11 Supporting Data: Assessment Counts for ABT Rules and Guidelines

This document records supporting data for Table 11, which analyzes whether the evaluated ABT traces exercise the rules and guidelines defined in Section 3.3. The purpose of this analysis is not to prove that the ABT Model is universally valid. It checks whether the generated traces used in the evaluation instantiate the model-level rules and sequence guidelines, and whether the resulting traces satisfy the observable conditions associated with each rule or guideline.

## Measurement Command

The following command generates the table below:

```powershell
$env:PYTHONPATH='src'
python -X utf8 .\src\experiments\agent_trace_experiments\rule_guideline_analysis.py
```

The measurement script is located at:

```text
src/experiments/agent_trace_experiments/rule_guideline_analysis.py
```

## Measurement Scope

The analysis uses the same five target agents and thirty controlled scenarios used in the framework evaluation:

| Target agent | Scenario count |
|---|---:|
| Customer Support Agent | 8 |
| Open Deep Research | 5 |
| CrewAI Write-a-Book Flow | 3 |
| AutoGen Distributed Group Chat | 3 |
| SWE-agent Core Execution | 11 |
| Total | 30 |

The script executes the ABT-instrumented variant for each scenario, collects the generated spans, reads ABT metadata from the OpenInference metadata attribute, and evaluates each rule or guideline over the generated span hierarchy.

## Counting Rules

| Rule/Guideline | Counting method |
|---|---|
| R1.1 | Counts Agent spans and checks whether each Agent has one or more direct Trace children. |
| R1.2 | Counts Trace spans and checks whether each Trace has exactly one direct InputAction child and whether that child is the first ordered child. |
| R1.3 | Counts Trace spans and checks whether all non-input direct children are Task spans. |
| R1.4 | Counts Task and Block spans and checks whether each contains at least one descendant TraceAction. |
| R2.1 | Counts TraceAction spans and checks whether each completed action has `output.value`. |
| R2.2 | Counts typed TraceAction spans and checks subtype-specific required fields, such as LLM model information, Tool target information, Retriever/Reranker input and output, and judgment metadata. |
| R2.3 | Counts GuardrailAction and EvaluatorAction spans and checks whether each has decision metadata and `output.value`. |
| R3.1 | Counts TraceStructure spans with `input.value` and checks whether the value is consistent with a direct child input or output value. |
| R3.2 | Counts TraceStructure spans with `output.value` and checks whether the value is consistent with a direct child `output.value`. |
| R3.3 | Counts TraceStructure spans with children and checks whether each structure span contains the time intervals of its direct children. |
| G1 | Counts LLMAction spans and checks whether each LLMAction has a preceding PromptAction sibling in the same container. |
| G2 | Counts LLMAction spans and checks whether each LLMAction has a following GuardrailAction or EvaluatorAction sibling in the same container. |
| G3 | Counts GuardrailAction and EvaluatorAction spans and checks whether each judgment action has decision metadata and later or terminal behavior in the same Trace. |

## Aggregate Satisfaction Results

| Rule/Guideline | Meaning | Assessment unit | Satisfied/Assessable | Target count | Scenario count | Observed data |
|---|---|---|---:|---:|---:|---|
| R1.1 | Agent must contain request-level Traces | Agent spans | 30/30 | 5/5 | 30/30 | Agent spans with one or more direct Trace children. |
| R1.2 | Trace must begin with exactly one Initial InputAction | Trace spans | 30/30 | 5/5 | 30/30 | Trace spans with exactly one direct InputAction child as the first child. |
| R1.3 | Trace must contain Tasks after the Initial InputAction | Trace spans | 30/30 | 5/5 | 30/30 | Trace spans whose non-input direct children are Task spans. |
| R1.4 | Task and Block must contain at least one TraceAction | Task/Block spans | 500/500 | 5/5 | 30/30 | Task and Block spans with at least one descendant TraceAction. |
| R2.1 | Completed TraceAction must have final output | TraceAction spans | 1496/1496 | 5/5 | 30/30 | Finished action spans with `output.value`. |
| R2.2 | TraceAction subtype must satisfy subtype-specific required information | Typed action spans | 1496/1496 | 5/5 | 30/30 | Action spans with subtype-specific required attributes or metadata. |
| R2.3 | GuardrailAction and EvaluatorAction must record judgment output | Judgment action spans | 488/488 | 5/5 | 30/30 | Guardrail/Evaluator spans with decision metadata and `output.value`. |
| R3.1 | TraceStructure input must be consistent with child input | Structure spans with input | 560/560 | 5/5 | 30/30 | Structure `input.value` is consistent with a child input/output value. |
| R3.2 | TraceStructure output must be consistent with child output | Structure spans with output | 512/560 | 5/5 | 30/30 | Structure `output.value` is consistent with a child `output.value`. |
| R3.3 | TraceStructure time interval must be aligned with child intervals | Structure spans with children | 560/560 | 5/5 | 30/30 | Structure start/end time contains all direct child start/end times. |
| G1 | LLMAction should be preceded by PromptAction | LLM spans | 215/215 | 5/5 | 30/30 | LLM spans with a PromptAction sibling that starts no later in the same container. |
| G2 | LLMAction should be followed by GuardrailAction or EvaluatorAction | LLM spans | 215/215 | 5/5 | 30/30 | LLM spans with a later Guardrail/Evaluator sibling in the same container. |
| G3 | GuardrailAction or EvaluatorAction should be followed by behavior consistent with its judgment | Judgment action spans | 488/488 | 5/5 | 30/30 | Judgment spans with decision metadata and later or terminal behavior in the same Trace. |

## Applicable Situations by Target Agent

This table is the version intended for the paper body. Since every rule and guideline is assessed in all five target agents, a target-level present/not-present column is not informative. The table instead reports the number of assessment situations for each rule or guideline in each target agent. The Rule focus column clarifies why some rules have identical counts: they can be assessed over the same element population while checking different model-level conditions.

| Rule/Guideline | Rule focus | Assessment unit | Customer Support | Open Deep Research | CrewAI | AutoGen | SWE-agent | Total |
|---|---|---|---:|---:|---:|---:|---:|---:|
| R1.1 | Agent-to-Trace containment | Agent spans | 8 | 5 | 3 | 3 | 11 | 30 |
| R1.2 | Initial request input | Trace spans | 8 | 5 | 3 | 3 | 11 | 30 |
| R1.3 | Task organization after input | Trace spans | 8 | 5 | 3 | 3 | 11 | 30 |
| R1.4 | Observable actions in containers | Task/Block spans | 51 | 100 | 35 | 26 | 288 | 500 |
| R2.1 | Final action output | TraceAction spans | 97 | 369 | 137 | 107 | 786 | 1496 |
| R2.2 | Subtype-required fields | Typed action spans | 97 | 369 | 137 | 107 | 786 | 1496 |
| R2.3 | Judgment decision output | Judgment action spans | 39 | 100 | 35 | 26 | 288 | 488 |
| R3.1 | Structural input consistency | Structure spans with input | 67 | 110 | 41 | 32 | 310 | 560 |
| R3.2 | Structural output consistency | Structure spans with output | 67 | 110 | 41 | 32 | 310 | 560 |
| R3.3 | Structural time containment | Structure spans with children | 67 | 110 | 41 | 32 | 310 | 560 |
| G1 | Prompt before LLM | LLM spans | 13 | 64 | 32 | 26 | 80 | 215 |
| G2 | Judgment after LLM | LLM spans | 13 | 64 | 32 | 26 | 80 | 215 |
| G3 | Judgment-related subsequent behavior | Judgment action spans | 39 | 100 | 35 | 26 | 288 | 488 |

## Interpretation

The TraceStructure Completeness Rules are observed and satisfied in the evaluated traces. All thirty Agent spans contain request-level Traces, all Trace spans begin with one Initial InputAction, all non-input Trace children are Task spans, and all Task/Block spans contain at least one descendant TraceAction.

The TraceAction Completeness Rules are also observed and satisfied after accounting for successful and failure scenarios. Retriever and Reranker actions in failure scenarios may produce empty result sets, but they still record the input and final output required to interpret the action. GuardrailAction and EvaluatorAction spans consistently record judgment output through decision metadata and `output.value`.

The time consistency rule for TraceStructure is fully satisfied. Every structure span contains the time intervals of its direct children. This supports the interpretation that Agent, Trace, Task, and Block spans act as behavior scopes over their contained elements.

R3.1 is fully satisfied under the consistency criterion: each TraceStructure input is consistent with a direct child input or output value. R3.2 is partially satisfied because some Task spans record explicit state summaries rather than values directly contained in a child output. These cases are useful for evaluating the boundary of the rule: the paper should distinguish child-derived structural output from explicit structural summary. Therefore, the R3.2 row should be interpreted as data about structural-output consistency, not as a count of invalid traces.

The sequence guidelines G1, G2, and G3 are observed and satisfied under the measured criterion. Every LLMAction has a preceding PromptAction and a following GuardrailAction or EvaluatorAction in the same container. Every judgment action records decision metadata and is associated with either later behavior or terminal behavior in the same Trace. Since G3 is a guideline rather than a validity rule, terminal judgment cases should be discussed as boundary cases of sequence interpretation rather than as trace invalidity.

## Paper Use

If this analysis is included in the journal paper, it should be framed as analysis of ABT rules and guidelines:

- Section 3 defines ABT validity rules and sequence guidelines.
- Section 5 can report that the evaluated scenarios exercise all rule/guideline categories.
- The result supports the claim that the evaluation traces instantiate the model-level conditions defined in Section 3.
- It should not be stated as a proof that the ABT rules are complete for all possible agent systems.


