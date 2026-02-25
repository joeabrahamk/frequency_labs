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
    'battery_life': (0, 50, False),
    'water_resistance': (0, 1, False),
    'price': (0, 20000, True),      # Lower is better (INR)
    'device_type': (0, 1, False),   # Handled by strategy
}

# Driver size ranges by device type
DRIVER_SIZE_RANGES = {
    'earbuds': (6, 15),       # Earbuds: 6mm-15mm
    'over-ear': (30, 53),     # Over-ear: 30mm-53mm
    'wireless': (30, 53),     # Wireless (typically over-ear): 30mm-53mm
    'wired': (30, 53),        # Wired (typically over-ear): 30mm-53mm
    'neckband': (6, 15),      # Neckband (earbud-style): 6mm-15mm
}

def normalize_specs(headphone_dict):
    """Normalize all specs to 0-1 range"""
    normalized = {}
    device_type = headphone_dict.get('device_type', '').lower()
    is_wired = 'wired' in device_type
    
    for spec, (min_val, max_val, inverse) in SPEC_RANGES.items():
        value = headphone_dict.get(spec)
        
        # Skip device_type - it's handled by strategy adjustments
        if spec == 'device_type':
            normalized[spec] = 0.5  # Neutral default
            continue
        
        # Special handling for wired devices
        if is_wired:
            if spec == 'latency':
                # Wired headphones have zero latency - perfect score
                normalized[spec] = 1.0
                continue
            elif spec == 'battery_life':
                # Wired headphones don't need battery - neutral score (not a penalty)
                normalized[spec] = 0.75  # Slightly positive since no battery means always-on
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
    
    # Handle driver_size separately based on device_type
    driver_size = headphone_dict.get('driver_size')
    device_type = headphone_dict.get('device_type', '').lower()
    
    if driver_size is not None:
        # Get appropriate range for this device type
        min_driver, max_driver = DRIVER_SIZE_RANGES.get(device_type, (20, 50))
        
        # Normalize within appropriate range
        if max_driver == min_driver:
            normalized['driver_size'] = 0.5
        else:
            norm_value = (driver_size - min_driver) / (max_driver - min_driver)
            normalized['driver_size'] = max(0, min(1, norm_value))
    else:
        normalized['driver_size'] = 0.5
    
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
        
        # Calculate value score (performance per rupee)
        price = headphone.get('price', 1)
        if price <= 0:
            price = 1  # Avoid division by zero
        value_score = (final_score / price) * 10000  # Scale up for readability
        
        ranked.append({
            "model": headphone.get('name') or f"Headphone {idx + 1}",
            "score": round(final_score, 3),
            "value_score": round(value_score, 3),
            "price": price,
            "contributions": all_contributions,
            "use_case_scores": use_case_scores,
            "details": headphone
        })
    
    # Sort by performance score descending
    ranked.sort(key=lambda x: x['score'], reverse=True)
    
    # Create value-ranked list
    value_ranked = sorted(ranked, key=lambda x: x['value_score'], reverse=True)
    
    # Build explanation
    use_case_names = [uc.name.replace('_', ' ').title() for uc in request.use_cases]
    use_case_percentages = [f"{uc.name.replace('_', ' ').title()} ({uc.percentage}%)" 
                           for uc in request.use_cases]
    
    return {
        "ranked_headphones": ranked,
        "value_ranked_headphones": value_ranked,
        "explanation": {
            "reasoning": f"Headphones ranked for: {', '.join(use_case_percentages)}. "
                        f"Performance ranking shows best specs for your use cases. "
                        f"Value ranking shows best performance per rupee spent."
        }
    }

@app.post("/rank_headphones/")
async def rank_headphones(request: UserRequest):
    # Implement ranking logic here
    return {
        "ranked_headphones": [],
        "explanation": {}
    }
