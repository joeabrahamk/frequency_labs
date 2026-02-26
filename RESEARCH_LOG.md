# Research Log

## AI Prompts Used

### Prompt 1 – Backend Architecture

"I am building a Decision Companion System for selecting the best headphones based on user use cases and specifications.

The system must be deterministic and explainable.

Tech stack:

React frontend

Python FastAPI backend

Each headphone must include:

price

device_type (Wired Earbuds, Wireless Earbuds, Over-Ear Wired, Over-Ear Wireless, Neckband)

battery_life_hours

latency_ms

driver_size_mm

mic_quality (Poor, Average, Good, Excellent)

mic_count

anc_type (None, Passive, Active, Hybrid, Adaptive)

anc_effectiveness (None, Low, Medium, High, Very High)

water_resistance (None, IPX4, IPX5, IPX7)

comfort_score (Poor, Average, Good, Excellent)

sound_signature (Bass-heavy, Neutral, Bright, V-shaped, Balanced)

Use cases:

gaming

gym

work_calls

travel

casual_music

Each use case must define different scoring priorities.

System must:

Normalize numeric specs

Handle cost-type criteria like price

Score per use case

Blend scores if multiple use cases selected

Return ranked list

Return per-criterion contribution breakdown

Ask me doubts for better result"

### Prompt 2 – Different Scoring Per Use Case

"I want different scoring styles in different use cases.

If gaming prioritize:
latency, wired, mic count, ANC, driver size, battery life.

If gym prioritize:
water resistance, ANC and wireless.

If work call prioritize:
latency and mic count.

If travel prioritize:
battery life, driver size, wireless, mic, ANC and water resistance.

If casual music prioritize:
battery life and price.

Suggest structured strategy-based scoring design.

Ask me doubts for better result"

### Prompt 3 – Frontend Generation

"Generate the React frontend for the Decision Companion System.

Design must be minimal like apple.com.

Allow selecting use cases:

gaming

gym

work_calls

travel

casual_music

Headphone inputs:

Numeric:

Price

Battery life (hours)

Latency (ms)

Driver size (mm)

Dropdown:

Device Type (Wired Earbuds, Wireless Earbuds, Over-Ear Wired, Over-Ear Wireless, Neckband)

ANC Type (None, Passive, Active, Hybrid, Adaptive)

ANC Effectiveness (None, Low, Medium, High, Very High)

Mic Quality (Poor, Average, Good, Excellent)

Water Resistance (None, IPX4, IPX5, IPX7)

Comfort Score (Poor, Average, Good, Excellent)

Sound Signature (Bass-heavy, Neutral, Bright, V-shaped, Balanced)

UI must:

Be minimal

Use dropdowns

Show ranked results

Show contribution breakdown

Ask me doubts for better result"

### Prompt 4 – Hosting and Framework Decision

"What is your opinion on migrating from FastAPI to Flask since I have issue hosting backend? Should I switch framework or change hosting provider?

Ask me doubts for better result"

### Prompt 5 – Value Score Addition

"I want to include a final value_score in the response which represents overall suitability of the headphone based on selected use cases.

The backend must:

Compute deterministic value_score

Keep scoring transparent

Return contribution breakdown per criterion

Keep logic modular

Suggest how to integrate value_score cleanly into scoring engine.

Ask me doubts for better result"

## Google Search Queries

- multi criteria decision analysis weighted sum model
- normalization formula for scoring system
- min max normalization example
- cost criteria normalization
- latency ms good for gaming
- IPX rating meaning
- difference between active and passive noise cancellation
- driver size effect on sound
- does mic count affect call quality
- fastapi vs flask comparison
- deploy fastapi render
- minimal ui inspiration website
- apple website layout inspiration
- Design for details card Pinterest
- Driver size in over ear headphones vs earbuds

## References Checked

- FastAPI official documentation
- Pydantic validation documentation
- React documentation
- TailwindCSS documentation
- Articles explaining IPX ratings
- Headphone reviews discussing latency for gaming
- Manufacturer specification sheets for headphones
- Pinterest Designs

## Accepted From AI Outputs

- Strategy-based scoring per use case
- Separate normalization layer
- Independent use case scoring before blending
- Contribution breakdown logic
- Modular backend structure

## Rejected From AI Outputs

- AI-based ranking logic
- Black-box scoring methods
- Excessive multiplier stacking
- Overengineered microservice architecture
- Database integration for MVP

## Modified During Development

- Altered UI
- Initially merged weight tables before scoring; changed to independent strategy scoring per use case.
- Initially treated ANC type as strength; separated ANC type and ANC effectiveness.
- Initially tied mic quality directly to mic count; separated them.
- Simplified scoring adjustments to prevent unstable outputs.
- Added value_score after core logic stabilized.
- Added link-based comparison (Amazon URL input) to reduce manual spec entry friction during MVP testing.
