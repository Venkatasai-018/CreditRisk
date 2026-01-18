from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

from database import engine, get_db, Base
from models import Admin, User, LoanApplication
from schemas import (
    SignupRequest, LoginRequest, UserResponse, LoginResponse,
    LoanApplicationRequest, LoanApplicationResponse, PredictionResponse,
    AdminSignupRequest, AdminLoginRequest, AdminResponse, AdminLoginResponse,
    ApprovalRequest, RejectionRequest
)
from prediction_helper import predict
from credit_improvement import get_credit_improvement_suggestions

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Credit Risk API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_email(identifier: str) -> bool:
    """Check if identifier is an email"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, identifier))

def is_mobile(identifier: str) -> bool:
    """Check if identifier is a mobile number"""
    return identifier.isdigit() and len(identifier) == 10

def is_aadhar(identifier: str) -> bool:
    """Check if identifier is an aadhar number"""
    return identifier.isdigit() and len(identifier) == 12

@app.get("/")
def read_root():
    return {"message": "Credit Risk API is running"}

@app.post("/api/auth/signup", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if mobile number already exists
    existing_user = db.query(User).filter(User.mobile_number == request.mobile_number).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    # Check if aadhar already exists
    existing_user = db.query(User).filter(User.aadhar == request.aadhar).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aadhar already registered"
        )
    
    # Create new user - store password as plain text
    new_user = User(
        full_name=request.full_name,
        email=request.email,
        mobile_number=request.mobile_number,
        aadhar=request.aadhar,
        hashed_password=request.password  # Store plain password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return LoginResponse(
        success=True,
        message="User registered successfully",
        user=UserResponse.from_orm(new_user)
    )

@app.post("/api/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with email, mobile number, or aadhar
    """
    user = None
    
    # Try to find user by email first
    user = db.query(User).filter(User.email == request.identifier).first()
    
    # If not found by email, try mobile
    if not user:
        user = db.query(User).filter(User.mobile_number == request.identifier).first()
    
    # If not found by mobile, try aadhar
    if not user:
        user = db.query(User).filter(User.aadhar == request.identifier).first()
    
    # Check if user exists and password is correct (plain text comparison)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.hashed_password != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    return LoginResponse(
        success=True,
        message="Login successful",
        user=UserResponse.from_orm(user)
    )

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get user details by ID
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)

