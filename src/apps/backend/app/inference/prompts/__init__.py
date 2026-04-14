"""Glimmer prompt templates — task-specific system and user prompts.

PLAN:WorkstreamI.PackageI2.PromptFramework

Each module exports:
- SYSTEM_PROMPT: the system-level instruction
- build_user_prompt(...): assembles domain context into the user message
- RESPONSE_SCHEMA_DOC: human-readable doc of expected JSON output shape

All templates are Python string constants (not external files).
Prompt engineering approach: instruct the model to output ONLY valid JSON,
without relying on provider-specific response_format modes (portability).
"""

