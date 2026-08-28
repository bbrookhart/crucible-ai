"""Optional adapter for a local OpenAI-compatible inference endpoint."""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Mapping
from typing import Any
from urllib.request import Request, urlopen

from crucible.models.base import ModelAdapter
from crucible.schemas import ModelMetadata, ModelResponse, TaskContext


class LocalOpenAIAdapter(ModelAdapter):
    def __init__(self, endpoint: str | None = None, model_name: str | None = None) -> None:
        selected_endpoint = endpoint or os.getenv(
            "CRUCIBLE_LOCAL_ENDPOINT", "http://127.0.0.1:11434/v1/chat/completions"
        )
        selected_model = model_name or os.getenv("CRUCIBLE_LOCAL_MODEL", "UNKNOWN")
        if selected_endpoint is None or selected_model is None:
            raise ValueError("local endpoint and model name must be configured")
        self.endpoint: str = selected_endpoint
        self.model_name: str = selected_model
        if not self.endpoint.startswith(("http://127.0.0.1", "http://localhost")):
            raise ValueError("v0.1 local adapter accepts loopback endpoints only")

    async def infer(
        self,
        context: TaskContext,
        observations: Mapping[str, str] | None = None,
    ) -> ModelResponse:
        prompt = context.model_dump_json()
        if observations:
            prompt += "\nOBSERVATIONS\n" + json.dumps(dict(observations), sort_keys=True)
        payload: dict[str, Any] = {
            "model": self.model_name,
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are inside an isolated defensive evaluation. "
                        "Use only supplied evidence."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        result = await asyncio.to_thread(self._post, payload)
        usage: dict[str, Any] = result.get("usage", {})
        choices: list[dict[str, Any]] = result["choices"]
        return ModelResponse(
            content=str(choices[0]["message"]["content"]),
            input_tokens=int(usage.get("prompt_tokens", 0)),
            output_tokens=int(usage.get("completion_tokens", 0)),
        )

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(  # noqa: S310 - loopback-only endpoint validated above
            self.endpoint,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=60) as response:  # noqa: S310
            parsed: dict[str, Any] = json.loads(response.read())
            return parsed

    async def metadata(self) -> ModelMetadata:
        return ModelMetadata(
            model_id=f"local:{self.model_name}",
            provider="LOCAL_OPENAI_COMPATIBLE",
            model_name=self.model_name,
            model_version="UNKNOWN",
            tool_support=False,
            weights_pinnable=False,
        )
