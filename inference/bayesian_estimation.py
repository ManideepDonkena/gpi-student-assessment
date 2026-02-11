
import numpy as np

def update_posterior(priors, evidence_weights):
    """
    Update priors with new evidence using a simple Bayesian framework.
    
    Args:
        priors (dict): Current probabilities {'sattva': p1, 'rajas': p2, 'tamas': p3}
        evidence_weights (dict): Evidence strength from choice {'sattva': w1, 'rajas': w2, 'tamas': w3}
        
    Returns:
        dict: Updated normalized posterior probabilities
    """
    # Likelihood heuristic: meaningful weight acts as evidence
    # We treat weights as proportional likelihoods
    # P(Evidence | Guna) ~ weight
    
    posteriors = {}
    total_evidence = 0
    
    for guna, prior in priors.items():
        likelihood = evidence_weights.get(guna, 0)
        # Add a small epsilon to avoid zeroing out completely if not intended
        likelihood = max(likelihood, 0.01)
        
        # Unnormalized posterior
        posteriors[guna] = prior * likelihood
        total_evidence += posteriors[guna]
        
    # Normalize
    if total_evidence > 0:
        for guna in posteriors:
            posteriors[guna] /= total_evidence
    else:
        return priors # No update if evidence is zero
        
    return posteriors

def estimate_guna_profile(responses, scenarios):
    """
    Estimate the final Guna profile for a session.
    """
    # Start with uniform prior (Dirichlet alpha=1,1,1)
    current_probs = {'sattva': 0.333, 'rajas': 0.333, 'tamas': 0.333}
    
    # Create a map for fast scenario lookup
    scenario_map = {s['id']: s for s in scenarios}
    
    history = [current_probs.copy()]
    
    for resp in responses:
        scenario = scenario_map.get(resp['scenarioId'])
        if not scenario:
            continue
            
        # Find the chosen option's weights
        choice = next((c for c in scenario['choices'] if c['id'] == resp['choiceId']), None)
        if choice:
            current_probs = update_posterior(current_probs, choice['weights'])
            history.append(current_probs.copy())
            
    return current_probs, history
