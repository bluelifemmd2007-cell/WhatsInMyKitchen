# 🍳 Kitchen Helper

Tell it what's in your kitchen — it tells you what to cook.

Kitchen Helper takes the ingredients you have on hand and finds matching recipes from a built-in database, ranked by how much of each recipe you can already make. If nothing fits well, it can also invent a brand-new recipe on the spot using AI.

Built with **FastAPI** + **SQLite** for fast, deterministic matching, with **Groq (Llama 3.3)** as an optional creative layer.

---

## ✨ Features

- **Smart ingredient matching** — ranks 50+ built-in recipes by percentage overlap with what you have, not just keyword search
- **Handles plurals/casing** — "Eggs", "egg", and "EGG" all match the same ingredient
- **Shows exactly what's missing** — each result lists which ingredients you have and which you'd need to buy
- **AI fallback** — when the database doesn't have a great match, generate an original recipe idea from the same ingredients via Groq
- **Meal-type filtering** — narrow results to breakfast, lunch, dinner, or snack
- **Self-seeding database** — first run automatically loads 51 starter recipes, no manual setup
- **Zero-cost AI** — runs on Groq's free tier (and the database matching works with zero API keys at all)

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| Database | SQLite via SQLAlchemy |
| Matching algorithm | Set-overlap scoring with lightweight normalization (in `matcher.py`) |
| AI recipe generation | Groq (Llama 3.3 70B Versatile) |
| Frontend | Plain HTML/CSS/JS (no build step) |

---

## 📁 Project Structure

```
kitchen-helper/
├── app.py                  # FastAPI routes
├── matcher.py               # Ingredient-overlap matching algorithm
├── ai_chef.py                # Groq-powered creative recipe generator
├── database.py                # SQLAlchemy models + auto-seeding
├── models.py                   # Pydantic request/response schemas
├── config.py
├── seed_recipes.json            # 51 starter recipes
├── static/
│   └── index.html              # Single-page web app
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. (Optional) Configure AI generation

Database matching works immediately with no setup. To enable the "✨ AI Idea" button:

```bash
cp .env.example .env
```

Get a **free** Groq API key at [console.groq.com/keys](https://console.groq.com/keys) and paste it into `GROQ_API_KEY` in `.env`.

### 3. Run the app

```bash
uvicorn app:app --reload
```

Open **http://127.0.0.1:8000** in your browser — go to that URL directly, don't double-click `static/index.html`, since the page needs to be served by the backend to talk to the API.

The database (`kitchen.db`) is created and seeded with 51 recipes automatically on first run.

### 4. Use it

1. Type an ingredient and hit **Add** (or Enter) — repeat for everything you have
2. Optionally pick a meal type
3. Click **Find Recipes** to search the database, or **✨ AI Idea** to generate something original
4. Click any result card to expand it and see full instructions + which ingredients you're missing

---

## 📡 API Reference

### `POST /api/match`

```json
{
  "ingredients": ["egg", "onion", "tomato"],
  "category": "breakfast"
}
```

Returns recipes from the database, ranked by match percentage:

```json
{
  "results": [
    {
      "id": 3,
      "name": "Tomato and Onion Omelette",
      "category": "breakfast",
      "ingredients": ["egg", "tomato", "onion", "salt", "pepper", "oil"],
      "instructions": "...",
      "prep_minutes": 15,
      "match_percent": 100.0,
      "matched_ingredients": ["egg", "tomato", "onion"],
      "missing_ingredients": ["salt", "pepper", "oil"],
      "is_ai_generated": false
    }
  ],
  "total_recipes_in_db": 51
}
```

### `POST /api/generate`

```json
{
  "ingredients": ["egg", "spinach", "feta"],
  "category": "dinner"
}
```

Returns a single AI-generated recipe in the same shape as above, with `is_ai_generated: true`.

---

## 🧠 How the matching works

Each recipe's ingredient list is compared against your input as sets, after light normalization (lowercasing, basic plural stripping — "tomatoes" → "tomato"). The match score is:

```
match % = (ingredients you have ∩ recipe needs) / (total ingredients recipe needs) × 100
```

Results are sorted by match percentage first, then by fewest missing ingredients as a tiebreaker. This keeps the scoring fully transparent — no hidden weighting, no embeddings — so the percentage you see is exactly what it claims to be.

---

## ⚠️ Limitations

- The normalization is a simple heuristic (strips trailing "s"/"es"), not a full lemmatizer — unusual plural forms (e.g. "tomatoes" handled, but irregular words may not normalize perfectly).
- The 51 seed recipes are a starter set, not a comprehensive cookbook — matches will be best for common, simple home-cooking ingredients.
- AI-generated recipes aren't tested for real-world cookability — treat them as inspiration, not professionally verified instructions.
- No persistence of AI-generated recipes back into the database (each one is generated fresh and not saved) — see Next Steps.

---

## 🗺 Possible Next Steps

- [ ] Let users save AI-generated recipes into the database for future matching
- [ ] Add dietary filters (vegetarian, gluten-free, etc.)
- [ ] Support ingredient quantities, not just presence/absence
- [ ] User accounts with a persistent pantry list
- [ ] "Surprise me" mode that picks a category and ingredient set randomly
- [ ] Dockerize for one-command deployment

---

## 📄 License

MIT — free to use, modify, and build on.
Mohammad Mahdi Mohammadi





