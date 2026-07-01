# Table 8 Supporting Data: SWE-agent Core Execution Scenario Scale

This document records the SWE-agent core execution data used to extend Table 8.

## Source Target

Source repository: https://github.com/princeton-nlp/SWE-agent

Evaluated scope: core execution scope consisting of `sweagent/agent`, `sweagent/tools`, and `sweagent/environment`.

Measured source LOC: 5,001 non-empty, non-comment LOC.

The experiment uses controlled source-level scenarios modeled after the SWE-agent issue-solving loop. The purpose is to cover software-engineering agent behavior not emphasized by the other target agents, including file inspection, patch application, shell command execution, test execution, submission, and failure-driven retry. Semantic action instrumentation records PromptAction and LLMAction spans for issue parsing, patch generation, direct file editing, and test-failure diagnosis; RetrieverAction spans for file inspection; and GuardrailAction spans for command, patch, retrieval, and test-result validation.

## Scenario Catalog Data

| Scenario | Main situation | Source node steps | Generated spans | Major Action span counts |
|---|---|---:|---:|---|
| `fix_small_bug_success` | Localize a bug, apply a patch, pass tests, and submit | 5 | 23 | Input 1; Prompt 2; LLM 2; Tool 5; Retriever 1; Guardrail 5 |
| `test_failure_retry_success` | Apply a patch, observe failing tests, revise, pass tests, and submit | 8 | 36 | Input 1; Prompt 4; LLM 4; Tool 8; Retriever 1; Guardrail 8 |
| `invalid_command_recovery` | Recover from an invalid shell command before patching and submitting | 7 | 29 | Input 1; Prompt 2; LLM 2; Tool 7; Retriever 1; Guardrail 7 |
| `patch_apply_failure_recovery` | Recover from a rejected patch with direct file editing | 6 | 28 | Input 1; Prompt 3; LLM 3; Tool 6; Retriever 1; Guardrail 6 |
| `multi_file_patch_success` | Inspect and patch multiple files before final validation | 15 | 64 | Input 1; Prompt 6; LLM 6; Tool 15; Retriever 4; Guardrail 15 |
| `long_debugging_session` | Diagnose repeated test failures and command recovery over a longer debugging session | 20 | 81 | Input 1; Prompt 7; LLM 7; Tool 20; Retriever 4; Guardrail 20 |
| `regression_retry_loop` | Exercise repeated regression retries, patch failures, test failures, and final submission | 31 | 120 | Input 1; Prompt 11; LLM 11; Tool 31; Retriever 2; Guardrail 31 |
| `repository_exploration_repair` | Explore repository structure, inspect multiple files, recover from patch rejection, and validate the fix | 35 | 128 | Input 1; Prompt 6; LLM 6; Tool 35; Retriever 8; Guardrail 35 |
| `multi_file_regression_repair` | Repair a multi-file regression with repeated test failures and patch revisions | 46 | 171 | Input 1; Prompt 12; LLM 12; Tool 46; Retriever 6; Guardrail 46 |
| `long_patch_validation_loop` | Validate a difficult patch through repeated targeted tests, full tests, command recovery, and submissions | 55 | 198 | Input 1; Prompt 13; LLM 13; Tool 55; Retriever 4; Guardrail 55 |
| `complex_issue_resolution` | Resolve a complex issue with repository exploration, patch failures, test failures, retries, and final validation | 60 | 218 | Input 1; Prompt 14; LLM 14; Tool 60; Retriever 7; Guardrail 60 |

## Summary Statistics

| Statistic | Value |
|---|---:|
| Scenario count | 11 |
| Total generated span instances | 1,096 |
| Average generated span count per scenario | 99.64 |
| Minimum generated span count | 23 |
| Maximum generated span count | 218 |

## Span Kind Breakdown

| Scenario | Total spans | AGENT | CHAIN | PROMPT | LLM | TOOL | RETRIEVER | GUARDRAIL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `fix_small_bug_success` | 23 | 1 | 6 | 2 | 2 | 6 | 1 | 5 |
| `test_failure_retry_success` | 36 | 1 | 9 | 4 | 4 | 9 | 1 | 8 |
| `invalid_command_recovery` | 29 | 1 | 8 | 2 | 2 | 8 | 1 | 7 |
| `patch_apply_failure_recovery` | 28 | 1 | 7 | 3 | 3 | 7 | 1 | 6 |
| `multi_file_patch_success` | 64 | 1 | 16 | 6 | 6 | 16 | 4 | 15 |
| `long_debugging_session` | 81 | 1 | 21 | 7 | 7 | 21 | 4 | 20 |
| `regression_retry_loop` | 120 | 1 | 32 | 11 | 11 | 32 | 2 | 31 |
| `repository_exploration_repair` | 128 | 1 | 36 | 6 | 6 | 36 | 8 | 35 |
| `multi_file_regression_repair` | 171 | 1 | 47 | 12 | 12 | 47 | 6 | 46 |
| `long_patch_validation_loop` | 198 | 1 | 56 | 13 | 13 | 56 | 4 | 55 |
| `complex_issue_resolution` | 218 | 1 | 61 | 14 | 14 | 61 | 7 | 60 |


