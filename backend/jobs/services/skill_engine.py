"""
Universal Skill Translation — LLM extraction + embedding generation.

Uses LangChain + Google Gemini when GEMINI_API_KEY is configured;
falls back to deterministic dev stubs otherwise.
"""

import hashlib
import json
import logging
import re
import struct
from typing import Any

from django.conf import settings

from core.embeddings import EMBEDDING_DIMENSIONS

logger = logging.getLogger(__name__)

SKILL_EXTRACTION_PROMPT = """You are a universal skill translator for a global employment marketplace.
The input job posting may be in ANY language (local trades, tech, vocational work).

Extract normalized skill tags in English (snake_case, 1-4 words each).
Include both hard skills and tools. Return ONLY valid JSON:

{{
  "detected_language": "iso-639-1 code or unknown",
  "normalized_skills": ["skill_one", "skill_two"],
  "summary_en": "One sentence English summary of required capabilities"
}}

Job title: {title}
Job field: {field}
Job description:
{description}
"""


def extract_skill_tags(title: str, description: str, field: str) -> dict[str, Any]:
    """Pass raw local-language description to Gemini for normalized skill tags."""
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if api_key:
        try:
            return _extract_with_gemini(title, description, field, api_key)
        except Exception:
            logger.exception("Gemini skill extraction failed — using fallback")
    return _extract_fallback(title, description, field)


def _extract_with_gemini(
    title: str, description: str, field: str, api_key: str
) -> dict[str, Any]:
    from langchain_core.messages import HumanMessage
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=getattr(settings, "GEMINI_MODEL", "gemini-2.0-flash"),
        google_api_key=api_key,
        temperature=0.1,
    )
    prompt = SKILL_EXTRACTION_PROMPT.format(
        title=title, field=field, description=description
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    text = response.content if isinstance(response.content, str) else str(response.content)

    # Strip markdown fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    parsed = json.loads(text)

    skills = parsed.get("normalized_skills", [])
    if not isinstance(skills, list):
        skills = []
    parsed["normalized_skills"] = [str(s).strip().lower().replace(" ", "_") for s in skills if s]
    return parsed


def _extract_fallback(title: str, description: str, field: str) -> dict[str, Any]:
    """Deterministic fallback when Gemini is unavailable."""
    tokens = re.findall(r"[a-zA-Z\u00C0-\u024F\u4e00-\u9fff]{3,}", f"{title} {description}")
    seen: set[str] = set()
    skills: list[str] = []
    for token in tokens[:20]:
        tag = token.lower().replace(" ", "_")
        if tag not in seen and len(tag) > 2:
            seen.add(tag)
            skills.append(tag)
    if field and field not in seen:
        skills.insert(0, field.lower())
    return {
        "detected_language": "unknown",
        "normalized_skills": skills[:15],
        "summary_en": title,
    }


def generate_embedding(text: str) -> list[float]:
    """Generate a dense embedding vector for the given text."""
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if api_key:
        try:
            return _embed_with_gemini(text, api_key)
        except Exception:
            logger.exception("Gemini embedding failed — using fallback")
    return _embed_fallback(text)


def _embed_with_gemini(text: str, api_key: str) -> list[float]:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    embedder = GoogleGenerativeAIEmbeddings(
        model=getattr(settings, "GEMINI_EMBEDDING_MODEL", "models/text-embedding-004"),
        google_api_key=api_key,
    )
    vector = embedder.embed_query(text)
    return _resize_vector(vector, EMBEDDING_DIMENSIONS)


def _embed_fallback(text: str) -> list[float]:
    """Hash-seeded deterministic pseudo-embedding for local dev."""
    dim = EMBEDDING_DIMENSIONS
    digest = hashlib.sha512(text.encode("utf-8")).digest()
    values: list[float] = []
    while len(values) < dim:
        for i in range(0, len(digest) - 3, 4):
            (raw,) = struct.unpack(">I", digest[i : i + 4])
            values.append((raw / 0xFFFFFFFF) * 2 - 1)
            if len(values) >= dim:
                break
        digest = hashlib.sha512(digest).digest()
    norm = sum(v * v for v in values) ** 0.5 or 1.0
    return [v / norm for v in values]


def _resize_vector(vector: list[float], target_dim: int) -> list[float]:
    if len(vector) == target_dim:
        return vector
    if len(vector) > target_dim:
        return vector[:target_dim]
    padded = vector + [0.0] * (target_dim - len(vector))
    norm = sum(v * v for v in padded) ** 0.5 or 1.0
    return [v / norm for v in padded]


def build_embedding_text(
    title: str,
    description: str,
    field: str,
    skill_tags: list[str],
    summary_en: str = "",
) -> str:
    tags = ", ".join(skill_tags)
    parts = [f"Title: {title}", f"Field: {field}", f"Skills: {tags}"]
    if summary_en:
        parts.append(f"Summary: {summary_en}")
    parts.append(f"Description: {description[:2000]}")
    return "\n".join(parts)
