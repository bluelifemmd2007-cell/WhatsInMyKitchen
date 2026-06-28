from typing import List

from database import Recipe
from models import RecipeMatch


def normalize(ingredient: str) -> str:

    cleaned = ingredient.strip().lower()
    if cleaned.endswith("oes"):
        cleaned = cleaned[:-2]  # tomatoes -> tomato
    elif cleaned.endswith("s") and not cleaned.endswith("ss"):
        cleaned = cleaned[:-1]  # eggs -> egg, but not "grass" -> "gras"
    return cleaned


def compute_match(user_ingredients: List[str], recipe: Recipe) -> RecipeMatch:
    """
    Computes what fraction of the recipe's ingredients the user already
    has, and which ones are missing.
    """
    user_set = {normalize(i) for i in user_ingredients if i.strip()}
    recipe_ingredients = recipe.ingredients
    recipe_set = {normalize(i) for i in recipe_ingredients}

    matched = recipe_set & user_set
    missing = recipe_set - user_set

    match_percent = (len(matched) / len(recipe_set)) * 100 if recipe_set else 0

   
    matched_display = [ing for ing in recipe_ingredients if normalize(ing) in matched]
    missing_display = [ing for ing in recipe_ingredients if normalize(ing) in missing]

    return RecipeMatch(
        id=recipe.id,
        name=recipe.name,
        category=recipe.category,
        ingredients=recipe_ingredients,
        instructions=recipe.instructions,
        prep_minutes=recipe.prep_minutes,
        match_percent=round(match_percent, 1),
        matched_ingredients=matched_display,
        missing_ingredients=missing_display,
        is_ai_generated=bool(recipe.is_ai_generated),
    )


def rank_recipes(
    user_ingredients: List[str],
    all_recipes: List[Recipe],
    category: str | None = None,
    min_match_percent: float = 0,
    max_results: int = 10,
) -> List[RecipeMatch]:
    """
    Scores every recipe against the user's pantry, optionally filters by
    category, and returns the top matches sorted by match percentage
    (highest first), then by fewer missing ingredients as a tiebreaker.
    """
    candidates = all_recipes
    if category:
        candidates = [r for r in candidates if r.category.lower() == category.lower()]

    scored = [compute_match(user_ingredients, r) for r in candidates]
    scored = [m for m in scored if m.match_percent >= min_match_percent]

    scored.sort(key=lambda m: (-m.match_percent, len(m.missing_ingredients)))
    return scored[:max_results]