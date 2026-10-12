-- Meal Planner - MySQL / MariaDB schema + starter data
-- Run:  mysql -u root -p < database/schema.sql

CREATE DATABASE IF NOT EXISTS mealplanner CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mealplanner;

CREATE TABLE IF NOT EXISTS users (
  user_id       INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  email         VARCHAR(100) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS aisles (
  aisle_id INT AUTO_INCREMENT PRIMARY KEY,
  name     VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ingredients (
  ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  unit          VARCHAR(50)  NOT NULL DEFAULT 'g',
  aisle_id      INT NULL,
  FOREIGN KEY (aisle_id) REFERENCES aisles(aisle_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS recipes (
  recipe_id    INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NULL,
  name         VARCHAR(255) NOT NULL,
  instructions TEXT,
  servings     INT,
  prep_time    INT COMMENT 'minutes',
  FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS recipe_ingredients (
  recipe_ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
  recipe_id     INT NOT NULL,
  ingredient_id INT NOT NULL,
  amount        DECIMAL(10,2) NOT NULL,
  unit          VARCHAR(50) NOT NULL,
  notes         VARCHAR(255),
  FOREIGN KEY (recipe_id)     REFERENCES recipes(recipe_id)         ON DELETE CASCADE,
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pantry_items (
  pantry_id     INT AUTO_INCREMENT PRIMARY KEY,
  user_id       INT NOT NULL,
  ingredient_id INT NOT NULL,
  amount        DECIMAL(10,2) NOT NULL,
  unit          VARCHAR(50) NOT NULL,
  FOREIGN KEY (user_id)       REFERENCES users(user_id)             ON DELETE CASCADE,
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS meal_plan_entries (
  entry_id     INT AUTO_INCREMENT PRIMARY KEY,
  user_id      INT NOT NULL,
  recipe_id    INT NOT NULL,
  planned_date DATE NOT NULL,
  meal_slot    VARCHAR(50) NOT NULL COMMENT 'breakfast / lunch / dinner / snack',
  FOREIGN KEY (user_id)   REFERENCES users(user_id)     ON DELETE CASCADE,
  FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id) ON DELETE CASCADE,
  INDEX idx_plan_user_date (user_id, planned_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS grocery_list_items (
  item_id         INT AUTO_INCREMENT PRIMARY KEY,
  user_id         INT NOT NULL,
  ingredient_id   INT NOT NULL,
  quantity_needed DECIMAL(10,2) NOT NULL DEFAULT 0,
  is_checked      BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (user_id)       REFERENCES users(user_id)             ON DELETE CASCADE,
  FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------- Starter data (optional) ----------
INSERT INTO aisles (name) VALUES ('Produce'), ('Dairy'), ('Meat & Fish'), ('Pantry'), ('Bakery');

INSERT INTO ingredients (name, unit, aisle_id) VALUES
  ('Chicken breast', 'g', 3), ('Rice', 'g', 4), ('Tomato', 'pcs', 1),
  ('Onion', 'pcs', 1), ('Olive oil', 'ml', 4), ('Eggs', 'pcs', 2);
