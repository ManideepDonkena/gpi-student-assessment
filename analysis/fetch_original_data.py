
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
SERVICE_ACCOUNT_KEY = "../analysis/firebase_service_account_key.json" 
# Note: adjusted path assuming running from student-assessment folder or similar. 
# Check where user runs it. Best to look in current dir.
if not os.path.exists(SERVICE_ACCOUNT_KEY):
    SERVICE_ACCOUNT_KEY = "firebase_service_account_key.json"

def fetch_original_data():
    """Fetches ONLY 'original-gpi' sessions from Firestore"""
    
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
            
            # FILTER: Only keep sessions from the Original GPI version
            if session.get('version') == 'original-gpi':
                data_list.append(session)
            
    except Exception as e:
        print(f"Error: {e}")
        return None
        
    print(f"Fetched {len(data_list)} sessions matching 'original-gpi'.")
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
        "Version": session.get('version'),
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
    guna_details = session.get('gunaDetails', {})
    
    for q_id, val in guna_res.items():
        row[f"{q_id}"] = val
        # Extract details if available
        detail = guna_details.get(q_id)
        if detail:
           row[f"{q_id}_Text"] = detail.get('text')
           row[f"{q_id}_TimeMs"] = detail.get('reactionTimeMs')

    # Big Five Responses
    bf_res = session.get('bigFiveResponses', {})
    bf_details = session.get('bigFiveDetails', {})
    
    for q_id, val in bf_res.items():
        row[f"BigFive_{q_id}"] = val
        detail = bf_details.get(q_id)
        if detail:
           row[f"BigFive_{q_id}_Text"] = detail.get('text')
           row[f"BigFive_{q_id}_TimeMs"] = detail.get('reactionTimeMs')
        
    return row

def save_to_csv(data_list, filename="original_gpi_data.csv"):
    if not data_list:
        print("No data to save.")
        return
        
    flat_data = [flatten_session(s) for s in data_list]
    df = pd.DataFrame(flat_data)
    
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    return df

if __name__ == "__main__":
    # 1. Fetch
    data = fetch_original_data()
    
    if data:
        # 2. Save Raw JSON (Backup)
        with open("original_gpi_dump.json", "w") as f:
            json.dump(data, f, indent=2)
            
        # 3. Flatten to CSV for Analysis
        save_to_csv(data)
