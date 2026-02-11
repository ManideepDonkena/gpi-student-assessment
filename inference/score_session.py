
import json

def calculate_weighted_scores(session_data, scenarios):
    """
    Calculate raw and normalized scores based on weighted evidence sum.
    Also applies time-based modifiers.
    """
    scenario_map = {s['id']: s for s in scenarios}
    
    scores = {'sattva': 0.0, 'rajas': 0.0, 'tamas': 0.0}
    max_scores = {'sattva': 0.0, 'rajas': 0.0, 'tamas': 0.0}
    
    for resp in session_data['responses']:
        scenario = scenario_map.get(resp['scenarioId'])
        if not scenario:
            continue
            
        choice = next((c for c in scenario['choices'] if c['id'] == resp['choiceId']), None)
        if not choice:
            continue
            
        weights = choice['weights']
        time_taken = resp.get('timeToSelectMs', 5000)
        
        # --- Time-based modifiers (Heuristic) ---
        # Very fast (< 2s) suggests impulsivity -> slight Rajas boost
        # Very slow (> 10s) suggests inertia/indecision -> slight Tamas boost
        # Moderate (3-8s) suggests deliberation -> slight Sattva boost (for Sattva choices)
        
        modifier = {'sattva': 1.0, 'rajas': 1.0, 'tamas': 1.0}
        
        if time_taken < 2000:
            modifier['rajas'] = 1.1 # 10% boost to Rajas weight
        elif time_taken > 10000:
            modifier['tamas'] = 1.1
        
        # Apply weights to totals
        for guna in scores:
            scores[guna] += weights.get(guna, 0) * modifier[guna]
            
        # Track max possible (theoretical max for normalization)
        # Simplification: max possible is sum of max weights per scenario
        # But this depends on which path is taken. 
        # For now, we normalize by total points earned to get a % profile.
        
    # Profile normalization
    total_score = sum(scores.values())
    profile = {}
    if total_score > 0:
        for guna, score in scores.items():
            profile[guna] = (score / total_score) * 100
    else:
        profile = {'sattva': 0, 'rajas': 0, 'tamas': 0}
            
    return scores, profile
