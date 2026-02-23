# Scoring System Documentation

## Overview

The scoring system evaluates headphones differently based on use case. Each use case has its own scoring strategy with specific weights assigned to different specifications.

All specifications are normalized to a 0-1 scale before scoring, where:

- 1.0 = best score for that spec
- 0.0 = worst score for that spec

**Weight Distribution:**

- Critical (0.3): Most important - heavily influences ranking
- Important (0.15): Moderately important
- Secondary (0.05): Low influence

---

## Gaming Strategy

**Use Case:** Low-latency, high-clarity gaming sessions

### Weight Distribution

| Specification | Weight   | Importance | Notes                                            |
| ------------- | -------- | ---------- | ------------------------------------------------ |
| Latency       | 0.3      | Critical   | Lower latency = better for real-time gameplay    |
| Num Mics      | 0.3      | Critical   | More mics = clearer communication with teammates |
| Device Type   | 0.15     | Important  | Wired gets bonus (1.3x multiplier)               |
| Driver Size   | 0.15     | Important  | Larger drivers for better audio clarity          |
| Price         | 0.15     | Important  | Value consideration for budget gamers            |
| **Total**     | **1.05** | —          | —                                                |

### Scoring Techniques

1. **Latency Adjustment:**
   - ≤ 30ms → 1.0 (perfect)
   - 30-50ms → 0.8 (good)
   - 50-100ms → 0.4 (acceptable)
   - > 100ms → 0.1 (poor - severe penalty)

2. **Device Type Adjustment:**
   - Wired → 1.0 × 1.3 = 1.3 multiplier (strong preference)
   - Wireless → 0.6

3. **Mic Count Adjustment:**
   - ≥ 4 mics → normalized_score × 1.2 (boost)
   - < 4 mics → keep as normalized

4. **Price:** Uses base normalization (cheaper = higher score)

---

## Gym Strategy

**Use Case:** Active workouts with durability and water resistance needs

### Weight Distribution

| Specification    | Weight  | Importance | Notes                                    |
| ---------------- | ------- | ---------- | ---------------------------------------- |
| Water Resistance | 0.3     | Critical   | IPX7+ essential for sweat/water exposure |
| Device Type      | 0.3     | Critical   | Wireless preferred for mobility          |
| Battery Life     | 0.3     | Critical   | Long sessions need sustained power       |
| Price            | 0.05    | Secondary  | Less critical for gym users              |
| Latency          | 0.025   | Secondary  | Minor impact                             |
| Driver Size      | 0.025   | Secondary  | Minor impact                             |
| **Total**        | **1.0** | —          | —                                        |

### Scoring Techniques

1. **Device Type Adjustment:**
   - Wireless → 1.0 (strongly preferred)
   - Wired → 0.1 (major reduction)

2. **Water Resistance Adjustment:**
   - IPX7+ → normalized_score × 1.25 (boost)
   - IPX4-5 → normalized_score (keep as is)
   - None → 0.2 (major reduction)

3. **Other Specs:** Use base normalization

---

## Work Calls Strategy

**Use Case:** Clear microphone quality for professional calls

### Weight Distribution

| Specification    | Weight  | Importance     | Notes                                  |
| ---------------- | ------- | -------------- | -------------------------------------- |
| Num Mics         | 0.45    | Critical × 1.5 | Dominant factor - clarity is essential |
| Latency          | 0.15    | Important      | Smooth real-time conversation          |
| Battery Life     | 0.15    | Important      | Long workday support                   |
| Price            | 0.15    | Important      | Professional budget considerations     |
| Driver Size      | 0.05    | Secondary      | Minor impact                           |
| Water Resistance | 0.05    | Secondary      | Minor impact                           |
| **Total**        | **1.0** | —              | —                                      |

### Scoring Techniques

1. **Mic Count Adjustment:**
   - ≥ 8 mics → 1.0 (excellent)
   - 4-7 mics → 0.8 (very good)
   - 2-3 mics → 0.5 (average)
   - 0-1 mics → 0.2 (poor)