@app.post("/api/loan/apply", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def apply_for_loan(request: LoanApplicationRequest, user_id: int, db: Session = Depends(get_db)):
    """
    Submit loan application and get credit risk prediction
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if identical application already exists
    existing_app = db.query(LoanApplication).filter(
        LoanApplication.user_id == user_id,
        LoanApplication.age == request.age,
        LoanApplication.income == request.income,
        LoanApplication.loan_amount == request.loan_amount,
        LoanApplication.loan_tenure_months == request.loan_tenure_months,
        LoanApplication.avg_dpd_per_delinquency == request.avg_dpd_per_delinquency,
        LoanApplication.delinquency_ratio == request.delinquency_ratio,
        LoanApplication.credit_utilization_ratio == request.credit_utilization_ratio,
        LoanApplication.num_open_accounts == request.num_open_accounts,
        LoanApplication.residence_type == request.residence_type,
        LoanApplication.loan_purpose == request.loan_purpose,
        LoanApplication.loan_type == request.loan_type
    ).first()
    
    if existing_app:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identical application already exists"
        )
    
    # Get prediction
    try:
        default_probability, credit_score, rating = predict(
            request.age,
            request.income,
            request.loan_amount,
            request.loan_tenure_months,
            request.avg_dpd_per_delinquency,
            request.delinquency_ratio,
            request.credit_utilization_ratio,
            request.num_open_accounts,
            request.residence_type,
            request.loan_purpose,
            request.loan_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )
    
    # All new applications go to Pending status for admin review
    application_status = "Pending"
    
    # Create loan application record
    loan_application = LoanApplication(
        user_id=user_id,
        age=request.age,
        income=request.income,
        loan_amount=request.loan_amount,
        loan_tenure_months=request.loan_tenure_months,
        avg_dpd_per_delinquency=request.avg_dpd_per_delinquency,
        delinquency_ratio=request.delinquency_ratio,
        credit_utilization_ratio=request.credit_utilization_ratio,
        num_open_accounts=request.num_open_accounts,
        residence_type=request.residence_type,
        loan_purpose=request.loan_purpose,
        loan_type=request.loan_type,
        default_probability=float(default_probability),
        credit_score=int(credit_score),
        rating=rating,
        status=application_status
    )
    
    db.add(loan_application)
    db.commit()
    db.refresh(loan_application)
    
    # Calculate loan to income ratio
    loan_to_income_ratio = request.loan_amount / request.income if request.income > 0 else 0
    
    return PredictionResponse(
        success=True,
        message="Application submitted successfully. Awaiting admin review.",
        application=LoanApplicationResponse.from_orm(loan_application),
        loan_to_income_ratio=loan_to_income_ratio
    )

@app.get("/api/loan/applications/{user_id}", response_model=list[LoanApplicationResponse])
def get_user_applications(user_id: int, db: Session = Depends(get_db)):
    """
    Get all loan applications for a user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    applications = db.query(LoanApplication).filter(
        LoanApplication.user_id == user_id
    ).order_by(LoanApplication.created_at.desc()).all()
    
    return [LoanApplicationResponse.from_orm(app) for app in applications]

@app.get("/api/credit/improvement/{user_id}")
def get_improvement_suggestions(user_id: int, db: Session = Depends(get_db)):
    """
    Get credit improvement suggestions for a user based on all historical data
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get all applications ordered by date (latest first)
    all_applications = db.query(LoanApplication).filter(
        LoanApplication.user_id == user_id
    ).order_by(LoanApplication.created_at.desc()).all()
    
    if not all_applications:
        return {
            "success": False,
            "message": "No loan application found. Please apply for a loan first.",
            "suggestions": []
        }
    
    latest_app = all_applications[0]
    
    # Prepare user data
    user_data = {
        "credit_score": latest_app.credit_score,
        "income": latest_app.income,
        "loan_amount": latest_app.loan_amount,
        "credit_utilization_ratio": latest_app.credit_utilization_ratio,
        "delinquency_ratio": latest_app.delinquency_ratio,
        "avg_dpd_per_delinquency": latest_app.avg_dpd_per_delinquency,
        "num_open_accounts": latest_app.num_open_accounts,
        "loan_tenure_months": latest_app.loan_tenure_months
    }
    
    # Get suggestions with historical analysis
    suggestions = get_credit_improvement_suggestions(
        latest_app.credit_score, 
        user_data,
        all_applications  # Pass all applications for trend analysis
    )
    
    return {
        "success": True,
        "message": "Credit improvement suggestions generated successfully",
        "credit_score": latest_app.credit_score,
        "total_applications": len(all_applications),
        "suggestions": suggestions
    }

# ============== ADMIN ENDPOINTS ==============

@app.post("/api/admin/signup", response_model=AdminLoginResponse, status_code=status.HTTP_201_CREATED)
def admin_signup(request: AdminSignupRequest, db: Session = Depends(get_db)):
    """Create new admin account"""
    # Check if email exists
    existing_admin = db.query(Admin).filter(Admin.email == request.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if mobile exists
    existing_mobile = db.query(Admin).filter(Admin.mobile_number == request.mobile_number).first()
    if existing_mobile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    # Create admin
    new_admin = Admin(
        full_name=request.full_name,
        email=request.email,
        mobile_number=request.mobile_number,
        password=request.password  # Plain text as per requirement
    )
    
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return AdminLoginResponse(
        success=True,
        message="Admin account created successfully",
        admin=AdminResponse.from_orm(new_admin)
    )

@app.post("/api/admin/login", response_model=AdminLoginResponse)
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Admin login with email and password"""
    admin = db.query(Admin).filter(Admin.email == request.email).first()
    
    if not admin or admin.password != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    return AdminLoginResponse(
        success=True,
        message="Admin login successful",
        admin=AdminResponse.from_orm(admin)
    )

@app.get("/api/admin/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get KPIs for admin dashboard"""
    total_users = db.query(User).count()
    total_applications = db.query(LoanApplication).count()
    approved_count = db.query(LoanApplication).filter(LoanApplication.status == "Approved").count()
    rejected_count = db.query(LoanApplication).filter(LoanApplication.status == "Rejected").count()
    pending_count = db.query(LoanApplication).filter(LoanApplication.status == "Pending").count()
    
    total_disbursed = db.query(func.sum(LoanApplication.disbursed_amount)).filter(
        LoanApplication.status == "Approved"
    ).scalar() or 0.0
    
    total_repaid = db.query(func.sum(LoanApplication.repaid_amount)).filter(
        LoanApplication.status == "Approved"
    ).scalar() or 0.0
    
    return {
        "total_users": total_users,
        "total_applications": total_applications,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
        "pending_count": pending_count,
        "total_disbursed": total_disbursed,
        "total_repaid": total_repaid
    }

@app.get("/api/admin/applications/pending")
def get_pending_applications(db: Session = Depends(get_db)):
    """Get all pending loan applications"""
    applications = db.query(LoanApplication).filter(
        LoanApplication.status == "Pending"
    ).order_by(LoanApplication.created_at.desc()).all()
    
    result = []
    for app in applications:
        user = db.query(User).filter(User.id == app.user_id).first()
        result.append({
            **LoanApplicationResponse.from_orm(app).dict(),
            "user_name": user.full_name if user else "Unknown",
            "user_email": user.email if user else "Unknown"
        })
    
    return result

@app.post("/api/admin/applications/{app_id}/approve")
def approve_application(app_id: int, request: ApprovalRequest, admin_id: int, db: Session = Depends(get_db)):
    """Approve a loan application"""
    application = db.query(LoanApplication).filter(LoanApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status != "Pending":
        raise HTTPException(status_code=400, detail="Application already processed")
    
    application.status = "Approved"
    application.approved_by = admin_id
    application.approved_at = datetime.utcnow()
    application.disbursed_amount = request.disbursed_amount or application.loan_amount
    
    db.commit()
    db.refresh(application)
    
    return {"message": "Application approved successfully", "application": LoanApplicationResponse.from_orm(application)}

@app.post("/api/admin/applications/{app_id}/reject")
def reject_application(app_id: int, request: RejectionRequest, admin_id: int, db: Session = Depends(get_db)):
    """Reject a loan application"""
    application = db.query(LoanApplication).filter(LoanApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    if application.status != "Pending":
        raise HTTPException(status_code=400, detail="Application already processed")
    
    application.status = "Rejected"
    application.approved_by = admin_id
    application.approved_at = datetime.utcnow()
    application.rejection_reason = request.rejection_reason
    
    db.commit()
    db.refresh(application)
    
    return {"message": "Application rejected successfully", "application": LoanApplicationResponse.from_orm(application)}

@app.get("/api/admin/applications/history")
def get_application_history(
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get loan application history with filters"""
    query = db.query(LoanApplication).filter(LoanApplication.status.in_(["Approved", "Rejected"]))
    
    if status:
        query = query.filter(LoanApplication.status == status)
    
    if start_date:
        query = query.filter(LoanApplication.created_at >= datetime.fromisoformat(start_date))
    
    if end_date:
        query = query.filter(LoanApplication.created_at <= datetime.fromisoformat(end_date))
    
    applications = query.order_by(LoanApplication.created_at.desc()).all()
    
    result = []
    for app in applications:
        user = db.query(User).filter(User.id == app.user_id).first()
        app_dict = {
            **LoanApplicationResponse.from_orm(app).dict(),
            "user_name": user.full_name if user else "Unknown",
            "user_email": user.email if user else "Unknown"
        }
        
        if search and search.lower() not in user.full_name.lower():
            continue
            
        result.append(app_dict)
    
    return result

@app.get("/api/admin/analytics/insights")
def get_loan_insights(db: Session = Depends(get_db)):
    """Get comprehensive loan analytics and insights"""
    
    # Total loans disbursed over time (monthly)
    monthly_disbursed = db.query(
        extract('year', LoanApplication.approved_at).label('year'),
        extract('month', LoanApplication.approved_at).label('month'),
        func.count(LoanApplication.id).label('count'),
        func.sum(LoanApplication.disbursed_amount).label('total_amount')
    ).filter(LoanApplication.status == "Approved").group_by('year', 'month').all()
    
    # Amount disbursed vs repaid
    total_disbursed = db.query(func.sum(LoanApplication.disbursed_amount)).filter(
        LoanApplication.status == "Approved"
    ).scalar() or 0.0
    
    total_repaid = db.query(func.sum(LoanApplication.repaid_amount)).filter(
        LoanApplication.status == "Approved"
    ).scalar() or 0.0
    
    # Risk distribution
    low_risk = db.query(LoanApplication).filter(
        LoanApplication.credit_score >= 750
    ).count()
    
    medium_risk = db.query(LoanApplication).filter(
        LoanApplication.credit_score >= 500,
        LoanApplication.credit_score < 750
    ).count()
    
    high_risk = db.query(LoanApplication).filter(
        LoanApplication.credit_score < 500
    ).count()
    
    # Credit score distribution
    score_ranges = {
        "300-400": db.query(LoanApplication).filter(LoanApplication.credit_score >= 300, LoanApplication.credit_score < 400).count(),
        "400-500": db.query(LoanApplication).filter(LoanApplication.credit_score >= 400, LoanApplication.credit_score < 500).count(),
        "500-600": db.query(LoanApplication).filter(LoanApplication.credit_score >= 500, LoanApplication.credit_score < 600).count(),
        "600-700": db.query(LoanApplication).filter(LoanApplication.credit_score >= 600, LoanApplication.credit_score < 700).count(),
        "700-800": db.query(LoanApplication).filter(LoanApplication.credit_score >= 700, LoanApplication.credit_score < 800).count(),
        "800-900": db.query(LoanApplication).filter(LoanApplication.credit_score >= 800, LoanApplication.credit_score <= 900).count(),
    }
    
    # Active vs Closed (assuming closed means fully repaid)
    active_loans = db.query(LoanApplication).filter(
        LoanApplication.status == "Approved",
        LoanApplication.repaid_amount < LoanApplication.disbursed_amount
    ).count()
    
    closed_loans = db.query(LoanApplication).filter(
        LoanApplication.status == "Approved",
        LoanApplication.repaid_amount >= LoanApplication.disbursed_amount
    ).count()
    
    return {
        "monthly_disbursed": [
            {"year": int(m.year), "month": int(m.month), "count": m.count, "amount": m.total_amount}
            for m in monthly_disbursed
        ],
        "disbursed_vs_repaid": {
            "total_disbursed": total_disbursed,
            "total_repaid": total_repaid,
            "outstanding": total_disbursed - total_repaid
        },
        "risk_distribution": {
            "low_risk": low_risk,
            "medium_risk": medium_risk,
            "high_risk": high_risk
        },
        "credit_score_distribution": score_ranges,
        "active_vs_closed": {
            "active": active_loans,
            "closed": closed_loans
        }
    }

@app.get("/api/admin/users", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Get all users (Admin only)"""
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]

@app.get("/api/admin/applications")
def get_all_applications(db: Session = Depends(get_db)):
    """Get all loan applications (Admin only)"""
    applications = db.query(LoanApplication).all()
    return [LoanApplicationResponse.from_orm(app) for app in applications]

@app.put("/api/admin/users/{user_id}")
def update_user(user_id: int, request: SignupRequest, db: Session = Depends(get_db)):
    """Update user details (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.full_name = request.full_name
    user.email = request.email
    user.mobile_number = request.mobile_number
    user.aadhar_number = request.aadhar_number
    if request.password:
        user.password = request.password
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User updated successfully",
        "user": UserResponse.from_orm(user)
    }

@app.delete("/api/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Delete user (Admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete all loan applications for this user
    db.query(LoanApplication).filter(LoanApplication.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    
    return {"message": "User and associated applications deleted successfully"}

@app.put("/api/admin/applications/{app_id}")
def update_application(app_id: int, request: LoanApplicationRequest, db: Session = Depends(get_db)):
    """Update loan application (Admin only)"""
    application = db.query(LoanApplication).filter(LoanApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application.income = request.income
    application.loan_amount = request.loan_amount
    application.loan_tenure_months = request.loan_tenure_months
    application.credit_utilization_ratio = request.credit_utilization_ratio
    application.num_open_accounts = request.num_open_accounts
    application.residence_type = request.residence_type
    application.loan_purpose = request.loan_purpose
    application.loan_type = request.loan_type
    application.delinquency_ratio = request.delinquency_ratio
    application.avg_dpd_per_delinquency = request.avg_dpd_per_delinquency
    application.num_inquiries = request.num_inquiries
    
    # Recalculate prediction
    prediction_result = predict(
        request.income,
        request.loan_amount,
        request.loan_tenure_months,
        request.credit_utilization_ratio,
        request.num_open_accounts,
        request.residence_type,
        request.loan_purpose,
        request.loan_type,
        request.delinquency_ratio,
        request.avg_dpd_per_delinquency,
        request.num_inquiries
    )
    
    application.credit_score = prediction_result['credit_score']
    application.rating = prediction_result['rating']
    application.default_probability = prediction_result['default_probability']
    
    db.commit()
    db.refresh(application)
    
    return {
        "message": "Application updated successfully",
        "application": LoanApplicationResponse.from_orm(application)
    }

@app.delete("/api/admin/applications/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    """Delete loan application (Admin only)"""
    application = db.query(LoanApplication).filter(LoanApplication.id == app_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(application)
    db.commit()
    
    return {"message": "Application deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
