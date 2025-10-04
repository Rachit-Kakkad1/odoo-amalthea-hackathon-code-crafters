# app/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, Float, JSON, DateTime, func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .database import Base


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
