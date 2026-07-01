from types import TracebackType

from aof.abt import ABT, ExportTargetFactory
from experiments.customer_support_agent_abt.telemetry_config import TelemetryConfig


class NoTelemetrySession:
    def __enter__(self):
        return None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        return False


class AbtTelemetrySession:
    def __init__(self, telemetry_config: TelemetryConfig):
        self._telemetry_config = telemetry_config

    def __enter__(self):
        export_target = ExportTargetFactory().create_network_export_target(
            self._telemetry_config.otlp_endpoint,
            service_name=self._telemetry_config.service_name,
        )
        self._abt = ABT.start_recording(
            export_target=export_target,
            capture_message_content=self._telemetry_config.capture_message_content,
        )
        return self._abt

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        self._abt.export_recorded_traces()
        self._abt.close_recording()
        return False
