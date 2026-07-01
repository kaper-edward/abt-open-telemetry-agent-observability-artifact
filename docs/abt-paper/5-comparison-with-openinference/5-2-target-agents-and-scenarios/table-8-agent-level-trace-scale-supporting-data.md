# Table 8 Supporting Data: Agent-Level Generated Trace Scale

This document records the agent-level summary used in Table 8. Per-scenario details are recorded in the target-specific Table 8 supporting-data files.

| Target agent | Scenarios | Total spans | Avg. spans/scenario | Min-Max spans/scenario | Major Action span totals |
|---|---:|---:|---:|---:|---|
| Customer support agent | 8 | 164 | 20.50 | 13-30 | Input 8; Prompt 13; LLM 13; Embedding 3; Tool 15; Retriever 3; Reranker 3; Guardrail 37; Evaluator 2 |
| Open Deep Research | 5 | 479 | 95.80 | 59-151 | Input 5; Prompt 64; LLM 64; Tool 100; Retriever 36; Guardrail 100 |
| CrewAI Write-a-Book Flow | 3 | 178 | 59.33 | 41-81 | Input 3; Prompt 32; LLM 32; Tool 35; Guardrail 19; Evaluator 16 |
| AutoGen Distributed Group Chat | 3 | 139 | 46.33 | 28-58 | Input 3; Prompt 26; LLM 26; Tool 26; Guardrail 18; Evaluator 8 |
| SWE-agent Core Execution | 11 | 1,096 | 99.64 | 23-218 | Input 11; Prompt 80; LLM 80; Tool 288; Retriever 39; Guardrail 288 |

## Total

| Statistic | Value |
|---|---:|
| Target agents | 5 |
| Scenarios | 30 |
| Generated span instances | 2,056 |


