# CreditRisk

A credit risk assessment platform with ML-powered credit scoring, built with FastAPI backend and React frontend.

## Features

- **ML-Powered Credit Scoring**: Uses trained ML model for accurate credit score predictions (300-900 range)
- **User Dashboard**: Track credit applications and score history with analytics
- **Admin Portal**: Comprehensive analytics with interactive charts and application management
- **Premium UI**: Modern white theme with gradient accents and smooth animations

## Tech Stack

**Backend:**
- FastAPI
- SQLite
- scikit-learn (ML model)
- Python 3.x

**Frontend:**
- React
- React Router
- CSS3 with gradients and animations

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Populate sample data (optional):
```bash
python populate_sample_data.py
```

4. Start the FastAPI server:
```bash
python -m uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will run on `http://localhost:3000`

## Usage

1. **Start Backend**: Run `python -m uvicorn main:app --reload` in the `backend` directory
2. **Start Frontend**: Run `npm start` in the `frontend` directory
3. **Access Application**: Open `http://localhost:3000` in your browser

### Default Accounts

**User Account:**
- Email: `user@example.com`
- Password: `password123`

**Admin Account:**
- Email: `admin@example.com`
- Password: `admin123`

## Project Structure

```
CreditRisk/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── prediction_helper.py    # ML model integration
│   ├── populate_sample_data.py # Sample data generator
│   ├── artifacts/
│   │   └── model_data.joblib   # Trained ML model
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── Login.js
│   │   │   ├── CreditForm.js
│   │   │   ├── CreditAnalytics.js
│   │   │   └── AdminDashboard.js
│   │   └── App.js
│   └── package.json
└── README.md
```

## API Endpoints

- `POST /register` - Register new user
- `POST /login` - User authentication
- `POST /predict` - Submit credit application
- `GET /applications/{user_id}` - Get user applications
- `GET /admin/stats` - Admin statistics
- `GET /admin/insights` - Admin insights and analytics

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Layer                              │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Landing     │  │  User        │  │  Admin       │             │
│  │  Page        │  │  Dashboard   │  │  Dashboard   │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│         │                 │                  │                      │
│         └─────────────────┴──────────────────┘                      │
│                          │                                          │
│                    React Router                                     │
│                          │                                          │
└──────────────────────────┼──────────────────────────────────────────┘
                           │
                      HTTP/REST
                           │
┌──────────────────────────┼──────────────────────────────────────────┐
│                    FastAPI Backend                                  │
│                          │                                          │
│  ┌────────────────────────────────────────────────────────┐        │
│  │              API Endpoints Layer                        │        │
│  │                                                          │        │
│  │  /register  /login  /predict  /applications  /admin/*   │        │
│  └────────┬───────────────┬───────────────┬────────────────┘        │
│           │               │               │                         │
│  ┌────────▼───────┐  ┌───▼──────────┐  ┌─▼─────────────┐          │
│  │  Auth          │  │  ML          │  │  Admin        │          │
│  │  Service       │  │  Prediction  │  │  Service      │          │
│  └────────┬───────┘  └───┬──────────┘  └─┬─────────────┘          │
│           │              │                │                         │
│           │         ┌────▼─────────┐      │                         │
│           │         │  ML Model    │      │                         │
│           │         │  (joblib)    │      │                         │
│           │         │              │      │                         │
│           │         │ - Logistic   │      │                         │
│           │         │   Regression │      │                         │
│           │         │ - MinMax     │      │                         │
│           │         │   Scaler     │      │                         │
│           │         └──────────────┘      │                         │
│           │                               │                         │
│  ┌────────▼───────────────────────────────▼─────────────┐          │
│  │              SQLAlchemy ORM                           │          │
│  └────────────────────────────┬──────────────────────────┘          │
│                               │                                     │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                        SQLite Database                              │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   admins     │  │    users     │  │  loan_applications       │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Database Schema

```
┌─────────────────────────────────────┐
│            admins                   │
├─────────────────────────────────────┤
│ id              INTEGER PK          │
│ full_name       STRING              │
│ email           STRING UNIQUE       │
│ mobile_number   STRING UNIQUE       │
│ password        STRING              │
│ created_at      DATETIME            │
│ updated_at      DATETIME            │
└─────────────────────────────────────┘
                    │
                    │ approved_by (FK)
                    │
┌─────────────────────────────────────┐
│            users                    │
├─────────────────────────────────────┤
│ id              INTEGER PK          │
│ full_name       STRING              │
│ email           STRING UNIQUE       │
│ mobile_number   STRING UNIQUE       │
│ aadhar          STRING UNIQUE       │
│ hashed_password STRING              │
│ created_at      DATETIME            │
│ updated_at      DATETIME            │
└───────────┬─────────────────────────┘
            │
            │ user_id (FK)
            │
            ▼
┌─────────────────────────────────────────────────┐
│         loan_applications                       │
├─────────────────────────────────────────────────┤
│ id                      INTEGER PK              │
│ user_id                 INTEGER FK → users      │
│                                                  │
│ /* Application Inputs */                        │
│ age                     INTEGER                 │
│ income                  FLOAT                   │
│ loan_amount             FLOAT                   │
│ loan_tenure_months      INTEGER                 │
│ avg_dpd_per_delinquency FLOAT                   │
│ delinquency_ratio       FLOAT                   │
│ credit_utilization_ratio FLOAT                  │
│ num_open_accounts       INTEGER                 │
│ residence_type          STRING                  │
│ loan_purpose            STRING                  │
│ loan_type               STRING                  │
│                                                  │
│ /* ML Predictions */                            │
│ default_probability     FLOAT                   │
│ credit_score            INTEGER (300-900)       │
│ rating                  STRING (A+, A, B, C)    │
│                                                  │
│ /* Workflow */                                  │
│ status                  STRING                  │
│                         (Pending/Approved/      │
│                          Rejected)              │
│ approved_by             INTEGER FK → admins     │
│ approved_at             DATETIME                │
│ rejection_reason        STRING                  │
│ disbursed_amount        FLOAT                   │
│ repaid_amount           FLOAT                   │
│ created_at              DATETIME                │
└─────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
┌──────────────┐
│   User       │
│  (Browser)   │
└──────┬───────┘
       │
       │ 1. Submit Application
       │
       ▼
