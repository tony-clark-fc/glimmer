"""LLM task modules — high-level task functions wiring provider + prompts.

PLAN:WorkstreamI.PackageI3-I7

Each task module provides:
- An async function that calls the provider with the right prompt
- Input from domain context (projects, messages, stakeholders)
- Output as validated typed results
- Clean fallback when the provider is unavailable
"""

