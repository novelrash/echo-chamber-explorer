#!/usr/bin/env python3
"""
LLM Bias Analyzer
Uses Claude to assess political bias via structured linguistic analysis.
Runs alongside the keyword analyzer as an independent signal.
"""

import os
import json
import anthropic
from typing import Optional

SYSTEM_PROMPT = """You are a media bias analyst. Your role is to assess political bias in news \
text by analyzing observable linguistic patterns — word choice, framing, source attribution, \
and partisan terminology.

You do not express your own political views. You do not assess whether claims are true or false. \
You analyze how language is used, not what is being said.

Score political bias on a scale from -1.0 (strongly left-leaning) to +1.0 (strongly \
right-leaning) in 0.1 increments, where 0.0 is neutral.

Calibration anchors:
- A straight AP wire report about a Senate vote: 0.0
- A balanced news analysis quoting both parties equally: 0.0 to ±0.1
- A news article consistently using terms preferred by one side: ±0.3 to ±0.5
- A partisan op-ed using loaded language throughout: ±0.6 to ±0.8
- A fundraising email or propaganda piece: ±0.9 to ±1.0

Score the LANGUAGE, not the topic. An article about climate change can score 0.0 if it uses \
neutral language. An article about tax cuts can score ±0.8 if it uses consistently loaded framing.

Return ONLY a valid JSON object with exactly this structure, no other text:
{
  "score": <float, one of: -1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, \
0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0>,
  "confidence": <"low" | "medium" | "high">,
  "lean": <"left" | "center-left" | "center" | "center-right" | "right">,
  "reasoning": {
    "word_choice": "<specific observations about loaded or neutral language choices>",
    "framing": "<how the story is framed, what is emphasized or omitted>",
    "sources": "<who is quoted, how sources are described and attributed>",
    "headline": "<assessment of headline language, or 'No headline provided'>"
  },
  "flagged_phrases": ["<phrase1>", "<phrase2>"],
  "limitations": "<context missing that affects confidence, or 'None identified'>"
}

Use low confidence for: texts under 100 words, obvious satire, technical or legal documents, \
translated content, or any text where political lean is genuinely ambiguous."""


class LLMBiasAnalyzer:
    def __init__(self):
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-haiku-4-5-20251001"
        self.max_content_chars = 12000  # ~3k tokens, well within haiku's context

    def analyze(
        self,
        content: str,
        title: Optional[str] = None,
        source: Optional[str] = None
    ) -> dict:
        """
        Analyze content for political bias using an LLM.
        Returns a dict with score, confidence, reasoning, flagged_phrases, limitations.
        On failure, returns a dict with error set and score=None.
        """
        truncated = self.was_truncated(content)
        user_message = self._build_user_message(content, title, source)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )

            raw = response.content[0].text.strip()
            # Strip markdown code fences if the model added them despite instructions
            if raw.startswith("```"):
                raw = raw.split("```", 2)[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0].strip()
            result = json.loads(raw)
            result['model'] = self.model
            result['truncated'] = truncated
            result['error'] = None
            return result

        except json.JSONDecodeError as e:
            return self._error_result(f"Failed to parse model response as JSON: {e}")
        except anthropic.APIStatusError as e:
            return self._error_result(f"API error {e.status_code}: {e.message}")
        except Exception as e:
            return self._error_result(str(e))

    def was_truncated(self, content: str) -> bool:
        return len(content) > self.max_content_chars

    def _build_user_message(
        self,
        content: str,
        title: Optional[str],
        source: Optional[str]
    ) -> str:
        parts = []
        if title:
            parts.append(f"TITLE: {title}")
        if source:
            parts.append(f"SOURCE: {source}")
        truncated = content[:self.max_content_chars]
        suffix = "\n[NOTE: Content truncated to first 12,000 characters for analysis.]" \
            if self.was_truncated(content) else ""
        parts.append(f"TEXT:\n{truncated}{suffix}")
        return "\n".join(parts)

    def _error_result(self, error_msg: str, truncated: bool = False) -> dict:
        return {
            "score": None,
            "confidence": None,
            "lean": None,
            "reasoning": None,
            "flagged_phrases": [],
            "limitations": None,
            "truncated": truncated,
            "model": self.model,
            "error": error_msg
        }
