from aof.abt.abt_model.trace_action import TraceAction


class PromptAction(TraceAction):
    _element_type = "prompt"
    _span_prefix = "prompt"

    def template(self, value: str):
        self._ensure_open()
        self._semantic_mapper.set_prompt_template(self, value)
        return self

    def variables(self, value: object):
        self._ensure_open()
        self._semantic_mapper.set_prompt_variables(self, value)
        return self
