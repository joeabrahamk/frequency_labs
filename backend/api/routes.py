from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.headphone import UserRequest
from scoring.strategies import get_strategy

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for keeping backend alive on Render free tier
@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

# Normalization ranges for each spec
SPEC_RANGES = {
    'latency': (0, 200, True),      # Lower is better
    'num_mics': (0, 16, False),     # More is better
    'anc_strength': (0, 1, False),
    'battery_life': (0, 50, False),
    'water_resistance': (0, 1, False),
    'comfort_score': (0, 1, False),
    'price': (0, 500, True),        # Lower is better
    'driver_size': (20, 50, False), # Bigger generally better
    'device_type': (0, 1, False),   # Handled by strategy
}

def normalize_specs(headphone_dict):
    """Normalize all specs to 0-1 range"""
    normalized = {}
    
    for spec, (min_val, max_val, inverse) in SPEC_RANGES.items():
        value = headphone_dict.get(spec)
        
        # Skip device_type - it's handled by strategy adjustments
        if spec == 'device_type':
            normalized[spec] = 0.5  # Neutral default
            continue
        
        if value is None:
            normalized[spec] = 0.5
            continue
            
        # Normalize to 0-1
        if min_val == max_val:
            norm_value = 0.5
        else:
            norm_value = (value - min_val) / (max_val - min_val)
            norm_value = max(0, min(1, norm_value))  # Clamp to 0-1
        
        # Invert if lower is better
        if inverse:
            norm_value = 1 - norm_value
            
        normalized[spec] = norm_value
    
    return normalized

def score_headphone_for_use_case(headphone_dict, use_case_name):
    """
    Score a single headphone for a specific use case.
    Returns: (score, contributions_dict)
    
    Note: All specs are normalized and visible to strategies,
    but only specs in strategy.weights contribute to final score.
    This allows strategies to adjust based on any spec (e.g., penalize expensive options).
    """
    strategy = get_strategy(use_case_name)
    
    # Step 1: Normalize ALL specs (strategies can see everything)
    normalized_scores = normalize_specs(headphone_dict)
    
    # Step 2: Apply strategy-specific adjustments
    # Strategy can use any spec to make decisions, even if not weighted
    adjusted_scores = strategy.adjust_scores(normalized_scores, headphone_dict)
    
    # Step 3: Calculate weighted sum - ONLY specs in strategy.weights contribute
    score = 0
    contributions = {}
    
    for spec, weight in strategy.weights.items():
        spec_score = adjusted_scores.get(spec, 0)
        contribution = spec_score * weight
        score += contribution
        contributions[spec] = round(contribution, 4)
    
    # Debug logging
    print(f"\n=== {use_case_name} ===")
    print(f"Strategy weights: {strategy.weights}")
    print(f"Contributions: {contributions}")
    print(f"Final score: {score}")
    
    return score, contributions

@app.post("/evaluate")
async def evaluate(request: UserRequest):
    """
    Evaluate headphones across multiple use cases.
    Each use case is scored independently, then blended by percentage.
    """
    headphones_data = [h.dict() for h in request.headphones]
    
    # Validate total percentage
    total_percentage = sum(uc.percentage for uc in request.use_cases)
    
    # Score each headphone
    ranked = []
    for idx, headphone in enumerate(headphones_data):
        # Calculate independent scores for each use case
        use_case_scores = {}
        all_contributions = {}
        final_score = 0
        
        for use_case in request.use_cases:
            # Score for this specific use case
            uc_score, contributions = score_headphone_for_use_case(
                headphone, 
                use_case.name
            )
            
            # Weight by use case percentage
            weighted_score = uc_score * (use_case.percentage / 100)
            final_score += weighted_score
            
            use_case_scores[use_case.name] = round(uc_score, 3)
            
            # Accumulate contributions
            for spec, contrib in contributions.items():
                weighted_contrib = contrib * (use_case.percentage / 100)
                all_contributions[spec] = all_contributions.get(spec, 0) + weighted_contrib
        
        # Round contributions
        all_contributions = {k: round(v, 4) for k, v in all_contributions.items()}
        
        ranked.append({
            "model": headphone.get('name') or f"Headphone {idx + 1}",
            "score": round(final_score, 3),
            "contributions": all_contributions,
            "use_case_scores": use_case_scores,
            "details": headphone
        })
    
    # Sort by score descending
    ranked.sort(key=lambda x: x['score'], reverse=True)
    
    # Build explanation
    use_case_names = [uc.name.replace('_', ' ').title() for uc in request.use_cases]
    use_case_percentages = [f"{uc.name.replace('_', ' ').title()} ({uc.percentage}%)" 
                           for uc in request.use_cases]
    
    return {
        "ranked_headphones": ranked,
        "explanation": {
            "reasoning": f"Headphones ranked for: {', '.join(use_case_percentages)}. "
                        f"Each use case scored independently using strategy-based weighting, "
                        f"then blended by your percentages. Higher scores indicate better fit."
        }
    }

@app.post("/rank_headphones/")
async def rank_headphones(request: UserRequest):
    # Implement ranking logic here
    return {
        "ranked_headphones": [],
        "explanation": {}
    }
