
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json
import os

# =========================================================
# CONFIGURATION
# =========================================================
# Key is expected to be in the root 'analysis' folder (parent of 'scripts')
# or in the same folder if run from root.
SERVICE_ACCOUNT_KEY = "firebase_service_account_key.json"

def get_service_account_path():
    # Check current directory
    if os.path.exists(SERVICE_ACCOUNT_KEY):
        return SERVICE_ACCOUNT_KEY
    # Check parent directory (if running from scripts/)
    elif os.path.exists(f"../{SERVICE_ACCOUNT_KEY}"):
        return f"../{SERVICE_ACCOUNT_KEY}"
    # Check sibling analysis folder (if running from somewhere else)
    elif os.path.exists(f"analysis/{SERVICE_ACCOUNT_KEY}"):
        return f"analysis/{SERVICE_ACCOUNT_KEY}"
    return None

def fetch_data():
    """Fetches all assessment sessions from Firestore"""
    
    key_path = get_service_account_path()
    if not key_path:
        print(f"Error: Service account key not found. Expected 'firebase_service_account_key.json' in root analysis folder.")
        print("Please download it from Firebase Console and place it in the 'student-assessment/analysis' directory.")
        return None

    # Initialize Firebase Admin
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_path)
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
        "Version": session.get('version'),
        # Demographics
        "Age": session.get('demographics', {}).get('age'),
        "Gender": session.get('demographics', {}).get('gender'),
        "Occupation": session.get('demographics', {}).get('occupation'),
        "Education": session.get('demographics', {}).get('education'),
        "Major": session.get('demographics', {}).get('major'),
        "Year": session.get('demographics', {}).get('year'),
        "GPA": session.get('demographics', {}).get('gpa'),
        "Spiritual_Practice": session.get('demographics', {}).get('spiritualPractice'),
        "Gita_Familiarity": session.get('demographics', {}).get('gitaFamiliarity'),
        "Feedback": session.get('feedback'),
    }

    # Computed Scores
    computed = session.get('computedScores', {})
    guna_raw = computed.get('gunaRaw', {})
    row['Score_Sattva_Raw'] = guna_raw.get('Sattva')
    row['Score_Rajas_Raw'] = guna_raw.get('Rajas')
    row['Score_Tamas_Raw'] = guna_raw.get('Tamas')
    row['Dominant_Guna'] = computed.get('dominantGuna')

    big_five = computed.get('bigFive', {})
    for trait, score in big_five.items():
        row[f'Score_BigFive_{trait}'] = score
    
    # Behavioral Metadata
    row["Guna_Changes"] = session.get('gunaMetadata', {}).get('answerChanges')
    row["Tab_Switches"] = session.get('gunaMetadata', {}).get('tabSwitches', 0)
    
    # Big Five Responses
    bf_details = session.get('bigFiveDetails', {})
    bf_resps = session.get('bigFiveResponses', {})
    
    if bf_details:
        for q_id, detail in bf_details.items():
            header = f"BFI_{q_id}"
            row[header] = detail.get('value')
            text = detail.get('text', '')
            if text:
                row[f"{header}_Text"] = text
            row[f"Duration_{header}"] = detail.get('reactionTimeMs')
    elif bf_resps:
        for q_id, val in bf_resps.items():
            header = f"BFI_{q_id}"
            row[header] = val

    return row

def save_to_csv(data_list, filename="data/firebase_data.csv"):
    if not data_list:
        print("No data to save.")
        return
        
    flat_data = [flatten_session(s) for s in data_list]
    df = pd.DataFrame(flat_data)
    cols = list(df.columns)
    
    # Prioritized prefix list
    priority = ['SessionID', 'FirebaseID', 'Timestamp', 'Version', 
                'Age', 'Gender', 'Occupation', 'Education', 'Major', 'Year', 'GPA',
                'Spiritual_Practice', 'Gita_Familiarity', 'Feedback',
                'Score_Sattva_Raw', 'Score_Rajas_Raw', 'Score_Tamas_Raw', 'Dominant_Guna',
                'Score_BigFive_extraversion', 'Score_BigFive_agreeableness', 
                'Score_BigFive_conscientiousness', 'Score_BigFive_neuroticism', 
                'Score_BigFive_openness']
    
    ordered_cols = [c for c in priority if c in cols]
    remaining_cols = [c for c in cols if c not in priority]
    
    # Group BFI columns and sort numerically
    def bfi_sort_key(c):
        if c.startswith('BFI_'): part = c.replace('BFI_', '')
        elif c.startswith('Duration_BFI_'): part = c.replace('Duration_BFI_', '')
        else: return (999, c)
        num_str = ''.join(filter(str.isdigit, part))
        return (int(num_str), c) if num_str else (999, c)

    bfi_cols = sorted([c for c in remaining_cols if c.startswith('BFI_') or c.startswith('Duration_BFI_')],
                      key=bfi_sort_key)
    remaining_cols = [c for c in remaining_cols if c not in bfi_cols]
    
    final_order = ordered_cols + bfi_cols + remaining_cols
    df = df[final_order]
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    return df

if __name__ == "__main__":
    # 1. Fetch
    data = fetch_data()
    
    if data:
        # 2. Save Raw JSON (Backup)
        json_path = "data/firebase_dump.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
            
        # 3. Flatten to CSV for Analysis
        save_to_csv(data)
