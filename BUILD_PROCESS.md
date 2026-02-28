## 1. How I Started

I began by reflecting on the last time I personally struggled with a real-world decision. Initially, I thought about purchasing a laptop, since it was also suggested in the assignment examples. However, I realized that when I bought my laptop, I had access to multiple comparison platforms that helped evaluate specifications side by side.

That made me question whether I had recently faced a decision problem where structured help was not easily available.

I then recalled purchasing earbuds. During that process, I searched across multiple websites trying to compare specifications, use cases, and trade-offs in a structured way. Unlike laptops, I did not find a clear, context-aware comparison system that helped me decide based on how I intended to use the device. Most platforms either focused on raw specifications or generic reviews, without aligning features with user-specific needs like gaming, gym usage, work calls, or travel.

This realization shaped the direction of the project.

Instead of building a generic product comparison tool, I decided to build a context-aware decision companion for headphones. The goal was not to compare specs in isolation, but to model how different use cases influence the importance of each specification.

That shift from “spec comparison” to “context-driven decision modeling” became the foundation of the system.

While testing early MVP flows, I noticed that constantly filling specs was inconvenient for me. That inconvenience would be even worse for users who are not comfortable with technical specifications. This pushed me to add a link-based comparison idea: let users paste product links so the system can extract specs automatically.

## 2. How My Thinking Evolved

While modeling early scoring logic, I realized that real-world decisions are not spec-centric, they are context-centric.

For example:

Latency is critical for gaming but nearly irrelevant for gym usage.

Water resistance is essential for gym but unnecessary for office work.

Wired vs wireless preference depends entirely on context.

This led me to shift from a "spec-driven scoring system" to a "use-case-driven strategy system."

Instead of applying one global scoring formula, I introduced distinct scoring strategies for each use case.

Each use case now defines:

A weight profile.

Optional scoring adjustments (e.g., stronger penalty for high latency in gaming).

Context-aware interpretation of specifications.

This change made the system more realistic and aligned with how humans actually evaluate products.

## 3. Alternative Approaches Considered

# 1. Pure Weighted Average Model

I initially considered a single universal weighted scoring engine where use cases only modified weights.

Reason rejected:
This approach did not allow behavior-specific scoring (e.g., severe latency penalties in gaming). It felt too simplistic.

# 2. Machine Learning-Based Ranking

I briefly considered training or simulating a model to rank devices dynamically.

Reason rejected:

Black-box behavior.

Lack of explainability.

Violates requirement of deterministic logic.

Over-engineered for the scope of the assignment.

# 3. AI-Driven Scoring

I explored allowing AI to directly score headphones based on user input.

Reason rejected:

Non-deterministic.

Hard to justify.

Not transparent.

Makes system untestable and non-reproducible.

Instead, AI was limited to optional intent classification only.

# 4. Single Combined Weight Profile for Multiple Use Cases

For blended use cases (e.g., 70% gaming + 30% travel), I initially merged weight tables first.

Reason rejected:
Merging weight tables before scoring flattened behavioral differences between strategies.

Final approach:
Compute individual use case scores independently and blend the final scores.

This preserved strategy-specific behavior.

## 4. Refactoring Decisions

Refactoring 1: Separating Normalization from Strategy Logic

Initially, normalization and scoring logic were tightly coupled.

I refactored to:

Create a dedicated normalization module.

Keep scoring strategies separate.

This improved modularity and made the system easier to extend.

Refactoring 2: Isolating Explanation Engine

The explanation logic was initially embedded inside the ranking module.

I separated it into a distinct explanation engine that:

Calculates per-criterion contributions.

Generates structured reasoning objects.

Remains independent from API routing.

This improved clarity and maintainability.

Refactoring 3: Strategy Pattern for Use Cases

Instead of condition-heavy if/else logic for use cases, I refactored to a strategy-based design.

Each use case now:

Defines its own weight profile.

Applies context-aware scoring adjustments.

