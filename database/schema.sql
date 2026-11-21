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

INSERT INTO ingredients (ingredient_id, name, unit, aisle_id) VALUES
  (1, 'Chicken breast', 'g', 3),
  (2, 'Rice', 'g', 4),
  (3, 'Tomato', 'pcs', 1),
  (4, 'Onion', 'pcs', 1),
  (5, 'Olive oil', 'ml', 4),
  (6, 'Eggs', 'pcs', 2);

-- Demo user (email: demo@example.com / password: password123)
INSERT INTO users (user_id, name, email, password_hash) VALUES
  (1, 'Demo User', 'demo@example.com', 'WGqbyGKjtz0UwlKeHZtwhfu3Rnfs+6qaP7q/5S5iqRMoOk5a3CwQMMu3ID/SdI8B');

-- Demo recipe
INSERT INTO recipes (recipe_id, user_id, name, instructions, servings, prep_time) VALUES
  (1, 1, 'Chicken & Rice Bowl', '1. Season chicken.\n2. Sauté chicken with olive oil.\n3. Serve with cooked rice.', 2, 25);

INSERT INTO recipe_ingredients (recipe_ingredient_id, recipe_id, ingredient_id, amount, unit, notes) VALUES
  (1, 1, 1, 500.00, 'g', 'Chicken breast'),
  (2, 1, 2, 300.00, 'g', 'Rice'),
  (3, 1, 5, 20.00, 'ml', 'Olive oil');

-- Demo pantry stock (has 200g of chicken)
INSERT INTO pantry_items (pantry_id, user_id, ingredient_id, amount, unit) VALUES
  (1, 1, 1, 200.00, 'g');

-- Demo planned meal for today
INSERT INTO meal_plan_entries (entry_id, user_id, recipe_id, planned_date, meal_slot) VALUES
  (1, 1, 1, CURRENT_DATE(), 'dinner');

