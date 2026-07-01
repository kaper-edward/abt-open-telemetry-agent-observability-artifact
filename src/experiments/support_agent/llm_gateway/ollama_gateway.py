from typing import Any

from experiments.support_agent.prompting import Prompt


class OllamaGateway:
    def __init__(self, model: Any):
        self._model = model

    @property
    def model_name(self) -> str | None:
        model_name = getattr(self._model, "model", None)
        if isinstance(model_name, str):
            return model_name
        return None

    def invoke(self, prompt: Prompt | list[Any]) -> str:
        messages = self._messages(prompt)
        response = self._model.invoke(messages)
        content = getattr(response, "content", response)
        if not isinstance(content, str):
            raise TypeError("model response content must be text")
        return content

    @staticmethod
    def _messages(prompt: Prompt | list[Any]) -> list[Any]:
        if isinstance(prompt, Prompt):
            return [("human", prompt.render())]
        return prompt
