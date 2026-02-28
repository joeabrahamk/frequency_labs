import os
import re
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import sys
from pathlib import Path

# Add backend directory to Python path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from models.headphone import UserRequest, UseCase
from scoring.strategies import get_strategy

# Load environment variables from .env file in backend directory
env_file = backend_dir / ".env"
load_dotenv(env_file)

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

def expand_url(short_url: str) -> str:
    try:
        response = requests.get(short_url, allow_redirects=False, timeout=10)
        location = response.headers.get("Location")
        return location or short_url
    except requests.RequestException:
        return short_url

def extract_asin(input_value: str) -> str:
    if not input_value:
        return ""

    trimmed = input_value.strip()

    if len(trimmed) == 10 and "http" not in trimmed:
        return trimmed

    patterns = [
        r"/dp/([A-Z0-9]{10})",
        r"/gp/product/([A-Z0-9]{10})",
        r"/product/([A-Z0-9]{10})",
    ]

    for pattern in patterns:
        match = re.search(pattern, trimmed, flags=re.IGNORECASE)
        if match:
            return match.group(1)

    return ""

def fetch_html_from_url(url: str) -> Optional[str]:
    """Fetch HTML content from a product URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

def clean_html(html: str) -> str:
    """Clean HTML by removing scripts, styles, and extra whitespace."""
    # Remove script and style tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags but keep text
    html = re.sub(r'<[^>]+>', ' ', html)
    # Remove extra whitespace
    html = re.sub(r'\s+', ' ', html)
    return html.strip()[:10000]  # Limit to first 10k characters

def extract_specs_with_llm(html_content: str, product_url: str, model: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Use OpenRouter LLM to extract headphone specs from HTML content.
    Args:
        html_content: Cleaned HTML text
        product_url: URL for context
        model: Model name (e.g., "openrouter/auto", "mistralai/mistral-small", etc.)
        api_key: OpenRouter API key
    Returns: Dictionary with extracted specs or None on failure
    """
    if not api_key:
        print("No API key provided")
        return None
    
    try:
        prompt = f"""Extract headphone specifications from this product page HTML. Return ONLY a JSON object with these exact fields:
{{
  "name": "product name",
  "price": numeric price in INR (extract from page, convert USD to INR if needed, use 83.0 exchange rate),
  "battery_life": numeric hours (null if not applicable or wired),
  "latency": numeric milliseconds (null if not available),
  "num_mics": numeric count (0 if not mentioned),
  "device_type": one of ["Wireless Earbuds", "Wired Earbuds", "Over-Ear Wireless", "Over-Ear Wired", "Neckband"],
  "water_resistance": string rating like "IPX4" or "IPX5" (use "None" if not found),
  "driver_size": numeric millimeters (null if not available)
}}

Extract ALL available information. Use sensible defaults only when truly unavailable.
Return ONLY valid JSON, no additional text.

HTML Content:
{html_content}

URL: {product_url}
"""
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "https://frequency-labs.com",
                "X-Title": "Frequency Labs",
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,  # Low temperature for structured output
            },
            timeout=30,
        )
        
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            error_msg = result["error"].get("message", str(result["error"]))
            print(f"OpenRouter error: {error_msg}")
            
            if "quota" in error_msg.lower() or "rate" in error_msg.lower():
                raise HTTPException(status_code=429, detail=f"API quota/rate limit: {error_msg}")
            if "auth" in error_msg.lower() or "invalid" in error_msg.lower():
                raise HTTPException(status_code=401, detail=f"API authentication failed: {error_msg}")
            
            return None
        
        # Extract text from response
        if "choices" not in result or not result["choices"]:
            print("No choices in OpenRouter response")
            return None
        
        message = result["choices"][0].get("message", {})
        response_text = message.get("content", "").strip()
        
        if not response_text:
            print("Empty response from OpenRouter")
            return None
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            parsed = json.loads(json_str)
            return parsed
        
        print(f"Could not extract JSON from response: {response_text[:200]}")
        return None
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Error extracting specs: {type(e).__name__}: {str(e)}")
        return None


def parse_number_from_text(text: str) -> Optional[float]:
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    return float(match.group(1))

def parse_price_value(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return parse_number_from_text(cleaned)
    return None

def parse_hours_from_text(text: str) -> Optional[float]:
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)\s*(hour|hours|hr|hrs)", text, flags=re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None

