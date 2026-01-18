from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, List
import re

# ============== ADMIN SCHEMAS ==============

class AdminSignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    mobile_number: str
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class AdminLoginRequest(BaseModel):
    email: str
    password: str

class AdminResponse(BaseModel):
    id: int
    full_name: str
    email: str
    mobile_number: str
    created_at: datetime

    class Config:
        from_attributes = True

class AdminLoginResponse(BaseModel):
    success: bool
    message: str
    admin: AdminResponse

# ============== USER SCHEMAS ==============

class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    mobile_number: str
    aadhar: str
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class LoginRequest(BaseModel):
    identifier: str  # Can be email, mobile, or aadhar
    password: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    mobile_number: str
    aadhar: str
    created_at: datetime

    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: UserResponse


class LoanApplicationRequest(BaseModel):
    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., gt=0)
    loan_amount: float = Field(..., gt=0)
    loan_tenure_months: int = Field(..., gt=0)
    avg_dpd_per_delinquency: float = Field(..., ge=0)
    delinquency_ratio: float = Field(..., ge=0, le=100)
    credit_utilization_ratio: float = Field(..., ge=0, le=100)
    num_open_accounts: int = Field(..., ge=1, le=10)
    residence_type: str = Field(..., pattern='^(Owned|Rented|Mortgage)$')
    loan_purpose: str = Field(..., pattern='^(Education|Home|Auto|Personal)$')
    loan_type: str = Field(..., pattern='^(Secured|Unsecured)$')


class LoanApplicationResponse(BaseModel):
    id: int
    user_id: int
    age: int
    income: float
    loan_amount: float
    loan_tenure_months: int
    avg_dpd_per_delinquency: float
    delinquency_ratio: float
    credit_utilization_ratio: float
    num_open_accounts: int
    residence_type: str
    loan_purpose: str
    loan_type: str
    default_probability: Optional[float]
    credit_score: Optional[int]
    rating: Optional[str]
    status: str
    created_at: datetime
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    disbursed_amount: Optional[float]
    repaid_amount: Optional[float]

    class Config:
        from_attributes = True


class ApprovalRequest(BaseModel):
    disbursed_amount: Optional[float] = None

class RejectionRequest(BaseModel):
    rejection_reason: str


class PredictionResponse(BaseModel):
    success: bool
    message: str
    application: LoanApplicationResponse
    loan_to_income_ratio: float
