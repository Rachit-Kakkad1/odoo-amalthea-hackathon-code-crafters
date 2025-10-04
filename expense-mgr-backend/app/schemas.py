from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List, Any
from datetime import datetime
from .models import Role, ExpenseStatus

# --- User Schemas ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Role

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    manager_id: Optional[int] = None

    class Config:
        orm_mode = True

# --- Expense Schemas ---
class ExpenseBase(BaseModel):
    name: str
    amount: float
    category: str

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    owner_id: int
    status: ExpenseStatus
    date: datetime
    owner: User

    class Config:
        orm_mode = True

# --- Token Schema for Authentication ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Password Reset Schemas ---
class PasswordResetRequest(BaseModel):
    username: str

class PasswordReset(BaseModel):
    token: str
    new_password: str

# --- FIX IS HERE: Approval Rule Schema ---
class ApprovalRuleBase(BaseModel):
    # This is an example structure, adjust to your actual fields
    name: str
    conditions: dict[str, Any]  # Using Any from typing is better practice

    # This configuration tells Pydantic to allow complex types like 'any'
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ApprovalRule(ApprovalRuleBase):
    id: int

    class Config:
        orm_mode = True