┌─────────────────────────────────────────┐
│  POST /predict                          │
│                                         │
│  Request Body:                          │
│  {                                      │
│    user_id, age, income,                │
│    loan_amount, loan_tenure_months,     │
│    avg_dpd_per_delinquency,            │
│    delinquency_ratio,                   │
│    credit_utilization_ratio,            │
│    num_open_accounts,                   │
│    residence_type, loan_purpose,        │
│    loan_type                            │
│  }                                      │
└───────────┬─────────────────────────────┘
            │
            │ 2. Validate & Extract Features
            │
            ▼
┌──────────────────────────────────────────┐
│  ML Prediction Pipeline                  │
│                                          │
│  ┌────────────────────────────┐         │
│  │ 1. Create Feature DataFrame │         │
│  │    (13 features)            │         │
│  └────────┬───────────────────┘         │
│           │                              │
│  ┌────────▼───────────────────┐         │
│  │ 2. Apply MinMaxScaler      │         │
│  │    (normalize features)     │         │
│  └────────┬───────────────────┘         │
│           │                              │
│  ┌────────▼───────────────────┐         │
│  │ 3. LogisticRegression      │         │
│  │    predict_proba()         │         │
│  └────────┬───────────────────┘         │
│           │                              │
│  ┌────────▼───────────────────┐         │
│  │ 4. Calculate Credit Score  │         │
│  │    300 + (prob × 600)       │         │
│  └────────┬───────────────────┘         │
│           │                              │
│  ┌────────▼───────────────────┐         │
│  │ 5. Assign Rating           │         │
│  │    A+ / A / B / C          │         │
│  └────────────────────────────┘         │
└───────────┬──────────────────────────────┘
            │
            │ 3. Save to Database
            │
            ▼
┌──────────────────────────────────────────┐
│  loan_applications Table                 │
│                                          │
│  INSERT INTO loan_applications           │
│  VALUES (user inputs + predictions)      │
└───────────┬──────────────────────────────┘
            │
            │ 4. Return Response
            │
            ▼
┌──────────────────────────────────────────┐
│  Response:                               │
│  {                                       │
│    default_probability: 0.15,            │
│    credit_score: 720,                    │
│    rating: "A",                          │
│    suggestions: [...]                    │
│  }                                       │
└───────────┬──────────────────────────────┘
            │
            │ 5. Display Results
            │
            ▼
┌──────────────┐
│   User       │
│  Dashboard   │
└──────────────┘
```

### Component Architecture

```
Frontend (React)
├── App.js (Router Configuration)
├── pages/
│   ├── LandingPage.js
│   │   └── Hero Section with CTA
│   ├── Login.js
│   │   ├── User Login
│   │   └── Admin Login
│   ├── CreditForm.js
│   │   ├── Multi-step Form
│   │   └── API Integration
│   ├── CreditAnalytics.js
│   │   ├── Score Trends
│   │   ├── Application History
│   │   └── Credit Improvement Tips
│   └── AdminDashboard.js
│       ├── Stats Overview
│       ├── Application Management
│       ├── Insights & Charts
│       │   ├── Risk Distribution (Pie)
│       │   ├── Disbursed vs Repaid (Pie)
│       │   ├── Credit Score Distribution (Bars)
│       │   ├── Avg Loan Amount (Bars)
│       │   ├── Loan Purpose (Bars)
│       │   └── Loan Type (Bars)
│       └── Settings

Backend (FastAPI)
├── main.py (API Routes)
├── models.py (SQLAlchemy Models)
│   ├── Admin
│   ├── User
│   └── LoanApplication
├── schemas.py (Pydantic Schemas)
├── database.py (DB Connection)
├── prediction_helper.py (ML Integration)
│   ├── Model Loading
│   ├── Feature Engineering
│   ├── Prediction Pipeline
│   └── Fallback Heuristics
├── credit_improvement.py (Suggestions)
└── artifacts/
    └── model_data.joblib
        ├── LogisticRegression
        ├── MinMaxScaler
        ├── features_list (13)
        └── cols_to_scale
```

### ML Model Features

The trained model uses **13 features**:

1. **age** - Applicant's age
2. **Income** - Annual income
3. **loan_amount** - Requested loan amount
4. **loan_tenure_months** - Loan duration in months
5. **avg_dpd_per_delinquency** - Average days past due
6. **delinquency_ratio** - Ratio of delinquent payments
7. **credit_utilization_ratio** - Credit utilization percentage
8. **number_of_open_accounts** - Active credit accounts
9. **residence_type_Owned** - Binary: Owns residence
10. **residence_type_Rented** - Binary: Rents residence
11. **loan_purpose_Education** - Binary: Education loan
12. **loan_purpose_Home** - Binary: Home loan
13. **loan_purpose_Personal** - Binary: Personal loan

**Model Output:**
- Default Probability (0-1)
- Credit Score (300-900)
- Rating (A+: 750+, A: 650-749, B: 550-649, C: <550)

## License

MIT
