from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import ai
import models as m
from db import Base, engine, get_db
from security import hash_password, make_token, verify_password

# Safe no-op if you already ran database/schema.sql; creates missing tables otherwise
# (the database itself must exist).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meal Planner API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
api = APIRouter(prefix="/api")


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


def get_or_404(db: Session, model, pk, label="Item"):
    obj = db.get(model, pk)
    if not obj:
        raise HTTPException(404, f"{label} not found")
    return obj


# ---------------- auth ----------------
class RegisterIn(BaseModel):
    name: str
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


@api.post("/register", status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if len(data.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")
    user = m.User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Email already registered")
    return {"message": "Registered", "user_id": user.user_id}


@api.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(m.User).filter(m.User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"token": make_token(user.user_id), "user_id": user.user_id, "name": user.name}


class UserOut(ORM):
    user_id: int
    name: str
    email: str


@api.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(m.User).all()


# ---------------- aisles ----------------
class AisleIn(BaseModel):
    name: str


class AisleOut(ORM):
    aisle_id: int
    name: str


@api.get("/aisles", response_model=list[AisleOut])
def list_aisles(db: Session = Depends(get_db)):
    return db.query(m.Aisle).all()


@api.post("/aisles", response_model=AisleOut, status_code=201)
def create_aisle(data: AisleIn, db: Session = Depends(get_db)):
    obj = m.Aisle(name=data.name)
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


# ---------------- ingredients ----------------
class IngredientIn(BaseModel):
    name: str
    unit: str = "g"
    aisle_id: Optional[int] = None


class IngredientOut(ORM):
    ingredient_id: int
    name: str
    unit: str
    aisle_id: Optional[int] = None


@api.get("/ingredients", response_model=list[IngredientOut])
def list_ingredients(db: Session = Depends(get_db)):
    return db.query(m.Ingredient).all()


@api.get("/ingredients/{ingredient_id}", response_model=IngredientOut)
def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, m.Ingredient, ingredient_id, "Ingredient")


@api.post("/ingredients", response_model=IngredientOut, status_code=201)
def create_ingredient(data: IngredientIn, db: Session = Depends(get_db)):
    obj = m.Ingredient(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@api.put("/ingredients/{ingredient_id}", response_model=IngredientOut)
def update_ingredient(ingredient_id: int, data: IngredientIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, m.Ingredient, ingredient_id, "Ingredient")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


@api.delete("/ingredients/{ingredient_id}")
def delete_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, m.Ingredient, ingredient_id, "Ingredient")); db.commit()
    return {"message": "Ingredient deleted successfully"}


# ---------------- recipes ----------------
class RecipeIn(BaseModel):
    user_id: Optional[int] = None
    name: str
    instructions: Optional[str] = None
    servings: Optional[int] = None
    prep_time: Optional[int] = None


class RecipeOut(RecipeIn, ORM):
    recipe_id: int


@api.get("/recipes", response_model=list[RecipeOut])
def list_recipes(db: Session = Depends(get_db)):
    return db.query(m.Recipe).all()


