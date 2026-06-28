import json
import re

import httpx

from config import settings
from models import RecipeMatch

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = (
    "You are a creative home cook who invents simple, realistic recipes "
    "using only the ingredients a person tells you they have (plus common "
    "pantry basics like salt, pepper, oil, and water, which can always be "
    "assumed available). You respond with ONLY a single valid JSON object, "
    "no markdown fences, no extra commentary, no preamble."
)


class AIChefError(Exception):
    """Raised when recipe generation fails."""


def _build_user_prompt(ingredients: list[str], category: str | None) -> str:
    ingredient_list = ", ".join(ingredients)
    category_hint = f" The recipe should be a {category}." if category else ""
    return (
        f"Available ingredients: {ingredient_list}.{category_hint}\n\n"
        "Invent one simple, realistic recipe using mostly these ingredients "
        "(you may assume salt, pepper, oil, and water are also available). "
        "Respond with ONLY this JSON shape, no other text:\n"
        "{\n"
        '  "name": "Recipe Name",\n'
        '  "category": "breakfast|lunch|dinner|snack",\n'
        '  "ingredients": ["ingredient1", "ingredient2", ...],\n'
        '  "instructions": "Step by step instructions as a single paragraph.",\n'
        '  "prep_minutes": 20\n'
        "}"
    )


def _extract_json(raw_text: str) -> dict:
    """Strips markdown code fences if present, then parses JSON."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.MULTILINE)
    return json.loads(cleaned)


async def generate_recipe(ingredients: list[str], category: str | None = None) -> RecipeMatch:
    if not settings.GROQ_API_KEY:
        raise AIChefError(
            "GROQ_API_KEY is not configured. Add it to your .env file to enable "
            "AI-generated recipes."
        )

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(ingredients, category)},
        ],
        "temperature": 0.8,
        "max_tokens": 600,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise AIChefError(
                f"Groq API returned an error: {exc.response.status_code} "
                f"{exc.response.text[:200]}"
            ) from exc
        except httpx.RequestError as exc:
            raise AIChefError(f"Failed to reach Groq API: {exc}") from exc

    data = response.json()
    try:
        raw_text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise AIChefError(f"Unexpected Groq response shape: {data}") from exc

    try:
        parsed = _extract_json(raw_text)
    except json.JSONDecodeError as exc:
        raise AIChefError(
            f"Model did not return valid JSON. Raw output: {raw_text[:300]}"
        ) from exc

    required_keys = {"name", "category", "ingredients", "instructions"}
    if not required_keys.issubset(parsed.keys()):
        raise AIChefError(f"Model response missing required fields: {parsed}")

    user_set = {i.strip().lower() for i in ingredients}
    recipe_ingredients = parsed["ingredients"]
    recipe_set = {i.strip().lower() for i in recipe_ingredients}
    matched = [i for i in recipe_ingredients if i.strip().lower() in user_set]
    missing = [i for i in recipe_ingredients if i.strip().lower() not in user_set]
    match_percent = (len(matched) / len(recipe_set)) * 100 if recipe_set else 0

    return RecipeMatch(
        id=None,
        name=parsed["name"],
        category=parsed.get("category", category or "dinner"),
        ingredients=recipe_ingredients,
        instructions=parsed["instructions"],
        prep_minutes=parsed.get("prep_minutes"),
        match_percent=round(match_percent, 1),
        matched_ingredients=matched,
        missing_ingredients=missing,
        is_ai_generated=True,
    )