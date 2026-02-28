#!/usr/bin/env python3
"""
Test script for /evaluate-amazon endpoint
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from api.routes import app, AmazonEvaluateRequest
from fastapi.testclient import TestClient

client = TestClient(app)

# Test data
payload = {
    "amazon_urls": ["https://www.amazon.in/dp/B0BYR2KZ1M"],
    "use_cases": [
        {"name": "gaming", "percentage": 100}
    ]
}

print("Testing /evaluate-amazon endpoint...")
print(f"Payload: {payload}")
print()

response = client.post("/evaluate-amazon", json=payload)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")  # Print first 500 chars

if response.status_code != 200:
    print(f"\nERROR: Expected 200, got {response.status_code}")
else:
    print(f"\nSUCCESS: Endpoint responded correctly")
