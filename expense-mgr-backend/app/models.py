from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, Float, JSON, DateTime, func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .database import Base

# Enums
class Role(PyEnum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class ExpenseStatus(PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

# Models
class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    currency = Column(String(3))  # e.g., 'USD', 'EUR'
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="company")
    expenses = relationship("Expense", back_populates="company")  # Optional link for company-wide view
    approval_rules = relationship("ApprovalRule", back_populates="company")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(Role), default=Role.EMPLOYEE)
    company_id = Column(Integer, ForeignKey("companies.id"))
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_manager_approver = Column(Boolean, default=True)

    company = relationship("Company", back_populates="users")
    manager = relationship("User", remote_side=[id], back_populates="employees")
    employees = relationship("User", back_populates="manager")
    expenses = relationship("Expense", back_populates="user")
    approvals = relationship("ApprovalRequest", back_populates="approver")

class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # e.g., 'Travel', 'Food'
    company_id = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))  # Link to company for currency context
    amount = Column(Float)  # Can be different from company currency
    currency = Column(String(3))  # Submitted currency
    company_amount = Column(Float, nullable=True)  # Converted to company currency
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=True)
    description = Column(String)
    date = Column(DateTime)
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING)
    receipt_path = Column(String, nullable=True)  # For OCR-processed receipts
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="expenses")
    company = relationship("Company", back_populates="expenses")
    category = relationship("ExpenseCategory", back_populates="expenses")
    approvals = relationship("ApprovalRequest", back_populates="expense")

class ApprovalRule(Base):
    __tablename__ = "approval_rules"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String)  # e.g., "Standard Approval"
    is_sequential = Column(Boolean, default=True)  # Sequential vs. Conditional
    rules = Column(JSON)  # Flexible JSON for rules (e.g., steps, percentage, specific approvers)
    # Example JSON: {"steps": [{"approvers": [1,2], "sequence": 1}, ...]} or {"type": "percentage", "threshold": 60}

    company = relationship("Company", back_populates="approval_rules")

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    step = Column(Integer, default=1)  # For sequential flow
    approved = Column(Boolean, nullable=True)  # Null: pending, True: approved, False: rejected
    comments = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    expense = relationship("Expense", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")