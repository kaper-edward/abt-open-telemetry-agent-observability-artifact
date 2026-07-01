from aof.abt.abt_model.trace_action_container import TraceActionContainer


class Task(TraceActionContainer):
    _element_type = "task"
    _span_prefix = "task"
