#!/usr/bin/env python3
"""
Debug Rainforest API calls
"""
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Load env
env_file = backend_dir / ".env"
load_dotenv(env_file)

from api.routes import fetch_from_rainforest

api_key = os.getenv("RAINFOREST_API_KEY")
print(f"API Key loaded: {bool(api_key)}")
if api_key:
    print(f"API Key (first 10 chars): {api_key[:10]}")

# Test with a valid ASIN (popular headphones)
valid_asin = "B0BX5G7GPP"  # Sony WF-C700N
print(f"\nTesting Rainforest API with ASIN: {valid_asin}")

product_data, response = fetch_from_rainforest(api_key, "amazon.in", "product", valid_asin)

if product_data:
    print("✓ Product found!")
    print(f"Product name: {product_data.get('title', 'N/A')[:50]}")
else:
    print("✗ Product not found")
    print(f"Full response: {response}")
