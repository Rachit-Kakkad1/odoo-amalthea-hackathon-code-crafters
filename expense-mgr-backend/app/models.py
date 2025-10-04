from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, Float, JSON, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base
from enum import Enum as PyEnum

class Role(PyEnum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"

class ExpenseStatus(PyEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    currency = Column(String(3))
    created_at = Column(DateTime, server_default=func.now())
    users = relationship("User", back_populates="company")
    expenses = relationship("Expense", back_populates="company")

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
    expenses = relationship("Expense", back_populates="employee")
    approvals = relationship("ApprovalRequest", back_populates="approver")

class ExpenseCategory(Base):
    __tablename__ = "expense_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    amount_in_company_currency = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    description = Column(String, nullable=True)
    date = Column(DateTime, server_default=func.now())
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING)
    employee = relationship("User", back_populates="expenses")
    company = relationship("Company", back_populates="expenses")
    category = relationship("ExpenseCategory", back_populates="expenses")
    approvals = relationship("ApprovalRequest", back_populates="expense")

class ApprovalRule(Base):
    __tablename__ = "approval_rules"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    name = Column(String)
    is_sequential = Column(Boolean, default=True)
    rules = Column(JSON)
    company = relationship("Company", back_populates="approval_rules")

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    step = Column(Integer, default=1)
    approved = Column(Boolean, nullable=True)
    comments = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    expense = relationship("Expense", back_populates="approvals")
    approver = relationship("User", back_populates="approvals")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="audit_logs")