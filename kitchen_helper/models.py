from typing import List, Optional

from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    ingredients: List[str] = Field(
        ..., min_length=1, description="List of ingredients the user has on hand"
    )
    category: Optional[str] = Field(
        default=None,
        description="Optional filter: 'breakfast', 'lunch', 'dinner', or 'snack'",
    )


class RecipeMatch(BaseModel):
    id: Optional[int] = None
    name: str
    category: str
    ingredients: List[str]
    instructions: str
    prep_minutes: Optional[int] = None
    match_percent: float
    matched_ingredients: List[str]
    missing_ingredients: List[str]
    is_ai_generated: bool = False


class MatchResponse(BaseModel):
    results: List[RecipeMatch]
    total_recipes_in_db: int


class GenerateRequest(BaseModel):
    ingredients: List[str] = Field(..., min_length=1)
    category: Optional[str] = Field(
        default=None, description="Optional meal type hint, e.g. 'dinner'"
    )


class GenerateResponse(BaseModel):
    recipe: RecipeMatch