# Decision-Making Thought Process

## Key Architectural Decisions

### Decision 1: Strategies See All Specs, But Only Weighted Specs Contribute

**Date**: February 19, 2026

**The Question**: Should strategies only see and normalize the specs in their weight profile, or should they have access to all specs?

**Initial Approach**: Only normalize specs that are in each strategy's weights.

- Gaming would only see: latency, num_mics, device_type, driver_size, battery_life, price
- Gym would only see: water_resistance, device_type, battery_life, latency, driver_size
- Complete isolation between use cases

**The Problem**:
"What if a headphone has perfect gaming specs but costs ₹1,000,000? The whole decision-making collapses."

Even if price isn't weighted for gaming, the strategy should be able to see it and make informed adjustments.

**Final Decision**:

```python
# Step 1: Normalize ALL specs (strategies can see everything)
normalized_scores = normalize_specs(headphone_dict)

# Step 2: Strategy can use ANY spec to make decisions
adjusted_scores = strategy.adjust_scores(normalized_scores, headphone_dict)

# Step 3: Only weighted specs contribute to final score
for spec, weight in strategy.weights.items():
    contribution = spec_score * weight
    score += contribution
```

**Why This Works**:

1. **Flexibility**: Strategies can make contextual decisions based on ANY spec
   - Gaming could penalize if price > ₹15,000 even though price isn't weighted
   - Travel could boost for long battery life devices
   - Gym could check driver size for durability context

2. **Clean Scoring**: Only explicitly weighted specs affect the final score
   - Gaming score = 0.3×latency + 0.3×mics + 0.15×device + 0.15×driver + 0.05×battery + 0.05×price
   - No accidental contamination from non-weighted specs

3. **Real-World Decision Making**: Mimics how humans evaluate
   - "This is perfect for gaming, but it's ₹20,000... maybe reduce the overall appeal"
   - "Battery life is great for travel, so boost the overall appeal"

**Example Use Case**:

```python
class GamingStrategy:
    weights = {
        'latency': 0.3,
        'num_mics': 0.3,
        # price NOT in weights
    }

    def adjust_scores(self, normalized, raw_specs):
        adjusted = normalized.copy()

        # Can still see price even though not weighted
        price = raw_specs.get('price', 0)

        # If too expensive, penalize latency contribution
        if price > 15000:
            adjusted['latency'] *= 0.8  # 20% penalty

        return adjusted
```

**Trade-offs**:

- ✅ More realistic decision-making
- ✅ Handles edge cases (perfect specs, terrible price)
- ✅ Strategies can implement smart cross-spec logic
- ⚠️ Slight complexity - strategies must be careful not to abuse access
- ⚠️ Normalizing all specs uses more computation (negligible in practice)

**Constraint**:
Strategies should use non-weighted specs sparingly and only for contextual adjustments. The core scoring must come from weighted specs to maintain use case distinctiveness.

---

## Future Decisions to Document

- Multi-use case blending strategy
- Confidence intervals
- User feedback integration
- Custom weight profiles