@api.get("/recipes/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, m.Recipe, recipe_id, "Recipe")


@api.post("/recipes", response_model=RecipeOut, status_code=201)
def create_recipe(data: RecipeIn, db: Session = Depends(get_db)):
    obj = m.Recipe(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@api.put("/recipes/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, data: RecipeIn, db: Session = Depends(get_db)):
    obj = get_or_404(db, m.Recipe, recipe_id, "Recipe")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


@api.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, m.Recipe, recipe_id, "Recipe")); db.commit()
    return {"message": "Recipe deleted successfully"}


# ---------------- recipe ingredients ----------------
class RecipeIngredientIn(BaseModel):
    ingredient_id: int
    amount: Decimal
    unit: str
    notes: Optional[str] = ""


@api.post("/recipes/{recipe_id}/ingredients", status_code=201)
def add_recipe_ingredient(recipe_id: int, data: RecipeIngredientIn, db: Session = Depends(get_db)):
    get_or_404(db, m.Recipe, recipe_id, "Recipe")
    get_or_404(db, m.Ingredient, data.ingredient_id, "Ingredient")
    obj = m.RecipeIngredient(recipe_id=recipe_id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"message": "Ingredient linked to recipe successfully", "recipe_ingredient_id": obj.recipe_ingredient_id}


@api.get("/recipes/{recipe_id}/ingredients")
def list_recipe_ingredients(recipe_id: int, db: Session = Depends(get_db)):
    rows = (db.query(m.RecipeIngredient, m.Ingredient.name)
            .join(m.Ingredient, m.Ingredient.ingredient_id == m.RecipeIngredient.ingredient_id)
            .filter(m.RecipeIngredient.recipe_id == recipe_id).all())
    return [{"id": ri.recipe_ingredient_id, "ingredient_id": ri.ingredient_id, "ingredient_name": n,
             "amount": float(ri.amount), "unit": ri.unit, "notes": ri.notes} for ri, n in rows]


# ---------------- pantry ----------------
class PantryIn(BaseModel):
    ingredient_id: int
    amount: Decimal
    unit: str


@api.post("/users/{user_id}/pantry", status_code=201)
def add_to_pantry(user_id: int, data: PantryIn, db: Session = Depends(get_db)):
    get_or_404(db, m.User, user_id, "User")
    get_or_404(db, m.Ingredient, data.ingredient_id, "Ingredient")
    obj = m.PantryItem(user_id=user_id, **data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return {"message": "Item added to pantry successfully", "pantry_item_id": obj.pantry_id}


@api.get("/users/{user_id}/pantry")
def get_pantry(user_id: int, db: Session = Depends(get_db)):
    rows = (db.query(m.PantryItem, m.Ingredient.name)
            .join(m.Ingredient, m.Ingredient.ingredient_id == m.PantryItem.ingredient_id)
            .filter(m.PantryItem.user_id == user_id).all())
    return [{"id": p.pantry_id, "ingredient_id": p.ingredient_id, "ingredient_name": n,
             "amount": float(p.amount), "unit": p.unit} for p, n in rows]


@api.delete("/pantry/{pantry_id}")
def delete_from_pantry(pantry_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, m.PantryItem, pantry_id, "Pantry item")); db.commit()
    return {"message": "Item removed from pantry successfully"}


# ---------------- meal plan ----------------
class MealPlanIn(BaseModel):
    user_id: int
    recipe_id: int
    planned_date: date
    meal_slot: str


class MealPlanUpdate(BaseModel):
    recipe_id: Optional[int] = None
    planned_date: Optional[date] = None
    meal_slot: Optional[str] = None


class MealPlanOut(MealPlanIn, ORM):
    entry_id: int


@api.get("/mealplan", response_model=list[MealPlanOut])
def list_mealplan(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(m.MealPlanEntry)
    if user_id is not None:
        q = q.filter(m.MealPlanEntry.user_id == user_id)
    return q.order_by(m.MealPlanEntry.planned_date).all()


@api.post("/mealplan", response_model=MealPlanOut, status_code=201)
def create_mealplan(data: MealPlanIn, db: Session = Depends(get_db)):
    obj = m.MealPlanEntry(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@api.put("/mealplan/{entry_id}", response_model=MealPlanOut)
def update_mealplan(entry_id: int, data: MealPlanUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, m.MealPlanEntry, entry_id, "Meal plan entry")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


@api.delete("/mealplan/{entry_id}")
def delete_mealplan(entry_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, m.MealPlanEntry, entry_id, "Meal plan entry")); db.commit()
    return {"message": "Meal plan entry deleted successfully"}


# ---------------- saved grocery items ----------------
class GroceryIn(BaseModel):
    user_id: int
    ingredient_id: int
    quantity_needed: Decimal


class GroceryUpdate(BaseModel):
    quantity_needed: Optional[Decimal] = None
    is_checked: Optional[bool] = None


class GroceryOut(ORM):
    item_id: int
    user_id: int
    ingredient_id: int
    quantity_needed: Decimal
    is_checked: bool


@api.get("/grocery-items", response_model=list[GroceryOut])
def list_grocery_items(user_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(m.GroceryListItem)
    if user_id is not None:
        q = q.filter(m.GroceryListItem.user_id == user_id)
    return q.all()


@api.post("/grocery-items", response_model=GroceryOut, status_code=201)
def create_grocery_item(data: GroceryIn, db: Session = Depends(get_db)):
    obj = m.GroceryListItem(**data.model_dump())
    db.add(obj); db.commit(); db.refresh(obj)
    return obj


@api.put("/grocery-items/{item_id}", response_model=GroceryOut)
def update_grocery_item(item_id: int, data: GroceryUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, m.GroceryListItem, item_id, "Grocery item")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit(); db.refresh(obj)
    return obj


@api.delete("/grocery-items/{item_id}")
def delete_grocery_item(item_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, m.GroceryListItem, item_id, "Grocery item")); db.commit()
    return {"message": "Grocery list item deleted successfully"}


# ---------------- computed grocery list (what the frontend page uses) ----------------
@api.get("/users/{user_id}/grocery-list")
def generate_grocery_list(user_id: int, db: Session = Depends(get_db)):
    """Everything the user's planned meals need, minus what's already in their pantry."""
    required = (db.query(m.RecipeIngredient.ingredient_id, m.Ingredient.name, m.RecipeIngredient.unit,
                         func.sum(m.RecipeIngredient.amount))
                .join(m.Ingredient, m.Ingredient.ingredient_id == m.RecipeIngredient.ingredient_id)
                .join(m.MealPlanEntry, m.MealPlanEntry.recipe_id == m.RecipeIngredient.recipe_id)
                .filter(m.MealPlanEntry.user_id == user_id)
                .group_by(m.RecipeIngredient.ingredient_id, m.Ingredient.name, m.RecipeIngredient.unit).all())
    pantry = {}
    for ing_id, unit, total in (db.query(m.PantryItem.ingredient_id, m.PantryItem.unit, func.sum(m.PantryItem.amount))
                                .filter(m.PantryItem.user_id == user_id)
                                .group_by(m.PantryItem.ingredient_id, m.PantryItem.unit).all()):
        pantry[(ing_id, unit)] = total or Decimal(0)

    out = []
    for ing_id, name, unit, total in required:
        need = (total or Decimal(0)) - pantry.get((ing_id, unit), Decimal(0))
        if need > 0:
            out.append({"ingredient_id": ing_id, "ingredient_name": name,
                        "needed_amount": float(round(need, 2)), "unit": unit})
    return {"status": "success", "grocery_list": out}


# ---------------- AI ----------------
class SuggestRecipeIn(BaseModel):
    ingredients: str


class DietIn(BaseModel):
    weight: float
    height: float
    age: int
    gender: str
    activity_level: Optional[str] = "moderate"
    goal: Optional[str] = "weight loss"
    diet_type: Optional[str] = "Balanced"


def run_ai(system: str, prompt: str, tokens: int) -> str:
    try:
        return ai.generate(system, prompt, tokens)
    except ImportError:
        raise HTTPException(503, "AI dependencies missing. Run: pip install torch transformers accelerate")


@api.post("/suggest-recipe")
def suggest_recipe(data: SuggestRecipeIn):
    if not data.ingredients.strip():
        raise HTTPException(400, "Ingredients list is required")
    prompt = (f"Based on these ingredients: ({data.ingredients}), suggest one detailed recipe.\n"
              "You MUST include:\n1. Recipe Name\n2. Preparation steps\n"
              "3. Detailed Nutritional Information (Total Calories, Protein in grams, Carbs in grams, Fats in grams).")
    text = run_ai("You are a professional nutritionist and meal planner. Always provide accurate macro and calorie calculations.",
                  prompt, 450)
    first = data.ingredients.split(",")[0].strip().replace(" ", ",")
    return {"status": "success", "recipe": text, "image_url": f"https://loremflickr.com/600/300/food,{first}"}


@api.post("/create-diet")
def create_diet(data: DietIn):
    prompt = (f"Create a custom daily diet plan:\n- Weight: {data.weight} kg\n- Height: {data.height} cm\n"
              f"- Age: {data.age}\n- Gender: {data.gender}\n- Activity: {data.activity_level}\n"
              f"- Goal: {data.goal}\n- Diet: {data.diet_type}\n\n"
              "Include: 1) daily target calories and TDEE, 2) macros (protein/carbs/fats in g), "
              "3) full meal plan (Breakfast, Lunch, Dinner, Snacks) with calories and macros per meal.")
    text = run_ai("You are an expert clinical nutritionist. Precise calorie and macro breakdowns are required.", prompt, 800)
    return {"status": "success", "diet_plan": text}


@app.get("/")
def health():
    return {"status": "ok"}


app.include_router(api)
