from dataclasses import dataclass
from typing import Literal, Optional

LLMBackendName = Literal["ollama", "openai", "claude"]

@dataclass
class LLMRequest:
    messages: list[dict]
    model: Optional[str] = None
    temperature: float = 0.7
    stream: bool = False

@dataclass
class LLMResponse:
    text: str
    backend: str
    model: Optional[str] = None
