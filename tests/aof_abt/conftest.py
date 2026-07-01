import pytest

from aof.abt import ABT, ExportTargetFactory


@pytest.fixture
def memory_export_target():
    return ExportTargetFactory().create_memory_export_target(
        service_name="test-abt",
    )


@pytest.fixture
def abt(memory_export_target):
    return ABT.start_recording(
        export_target=memory_export_target,
        capture_message_content=True,
    )


