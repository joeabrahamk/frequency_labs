# Headphone Scoring System - Strategy Architecture

## Core Principle

Every use case follows the same fundamental formula:

```
FinalScore = Σ (weight × adjusted_spec_score)
```

This ensures consistency while allowing use case-specific behavior through:

1. **Priority weights** (Critical, Important, Secondary)
2. **Scoring adjustments** (spec-specific modifiers)

## Weight Tiers

- **Critical**: 0.3 (dominant factors)
- **Important**: 0.15 (significant influence)
- **Secondary**: 0.05 (minor considerations)

## Use Case Strategies

### Gaming

**Philosophy**: Prioritize responsiveness and communication quality. Penalize latency heavily.

**Critical Factors**:

- **Latency** (0.3): Aggressive inverse normalization
  - ≤30ms = 1.0 (perfect)
  - 30-50ms = 0.8
  - 50-100ms = 0.4
  - > 100ms = 0.1 (severe penalty)
- **Mic Count** (0.3): More mics = better clarity
  - 4+ mics get 1.2x multiplier

**Important Factors**:

- **Device Type** (0.15): Wired gets 1.3x bonus (lower latency)
- **ANC** (0.15): Moderate weight for immersion

**Secondary Factors**:

- **Driver Size** (0.05): Small positive influence
- **Battery** (0.05): Low priority unless wireless

**Why**: Gamers need instant audio feedback and clear team communication. High latency breaks immersion and competitive performance.

---

### Gym

**Philosophy**: Durability and wireless freedom. Wired devices are impractical.

**Critical Factors**:

- **Water Resistance** (0.3): IPX7+ gets 1.25x multiplier
  - None = 0.2 (major penalty)
- **Device Type** (0.3): Wireless preference
  - Wired = 0.1 (heavy penalty)
  - Wireless = 1.0

**Important Factors**:

- **ANC** (0.15): Block gym noise
- **Comfort** (0.15): Extended wear during workouts

**Secondary Factors**:

- **Battery** (0.05): Moderate importance
- **Latency** (0.01): Almost irrelevant

**Why**: Gym users hate tangled wires and need sweat resistance. Music timing isn't critical.

---

### Work Calls

**Philosophy**: Crystal-clear communication is paramount. Everything else is secondary.

**Critical Factors**:

- **Mic Count** (0.45): DOMINANT factor
  - 1 mic = 0.3
  - 2 mics = 0.6
  - 3+ mics = 0.7 + 0.1 per additional mic (steep curve)

**Important Factors**:

- **Latency** (0.15): Moderate importance for call quality
- **Comfort** (0.15): All-day wear

**Secondary Factors**:

- **ANC** (0.05): Minor (helps with call focus)
- **Battery** (0.05): Minor

**Why**: Professional communication requires excellent mic quality. Triple-mic arrays with beamforming excel here.

---

### Travel

**Philosophy**: Balanced priorities with emphasis on battery and noise cancellation.

**Critical Factors**:

- **Battery Life** (0.3): Linear importance
- **ANC** (0.3): Strong/Very Strong gets 1.2x multiplier

**Important Factors**:

- **Device Type** (0.15): Wireless preference
- **Comfort** (0.15): Long flights/commutes

**Secondary Factors**:

- **Water Resistance** (0.05): Moderate
- **Driver Size** (0.05): Low to moderate

**Why**: Travelers need long-lasting battery and effective noise isolation for planes/trains.

---

### Casual Music

**Philosophy**: Budget-conscious, value-oriented listening.

**Critical Factors**:

- **Price** (0.3): Strong cost sensitivity
  - ≤$50 = 1.0
  - $50-100 = 0.8
  - $100-200 = 0.5
  - > $200 = 0.2
- **Battery Life** (0.3): Value for money

**Important Factors**:

- **Comfort** (0.15): Enjoyable listening
- **Driver Size** (0.15): Sound quality indicator

**Secondary Factors**:

- **ANC** (0.05): Nice-to-have

**Why**: Casual listeners prioritize affordability and don't need premium features.

---

## Multi-Use Case Scoring

When a user selects multiple use cases (e.g., Gaming 60% + Travel 40%):

1. **Compute independent scores** for each use case
2. **Blend by percentage**: `FinalScore = 0.6 × GamingScore + 0.4 × TravelScore`

**DO NOT** merge weight profiles first. This preserves behavioral uniqueness.

## Design Constraints

### Strategies See Everything, But Only Weighted Specs Score

**Philosophy**: A strategy can observe all specs to make intelligent adjustments, but only specs in its weight profile contribute to the final score.

**Example**:

```python
class GamingStrategy:
    weights = {
        'latency': 0.3,
        'num_mics': 0.3,
        # Note: price is NOT in weights
    }

    def adjust_scores(self, normalized_scores, raw_specs):
        adjusted = normalized_scores.copy()

        # Can still see price even though not weighted
        price = raw_specs.get('price', 0)

        # Penalize latency if headphone is too expensive
        if price > 500:
            adjusted['latency'] *= 0.8

        return adjusted
```

**Why**:

- Handles edge cases: "Perfect gaming specs but costs $1M? Decision collapses."
- Allows contextual intelligence: Strategies can cross-reference specs
- Maintains clean scoring: Only weighted specs affect final number

**Constraint**: Use non-weighted specs ONLY for contextual adjustments, not for direct scoring.

### One Adjustment Per Spec Per Use Case

Avoid stacking multipliers. Choose either:

- Weight increase, OR
- Bonus multiplier, OR
- Curve scaling

Never combine all three—keeps the system interpretable.

### Normalization First, Adjust Second

```python
# All specs normalized (strategies can see everything)
normalized = normalize_specs(raw_specs)

# Strategy can adjust based on ANY spec
adjusted = strategy.adjust_scores(normalized, raw_specs)

# But only weighted specs contribute to score
final_score = sum(adjusted[spec] * weight
                  for spec, weight in strategy.weights.items())
```

This ensures:

1. Strategies have full context for intelligent decisions
2. Adjustments operate on consistent 0-1 scales
3. Scoring remains focused on use case priorities

## Why This Architecture?

### Modularity

Each strategy is self-contained. Adding a new use case:

1. Create `NewUseCaseStrategy` class
2. Define weights
3. Implement `adjust_scores()`
4. Register in `STRATEGIES` dict

### Transparency

Every score is traceable:

- Which specs contributed?
- How much weight?
- What adjustments applied?

### Behavioral Distinctness

Each use case has unique "personality":

- Gaming: Latency-obsessed
- Gym: Wireless-only
- Work: Mic-dominant
- Travel: Battery-first
- Casual: Budget-sensitive

## Example Scoring Flow

```
Input: Sony WH-1000XM4 for Gaming (60%) + Travel (40%)

Gaming Strategy:
  latency: 35ms → normalized=0.825 → adjusted=0.8 → 0.8×0.3 = 0.24
  num_mics: 4 → normalized=0.25 → adjusted=0.3 → 0.3×0.3 = 0.09
  ...
  GamingScore = 0.65

Travel Strategy:
  battery_life: 30h → normalized=0.6 → adjusted=0.6 → 0.6×0.3 = 0.18
  anc_strength: 0.9 → normalized=0.9 → adjusted=1.0 → 1.0×0.3 = 0.30
  ...
  TravelScore = 0.82

FinalScore = 0.6×0.65 + 0.4×0.82 = 0.718
```

## Future Extensions

- Add confidence intervals based on spec quality
- Implement user-defined custom strategies
- Add explanatory text per contribution
- Weight learning from user feedback
