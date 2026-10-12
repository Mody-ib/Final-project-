# Meal Planner

```
meal-planner/
├── frontend/   static HTML/CSS/JS (no build step)
├── backend/    FastAPI + SQLAlchemy + MySQL
└── database/   schema.sql (tables + starter data)
```

## Run
1. **Database** – open MySQL Workbench, copy the /database/schema.sql file into an empty query, press execute (the lightning symbol), right click then refresh, and the database should be displayed.
2. **Backend**
   ```
   cd backend
   cp .env.example .env                # put your MySQL password in it
   pip install -r requirements.txt     # This could be a slow step so don't worry
   uvicorn main:app --reload           # http://127.0.0.1:8000  (docs at /docs)
   ```
3. **Frontend** – open `frontend/index.html`