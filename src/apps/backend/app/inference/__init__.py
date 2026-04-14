"""Glimmer inference module — LLM integration abstraction layer.

PLAN:WorkstreamI.PackageI1.InferenceAbstraction
PLAN:WorkstreamI.PackageI2.PromptFramework
ARCH:LocalInferenceBaseline

Provides a clean provider protocol for LLM inference, with an
OpenAI-compatible implementation targeting LM Studio (local-first).
Includes prompt templates, context assembly, and response parsing.
"""

from app.inference.base import (
    InferenceProvider,
    InferenceResult,
    ProviderHealth,
    InferenceError,
)
from app.inference.config import InferenceSettings
from app.inference.response_parser import ParseResult, parse_llm_response
from app.inference.context_builder import (
    TokenBudget,
    estimate_tokens,
    truncate_to_token_budget,
    assemble_messages,
)

__all__ = [
    # I1 — Provider abstraction
    "InferenceProvider",
    "InferenceResult",
    "ProviderHealth",
    "InferenceError",
    "InferenceSettings",
    # I2 — Prompt framework
    "ParseResult",
    "parse_llm_response",
    "TokenBudget",
    "estimate_tokens",
    "truncate_to_token_budget",
    "assemble_messages",
]

