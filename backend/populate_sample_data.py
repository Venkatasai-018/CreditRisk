"""
Script to populate the database with sample users and loan applications
Run this to create test data for the admin dashboard
"""

from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import User, LoanApplication, Admin
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_sample_data():
    db = SessionLocal()
    
    try:
        print("🚀 Starting to populate sample data...")
        
        # Create admin account if doesn't exist
        admin = db.query(Admin).filter(Admin.email == "admin@loansewa.com").first()
        if not admin:
            admin = Admin(
                full_name="Admin User",
                email="admin@loansewa.com",
                mobile_number="9999999999",
                password="admin123"  # Plain text as per requirement
            )
            db.add(admin)
            db.commit()
            print("✅ Admin account created (Email: admin@loansewa.com, Password: admin123)")
        
        # Get existing users or create new ones
        sample_users = [
            {
                "full_name": "Rajesh Kumar",
                "email": "rajesh.kumar@example.com",
                "mobile_number": "8876543210",
                "aadhar": "223456789012"
            },
            {
                "full_name": "Priya Sharma",
                "email": "priya.sharma@example.com",
                "mobile_number": "8876543211",
                "aadhar": "223456789013"
            },
            {
                "full_name": "Amit Patel",
                "email": "amit.patel@example.com",
                "mobile_number": "8876543212",
                "aadhar": "223456789014"
            },
            {
                "full_name": "Sneha Reddy",
                "email": "sneha.reddy@example.com",
                "mobile_number": "8876543213",
                "aadhar": "223456789015"
            },
            {
                "full_name": "Vikram Singh",
                "email": "vikram.singh@example.com",
                "mobile_number": "8876543214",
                "aadhar": "223456789016"
            },
            {
                "full_name": "Ananya Iyer",
                "email": "ananya.iyer@example.com",
                "mobile_number": "8876543215",
                "aadhar": "223456789017"
            },
            {
                "full_name": "Rahul Verma",
                "email": "rahul.verma@example.com",
                "mobile_number": "8876543216",
                "aadhar": "223456789018"
            },
            {
                "full_name": "Kavita Nair",
                "email": "kavita.nair@example.com",
                "mobile_number": "8876543217",
                "aadhar": "223456789019"
            }
        ]
        
        users = []
        new_users_count = 0
        
        # Try to create new users, if they exist just use them
        for user_data in sample_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if existing_user:
                users.append(existing_user)
            else:
                try:
                    user = User(
                        full_name=user_data["full_name"],
                        email=user_data["email"],
                        mobile_number=user_data["mobile_number"],
                        aadhar=user_data["aadhar"],
                        hashed_password=pwd_context.hash("password123")
                    )
                    db.add(user)
                    db.flush()  # Flush to get ID without committing
                    users.append(user)
                    new_users_count += 1
                except Exception as e:
                    db.rollback()
                    print(f"⚠️  Could not create user {user_data['email']}: {str(e)}")
                    # Try to find existing user again
                    existing_user = db.query(User).filter(User.email == user_data["email"]).first()
                    if existing_user:
                        users.append(existing_user)
        
        # If no users created but some exist, get all existing users
        if not users:
            users = db.query(User).limit(10).all()
        
        db.commit()
        
        if new_users_count > 0:
            print(f"✅ Created {new_users_count} new sample users")
        print(f"ℹ️  Using {len(users)} total users for loan applications")
        
        # Refresh to get user IDs
        for user in users:
            db.refresh(user)
        
        # Sample loan applications with variety
        loan_types = ["Personal Loan", "Home Loan", "Car Loan", "Business Loan", "Education Loan"]
        residence_types = ["Owned", "Rented", "Mortgage"]
        loan_purposes = ["Debt Consolidation", "Home Improvement", "Medical", "Education", "Business", "Wedding"]
        
        applications_data = []
        
        # Create 5 PENDING applications (for admin to approve)
        for i in range(5):
            user = random.choice(users)
            credit_score = random.randint(350, 850)
            
            # Determine rating based on credit score
            if credit_score >= 750:
                rating = "High"
            elif credit_score >= 500:
                rating = "Medium"
            else:
                rating = "Low"
            
            loan_amount = random.randint(50000, 2000000)
            
            app = LoanApplication(
                user_id=user.id,
                age=random.randint(25, 55),
                income=random.randint(300000, 2000000),
                loan_amount=loan_amount,
                loan_tenure_months=random.choice([12, 24, 36, 48, 60, 84]),
                avg_dpd_per_delinquency=round(random.uniform(0, 30), 2),
                delinquency_ratio=round(random.uniform(0, 0.5), 2),
                credit_utilization_ratio=round(random.uniform(0.1, 0.9), 2),
                num_open_accounts=random.randint(1, 10),
                residence_type=random.choice(residence_types),
                loan_purpose=random.choice(loan_purposes),
                loan_type=random.choice(loan_types),
                default_probability=round(random.uniform(0.05, 0.45), 4),
                credit_score=credit_score,
                rating=rating,
                status="Pending",
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 15))
            )
            applications_data.append(app)
        
        # Create 8 APPROVED applications (with disbursement data)
        for i in range(8):
            user = random.choice(users)
            credit_score = random.randint(600, 850)  # Higher scores for approved
            
            if credit_score >= 750:
                rating = "High"
            elif credit_score >= 500:
                rating = "Medium"
            else:
                rating = "Low"
            
            loan_amount = random.randint(100000, 1500000)
            disbursed_amount = loan_amount
            repaid_amount = random.randint(0, int(disbursed_amount * 0.8))
            
            app = LoanApplication(
                user_id=user.id,
                age=random.randint(25, 55),
                income=random.randint(400000, 2500000),
                loan_amount=loan_amount,
                loan_tenure_months=random.choice([12, 24, 36, 48, 60, 84]),
                avg_dpd_per_delinquency=round(random.uniform(0, 20), 2),
                delinquency_ratio=round(random.uniform(0, 0.3), 2),
                credit_utilization_ratio=round(random.uniform(0.1, 0.7), 2),
                num_open_accounts=random.randint(2, 8),
                residence_type=random.choice(residence_types),
                loan_purpose=random.choice(loan_purposes),
                loan_type=random.choice(loan_types),
                default_probability=round(random.uniform(0.05, 0.25), 4),
                credit_score=credit_score,
                rating=rating,
                status="Approved",
                approved_by=admin.id,
                approved_at=datetime.utcnow() - timedelta(days=random.randint(5, 60)),
                disbursed_amount=disbursed_amount,
                repaid_amount=repaid_amount,
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 120))
            )
            applications_data.append(app)
        
        # Create 4 REJECTED applications
        for i in range(4):
            user = random.choice(users)
            credit_score = random.randint(300, 600)  # Lower scores for rejected
            
            if credit_score >= 750:
                rating = "High"
            elif credit_score >= 500:
                rating = "Medium"
            else:
                rating = "Low"
            
            rejection_reasons = [
                "Low credit score below minimum threshold",
                "Insufficient income for requested loan amount",
                "High debt-to-income ratio",
                "Incomplete documentation",
                "Poor credit history with multiple defaults"
            ]
            
            app = LoanApplication(
                user_id=user.id,
                age=random.randint(22, 55),
                income=random.randint(200000, 800000),
                loan_amount=random.randint(100000, 2000000),
                loan_tenure_months=random.choice([12, 24, 36, 48, 60]),
                avg_dpd_per_delinquency=round(random.uniform(10, 60), 2),
                delinquency_ratio=round(random.uniform(0.3, 0.8), 2),
                credit_utilization_ratio=round(random.uniform(0.5, 1.0), 2),
                num_open_accounts=random.randint(1, 12),
                residence_type=random.choice(residence_types),
                loan_purpose=random.choice(loan_purposes),
                loan_type=random.choice(loan_types),
                default_probability=round(random.uniform(0.35, 0.75), 4),
                credit_score=credit_score,
                rating=rating,
                status="Rejected",
                approved_by=admin.id,
                approved_at=datetime.utcnow() - timedelta(days=random.randint(2, 30)),
                rejection_reason=random.choice(rejection_reasons),
                created_at=datetime.utcnow() - timedelta(days=random.randint(20, 90))
            )
            applications_data.append(app)
        
        # Add all applications
        for app in applications_data:
            db.add(app)
        
        db.commit()
        print(f"✅ Created {len(applications_data)} loan applications")
        print(f"   - 5 Pending (ready for approval)")
        print(f"   - 8 Approved (with disbursement data)")
        print(f"   - 4 Rejected")
        
        print("\n" + "="*60)
        print("🎉 Sample data populated successfully!")
        print("="*60)
        print("\n📋 Admin Login Credentials:")
        print("   Email: admin@loansewa.com")
        print("   Password: admin123")
        print("\n📋 Sample User Login (any of these):")
        print("   Email: rajesh.kumar@example.com")
        print("   Password: password123")
        print("\n🌐 Access Admin Dashboard:")
        print("   http://localhost:3000/admin/login")
        print("\n✨ You can now:")
        print("   - View pending applications in Dashboard tab")
        print("   - Approve/Reject pending loans")
        print("   - View history in History tab")
        print("   - See analytics in Loan Insights tab")
        print("   - Manage users in Settings tab")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
