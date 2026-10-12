import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Full URL wins (handy for tests); otherwise build the MySQL URL from parts.
DATABASE_URL = os.getenv("DATABASE_URL") or (
    "mysql+pymysql://{u}:{p}@{h}:{port}/{d}".format(
        u=os.getenv("DB_USER", "root"),
        p=quote_plus(os.getenv("DB_PASSWORD", "")),
        h=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "3306"),
        d=os.getenv("DB_NAME", "mealplanner"),
    )
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
