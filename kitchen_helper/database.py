import json
from pathlib import Path

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SEED_FILE = Path(__file__).parent / "seed_recipes.json"


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  
    ingredients_json = Column(Text, nullable=False)  
    instructions = Column(Text, nullable=False)
    prep_minutes = Column(Integer, nullable=True)
    is_ai_generated = Column(Integer, default=0)  

    @property
    def ingredients(self) -> list:
        return json.loads(self.ingredients_json)


def init_db():
    Base.metadata.create_all(bind=engine)
    _seed_if_empty()


def _seed_if_empty():
    db = SessionLocal()
    try:
        existing_count = db.query(Recipe).count()
        if existing_count > 0:
            return  

        if not SEED_FILE.exists():
            print(f"[WARNING] Seed file not found at {SEED_FILE}, skipping seed.")
            return

        with open(SEED_FILE, encoding="utf-8") as f:
            seed_data = json.load(f)

        for item in seed_data:
            recipe = Recipe(
                name=item["name"],
                category=item["category"],
                ingredients_json=json.dumps(item["ingredients"]),
                instructions=item["instructions"],
                prep_minutes=item.get("prep_minutes"),
                is_ai_generated=0,
            )
            db.add(recipe)
        db.commit()
        print(f"[INFO] Seeded database with {len(seed_data)} recipes.")
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()