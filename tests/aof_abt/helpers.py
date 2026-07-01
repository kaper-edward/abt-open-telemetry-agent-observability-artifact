import json

from openinference.semconv.trace import SpanAttributes


def spans_by_name(memory_export_target):
    return {span.name: span for span in memory_export_target.spans()}


def abt_metadata(span):
    return json.loads(span.attributes[SpanAttributes.METADATA])["abt"]
