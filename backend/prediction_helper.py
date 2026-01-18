import numpy as np
import pandas as pd
import joblib
import os

# Load the trained model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'artifacts', 'model_data.joblib')

try:
    model_data = joblib.load(MODEL_PATH)
    model = model_data['model']
    scaler = model_data.get('scaler', None)
    features_list = model_data.get('features', None)
    cols_to_scale = model_data.get('cols_to_scale', None)
    
    # Convert to list if pandas Index
    if features_list is not None and hasattr(features_list, 'tolist'):
        features_list = features_list.tolist()
    if cols_to_scale is not None and hasattr(cols_to_scale, 'tolist'):
        cols_to_scale = cols_to_scale.tolist()
    
    print(f"✅ Model loaded successfully from {MODEL_PATH}")
    if features_list is not None and len(features_list) > 0:
        print(f"   Expected features ({len(features_list)}): {features_list[:5]}...")
except Exception as e:
    print(f"⚠️ Warning: Could not load model from {MODEL_PATH}: {e}")
    print("   Using fallback heuristic-based prediction")
    model = None
    scaler = None
    features_list = None
    cols_to_scale = None
    model = None
    scaler = None
    features_list = None
    cols_to_scale = None

def prepare_input(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
                    delinquency_ratio, credit_utilization_ratio, num_open_accounts, residence_type,
                    loan_purpose, loan_type):
    """Prepare input data for prediction"""
    input_data = {
        'age': age,
        'income': income,
        'loan_amount': loan_amount,
        'loan_tenure_months': loan_tenure_months,
        'avg_dpd_per_delinquency': avg_dpd_per_delinquency,
        'delinquency_ratio': delinquency_ratio,
        'credit_utilization_ratio': credit_utilization_ratio,
        'num_open_accounts': num_open_accounts,
        'loan_to_income': loan_amount / income if income > 0 else 0,
        'residence_type': residence_type,
        'loan_purpose': loan_purpose,
        'loan_type': loan_type
    }
    return input_data


def calculate_credit_score(input_data, base_score=300, scale_length=600):
    """Calculate credit score based on input parameters"""
    
    # Risk factors calculation (simplified heuristic)
    risk_score = 0
    
    # Age factor (younger = higher risk)
    if input_data['age'] < 25:
        risk_score += 15
    elif input_data['age'] < 35:
        risk_score += 10
    elif input_data['age'] < 50:
        risk_score += 5
    
    # Loan to income ratio (higher = higher risk)
    loan_to_income = input_data['loan_to_income']
    if loan_to_income > 5:
        risk_score += 25
    elif loan_to_income > 3:
        risk_score += 15
    elif loan_to_income > 2:
        risk_score += 10
    
    # Delinquency ratio (higher = higher risk)
    if input_data['delinquency_ratio'] > 50:
        risk_score += 30
    elif input_data['delinquency_ratio'] > 30:
        risk_score += 20
    elif input_data['delinquency_ratio'] > 10:
        risk_score += 10
    
    # Credit utilization (higher = higher risk)
    if input_data['credit_utilization_ratio'] > 80:
        risk_score += 20
    elif input_data['credit_utilization_ratio'] > 50:
        risk_score += 10
    elif input_data['credit_utilization_ratio'] > 30:
        risk_score += 5
    
    # Average DPD (higher = higher risk)
    if input_data['avg_dpd_per_delinquency'] > 30:
        risk_score += 25
    elif input_data['avg_dpd_per_delinquency'] > 15:
        risk_score += 15
    elif input_data['avg_dpd_per_delinquency'] > 5:
        risk_score += 8
    
    # Number of open accounts
    if input_data['num_open_accounts'] > 3:
        risk_score += 10
    elif input_data['num_open_accounts'] < 2:
        risk_score += 5
    
    # Residence type (Owned = lower risk)
    if input_data['residence_type'] == 'Rented':
        risk_score += 10
    elif input_data['residence_type'] == 'Mortgage':
        risk_score += 5
    
    # Loan type (Unsecured = higher risk)
    if input_data['loan_type'] == 'Unsecured':
        risk_score += 15
    
    # Calculate default probability (0-100 risk score maps to 0-1 probability)
    default_probability = min(risk_score / 100, 0.99)
    
    # Calculate credit score (inverse of risk)
    non_default_probability = 1 - default_probability
    credit_score = int(base_score + non_default_probability * scale_length)
    
    # Determine rating
    def get_rating(score):
        if 300 <= score < 500:
            return 'Poor'
        elif 500 <= score < 650:
            return 'Average'
        elif 650 <= score < 750:
            return 'Good'
        elif 750 <= score <= 900:
            return 'Excellent'
        else:
            return 'Undefined'
    
    rating = get_rating(credit_score)
    
    return default_probability, credit_score, rating


