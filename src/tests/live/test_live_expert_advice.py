"""Live expert advice (chat) test — full round-trip through real Gemini.

TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult
TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse
TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected

Each test run picks a RANDOM prompt from a large pool so that repeated
runs never produce the same interaction pattern. This avoids training
Gemini on a fixed sequence and keeps the tests from being trivially
predictable.

It uses Fast mode to minimize latency (~5-15 seconds).
"""

from __future__ import annotations

import random
from typing import Any, Tuple

import pytest
from app.research.adapter import GeminiAdapter
from app.research.contracts import ChatRequest, ChatResult

pytestmark = [pytest.mark.manual_only]


# ═══════════════════════════════════════════════════════════════════════
# Large question pool — each entry is (prompt, validator).
# The validator receives the response text and returns True if plausible.
# Keep prompts short and answers easily verifiable.
# ═══════════════════════════════════════════════════════════════════════

def _contains_any(text: str, words: list[str]) -> bool:
    """True if text (lowered) contains any of the given words."""
    low = text.lower()
    return any(w in low for w in words)


# (prompt_text, answer_validator_function)
QUESTION_POOL: list[Tuple[str, Any]] = [
    # ── Arithmetic ──
    ("What is 2 + 2? Reply with just the number.",
     lambda r: "4" in r),
    ("What is 7 × 8? Reply with just the number.",
     lambda r: "56" in r),
    ("What is 100 ÷ 4? Reply with just the number.",
     lambda r: "25" in r),
    ("What is 15 − 9? Reply with just the number.",
     lambda r: "6" in r),
    ("What is the square root of 144? Reply with just the number.",
     lambda r: "12" in r),
    ("What is 3 cubed? Reply with just the number.",
     lambda r: "27" in r),
    ("What is 17 + 28? Reply with just the number.",
     lambda r: "45" in r),
    ("What is 1000 − 777? Reply with just the number.",
     lambda r: "223" in r),
    ("What is 12 × 12? Reply with just the number.",
     lambda r: "144" in r),
    ("What is 256 ÷ 16? Reply with just the number.",
     lambda r: "16" in r),

    # ── Geography ──
    ("What is the capital of France? Reply with just the city name.",
     lambda r: "paris" in r.lower()),
    ("What is the capital of Japan? Reply with just the city name.",
     lambda r: "tokyo" in r.lower()),
    ("What is the capital of Australia? Reply with just the city name.",
     lambda r: "canberra" in r.lower()),
    ("What is the capital of Brazil? Reply with just the city name.",
     lambda r: _contains_any(r, ["brasília", "brasilia"])),
    ("What is the capital of Canada? Reply with just the city name.",
     lambda r: "ottawa" in r.lower()),
    ("What is the capital of Egypt? Reply with just the city name.",
     lambda r: "cairo" in r.lower()),
    ("What is the capital of South Korea? Reply with just the city name.",
     lambda r: "seoul" in r.lower()),
    ("What is the capital of Italy? Reply with just the city name.",
     lambda r: "rome" in r.lower() or "roma" in r.lower()),
    ("What is the capital of Germany? Reply with just the city name.",
     lambda r: "berlin" in r.lower()),
    ("What is the capital of Argentina? Reply with just the city name.",
     lambda r: "buenos aires" in r.lower()),

    # ── Science ──
    ("What is the chemical symbol for gold? Reply with just the symbol.",
     lambda r: "Au" in r or "au" in r.lower()),
    ("What is the chemical symbol for water? Reply with just the formula.",
     lambda r: "H2O" in r or "h2o" in r.lower()),
    ("How many planets are in our solar system? Reply with just the number.",
     lambda r: "8" in r),
    ("What is the boiling point of water in Celsius? Reply with just the number.",
     lambda r: "100" in r),
    ("What is the speed of light in km/s? Reply with just the approximate number.",
     lambda r: _contains_any(r, ["300000", "300,000", "299792", "299,792"])),
    ("What element has atomic number 1? Reply with just the name.",
     lambda r: "hydrogen" in r.lower()),
    ("What is the hardest natural mineral? Reply with just the name.",
     lambda r: "diamond" in r.lower()),
    ("What gas do plants absorb from the atmosphere? Reply briefly.",
     lambda r: _contains_any(r, ["co2", "carbon dioxide"])),
    ("How many bones are in the adult human body? Reply with just the number.",
     lambda r: "206" in r),
    ("What is the largest organ in the human body? Reply with just the name.",
     lambda r: "skin" in r.lower()),

    # ── Language ──
    ("What is the past tense of 'run'? Reply with just the word.",
     lambda r: "ran" in r.lower()),
    ("What is the plural of 'ox'? Reply with just the word.",
     lambda r: "oxen" in r.lower()),
    ("How many letters are in the English alphabet? Reply with just the number.",
     lambda r: "26" in r),
    ("What language has the most native speakers worldwide? Reply with just the name.",
     lambda r: _contains_any(r, ["mandarin", "chinese"])),
    ("What is the longest word using only the letters A through F? Just answer briefly.",
     lambda r: len(r.strip()) > 0),  # open-ended but must respond

    # ── History ──
    ("In what year did World War II end? Reply with just the year.",
     lambda r: "1945" in r),
    ("Who was the first person to walk on the Moon? Reply with just the name.",
     lambda r: _contains_any(r, ["armstrong", "neil"])),
    ("In what year was the Magna Carta signed? Reply with just the year.",
     lambda r: "1215" in r),
    ("In what century was the printing press invented? Reply briefly.",
     lambda r: "15" in r),
    ("What ancient civilization built the pyramids at Giza? Reply briefly.",
     lambda r: "egypt" in r.lower()),

    # ── Colors and nature ──
    ("What color do you get when you mix red and blue? Reply with just the color.",
     lambda r: "purple" in r.lower() or "violet" in r.lower()),
    ("What color do you get when you mix yellow and blue? Reply with just the color.",
     lambda r: "green" in r.lower()),
    ("Name the three primary colors of light. Reply with just the list.",
     lambda r: _contains_any(r, ["red", "green", "blue"])),
    ("What is the tallest mountain on Earth? Reply with just the name.",
     lambda r: "everest" in r.lower()),
    ("What is the largest ocean on Earth? Reply with just the name.",
     lambda r: "pacific" in r.lower()),
    ("What is the longest river in Africa? Reply with just the name.",
     lambda r: "nile" in r.lower()),
    ("How many continents are there? Reply with just the number.",
     lambda r: "7" in r),
    ("What is the driest continent? Reply with just the name.",
     lambda r: _contains_any(r, ["antarctica", "australia"])),
    ("What is the smallest country in the world by area? Reply with just the name.",
     lambda r: "vatican" in r.lower()),
    ("What is the deepest ocean trench? Reply with just the name.",
     lambda r: "mariana" in r.lower()),

    # ── Math ──
    ("Is 17 a prime number? Reply yes or no.",
     lambda r: "yes" in r.lower()),
    ("What is the value of pi to two decimal places? Reply with just the number.",
     lambda r: "3.14" in r),
    ("What is 2 to the power of 10? Reply with just the number.",
     lambda r: "1024" in r),
    ("How many sides does a hexagon have? Reply with just the number.",
     lambda r: "6" in r),
    ("What is the next prime after 7? Reply with just the number.",
     lambda r: "11" in r),

    # ── Culture and miscellany ──
    ("How many strings does a standard guitar have? Reply with just the number.",
     lambda r: "6" in r),
    ("In chess, which piece can only move diagonally? Reply with just the name.",
     lambda r: "bishop" in r.lower()),
    ("How many players are on a soccer team on the field? Reply with just the number.",
     lambda r: "11" in r),
    ("What note is in the middle of a piano keyboard? Reply briefly.",
     lambda r: _contains_any(r, ["middle c", "c4", "c"])),
    ("How many days are in a leap year? Reply with just the number.",
     lambda r: "366" in r),
    ("What is the Roman numeral for 50? Reply with just the numeral.",
     lambda r: "L" in r),
    ("How many zeros are in one million? Reply with just the number.",
     lambda r: "6" in r),
    ("What shape has three sides? Reply with just the name.",
     lambda r: "triangle" in r.lower()),
    ("What is the freezing point of water in Fahrenheit? Reply with just the number.",
     lambda r: "32" in r),
    ("How many hours are in a week? Reply with just the number.",
     lambda r: "168" in r),
]