Produces an independent score.

This significantly improved readability and extensibility.

## 5. Mistakes and Corrections

# Mistake 1: Overcomplicating Scoring Adjustments

I initially stacked multiple multipliers per criterion, which caused unstable scoring behavior.

Correction:
Restricted each use case to one primary adjustment per prioritized specification.

This kept the model interpretable.

# Mistake 2: Conflating Technology Type with Performance Strength

I initially treated ANC type (Hybrid, Adaptive, etc.) as a strength metric.

Correction:
Separated ANC type from ANC effectiveness score to maintain clarity.

# Mistake 3: Letting AI Influence Scoring Logic

In early drafts, I considered allowing AI to modify weight values directly.

Correction:
Restricted AI to classification only. Scoring remains fully deterministic.

This preserved explainability.

# Mistake 4: Backend Timeout on Free Tier Deployment

When deploying on Render's free tier, the backend would spin down after 15 minutes of inactivity, causing 500 errors for users.

Initial approach considered:

- Upgrading to paid tier (expensive)
- Switching to a different platform

Correction:
Implemented a keep-alive ping mechanism on the frontend:

- Frontend pings the backend health check endpoint immediately on page load
- Pings are sent every 5 minutes while users are on the site
- Pings fail silently (errors are logged but not displayed to users)
- Backend has a simple health check endpoint that returns `{"status": "ok"}`

This solved the cold-start problem without additional cost or platform migration.

# Mistake 5: Price Weight Too Low to Be Meaningful

Initially, price was weighted only at 0.05 (SECONDARY) across all strategies, making the price difference between headphones negligible in final scores.

Test case: ₹800 vs ₹2000 headphones showed only ~3% score difference despite 2.5x price difference.

Correction:

- Increased price weight to 0.15 (IMPORTANT) in Gaming, WorkCalls, and Travel strategies
- CasualMusicStrategy already had 0.3 (CRITICAL) weight on price
- Now ₹800 headphone gets 0.96 normalized score vs ₹2000 gets 0.90, making price sensitivity visible
- Updated frontend breakdown to show weight importance badges (Critical/Important/Secondary)

This ensures price differences are reflected appropriately in rankings while being balanced with other specifications.

# Mistake 6: Subjective/Unmeasurable Specifications

Initially included Sound Signature, Comfort Score, and ANC Effectiveness as scoring criteria.

Problem:

- These are subjective and difficult for users to quantify accurately
- No standardized way to measure comfort objectively
- Sound signature varies by personal preference

Correction:

- Removed Sound Signature, Comfort Score, and ANC Effectiveness fields entirely
- Retained objective specs: latency, battery life, num_mics, water resistance, driver size, device type, price
- Simplified the decision model to focus on measurable factors
- Updated all UI components and backend validation to exclude these fields

This improved system reliability and user experience by removing ambiguous inputs.

# Mistake 7: Driver Size Normalization Ignoring Device Type Context

Initially used a single normalization range (20-50mm) for all driver sizes, regardless of device type.

Problem:

- Over-ear headphones use 30-53mm drivers (standard: 40mm)
- Earbuds use 6-15mm drivers (standard: 10-12mm)
- Comparing a 12mm earbud driver to a 40mm over-ear driver using the same scale unfairly penalized earbuds
- A 12mm driver is excellent for earbuds but would score poorly on a 20-50mm scale

Correction:

- Implemented context-aware driver size normalization based on device type
- Earbuds/Neckband: normalized within 6-15mm range
- Over-ear/Wireless/Wired: normalized within 30-53mm range
- Each device type now normalized within its appropriate physical constraints
- A 12mm earbud (67% of its range) is now comparable to a 40mm over-ear (43% of its range)

This ensures fair comparison between fundamentally different headphone form factors.

# Mistake 8: Wired Devices Penalized for Battery and Latency

Initially, wired headphones received neutral scores (0.5) for battery life (null value) and were normalized like wireless devices for latency.

