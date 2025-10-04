from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

class Role(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class ExpenseStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class CompanyBase(BaseModel):
    name: str
    currency: str = Field(min_length=3, max_length=3)

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: Role

class UserCreate(UserBase):
    password: str = Field(min_length=8)

class User(UserBase):
    id: int
    company_id: int
    manager_id: Optional[int] = None
    is_manager_approver: bool = True

    class Config:
        from_attributes = True

class ExpenseCategoryBase(BaseModel):
    name: str

class ExpenseCategoryCreate(ExpenseCategoryBase):
    pass

class ExpenseCategory(ExpenseCategoryBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True

class ExpenseBase(BaseModel):
    amount: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseCreate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    employee_id: int
    company_id: int
    amount_in_company_currency: float
    status: ExpenseStatus
    receipt_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ApprovalRuleBase(BaseModel):
    name: str
    is_sequential: bool = True
    rules: Dict[str, any]

class ApprovalRuleCreate(ApprovalRuleBase):
    pass

class ApprovalRule(ApprovalRuleBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True

class ApprovalRequestBase(BaseModel):
    approved: Optional[bool] = None
    comments: Optional[str] = None

class ApprovalRequestCreate(ApprovalRequestBase):
    pass

class ApprovalRequest(ApprovalRequestBase):
    id: int
    expense_id: int
    approver_id: int
    step: int
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogBase(BaseModel):
    action: str
    details: Dict[str, any]

class AuditLogCreate(AuditLogBase):
    pass

class AuditLog(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(min_length=8)