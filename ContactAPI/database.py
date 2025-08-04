from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker ,declarative_base
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

DATABASE_URL= os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # 死んだ接続を検知して張り直す
    pool_recycle=1800,         # 30分で再作成
)
SessionLocal= sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base=declarative_base()