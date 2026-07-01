import json
from dataclasses import asdict, is_dataclass
from typing import Any

from pydantic import BaseModel


class JsonSerializer:
    def __init__(self, model_type: type[BaseModel] | type[Any]):
        self._model_type = model_type

    def to_json_schema(self) -> str:
        return json.dumps(
            self._model_type.model_json_schema(),
            ensure_ascii=False,
            indent=2,
        )

    def to_json(self, value: BaseModel | Any) -> str:
        if isinstance(value, BaseModel):
            data = value.model_dump(mode="json")
        elif is_dataclass(value):
            data = asdict(value)
        else:
            data = value
        return json.dumps(
            data,
            default=str,
            ensure_ascii=False,
            sort_keys=True,
        )
