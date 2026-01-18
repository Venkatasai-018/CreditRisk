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

## License

MIT
