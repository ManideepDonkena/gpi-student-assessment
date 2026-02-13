import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json
import os
import sys

# =========================================================
# CONFIGURATION
# =========================================================
SERVICE_ACCOUNT_KEY = "../analysis/firebase_service_account_key.json" 
if not os.path.exists(SERVICE_ACCOUNT_KEY):
    SERVICE_ACCOUNT_KEY = "firebase_service_account_key.json"

def fetch_original_data():
    """Fetches ONLY 'original-gpi' sessions from Firestore"""
    
    # Initialize Firebase Admin
    if not os.path.exists(SERVICE_ACCOUNT_KEY):
        print(f"Error: Service account key not found at {SERVICE_ACCOUNT_KEY}")
        return None

    if not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    
    try:
        assessments_ref = db.collection(u'assessments')
        docs = assessments_ref.stream()

        data_list = []
        print("Fetching data from Firestore...")
        for doc in docs:
            session = doc.to_dict()
            session['firebase_id'] = doc.id
            if session.get('version') == 'original-gpi':
                data_list.append(session)
            
    except Exception as e:
        print(f"Error: {e}")
        return None
        
    print(f"Fetched {len(data_list)} sessions matching 'original-gpi'.")
    return data_list

def flatten_session(session):
    row = {
        "SessionID": session.get('sessionId'),
        "FirebaseID": session.get('firebase_id'),
        "Timestamp": session.get('uploadedAt'),
        "Version": session.get('version')
    }

    # --- Demographics ---
    demo = session.get('demographics', {})
    if not demo: demo = {}
    
    row['Age'] = demo.get('age')
    row['Gender'] = demo.get('gender')
    row['Education'] = demo.get('education')
    row['Occupation'] = demo.get('occupation')
    row['Spiritual_Practice'] = demo.get('spiritualPractice')
    row['Gita_Familiarity'] = demo.get('gitaFamiliarity')
    row['Major'] = demo.get('major')
    row['Year'] = demo.get('year')
    row['GPA'] = demo.get('gpa')
    row['Industry'] = demo.get('industry')
    row['Experience'] = demo.get('experience')

    # --- View Timings ---
    timings = session.get('viewTimings', {})
    if timings:
        for view, ms in timings.items():
            row[f"Time_View_{view}_ms"] = ms

    # --- Computed Scores ---
    computed = session.get('computedScores', {})
    if not computed: computed = {}
    
    guna_raw = computed.get('gunaRaw', {})
    guna_norm = computed.get('gunaNormalized', {})

    row['Score_Sattva_Raw'] = guna_raw.get('Sattva')
    row['Score_Rajas_Raw'] = guna_raw.get('Rajas')
    row['Score_Tamas_Raw'] = guna_raw.get('Tamas')

    row['Dominant_Guna'] = computed.get('dominantGuna')
    
    big_five = computed.get('bigFive', {})
    for trait, score in big_five.items():
        row[f'Score_BigFive_{trait}'] = score
    
    # --- Metadata (Total Time) ---
    guna_meta = session.get('gunaMetadata', {})
    row["Total_Guna_Time_ms"] = guna_meta.get('timeMs')
    row["Guna_Changes"] = guna_meta.get('answerChanges')
    
    # --- Wide Format Questions (Header = Text) ---
    # Guna
    guna_details = session.get('gunaDetails', {})
    if guna_details:
        for q_id, detail in guna_details.items():
            # Use Question Text as Header if available, else Fallback ID
            text = detail.get('text')
            if not text:
                text = f"Question_{q_id}"
            
            # Value
            row[text] = detail.get('value')
            # Time for that specific question
            row[f"Time: {text}"] = detail.get('reactionTimeMs')

    # Big Five
    bf_details = session.get('bigFiveDetails', {})
    if bf_details:
        for q_id, detail in bf_details.items():
            text = detail.get('text')
            if not text:
                text = f"BigFive_{q_id}"
            
            row[text] = detail.get('value')
            row[f"Time: {text}"] = detail.get('reactionTimeMs')

    return row

def save_to_csv(data_list, filename="original_gpi_wide.csv"):
    if not data_list:
        print("No data to save.")
        return
        
    flat_data = [flatten_session(s) for s in data_list]
    df = pd.DataFrame(flat_data)
    
    # Reorder columns to put Metadata first
    cols = list(df.columns)
    
    # Prioritized prefix list
    priority = ['SessionID', 'FirebaseID', 'Timestamp', 'Version', 
                'Age', 'Gender', 'Occupation', 'Spiritual_Practice', 'Gita_Familiarity',
                'Score_Sattva_Raw', 'Score_Rajas_Raw', 'Score_Tamas_Raw', 'Dominant_Guna']
    
    ordered_cols = [c for c in priority if c in cols]
    remaining_cols = [c for c in cols if c not in priority]
    
    # Sort remaining cols: put View Timings first, then Question columns
    # It's hard to distinguish Question cols from others without explicit lists,
    # but grouping View Timings is helpful.
    view_cols = sorted([c for c in remaining_cols if c.startswith('Time_View')])
    other_cols = [c for c in remaining_cols if not c.startswith('Time_View')]
    
    # Try to sort other_cols alphabetically to group similar questions?
    # Or keep insertion order? Insertion order in dict is reliable in Py3.7+, but DataFrame constructor might shuffle keys if rows differ.
    # Let's keep DataFrame's default column order for the questions as it usually respects first appearance.
    
    final_order = ordered_cols + view_cols + other_cols
    df = df[final_order]
    
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    return df

if __name__ == "__main__":
    data = fetch_original_data()
    if data:
        # Save Raw JSON (Backup)
        with open("original_gpi_dump.json", "w") as f:
            json.dump(data, f, indent=2)
            
        # Flatten to CSV
        save_to_csv(data)
