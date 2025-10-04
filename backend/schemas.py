from pydantic import BaseModel, EmailStr
from .database import Role # Import the Role enum

# --- User Schemas ---
# Base model with common user attributes
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Role

# Schema for creating a new user (includes password)
class UserCreate(UserBase):
    password: str

# Schema for returning a user from the API (omits password)
class User(UserBase):
    id: int
    
    class Config:
        # This tells Pydantic to read data from SQLAlchemy model attributes
        from_attributes = True

# --- Token Schemas ---
# Schema for the login response
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for the data encoded in the JWT
class TokenData(BaseModel):
    email: str | None = None
    
# --- Forgot Password Schema ---
# Schema for the /forgot-password request body
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# --- Generic Message Schema ---
# A simple schema for returning a message in JSON format
class Msg(BaseModel):
    msg: str