def predict(age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
            delinquency_ratio, credit_utilization_ratio, num_open_accounts,
            residence_type, loan_purpose, loan_type):
    """Main prediction function using trained ML model"""
    
    # Prepare input
    input_data = prepare_input(
        age, income, loan_amount, loan_tenure_months, avg_dpd_per_delinquency,
        delinquency_ratio, credit_utilization_ratio, num_open_accounts,
        residence_type, loan_purpose, loan_type
    )
    
    # Use ML model if available
    if model is not None and features_list is not None and len(features_list) > 0:
        try:
            # Create full feature dictionary with all expected features
            full_data = {
                'age': age,
                'income': income,
                'loan_amount': loan_amount,
                'loan_tenure_months': loan_tenure_months,
                'number_of_open_accounts': num_open_accounts,
                'credit_utilization_ratio': credit_utilization_ratio,
                'loan_to_income': loan_amount / income if income > 0 else 0,
                'delinquency_ratio': delinquency_ratio,
                'avg_dpd_per_delinquency': avg_dpd_per_delinquency,
                'residence_type_Owned': 1 if residence_type == 'Owned' else 0,
                'residence_type_Rented': 1 if residence_type == 'Rented' else 0,
                'residence_type_Mortgage': 1 if residence_type == 'Mortgage' else 0,
                'loan_purpose_Education': 1 if loan_purpose == 'Education' else 0,
                'loan_purpose_Home': 1 if loan_purpose == 'Home' else 0,
                'loan_purpose_Personal': 1 if loan_purpose == 'Personal' else 0,
                'loan_type_Secured': 1 if loan_type == 'Secured' else 0,
                'loan_type_Unsecured': 1 if loan_type == 'Unsecured' else 0,
                # Dummy values for additional features
                'number_of_dependants': 2,
                'years_at_current_address': 3,
                'zipcode': 110001,
                'sanction_amount': loan_amount,
                'processing_fee': loan_amount * 0.02,
                'gst': loan_amount * 0.02 * 0.18,
                'net_disbursement': loan_amount * 0.98,
                'principal_outstanding': loan_amount * 0.5,
                'bank_balance_at_application': income * 0.3,
                'number_of_closed_accounts': 2,
                'enquiry_count': 1
            }
            
            # Create DataFrame
            df = pd.DataFrame([full_data])
            
            # Apply scaling if scaler and cols_to_scale exist
            if scaler is not None and cols_to_scale is not None and len(cols_to_scale) > 0:
                df[cols_to_scale] = scaler.transform(df[cols_to_scale])
            
            # Select only the features expected by the model
            features_df = df[features_list]
            
            # Get prediction from model
            default_probability = float(model.predict_proba(features_df)[0][1])
            
            # Calculate credit score from probability (inverse relationship)
            # Lower probability = higher score
            non_default_probability = 1 - default_probability
            credit_score = int(300 + non_default_probability * 600)
            
            # Determine rating based on credit score
            if credit_score >= 750:
                rating = 'Excellent'
            elif credit_score >= 650:
                rating = 'Good'
            elif credit_score >= 500:
                rating = 'Average'
            else:
                rating = 'Poor'
            
            return default_probability, credit_score, rating
            
        except Exception as e:
            print(f"⚠️ Model prediction failed: {e}, using fallback")
            # Fall through to heuristic method
    
    # Fallback: Calculate credit score using heuristic
    probability, credit_score, rating = calculate_credit_score(input_data)
    
    return probability, credit_score, rating
