# Controlled Evaluation Harness and Dependency Simulation Supporting Data

This document records how the evaluation uses controlled evaluation harnesses to fix nondeterministic external dependencies while preserving the behavior structures used for trace-generation validation. It is intended as supporting data for reviewer questions about whether the target agents were executed live, mocked, simulated, or replayed.

## Evaluation Principle

The evaluation validates trace generation rather than task quality or answer quality. Therefore, external dependencies that introduce nondeterminism, cost, credentials, or side effects are controlled through fixtures or test doubles. In this document, a controlled evaluation harness means an experimental program that makes the same scenario produce the same behavior sequence for both ABT and direct OI/Otel variants. The harness preserves the behavior boundaries being instrumented, including source-level orchestration boundaries, node boundaries, task boundaries, branch behavior, retry behavior, or multi-agent routing structure.

The following dependencies are considered safe to replace for this evaluation:

- LLM responses
- external API calls
- web search results
- retrieved documents
- network I/O
- credentials
- database contents
- filesystem side effects
- random or time-dependent outputs

The following elements should not be replaced if they are the object of instrumentation:

- source graph or flow node boundaries
- task or crew boundaries
- agent routing structure
- tool orchestration structure
- retry, fallback, and branch behavior
- source-level operation sequence used for span generation

## Target-Specific Evaluation Harnesses

| Target agent | Evaluation harness mode | Preserved behavior structure | Controlled dependencies |
|---|---|---|---|
| Customer support agent | Controlled local agent execution | Local task flow, routing, policy decision, fallback, handoff, response generation sequence | LLM gateway outputs, in-memory order/policy store, selected branch-forcing fixtures |
| Open Deep Research | Public source graph execution with controlled dependencies | Original LangGraph source graph nodes and subgraph responsibilities | LLM outputs, search results, retrieved documents, external service behavior |
| CrewAI Write-a-Book Flow | Controlled source-level evaluation harness derived from public CrewAI flow structure | Outline, chapter writing, review, conditional revision, and assembly sequence | Crew execution results, LLM outputs, generated chapter contents |
| AutoGen Distributed Group Chat | Controlled source-level evaluation harness derived from public AutoGen group-chat sample | Manager, writer, editor, optional fact-checker, routing, and finalizer sequence | Agent message contents, review decisions, final response contents |
| SWE-agent Core Execution | Controlled source-level evaluation harness derived from public SWE-agent core execution structure | Issue parsing, file inspection, patch application, shell command execution, test execution, failure diagnosis, retry, and submission sequence | Shell command results, test outcomes, patch application results, filesystem side effects |

## Interpretation

The five targets provide complementary execution scopes. The customer support agent and Open Deep Research preserve executable agent or source graph structure. CrewAI Write-a-Book Flow, AutoGen Distributed Group Chat, and SWE-agent Core Execution preserve public example or public agent behavior patterns through controlled source-level evaluation harnesses. For these targets, the artifact records the public source scope under `src/experiments/_evaluation_resources/target_agent_references/*/SOURCE-METADATA.md` and provides a reproducible controlled evaluation harness under `src/*_base/`. This evaluation design uses the public-framework targets to evaluate trace-generation portability across orchestration styles and domains, while the customer support target evaluates span-kind and ABT Action-type diversity.

Controlled fixtures make the trace-generation comparison reproducible. Both ABT and direct OI/Otel variants use the same controlled behavior sequence for each scenario.


