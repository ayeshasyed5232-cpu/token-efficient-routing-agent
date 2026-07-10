"""
Token-Efficient Routing Agent — Streamlit Web App
---------------------------------------------------
Web interface for the routing agent. Deployed on Streamlit Community Cloud.

Built for: AMD Developer Hackathon: ACT II
Author: Ayesha Syed
"""

import os
import streamlit as st
import requests

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
API_KEY = os.getenv("FIREWORKS_API_KEY") or st.secrets.get("FIREWORKS_API_KEY", "")

SMALL_MODEL = "accounts/fireworks/models/gpt-oss-20b"
LARGE_MODEL = "accounts/fireworks/models/gpt-oss-120b"
FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"

SMALL_MODEL_COST_PER_1K = 0.0002
LARGE_MODEL_COST_PER_1K = 0.0004

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
    response.raise_for_status()
    data = response.json()

    answer = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    total_tokens = usage.get("total_tokens", 0)

    cost_per_1k = LARGE_MODEL_COST_PER_1K if complex_query else SMALL_MODEL_COST_PER_1K
    estimated_cost = (total_tokens / 1000) * cost_per_1k
    baseline_cost = (total_tokens / 1000) * LARGE_MODEL_COST_PER_1K
    savings = baseline_cost - estimated_cost

    return {
        "model_used": "LARGE" if complex_query else "SMALL",
        "model_name": model,
        "answer": answer,
        "tokens_used": total_tokens,
        "estimated_cost": round(estimated_cost, 6),
        "estimated_savings": round(savings, 6),
    }


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.set_page_config(page_title="Token-Efficient Routing Agent", page_icon="🔀")

st.title("Token-Efficient Routing Agent")
st.caption("Built for AMD Developer Hackathon: ACT II — routes queries to a small or large model based on complexity.")

if not API_KEY:
    st.warning("No FIREWORKS_API_KEY found. Add it in Streamlit secrets to enable live responses.")

query = st.text_input("Ask a question:", placeholder="e.g. What is the capital of France?")

if st.button("Submit") and query:
    if not API_KEY:
        st.error("API key not configured. This demo cannot call Fireworks AI without it.")
    else:
        with st.spinner("Routing your query..."):
            try:
                result = route_query(query)
                badge_color = "blue" if result["model_used"] == "SMALL" else "violet"
                st.markdown(f"**Routed to:** :{badge_color}[{result['model_used']} model — {result['model_name']}]")
                st.write(result["answer"])
                col1, col2, col3 = st.columns(3)
                col1.metric("Tokens used", result["tokens_used"])
                col2.metric("Estimated cost", f"${result['estimated_cost']}")
                col3.metric("Savings vs always-large", f"${result['estimated_savings']}")
            except Exception as e:
                st.error(f"Error: {e}")

st.divider()
st.caption("Simple queries route to gpt-oss-20b (small/fast). Complex queries (long, or containing words like "
           "\"explain\", \"compare\", \"analyze\") route to gpt-oss-120b (large/powerful).")
