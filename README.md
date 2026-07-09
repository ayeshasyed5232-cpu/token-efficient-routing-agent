# Token-Efficient Routing Agent

A simple AI agent that routes each question to a **small/cheap model** or a
**large/powerful model** depending on how complex the question is. This saves
tokens and cost compared to always using a big model.

Built for **AMD Developer Hackathon: ACT II** (Beginner Track), using Fireworks AI.

---

## How it works

1. You type a question.
2. The agent checks: is this simple or complex?
   - Simple (short, direct question) → routed to **gpt-oss-20b** (small model)
   - Complex (long, or contains words like "explain", "why", "compare") → routed to **gpt-oss-120b** (large model)
3. It calls the Fireworks AI API with the chosen model and shows you:
   - The answer
   - Which model was used
   - Tokens used
   - Estimated cost and savings

---

## Example output

```
Your question: What is the capital of France?
[Routed to: SMALL model -> accounts/fireworks/models/gpt-oss-20b]
Answer: The capital of France is Paris.
Tokens used: 126
Estimated cost: $2.5e-05

Your question: Explain how neural networks work in detail
[Routed to: LARGE model -> accounts/fireworks/models/gpt-oss-120b]
Answer: [detailed multi-section explanation...]
Tokens used: 379
Estimated cost: $0.000152
```

---

## Setup Instructions

### 1. Install Python
Download from: https://www.python.org/downloads/
(check "Add Python to PATH" during install)

### 2. Clone this repo and install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Fireworks AI API key as an environment variable
This project reads the API key from an environment variable — it is **never
hardcoded in the code**, so it's safe to share this repo publicly.

- **Windows (PowerShell):**
```
$env:FIREWORKS_API_KEY="your_key_here"
```
- **Mac/Linux:**
```
export FIREWORKS_API_KEY=your_key_here
```

Get your API key from your Fireworks AI dashboard (Settings → API Keys).

### 4. Run it
```bash
python router.py
```

Type a question and press Enter. Type `quit` to exit.

---

## Example test questions

- `What is the capital of France?` → routes to SMALL model
- `Explain how transformers work in deep learning, step by step` → routes to LARGE model
- `Define photosynthesis` → SMALL
- `Compare REST and GraphQL APIs in detail` → LARGE

---

## Why this matters

Large language models cost significantly more per token than smaller ones.
Routing simple queries to a smaller model and reserving the large model for
genuinely complex questions cuts inference costs substantially at scale,
without sacrificing answer quality where it matters.

---

## Tech Stack

- Python
- Fireworks AI (serverless inference — `gpt-oss-20b` and `gpt-oss-120b`)
- `requests` library for API calls

---

## Author

Ayesha Syed — built for AMD Developer Hackathon: ACT II
