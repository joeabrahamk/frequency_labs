# OpenRouter Integration - Setup Guide

## Overview

Replaced Rainforest and Gemini APIs with **OpenRouter** for LLM-based product data extraction. OpenRouter provides:

- ✅ **Unified API** for 100+ models
- ✅ **Flexible pricing** - pay per use
- ✅ **No quotas** - scale as needed
- ✅ **Support for any model** - easily switch between models

## Architecture

```
User provides Amazon/Flipkart Link
    ↓
expand_url() - handle short URLs
    ↓
fetch_html_from_url() - fetch raw HTML
    ↓
clean_html() - remove scripts, styles, extra whitespace
    ↓
extract_specs_with_llm() - send HTML to OpenRouter LLM
    ↓
LLM returns JSON with specs
    ↓
map_llm_response_to_headphone() - convert to internal format
    ↓
Existing scoring system (unchanged)
```

## Setup

### Step 1: Get OpenRouter API Key

1. Visit: https://openrouter.ai
2. Sign up and get your API key from the dashboard
3. Copy the key

### Step 2: Add to .env

Edit `backend/.env`:

```
OPENROUTER_API_KEY=your_actual_api_key_here
OPENROUTER_MODEL=openrouter/auto
```

**Model options:**

- `openrouter/auto` - Auto-selects best available model (recommended for starting)
- `mistralai/mistral-small` - Fast and cheap
- `mistralai/mistral-large` - Faster than small
- `anthropic/claude-3.5-sonnet` - Highest quality but more expensive
- `meta-llama/llama-3.1-70b-instruct` - Good balance
- `google/gemini-pro` - Google's model via OpenRouter
- `openai/gpt-4-turbo` - OpenAI's GPT-4 via OpenRouter

See full list: https://openrouter.ai/docs/models

### Step 3: Test

```bash
cd backend
python -m uvicorn api.routes:app --reload
```

In another terminal:

```bash
curl -X POST http://localhost:8000/evaluate-amazon \
  -H "Content-Type: application/json" \
  -d '{
    "amazon_urls": ["https://www.amazon.in/dp/B0DFWXCZ5Z"],
    "use_cases": [{"name": "music_listening", "percentage": 100}]
  }'
```

## Configuration Examples

### Example 1: Cost-optimized (Fast & Cheap)

```env
OPENROUTER_API_KEY=sk-xxx...
OPENROUTER_MODEL=mistralai/mistral-small
```

**Cost**: ~$0.000070 per request
**Speed**: ~1-2 seconds per product
**Quality**: Good for structured extraction

### Example 2: Balanced (Recommended)

```env
OPENROUTER_API_KEY=sk-xxx...
OPENROUTER_MODEL=openrouter/auto
```

**Cost**: Varies by available models
**Speed**: ~2-3 seconds per product
**Quality**: OpenRouter picks the best value

### Example 3: High Quality

```env
OPENROUTER_API_KEY=sk-xxx...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
```

**Cost**: ~$0.005-0.01 per request
**Speed**: ~3-5 seconds per product
**Quality**: Excellent accuracy

## How It Works

1. **Fetch HTML** - Downloads page using User-Agent headers
2. **Clean HTML** - Removes scripts, styles, limits to 10k chars
3. **Send to OpenRouter** - Uses specified LLM to extract specs
4. **Parse JSON** - Extracts structured data from LLM response
5. **Validate** - Checks it's a headphone product
6. **Score** - Runs through existing scoring system

## Error Handling

| Error                             | Cause                 | Solution                |
| --------------------------------- | --------------------- | ----------------------- |
| OPENROUTER_API_KEY not configured | Missing env var       | Add to .env             |
| OPENROUTER_MODEL not configured   | Missing env var       | Add to .env             |
| Failed to fetch product page      | Network issue         | Check URL is accessible |
| Failed to extract product data    | LLM couldn't parse    | Try different product   |
| Not a headphone product           | Wrong product type    | Use headphone link      |
| 429 - Quota exceeded              | OpenRouter rate limit | Wait or upgrade plan    |
| 401 - Invalid auth                | Bad API key           | Verify key in .env      |

## Pricing

**OpenRouter Pricing:**

- No setup fee
- Pay per token (input + output)
- Different models cost differently
- Can set monthly budget limits

**Estimated costs per product:**

- Mistral Small: $0.00007 (0.07¢)
- Mistral Large: $0.0002 (0.2¢)
- Claude 3.5 Sonnet: $0.003 (0.3¢)
- GPT-4: $0.003 (0.3¢)

**For 100 products:**

- Mistral Small: $0.007 (less than 1¢)
- Claude 3.5 Sonnet: $0.30
- GPT-4: $0.30

## Switching Models

To switch models at runtime, just update `OPENROUTER_MODEL` in `.env` and restart the backend:

```bash
# Stop current server (Ctrl+C)

# Update .env
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Restart
python -m uvicorn api.routes:app --reload
```

## Status

✅ Routes updated for OpenRouter  
✅ Rainforest functions removed  
✅ Gemini code removed  
✅ LLM extraction implemented  
✅ Ready for testing

## Next Steps

1. Get OpenRouter API key
2. Add key + model to `.env`
3. Start backend
4. Test with sample products
5. Adjust model based on needs

## Support

- OpenRouter Docs: https://openrouter.ai/docs
- Available Models: https://openrouter.ai/docs/models
- Issues: Check OpenRouter dashboard for quota/billing