def parse_mic_count(text: str) -> Optional[int]:
    if not text:
        return None
    match = re.search(r"(\d+)\s*(mic|mics|microphone|microphones)", text, flags=re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_from_specifications(specs: List[Dict[str, Any]], name_patterns: List[str]) -> Optional[str]:
    for spec in specs or []:
        name = str(spec.get("name", "")).lower()
        if any(pattern in name for pattern in name_patterns):
            return str(spec.get("value", "")).strip()
    return None


def extract_from_specifications(specs: List[Dict[str, Any]], name_patterns: List[str]) -> Optional[str]:
    """Placeholder for compatibility - not used with LLM extraction."""
    for spec in specs or []:
        name = str(spec.get("name", "")).lower()
        if any(pattern in name for pattern in name_patterns):
            return str(spec.get("value", "")).strip()
    return None

def extract_from_feature_bullets(bullets: List[str], pattern: str) -> Optional[str]:
    """Placeholder for compatibility - not used with LLM extraction."""
    for bullet in bullets or []:
        if re.search(pattern, bullet, flags=re.IGNORECASE):
            return bullet
    return None

def water_resistance_to_float(rating: str) -> float:
    """Convert IPX rating string to numeric score for Headphone model"""
    mapping = {
        'None': 0.0,
        'IPX0': 0.0,
        'IPX1': 0.1,
        'IPX2': 0.2,
        'IPX3': 0.3,
        'IPX4': 0.4,
        'IPX5': 0.5,
        'IPX6': 0.6,
        'IPX7': 0.7,
        'IPX8': 0.8,
        'IPX9': 0.9,
    }
    return mapping.get(rating, 0.4)

def map_llm_response_to_headphone(llm_data: Dict[str, Any]) -> tuple:
    """
    Map LLM extracted data to headphone input format.
    Returns: (headphone_dict, missing_fields_list)
    """
    missing_fields = []
    
    # Extract each field with validation
    name = llm_data.get("name") or "Unknown Headphone"
    
    price = parse_price_value(llm_data.get("price"))
    if price is None or price <= 0:
        price = 5000
        missing_fields.append("price")
    
    battery_life = parse_price_value(llm_data.get("battery_life"))
    if battery_life is None:
        missing_fields.append("battery_life")
    
    latency = parse_price_value(llm_data.get("latency"))
    if latency is None:
        missing_fields.append("latency")
    
    num_mics = int(parse_price_value(llm_data.get("num_mics") or 0))
    if num_mics == 0:
        missing_fields.append("num_mics")
    
    device_type = llm_data.get("device_type") or "Wireless Earbuds"
    
    water_resistance_str = llm_data.get("water_resistance") or "None"
    water_resistance = water_resistance_to_float(water_resistance_str)
    if water_resistance_str == "None":
        missing_fields.append("water_resistance")
    
    driver_size = parse_price_value(llm_data.get("driver_size"))
    if driver_size is None:
        missing_fields.append("driver_size")
    
    return {
        "name": name,
        "price": price,
        "battery_life": battery_life,
        "latency": latency,
        "num_mics": num_mics,
        "device_type": device_type,
        "water_resistance": water_resistance,
        "driver_size": driver_size,
    }, missing_fields

def evaluate_headphones(headphones_data: List[Dict[str, Any]], use_cases: List[UseCase]):
    ranked = []
    for idx, headphone in enumerate(headphones_data):
        use_case_scores = {}
        all_contributions = {}
        final_score = 0

        for use_case in use_cases:
            uc_score, contributions = score_headphone_for_use_case(
                headphone,
                use_case.name
            )

            weighted_score = uc_score * (use_case.percentage / 100)
            final_score += weighted_score

            use_case_scores[use_case.name] = round(uc_score, 3)

            for spec, contrib in contributions.items():
                weighted_contrib = contrib * (use_case.percentage / 100)
                all_contributions[spec] = all_contributions.get(spec, 0) + weighted_contrib

        all_contributions = {k: round(v, 4) for k, v in all_contributions.items()}

        price = headphone.get('price', 1)
        if price is None or price <= 0:
            price = 1
        value_score = (final_score / price) * 10000

        ranked.append({
            "model": headphone.get('name') or f"Headphone {idx + 1}",
            "score": round(final_score, 3),
            "value_score": round(value_score, 3),
            "price": price,
            "contributions": all_contributions,
            "use_case_scores": use_case_scores,
            "details": headphone
        })

    ranked.sort(key=lambda x: x['score'], reverse=True)
    value_ranked = sorted(ranked, key=lambda x: x['value_score'], reverse=True)

    use_case_percentages = [
        f"{uc.name.replace('_', ' ').title()} ({uc.percentage}%)"
        for uc in use_cases
    ]

    return {
        "ranked_headphones": ranked,
        "value_ranked_headphones": value_ranked,
        "explanation": {
            "reasoning": f"Headphones ranked for: {', '.join(use_case_percentages)}. "
                        f"Performance ranking shows best specs for your use cases. "
                        f"Value ranking shows best performance per rupee spent."
        }
    }

# Water resistance rating scores
WATER_RESISTANCE_SCORES = {
    'IPX0': 0.0,
    'IPX1': 0.1,
    'IPX2': 0.2,
    'IPX3': 0.3,
    'IPX4': 0.4,
    'IPX5': 0.5,
    'IPX6': 0.6,
    'IPX7': 0.7,
    'IPX8': 0.8,
    'IPX9': 0.9,
    'None': 0.0,
}

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
        
        # Handle water_resistance (now a float from map_product_to_headphone)
        if spec == 'water_resistance':
            if isinstance(value, str):
                # Fallback: convert string to float if needed
                normalized[spec] = WATER_RESISTANCE_SCORES.get(value, 0.4)
            elif isinstance(value, (int, float)):
                # Value is already a float (0.0-1.0 range), use it directly
                normalized[spec] = float(value)
            else:
                normalized[spec] = 0.5
            continue
        
        # Coerce numeric specs from strings
        if spec in ('price', 'battery_life', 'latency'):
            value = parse_price_value(value)
        if spec == 'num_mics':
            value = int(parse_price_value(value) or 0)
        
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
    
    return score, contributions

@app.post("/evaluate")
async def evaluate(request: UserRequest):
    """
    Evaluate headphones across multiple use cases.
    Each use case is scored independently, then blended by percentage.
    """
    headphones_data = [h.dict() for h in request.headphones]
    return evaluate_headphones(headphones_data, request.use_cases)

class AmazonEvaluateRequest(BaseModel):
    amazon_urls: List[str]
    use_cases: List[UseCase]

@app.post("/evaluate-amazon")
async def evaluate_amazon(request: AmazonEvaluateRequest):
    """
    Evaluate headphones from Amazon/Flipkart URLs using OpenRouter LLM for data extraction.
    """
    llm_api_key = os.getenv("OPENROUTER_API_KEY")
    llm_model = os.getenv("OPENROUTER_MODEL")
    
    if not llm_api_key:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_API_KEY environment variable is not configured."
        )
    
    if not llm_model:
        raise HTTPException(
            status_code=500,
            detail="OPENROUTER_MODEL environment variable is not configured."
        )

    try:
        headphones_data = []
        all_missing = {}
        
        for link in request.amazon_urls:
            # Expand short URLs
            parsed = urlparse(link)
            hostname = (parsed.hostname or "").lower()
            expanded_link = link

            if hostname.startswith("amzn.") or hostname.endswith("amzn.in"):
                expanded_link = expand_url(link)

            # Fetch HTML from the URL
            html_content = fetch_html_from_url(expanded_link)
            if not html_content:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to fetch product page from: {expanded_link}"
                )
            
            # Clean HTML
            cleaned_html = clean_html(html_content)
            
            # Use LLM to extract specs
            llm_data = extract_specs_with_llm(cleaned_html, expanded_link, llm_model, llm_api_key)
            if not llm_data:
                raise HTTPException(
                    status_code=502,
                    detail=f"Failed to extract product data from: {expanded_link}. Please try another product."
                )
            
            # Validate it's a headphone product by checking device_type
            device_type = llm_data.get("device_type", "").lower()
            valid_types = ["wireless earbuds", "wired earbuds", "over-ear", "neckband"]
            if not any(valid_type in device_type for valid_type in valid_types):
                product_name = llm_data.get("name", "Unknown Product")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid item: '{product_name}' is not a headphone product. Please provide a valid headphone/earbud link."
                )
            
            # Map LLM response to headphone format
            headphone_dict, missing_fields = map_llm_response_to_headphone(llm_data)
            headphones_data.append(headphone_dict)
            if missing_fields:
                all_missing[headphone_dict["name"]] = missing_fields

        result = evaluate_headphones(headphones_data, request.use_cases)
        
        if all_missing:
            result["missing_specs"] = all_missing
            result["explanation"]["note"] = (
                f"Some specs were not available and used neutral defaults: "
                f"{', '.join([k + ': ' + ', '.join(v) for k, v in all_missing.items()])}"
            )
        
        return result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/rank_headphones/")
async def rank_headphones(request: UserRequest):
    # Implement ranking logic here
    return {
        "ranked_headphones": [],
        "explanation": {}
    }
