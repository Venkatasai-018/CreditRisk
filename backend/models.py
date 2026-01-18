from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # Plain text as per requirement
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mobile_number = Column(String, unique=True, index=True, nullable=False)
    aadhar = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    loan_applications = relationship("LoanApplication", back_populates="user")


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Application inputs
    age = Column(Integer, nullable=False)
    income = Column(Float, nullable=False)
    loan_amount = Column(Float, nullable=False)
    loan_tenure_months = Column(Integer, nullable=False)
    avg_dpd_per_delinquency = Column(Float, nullable=False)
    delinquency_ratio = Column(Float, nullable=False)
    credit_utilization_ratio = Column(Float, nullable=False)
    num_open_accounts = Column(Integer, nullable=False)
    residence_type = Column(String, nullable=False)
    loan_purpose = Column(String, nullable=False)
    loan_type = Column(String, nullable=False)
    
    # Prediction results
    default_probability = Column(Float)
    credit_score = Column(Integer)
    rating = Column(String)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    approved_by = Column(Integer, ForeignKey("admins.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)
    disbursed_amount = Column(Float, nullable=True)
    repaid_amount = Column(Float, default=0.0)
    
    # Relationship
    user = relationship("User", back_populates="loan_applications")