Problem:

- Wired headphones have **zero latency** by design - they should get perfect latency score
- Wired headphones don't need batteries (always powered) - null battery shouldn't be a penalty
- Receiving 0.5 for latency when wired devices have inherent advantage was unfair
- Battery being null was treated as "missing data" rather than "not applicable"

Correction:

- **Latency for wired:** Automatically assigned 1.0 (perfect score) since wired = zero latency
- **Battery for wired:** Assigned 0.75 (slightly positive) since no battery means always-on reliability
- Updated normalization logic to detect `device_type: 'wired'` and apply special handling
- All strategies now include all 7 specs in weight distribution (even if some have very low weights)

Example impact:

- Before: Wired gaming headphone gets 0.5 latency score
- After: Wired gaming headphone gets 1.0 latency score (perfect)
- Before: Gym strategy penalizes wired heavily on battery (0.5 × 0.3 weight = 0.15 contribution)
- After: Gym strategy still penalizes wired on device_type (0.1 × 0.3 = 0.03), but battery gets 0.75 × 0.3 = 0.225

This ensures wired devices are evaluated fairly based on their actual characteristics.

# Mistake 9: Vendor Lock-in with Single API Provider

Initially built link-based comparison using only Rainforest API for product data extraction from Amazon/Flipkart.

Problem:

- Rainforest API encountered persistent 402 payment errors (account/billing issues)
- System had no fallback when the single provider failed
- Tightly coupled implementation made switching providers difficult
- No flexibility to adapt to market conditions or cost changes

First attempted fix (Gemini API):

- Switched to Google Gemini to avoid third-party API dependencies
- Implemented HTML fetching + LLM-based extraction
- New problem: free tier had `quota limit = 0`, all requests returned 429 errors

Correction:

- Migrated to OpenRouter for vendor-agnostic LLM access
- Decoupled API provider from business logic via generic HTTP interface
- Supports 100+ models (Mistral, Claude, GPT-4, Llama, etc.) via configuration
- Can switch models/providers instantly without code changes
- Implemented error handling for quota (429) and auth (401) issues

Key improvements:

- No quota limits or account suspension risks
- Easy parsing

This taught me that production systems need flexibility at the data integration layer. Abstracting away provider-specific details allows the system to evolve with market conditions without touching core scoring logic.

## 6. What Changed During Development and Why

Shift from spec-first scoring to use-case-first strategy design.
Reason: Better alignment with real-world decision behavior.

Shift from merged weight blending to independent use case scoring.
Reason: Preserve behavioral uniqueness of strategies.

Strengthened modularity.
Reason: Improve clarity and future extensibility.

Limited AI scope.
Reason: Maintain transparency and reproducibility.

Removed subjective specification fields (Sound Signature, Comfort Score, ANC Effectiveness).
Reason: These are hard to quantify accurately; replaced with objective, measurable specs.

Increased price weight in scoring strategies.
Reason: Ensure price differences are reflected meaningfully in rankings while being balanced with performance specs.

Introduced dual ranking system (Performance + Value rankings).
Reason: Previously, ranking was based only on performance score, which didn't account for price fairness. A headphone with 46 points at ₹21,000 would rank higher than one with 43 points at ₹6,000, despite the second being much better value. Value score (performance_score / price) now shows best performance-per-rupee, allowing users to see both best absolute performance and best value for money.

Localized pricing from USD to INR.
Reason: Simplified for Indian market evaluation.

Added link-based comparison (Amazon URL input) alongside manual spec entry.
Reason: During MVP testing, manual data entry was inconvenient. This would be worse for non-technical users who don’t know headphone specs. Link-based input reduces friction by extracting specs from product URLs.

## 7. Final Architecture Philosophy

The final system reflects three principles:

Deterministic scoring.

Context-aware strategy modeling.

Transparent explanation generation.

The system evolved from a generic comparison tool into a structured decision companion that models contextual trade-offs explicitly.
