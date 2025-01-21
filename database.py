from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL do banco de dados
DATABASE_URL = "sqlite:///./banco_de_dados.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # `check_same_thread`

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()
