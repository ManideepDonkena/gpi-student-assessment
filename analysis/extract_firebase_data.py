
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json
import os

# =========================================================
# CONFIGURATION
# =========================================================
# Path to your Firebase Service Account JSON
# Go to Firebase Console -> Project Settings -> Service Accounts -> Generate Private Key
SERVICE_ACCOUNT_KEY = "firebase_service_account_key.json" 

def fetch_data():
    """Fetches all assessment sessions from Firestore"""
    
    # Initialize Firebase Admin
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"Error: Service account key not found at {SERVICE_ACCOUNT_KEY}")
        print("Please download it from Firebase Console and place it in this directory.")
        return None

    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    
    try:
        # Reference collection
        assessments_ref = db.collection(u'assessments')
        docs = assessments_ref.stream()

        data_list = []
        
        print("Fetching data from Firestore...")
        for doc in docs:
            session = doc.to_dict()
            session['firebase_id'] = doc.id
            data_list.append(session)
            
    except Exception as e:
        if "404" in str(e) or "NotFound" in str(e):
            print("\n[CRITICAL ERROR] Firestore Database Not Found!")
            print("You created the Firebase Project, but you haven't created the DATABASE yet.")
            print(f"Please visit: https://console.firebase.google.com/project/{cred.project_id}/firestore")
            print("Click 'Create Database' -> Start in Test Mode -> Choose a location.")
            return None
        else:
            raise e
        
    print(f"Fetched {len(data_list)} sessions.")
    return data_list

def flatten_session(session):
    """
    Flattens the nested session JSON into a single row for CSV analysis.
    Extracts scores, metadata, and responses.
    """
    row = {
        "SessionID": session.get('sessionId'),
        "FirebaseID": session.get('firebase_id'),
        "Timestamp": session.get('uploadedAt'),
        # Demographics
        "Major": session.get('demographics', {}).get('major'),
        "Year": session.get('demographics', {}).get('year'),
        "GPA": session.get('demographics', {}).get('gpa'),
        "Gender": session.get('demographics', {}).get('gender'),
    }

    # Computed Scores (New)
    computed = session.get('computedScores', {})
    guna_raw = computed.get('gunaRaw', {})
    guna_norm = computed.get('gunaNormalized', {})

    row['Score_Sattva_Raw'] = guna_raw.get('Sattva')
    row['Score_Rajas_Raw'] = guna_raw.get('Rajas')
    row['Score_Tamas_Raw'] = guna_raw.get('Tamas')

    row['Score_Sattva_Norm'] = guna_norm.get('Sattva')
    row['Score_Rajas_Norm'] = guna_norm.get('Rajas')
    row['Score_Tamas_Norm'] = guna_norm.get('Tamas')

    row['Dominant_Guna'] = computed.get('dominantGuna')

    big_five = computed.get('bigFive', {})
    for trait, score in big_five.items():
        row[f'Score_BigFive_{trait}'] = score
    
    # Behavioral Metadata
    row["Guna_Time_ms"] = session.get('gunaMetadata', {}).get('timeMs')
    row["Guna_Cursor_px"] = session.get('gunaMetadata', {}).get('cursorDistancePx')
    row["Guna_Changes"] = session.get('gunaMetadata', {}).get('answerChanges')
    
    # Guna Responses
    guna_res = session.get('gunaResponses', {})
    for q_id, val in guna_res.items():
        row[f"Guna_{q_id}"] = val

    # Big Five Responses
    bf_res = session.get('bigFiveResponses', {})
    for q_id, val in bf_res.items():
        row[f"BigFive_{q_id}"] = val
        
    return row

def save_to_csv(data_list, filename="firebase_data.csv"):
    if not data_list:
        return
        
    flat_data = [flatten_session(s) for s in data_list]
    df = pd.DataFrame(flat_data)
    
    # Calculate Scores locally if needed (optional verification)
    
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    return df

if __name__ == "__main__":
    # 1. Fetch
    data = fetch_data()
    
    if data:
        # 2. Save Raw JSON (Backup)
        with open("firebase_dump.json", "w") as f:
            json.dump(data, f, indent=2)
            
        # 3. Flatten to CSV for Analysis
        save_to_csv(data)
