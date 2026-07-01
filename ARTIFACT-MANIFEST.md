# ABT GitHub Artifact Manifest

This folder is a clean GitHub-upload snapshot generated from the working repository.

Included groups:

- ABT framework source: `src/aof/abt/`
- Target agent controlled evaluation harnesses and instrumentation variants: `src/experiments/*_base/`, `src/experiments/*_abt/`, `src/experiments/*_oi/`
- Customer Support Agent source: `src/experiments/support_agent/`, `src/experiments/support_application/`
- Public target-agent source metadata: `src/experiments/_evaluation_resources/target_agent_references/*/SOURCE-METADATA.md`
- Open Deep Research source snapshot: `src/experiments/_evaluation_resources/target_agent_references/open_deep_research/source/` without nested `.git/`
- Evaluation scripts: `src/experiments/agent_trace_experiments/`
- Tests: `tests/`
- Artifact documentation, abbreviated-listing support, and table-level supporting data: `docs/abt-paper/ARTIFACT-PACKAGE.md`, `docs/abt-paper/4-agent-behavior-trace-framework/`, `docs/abt-paper/5-comparison-with-openinference/`

Excluded groups:

- local virtual environments and worktrees
- Python caches
- temporary outputs
- local Korean submission files
- internal drafting notes
- nested external `.git/` metadata
- full upstream source snapshots for CrewAI, AutoGen, and SWE-agent; these targets are represented by source metadata and controlled source-level evaluation harnesses

Reproduction entry point:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
$env:PYTHONPATH='src'
python -X utf8 .\src\experiments\agent_trace_experiments\validation_surface_measurement.py
python -X utf8 .\src\experiments\agent_trace_experiments\rule_guideline_analysis.py
python -X utf8 .\src\experiments\agent_trace_experiments\instrumentation_effort_measurement.py
```
