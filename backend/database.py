from sqlalchemy import create_engine, Column, Integer, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker, declarative_base
import enum

# --- Database Model Definition ---
class Role(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(SQLAlchemyEnum(Role))

# --- SQLite Database Connection ---
# This will create a file named "simple_auth.db" in your project folder.
SQLALCHEMY_DATABASE_URL = "sqlite:///./simple_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)