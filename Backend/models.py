from sqlalchemy import (Boolean, Column, Date, DateTime, ForeignKey, Integer,
                        Numeric, String, Text, UniqueConstraint, func)

from db import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Aisle(Base):
    __tablename__ = "aisles"
    aisle_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)


class Ingredient(Base):
    __tablename__ = "ingredients"
    ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=False, default="g")
    aisle_id = Column(Integer, ForeignKey("aisles.aisle_id", ondelete="SET NULL"))


class Recipe(Base):
    __tablename__ = "recipes"
    recipe_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    name = Column(String(255), nullable=False)
    instructions = Column(Text)
    servings = Column(Integer)
    prep_time = Column(Integer)


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"
    recipe_ingredient_id = Column(Integer, primary_key=True, autoincrement=True)
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.ingredient_id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)
    notes = Column(String(255))


class PantryItem(Base):
    __tablename__ = "pantry_items"
    pantry_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.ingredient_id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)


class MealPlanEntry(Base):
    __tablename__ = "meal_plan_entries"
    entry_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.recipe_id", ondelete="CASCADE"), nullable=False)
    planned_date = Column(Date, nullable=False)
    meal_slot = Column(String(50), nullable=False)  # breakfast / lunch / dinner / snack


class GroceryListItem(Base):
    __tablename__ = "grocery_list_items"
    item_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.ingredient_id", ondelete="CASCADE"), nullable=False)
    quantity_needed = Column(Numeric(10, 2), nullable=False, default=0)
    is_checked = Column(Boolean, nullable=False, default=False)
