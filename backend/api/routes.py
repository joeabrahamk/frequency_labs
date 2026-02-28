import os
import re
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

def fetch_from_rainforest(api_key: str, domain: str, request_type: str, value: str):
    endpoint = "https://api.rainforestapi.com/request"
    params = {
        "api_key": api_key,
        "type": request_type,
        "amazon_domain": domain,
    }

    if request_type == "product":
        params["asin"] = value
    else:
        params["search_term"] = value

    try:
        response = requests.get(endpoint, params=params, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Rainforest API Error: {e}")
        status_code = None
        body = None
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            body = e.response.text
            print(f"Status: {status_code}, Body: {body}")

        message = "Rainforest API request failed"
        if status_code == 402:
            message = (
                "Rainforest API account is suspended or requires a paid plan. "
                "Please resolve billing/account status in Rainforest dashboard."
            )
        elif status_code:
            message = f"Rainforest API returned status {status_code}"

        return None, None, {
            "status_code": status_code or 502,
            "message": message,
            "body": body,
        }

    result = response.json()

    if request_type == "product":
        return result.get("product"), result, None

    return result.get("search_results"), result, None

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

def extract_from_feature_bullets(bullets: List[str], pattern: str) -> Optional[str]:
    for bullet in bullets or []:
        if re.search(pattern, bullet, flags=re.IGNORECASE):
            return bullet
    return None

def detect_device_type(product: Dict[str, Any]) -> str:
    categories = [c.get("name", "").lower() for c in product.get("categories", [])]
    specs = product.get("specifications", [])
    form_factor = extract_from_specifications(specs, ["form factor", "ear placement", "earpiece shape"]) or ""
    connectivity = extract_from_specifications(specs, ["connectivity", "wireless communication"]) or ""
    jack = extract_from_specifications(specs, ["headphones jack"]) or ""

    is_in_ear = any("in-ear" in c for c in categories) or "in ear" in form_factor.lower()
    is_over_ear = any("over-ear" in c for c in categories) or "over ear" in form_factor.lower()
    is_neckband = any("neckband" in c for c in categories)

    is_wireless = "bluetooth" in connectivity.lower() or "wireless" in connectivity.lower() or "no jack" in jack.lower()

    if is_neckband:
        return "Neckband"
    if is_over_ear and is_wireless:
        return "Over-Ear Wireless"
    if is_over_ear:
        return "Over-Ear Wired"
    if is_in_ear and is_wireless:
        return "Wireless Earbuds"
    if is_in_ear:
        return "Wired Earbuds"
    return "Wireless Earbuds" if is_wireless else "Wired Earbuds"

def is_headphone_product(product: Dict[str, Any]) -> bool:
    """Check if product is headphone-related."""
    if not product:
        return False
    
    # Check categories
    categories = product.get("categories", [])
    category_names = [c.get("name", "").lower() for c in categories]
    headphone_keywords = ["headphone", "earbud", "earphone", "audio", "wireless earbuds", "in-ear", "over-ear", "neckband", "tws"]
    
    if any(keyword in " ".join(category_names) for keyword in headphone_keywords):
        return True
    
    # Check title
    title = (product.get("title") or "").lower()
    if any(keyword in title for keyword in headphone_keywords):
        return True
    
    # Check keywords
    keywords = product.get("keywords_list", [])
    keywords_str = " ".join([k.lower() for k in keywords])
    if any(keyword in keywords_str for keyword in headphone_keywords):
        return True
    
    return False

def map_water_resistance(value: str) -> str:
    if not value:
        return "None"
    upper = value.upper()
    match = re.search(r"IPX\d", upper)
    if match:
        return match.group(0)
    if "WATER RESISTANT" in upper or "WATERPROOF" in upper:
        return "IPX4"
    return "None"

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

def convert_price_to_inr(price_value: Optional[float], currency: str = "INR") -> float:
    """Convert price to INR if in USD."""
    price_value = parse_price_value(price_value)
    if price_value is None or price_value <= 0:
        return 0
    usd_to_inr = 83.0
    if currency and currency.upper() in ["USD", "$"]:
        return price_value * usd_to_inr
    return price_value

def map_product_to_headphone(product: Dict[str, Any]) -> tuple:
    """
    Map Rainforest API product data to headphone input format.
    Returns: (headphone_dict, missing_fields_list)
    """
    specs = product.get("specifications", [])
    bullets = product.get("feature_bullets", [])
    missing_fields = []

    battery_text = extract_from_specifications(specs, ["battery life", "playback", "battery"]) or ""
    if not battery_text:
        battery_text = extract_from_feature_bullets(bullets, r"(\d+\s*(hour|hr|hrs|hours))") or ""
    battery_life = parse_hours_from_text(battery_text)
    if battery_life is None:
        missing_fields.append("battery_life")

    driver_text = extract_from_specifications(specs, ["driver"]) or ""
    if not driver_text:
        driver_text = extract_from_feature_bullets(bullets, r"(\d+\s*mm)") or ""
    driver_size = parse_number_from_text(driver_text) if "mm" in driver_text.lower() else None
    if driver_size is None:
        missing_fields.append("driver_size")

    mic_text = extract_from_feature_bullets(bullets, r"mic|microphone") or ""
    if not mic_text:
        mic_text = extract_from_specifications(specs, ["mic", "microphone"]) or ""
    num_mics = parse_mic_count(mic_text) or 0
    if num_mics == 0:
        missing_fields.append("num_mics")

    water_text = extract_from_specifications(specs, ["water resistance", "water resistant"]) or ""
    water_resistance = map_water_resistance(water_text)
    if water_resistance == "None":
        water_resistance = "IPX4"
        missing_fields.append("water_resistance")

    price_value = None
    price_currency = "INR"
    buybox = product.get("buybox_winner", {}) or {}
    price_obj = (buybox.get("price", {}) or {})
    price_value = parse_price_value(price_obj.get("value"))
    price_currency = price_obj.get("currency", "INR") or "INR"
    
    if price_value is None:
        price_obj = (product.get("price", {}) or {})
        price_value = parse_price_value(price_obj.get("value"))
        price_currency = price_obj.get("currency", "INR") or "INR"
    
    price_value = convert_price_to_inr(price_value, price_currency)
    if price_value is None or price_value == 0:
        missing_fields.append("price")
        price_value = 5000

    missing_fields.append("latency")

    return {
        "name": product.get("title") or product.get("brand") or "Amazon Product",
        "price": price_value,
        "battery_life": battery_life,
        "latency": None,
        "num_mics": num_mics,
        "device_type": detect_device_type(product),
        "water_resistance": water_resistance_to_float(water_resistance),
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
    Evaluate headphones from Amazon URLs.
    """
    api_key = os.getenv("RAINFOREST_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="RAINFOREST_API_KEY environment variable is not configured. Please set it to use Amazon URL evaluation."
        )

    try:
        headphones_data = []
        all_missing = {}
        
        for link in request.amazon_urls:
            parsed = urlparse(link)
            hostname = (parsed.hostname or "").lower()
            expanded_link = link

            if hostname.startswith("amzn.") or hostname.endswith("amzn.in"):
                expanded_link = expand_url(link)

            asin = extract_asin(expanded_link)
            if not asin:
                raise HTTPException(status_code=400, detail=f"Invalid Amazon URL: {link}")

            domain = "amazon.in"
            if "amazon.com" in expanded_link:
                domain = "amazon.com"

            product_data, _, product_error = fetch_from_rainforest(api_key, domain, "product", asin)
            search_error = None

            if product_data is None and product_error and product_error.get("status_code") == 402:
                raise HTTPException(status_code=503, detail=product_error.get("message"))

            if product_data is None:
                search_data, _, search_error = fetch_from_rainforest(api_key, domain, "search", asin)
                if isinstance(search_data, list) and len(search_data) > 0:
                    product_data = search_data[0]

            if product_data is None:
                if search_error and search_error.get("status_code") == 402:
                    raise HTTPException(status_code=503, detail=search_error.get("message"))
                if product_error and product_error.get("status_code") not in (None, 404):
                    raise HTTPException(status_code=502, detail=product_error.get("message"))
                if search_error and search_error.get("status_code") not in (None, 404):
                    raise HTTPException(status_code=502, detail=search_error.get("message"))
                raise HTTPException(status_code=404, detail=f"Product not found for ASIN {asin}")

            # Validate that product is headphone-related
            if not is_headphone_product(product_data):
                product_name = product_data.get("title", "Unknown Product")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid item: '{product_name}' is not a headphone product. Please provide a valid headphone/earbud link."
                )

            headphone_dict, missing_fields = map_product_to_headphone(product_data)
            headphones_data.append(headphone_dict)
            if missing_fields:
                all_missing[headphone_dict["name"]] = missing_fields

        result = evaluate_headphones(headphones_data, request.use_cases)
        
        if all_missing:
            result["missing_specs"] = all_missing
            result["explanation"]["note"] = (
                f"Some specs were not available from Amazon and used neutral defaults: "
                f"{', '.join([k + ': ' + ', '.join(v) for k, v in all_missing.items()])}"
            )
        
        return result

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/product")
async def get_product(link: str | None = None, asin: str | None = None):
    api_key = os.getenv("RAINFOREST_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="RAINFOREST_API_KEY is not configured")

    if not asin and link:
        parsed = urlparse(link)
        hostname = (parsed.hostname or "").lower()

        if hostname.startswith("amzn.") or hostname.endswith("amzn.in"):
            link = expand_url(link)

        asin = extract_asin(link)

    if not asin:
        raise HTTPException(status_code=400, detail="Provide valid ASIN or product link")

    domain = "amazon.in"
    if link and "amazon.com" in link:
        domain = "amazon.com"

    product_data, full_response, product_error = fetch_from_rainforest(api_key, domain, "product", asin)

    if product_data is None:
        if product_error and product_error.get("status_code") == 402:
            raise HTTPException(status_code=503, detail=product_error.get("message"))

        search_data, _, search_error = fetch_from_rainforest(api_key, domain, "search", asin)

        if isinstance(search_data, list) and len(search_data) > 0:
            return {
                "asin": asin,
                "source": "search_fallback",
                "product": search_data[0],
            }

        if search_error and search_error.get("status_code") == 402:
            raise HTTPException(status_code=503, detail=search_error.get("message"))

        return {
            "asin": asin,
            "error": "Product not found",
            "raw": full_response,
        }

    return {
        "asin": asin,
        "source": "product_endpoint",
        "product": product_data,
    }

@app.post("/rank_headphones/")
async def rank_headphones(request: UserRequest):
    # Implement ranking logic here
    return {
        "ranked_headphones": [],
        "explanation": {}
    }
