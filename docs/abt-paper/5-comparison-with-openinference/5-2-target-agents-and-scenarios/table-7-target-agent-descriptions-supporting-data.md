# Table 7 Supporting Data: Target Agent Descriptions

This document records the data used in Table 7, "Descriptions of the target agents."

## Measurement Scope

The table reports target-agent characteristics relevant to the evaluation: evaluation purpose, source size, agent function, and major behavior tasks. Generated trace size is reported separately in Table 8. Implementation-level counts such as LLM call sites and tool-binding call sites are excluded from the paper table because they are implementation details rather than the primary reason for selecting the targets.

The Customer Support Agent is a local evaluation target developed for this study. The four other targets are based on public agent projects or examples: Open Deep Research (`https://github.com/langchain-ai/open_deep_research`), CrewAI examples (`https://github.com/crewAIInc/crewAI-examples`), Microsoft AutoGen (`https://github.com/microsoft/autogen`), and SWE-agent (`https://github.com/SWE-agent/SWE-agent`). Their source scopes and harness construction notes are recorded in `src/experiments/_evaluation_resources/target_agent_references/*/SOURCE-METADATA.md`.

## Measurement Results

| Target agent | Evaluation purpose | Source LOC | Agent function | Major behavior tasks |
|---|---|---:|---|---|
| Customer support agent | Span-kind and ABT Action-type diversity target | 1,453 | Handles customer support requests about orders and policies, then produces a grounded support response or fallback/handoff result. | Intent classification, request routing, order lookup, policy retrieval, policy reranking, policy decision, response generation, response grounding, answer evaluation, fallback handling, handoff, finalization |
| Open Deep Research | Public source graph node-level instrumentation target | 1,755 | Conducts research over a user question by planning research, delegating search work, compressing findings, and generating a final report. | Clarification, research brief generation, supervisor planning, delegated researcher execution, search/tool execution, research compression, final report generation |
| CrewAI Write-a-Book Flow | Public CrewAI flow orchestration target | 1,598 | Produces a book by creating an outline, writing chapters through crews, reviewing chapters, revising selected chapters, and assembling the final book. | Book outlining, chapter generation, chapter review, conditional revision, book assembly |
| AutoGen Distributed Group Chat | Public AutoGen multi-agent routing target | 579 | Coordinates a group-chat style workflow among manager, writer, editor, optional fact-checker, and finalizer agents. | Manager planning, writer drafting, editor review, fact checking, routing, final response generation |
| SWE-agent Core Execution | Public software-engineering agent core execution target | 5,001 | Solves software engineering issues by inspecting files, applying patches, executing shell commands and tests, recovering from failures, and submitting fixes. | Issue parsing, file inspection, patch application, shell command execution, test execution, failure diagnosis, retry, submission |

## Counting Notes

Source LOC counts non-empty, non-comment Python lines in the corresponding source target. The customer support major behavior tasks are based on the explicit task flow implemented by the local customer support agent. The Open Deep Research major behavior tasks are based on the executed source graph nodes and subgraph responsibilities in the pinned public source package. The CrewAI and AutoGen rows are based on the public example source directories `flows/write_a_book_with_flows` and `python/samples/core_distributed-group-chat`, respectively. The SWE-agent row is based on the core execution scope consisting of `sweagent/agent`, `sweagent/tools`, and `sweagent/environment`.

The Open Deep Research source also contains a legacy implementation. The current package is used for Table 7 because it is the active source package used as the public evaluation target.


