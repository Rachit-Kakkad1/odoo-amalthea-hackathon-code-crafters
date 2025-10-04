from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict

# Enums
class Role(str, Enum):
    """User roles in the system."""
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class ExpenseStatus(str, Enum):
    """Status of an expense request."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Authentication Schemas
class Token(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Data embedded in the JWT token."""
    username: str | None = None

# Company Schemas
class CompanyBase(BaseModel):
    """Base model for company data."""
    name: str
    currency: str = Field(min_length=3, max_length=3)  # e.g., 'INR', 'USD'

class CompanyCreate(CompanyBase):
    """Model for creating a new company."""
    pass

class Company(CompanyBase):
    """Response model for a company."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# User Schemas
class UserBase(BaseModel):
    """Base model for user data."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: Role

class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(min_length=8)

class User(UserBase):
    """Response model for a user."""
    id: int
    company_id: int
    manager_id: Optional[int] = None
    is_manager_approver: bool = True

    class Config:
        from_attributes = True

# Expense Category Schemas
class ExpenseCategoryBase(BaseModel):
    """Base model for expense category data."""
    name: str

class ExpenseCategoryCreate(ExpenseCategoryBase):
    """Model for creating a new expense category."""
    pass

class ExpenseCategory(ExpenseCategoryBase):
    """Response model for an expense category."""
    id: int
    company_id: int

    class Config:
        from_attributes = True

# Expense Schemas
class ExpenseBase(BaseModel):
    """Base model for expense data."""
    amount: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)  # e.g., 'USD', 'INR'
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None

class ExpenseCreate(ExpenseBase):
    """Model for creating a new expense."""
    pass

class Expense(ExpenseBase):
    """Response model for an expense."""
    id: int
    employee_id: int
    company_id: int
    amount_in_company_currency: float
    status: ExpenseStatus
    receipt_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Approval Rule Schemas
class ApprovalRuleBase(BaseModel):
    """Base model for approval rule data."""
    name: str
    is_sequential: bool = True
    rules: Dict[str, any]  # Flexible JSON for approval logic

class ApprovalRuleCreate(ApprovalRuleBase):
    """Model for creating a new approval rule."""
    pass

class ApprovalRule(ApprovalRuleBase):
    """Response model for an approval rule."""
    id: int
    company_id: int

    class Config:
        from_attributes = True

# Approval Request Schemas
class ApprovalRequestBase(BaseModel):
    """Base model for approval request data."""
    approved: Optional[bool] = None
    comments: Optional[str] = None

class ApprovalRequestCreate(ApprovalRequestBase):
    """Model for creating a new approval request."""
    pass

class ApprovalRequest(ApprovalRequestBase):
    """Response model for an approval request."""
    id: int
    expense_id: int
    approver_id: int
    step: int
    created_at: datetime

    class Config:
        from_attributes = True

# Audit Log Schemas
class AuditLogBase(BaseModel):
    """Base model for audit log data."""
    action: str
    details: Dict[str, any]

class AuditLogCreate(AuditLogBase):
    """Model for creating a new audit log."""
    pass

class AuditLog(AuditLogBase):
    """Response model for an audit log."""
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True