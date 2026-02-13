import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json
import os
import sys

from datetime import datetime, timezone, timedelta

# =========================================================
# CONFIGURATION
# =========================================================
SERVICE_ACCOUNT_KEY = "../analysis/firebase_service_account_key.json" 
if not os.path.exists(SERVICE_ACCOUNT_KEY):
    SERVICE_ACCOUNT_KEY = "firebase_service_account_key.json"

def format_ms_to_min_sec(ms):
    """Converts milliseconds to 'Xm Ys' format"""
    if not ms: return "0s"
    seconds = int(ms / 1000)
    minutes = seconds // 60
    rem_seconds = seconds % 60
    if minutes > 0:
        return f"{minutes}m {rem_seconds}s"
    return f"{rem_seconds}s"

def to_ist(iso_str):
    """Converts ISO UTC string to IST string"""
    if not iso_str: return ""
    try:
        # Parse ISO (handling Z)
        dt_utc = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        # Add 5:30 for IST
        ist_offset = timedelta(hours=5, minutes=30)
        dt_ist = dt_utc.astimezone(timezone(ist_offset))
        return dt_ist.strftime("%Y-%m-%d %H:%M:%S IST")
    except Exception as e:
        return iso_str # Fallback
    except Exception as e:
        return iso_str # Fallback

def calculate_durations(details_dict):
    """
    Returns a dict mapping { q_id: duration_ms }
    Duration is calculated as time delta from previous response.
    """
    if not details_dict: return {}
    
    # Convert to list of objects
    responses = []
    for q_id, detail in details_dict.items():
        responses.append({
            'id': q_id,
            'ms': detail.get('reactionTimeMs', 0)
        })
    
    # Sort by timestamp (ms) - Time of Action
    responses.sort(key=lambda x: x['ms'])
    
    durations = {}
    prev_ms = 0
    for resp in responses:
        curr_ms = resp['ms']
        # If curr_ms < prev_ms, it implies out of order? 
        # But we sort by ms, so curr_ms >= prev_ms always.
        duration = curr_ms - prev_ms
        
        # Safety for very fast concurrent weirdness
        if duration < 0: duration = 0 
        
        durations[resp['id']] = duration
        prev_ms = curr_ms
        
    return durations

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
        "Timestamp": to_ist(session.get('uploadedAt')),
        "Version": session.get('version')
    }

    # --- Demographics ---
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
            # row[f"Time_View_{view}_ms"] = ms  <-- Removed per user request
            row[f"Time_View_{view}"] = format_ms_to_min_sec(ms)

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
    
    total_time = guna_meta.get('timeMs')
    row["Total_Guna_Time"] = format_ms_to_min_sec(total_time)
    
    row["Guna_Changes"] = guna_meta.get('answerChanges')
    row["Tab_Switches"] = guna_meta.get('tabSwitches', 0)
    
    idle_ms = guna_meta.get('idleTimeMs', 0)
    # row["Idle_Time_ms"] = idle_ms
    row["Idle_Time_fmt"] = format_ms_to_min_sec(idle_ms)
    
    # --- Wide Format Questions (Header = Text) ---
    # Guna
    # Guna
    guna_details = session.get('gunaDetails', {})
    if guna_details:
        # Calculate Durations First
        guna_durations = calculate_durations(guna_details)
        
        for q_id, detail in guna_details.items():
            # Use Question Text as Header if available, else Fallback ID
            text = detail.get('text')
            if not text:
                text = f"Question_{q_id}"
            
            # Value
            row[text] = detail.get('value')
            
            # Timestamp (When answer occurred) - SKIPPED per user request
            # row[f"Timestamp: {text}"] = format_ms_to_min_sec(detail.get('reactionTimeMs'))
            
            # Duration (How long it took)
            dur_ms = guna_durations.get(q_id, 0)
            row[f"Duration: {text}"] = format_ms_to_min_sec(dur_ms)

    # Big Five
    bf_details = session.get('bigFiveDetails', {})
    if bf_details:
        bf_durations = calculate_durations(bf_details)
        
        for q_id, detail in bf_details.items():
            text = detail.get('text')
            if not text:
                text = f"BigFive_{q_id}"
            
            row[text] = detail.get('value')
            # Timestamp - SKIPPED
            # row[f"Timestamp: {text}"] = format_ms_to_min_sec(detail.get('reactionTimeMs'))
            # Duration
            dur_ms = bf_durations.get(q_id, 0)
            row[f"Duration: {text}"] = format_ms_to_min_sec(dur_ms)

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
    # Sort remaining cols: put View Timings first, then Question columns
    # Group formatted times with their ms counterparts
    view_cols = sorted([c for c in remaining_cols if c.startswith('Time_View') or c.startswith('Total_Guna')])
    other_cols = [c for c in remaining_cols if c not in view_cols]
    
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
