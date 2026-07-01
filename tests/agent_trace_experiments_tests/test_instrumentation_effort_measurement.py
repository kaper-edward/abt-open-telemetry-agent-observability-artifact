from pathlib import Path

from experiments.agent_trace_experiments.instrumentation_effort_measurement import measure_all


def test_crewai_and_autogen_have_target_specific_effort_measurements():
    measurements = {item.target_name: item for item in measure_all(Path.cwd())}

    crewai = measurements["CrewAI Write-a-Book Flow"]
    autogen = measurements["AutoGen Distributed Group Chat"]

    assert crewai.abt != autogen.abt
    assert crewai.direct != autogen.direct
