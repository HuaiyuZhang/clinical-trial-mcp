# MCP Server for ClinicalTrials.gov Natural Language API

This MCP (Model Control Protocol) server allows you to query ClinicalTrials.gov using natural language. It uses OpenAI's GPT models to translate your query into API parameters and returns structured results.

## Features
- Accepts natural language queries (e.g., "Show me completed phase 3 diabetes trials in Canada")
- Uses OpenAI API to parse and map to ClinicalTrials.gov API parameters
- Returns both the parsed parameters and the results

## Requirements
- Python 3.8+
- Dependencies in `requirements.txt`
- OpenAI API key (set as `OPENAI_API_KEY` environment variable)

## Running the Server

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Set your OpenAI API key:
   ```sh
   export OPENAI_API_KEY=sk-...
   ```
3. Start the server:
   ```sh
   uvicorn server:app --reload
   ```

## Usage

### cURL Example
```sh
curl -X POST "http://127.0.0.1:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "Show me completed phase 3 diabetes trials in Canada"}'
```

### Python Example
```python
import requests

query = "Show me completed phase 3 diabetes trials in Canada"
response = requests.post(
    "http://127.0.0.1:8000/query",
    json={"query": query}
)
print(response.json())
```

## What is MCP?
MCP (Model Control Protocol) is a pattern for building AI-driven APIs that act as a control layer between natural language and structured APIs. This server uses an LLM to interpret user intent and map it to API calls, making complex data accessible via plain language.

## Customization
- You can modify the prompt or add more parameter schema in `server.py` to support more query types or APIs.

---
For questions or improvements, open an issue or PR!
