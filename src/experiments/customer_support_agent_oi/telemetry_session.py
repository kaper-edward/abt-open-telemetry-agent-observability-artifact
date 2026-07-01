from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from experiments.customer_support_agent_abt.telemetry_config import TelemetryConfig
from experiments.customer_support_agent_oi.langchain_instrumentor import OiLangChainInstrumentor
from experiments.customer_support_agent_oi.telemetry_context import OiTelemetryContext


class OiTelemetrySession:
    def __init__(self, telemetry_config: TelemetryConfig):
        self._telemetry_config = telemetry_config
        self._tracer_provider = None

    def __enter__(self):
        tracer_provider = TracerProvider(
            resource=Resource.create(
                {"service.name": self._telemetry_config.service_name}
            )
        )
        tracer_provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=self._telemetry_config.otlp_endpoint)
            )
        )
        self._tracer_provider = tracer_provider
        OiLangChainInstrumentor().instrument(tracer_provider)
        OiTelemetryContext.configure(
            tracer_provider.get_tracer("customer_support_agent.direct_oi")
        )
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        OiTelemetryContext.clear()
        if self._tracer_provider is not None:
            self._tracer_provider.force_flush()
            self._tracer_provider.shutdown()
        return False
