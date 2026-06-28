from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from ai_chef import AIChefError, generate_recipe
from config import settings
from database import Recipe, SessionLocal, init_db
from matcher import rank_recipes
from models import GenerateRequest, GenerateResponse, MatchRequest, MatchResponse

app = FastAPI(
    title="Kitchen Helper",
    description=(
        "Tell us what's in your kitchen, and we'll tell you what you can cook — "
        "matched from a recipe database, or invented fresh by AI."
    ),
    version="1.0.0",
)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


init_db()


@app.on_event("startup")
def on_startup():
    init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def serve_app():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
def status():
    return {"ai_generation_available": bool(settings.GROQ_API_KEY)}


@app.post("/api/match", response_model=MatchResponse)
def match_recipes(payload: MatchRequest, db: Session = Depends(get_db)):
    """Find the best-matching recipes from the local database."""
    all_recipes = db.query(Recipe).all()

    results = rank_recipes(
        user_ingredients=payload.ingredients,
        all_recipes=all_recipes,
        category=payload.category,
        min_match_percent=0,  
        max_results=settings.MAX_RESULTS,
    )

    return MatchResponse(results=results, total_recipes_in_db=len(all_recipes))


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_creative_recipe(payload: GenerateRequest):
    try:
        recipe = await generate_recipe(payload.ingredients, payload.category)
    except AIChefError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return GenerateResponse(recipe=recipe)
