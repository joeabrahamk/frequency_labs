def normalize_value(value, min_value, max_value):
    if value is None:
        return 0  # or handle as needed
    return (value - min_value) / (max_value - min_value)

# Example scoring logic

def score_headphone(headphone, use_case_weights):
    score = 0
    for spec, weight in use_case_weights.items():
        normalized_value = normalize_value(headphone[spec], min_value, max_value)  # Define min/max for each spec
        score += normalized_value * weight
    return score