2. **Other Specs:** Use base normalization with increased price weight

---

## Travel Strategy

**Use Case:** Long journeys with comfort and battery endurance

### Weight Distribution

| Specification    | Weight  | Importance | Notes                                      |
| ---------------- | ------- | ---------- | ------------------------------------------ |
| Battery Life     | 0.3     | Critical   | Long flights/commutes need sustained power |
| Device Type      | 0.3     | Critical   | Wireless preferred for convenience         |
| Water Resistance | 0.15    | Important  | Weather/spillage protection                |
| Price            | 0.15    | Important  | Long-term investment value                 |
| Driver Size      | 0.05    | Secondary  | Minor impact                               |
| Num Mics         | 0.05    | Secondary  | Calls less important than gaming           |
| **Total**        | **1.0** | —          | —                                          |

### Scoring Techniques

1. **Device Type Adjustment:**
   - Wireless → 1.0 (strong preference)
   - Wired → 0.5 (not ideal for travel)

2. **Other Specs:** Use base normalization

---

## Casual Music Strategy

**Use Case:** Everyday listening with budget sensitivity

### Weight Distribution

| Specification    | Weight  | Importance | Notes                                 |
| ---------------- | ------- | ---------- | ------------------------------------- |
| Price            | 0.3     | Critical   | Budget-focused listeners              |
| Battery Life     | 0.3     | Critical   | Daily listening requires good battery |
| Driver Size      | 0.15    | Important  | Sound quality matters                 |
| Water Resistance | 0.15    | Important  | General protection                    |
| Device Type      | 0.05    | Secondary  | Less critical for casual use          |
| Num Mics         | 0.05    | Secondary  | Calls not primary use                 |
| **Total**        | **1.0** | —          | —                                     |

### Scoring Techniques

1. **Price Adjustment:** Uses base normalization (inverse - cheaper = higher)

2. **Other Specs:** Use base normalization

---

## Normalization Formula

For each specification:

```
normalized_score = (value - min) / (max - min)

If inverse (lower is better):
  normalized_score = 1 - normalized_score

Clamp to [0, 1]
```

**Price Normalization (Inverse - Lower is Better):**

- Min: ₹0
- Max: ₹20,000
- Example: ₹800 → (800-0)/(20000-0) = 0.04 → inverted = 0.96 (96%)

---

## Final Score Calculation

```
Final Score = Σ (weight × adjusted_score) for all specs in strategy.weights
```

**Example (Gaming with latency=25ms, num_mics=4, price=₹5000):**

- Latency: 0.3 × 1.0 = 0.30 (25ms gets full score)
- Num Mics: 0.3 × 0.80 = 0.24 (4 mics gets 0.8)
- Device Type: 0.15 × 0.60 = 0.09 (wireless)
- Driver Size: 0.15 × 0.75 = 0.11
- Price: 0.15 × 0.75 = 0.11 (₹5000 is 25% of max)
- **Total: 0.85 (85%)**

---

## Value Score Calculation

```
Value Score = (Performance Score / Price) × 10000

Higher value score = better performance per rupee spent
```

**Example:**

- Headphone A: Score 0.85, Price ₹5000 → Value = (0.85 / 5000) × 10000 = 1.7
- Headphone B: Score 0.80, Price ₹2000 → Value = (0.80 / 2000) × 10000 = 4.0

Headphone B has better value despite lower absolute performance.

---

## Multi-Use Case Blending

When multiple use cases selected (e.g., 50% Gaming + 50% Travel):

1. Calculate independent score for each use case
2. Weight blend by percentages
3. Return single blended score

```
Blended Score = (Gaming Score × 0.50) + (Travel Score × 0.50)
```

---

## Key Design Principles

1. **Deterministic:** Same input always produces same output
2. **Transparent:** Contribution breakdown shows why ranking happened
3. **Context-Aware:** Different use cases prioritize different specs
4. **Normalized:** All specs on same 0-1 scale for fair comparison
5. **Explainable:** Clear weight distribution and adjustment logic
