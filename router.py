"""
Token-Efficient Routing Agent
------------------------------
Simple AI agent that routes queries to a small/cheap model or a large/powerful
model depending on how complex the query looks. This saves tokens and cost.

Built for: AMD Developer Hackathon: ACT II (Beginner Track)
Author: Ayesha Syed
"""

import os
import sys
import requests

# ---------------------------------------------------------
# 1. CONFIG - API key is read from an environment variable
#    (never hardcode API keys in code you upload to GitHub!)
# ---------------------------------------------------------
API_KEY = os.getenv("FIREWORKS_API_KEY")

if not API_KEY:
    print("ERROR: FIREWORKS_API_KEY environment variable is not set.")
    print("Set it before running this script, for example:")
    print('  Windows (PowerShell): $env:FIREWORKS_API_KEY="your_key_here"')
    print("  Mac/Linux:            export FIREWORKS_API_KEY=your_key_here")
    sys.exit(1)

SMALL_MODEL = "accounts/fireworks/models/gpt-oss-20b"    # cheap/fast model
LARGE_MODEL = "accounts/fireworks/models/gpt-oss-120b"    # powerful model

FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

# Real Fireworks serverless pricing (per 1K tokens, blended input+output estimate)
SMALL_MODEL_COST_PER_1K = 0.0002   # gpt-oss-20b: ~$0.07 in / $0.30 out per 1M
LARGE_MODEL_COST_PER_1K = 0.0004   # gpt-oss-120b: ~$0.15 in / $0.60 out per 1M


# ---------------------------------------------------------
# 2. LOGIC - decide if a query is "simple" or "complex"
# ---------------------------------------------------------
COMPLEX_KEYWORDS = [
    "explain", "why", "analyze", "compare", "how does",
    "design", "architecture", "step by step", "in detail",
    "pros and cons", "difference between"
]

def is_complex(query: str) -> bool:
    word_count = len(query.split())
    lower_query = query.lower()

    if word_count > 15:
        return True
    if any(keyword in lower_query for keyword in COMPLEX_KEYWORDS):
        return True
    return False


# ---------------------------------------------------------
# 3. ROUTING - call Fireworks AI with the chosen model
# ---------------------------------------------------------
def route_query(query: str):
    complex_query = is_complex(query)
    model = LARGE_MODEL if complex_query else SMALL_MODEL

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 300
    }

    response = requests.post(FIREWORKS_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"\nFull error details: {response.status_code} - {response.text}")
    response.raise_for_status()
    data = response.json()

    answer = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    total_tokens = usage.get("total_tokens", 0)

    cost_per_1k = LARGE_MODEL_COST_PER_1K if complex_query else SMALL_MODEL_COST_PER_1K
    estimated_cost = (total_tokens / 1000) * cost_per_1k

    # Estimate what it WOULD have cost if we always used the large model
    baseline_cost = (total_tokens / 1000) * LARGE_MODEL_COST_PER_1K
    savings = baseline_cost - estimated_cost

    return {
        "query": query,
        "model_used": "LARGE" if complex_query else "SMALL",
        "model_name": model,
        "answer": answer,
        "tokens_used": total_tokens,
        "estimated_cost": round(estimated_cost, 6),
        "estimated_savings": round(savings, 6)
    }


# ---------------------------------------------------------
# 4. RUN - simple command line loop for testing
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print(" Token-Efficient Routing Agent")
    print(" Type 'quit' to exit")
    print("=" * 50)

    while True:
        user_query = input("\nYour question: ").strip()
        if user_query.lower() in ("quit", "exit"):
            break
        if not user_query:
            continue

        try:
            result = route_query(user_query)
            print(f"\n[Routed to: {result['model_used']} model -> {result['model_name']}]")
            print(f"Answer: {result['answer']}")
            print(f"Tokens used: {result['tokens_used']}")
            print(f"Estimated cost: ${result['estimated_cost']}")
            print(f"Estimated savings vs always-large-model: ${result['estimated_savings']}")
        except Exception as e:
            print(f"Error: {e}")