assert len(QUESTION_POOL) >= 50, (
    f"Question pool should have 50+ entries, got {len(QUESTION_POOL)}"
)


def _pick_random_question() -> Tuple[str, Any]:
    """Pick one random (prompt, validator) pair from the pool."""
    return random.choice(QUESTION_POOL)


class TestLiveExpertAdvice:
    """Full expert advice round-trip through real Gemini."""

    @pytest.mark.asyncio
    async def test_fast_mode_chat_returns_response(
        self, adapter: GeminiAdapter
    ) -> None:
        """Send a random prompt in Fast mode and get a real response.

        TEST:ExpertAdvice.Invocation.SendsPromptAndReturnsResponse
        TEST:Research.Adapter.GeminiBrowserPathReturnsStructuredResult
        """
        prompt, validator = _pick_random_question()

        request = ChatRequest(prompt=prompt, mode="Fast")
        result = await adapter.execute_chat(request)

        # Verify we got a ChatResult back
        assert isinstance(result, ChatResult)

        # Verify the response has content
        assert result.response_text, "Response text should not be empty"
        assert len(result.response_text) > 0

        # Verify the mode is recorded
        assert result.mode == "Fast"

        # Verify duration was tracked
        assert result.duration_ms > 0

        # Verify the answer is plausible
        assert validator(result.response_text), (
            f"Response validation failed.\n"
            f"  Prompt: {prompt!r}\n"
            f"  Response: {result.response_text!r}"
        )

        # Adapter should be idle after completion
        assert adapter.is_busy is False

    @pytest.mark.asyncio
    async def test_pro_mode_chat_returns_response(
        self, adapter: GeminiAdapter
    ) -> None:
        """Send a random prompt in Pro mode — verifies mode switching works.

        TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected
        """
        prompt, validator = _pick_random_question()

        request = ChatRequest(prompt=prompt, mode="Pro")
        result = await adapter.execute_chat(request)

        assert isinstance(result, ChatResult)
        assert result.response_text, "Response text should not be empty"
        assert result.mode == "Pro"
        assert result.duration_ms > 0

        # Verify the answer is plausible
        assert validator(result.response_text), (
            f"Response validation failed.\n"
            f"  Prompt: {prompt!r}\n"
            f"  Response: {result.response_text!r}"
        )

    @pytest.mark.asyncio
    async def test_adapter_not_busy_after_chat(
        self, adapter: GeminiAdapter
    ) -> None:
        """Adapter releases the operation lock after chat completes."""
        assert adapter.is_busy is False, (
            "Adapter should be idle — lock may be stuck from a previous failure"
        )


class TestLiveChatErrorHandling:
    """Verify error handling works with a real browser."""

    @pytest.mark.asyncio
    async def test_invalid_mode_rejected_before_browser(
        self, adapter: GeminiAdapter
    ) -> None:
        """Invalid mode raises ValueError before any browser interaction.

        TEST:ExpertAdvice.ModeSelection.FastThinkingProRespected
        """
        with pytest.raises(ValueError, match="Invalid mode"):
            await adapter.execute_chat(
                ChatRequest(prompt="Test", mode="Nonexistent")
            )

        # Adapter should still be idle (error before lock acquisition)
        assert adapter.is_busy is False

