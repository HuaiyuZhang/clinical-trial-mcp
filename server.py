from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import openai
from typing import Dict

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

def parse_natural_language_query(query: str) -> Dict:
    """
    Use OpenAI's GPT API to convert a natural language query into ClinicalTrials.gov API parameters.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set.")
    client = openai.OpenAI(api_key=openai_api_key)
    prompt = (
        "You are an expert in querying the ClinicalTrials.gov API. "
        "Given a user's natural language request, output a Python dictionary of API parameters for the v2 studies endpoint. "
        "Only include relevant parameters.\n"
        "Parameter schema (all are optional, use only those needed):\n"
        "  'query.cond': condition (string),\n"
        "  'query.locn': location (string, e.g. AREA[LocationCountry]United States),\n"
        "  'filter.overallStatus': status (string, e.g. COMPLETED, default: COMPLETED),\n"
        "  'filter.advanced': advanced filter (string, e.g. AREA[Phase](Early_Phase1 OR Phase1)),\n"
        "  'sort': sort field (string, e.g. LastUpdatePostDate, default: LastUpdatePostDate),\n"
        "  'pageSize': number of results (integer, default: 5)\n"
        "Example:\n"
        "User: Show me completed phase 3 diabetes trials in Canada\n"
        "Output: {'query.cond': 'diabetes', 'query.locn': 'AREA[LocationCountry]Canada', 'filter.advanced': 'AREA[Phase](Phase3)', 'sort': 'LastUpdatePostDate', 'pageSize': 5}\n"
        f"User: {query}\nOutput:"
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0
        )
        output = response.choices[0].message.content
        params = eval(output.strip())
        if not isinstance(params, dict):
            raise ValueError("Parsed output is not a dictionary.")
        print(f"\n[Parsed Query Params]: {params}")
        return params
    except Exception as e:
        # Return error instead of fallback parameters
        raise RuntimeError(f"OpenAI parsing query failed: {e}")

@app.post("/query")
def query_trials(request: QueryRequest):
    try:
        params = parse_natural_language_query(request.query)
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            "https://clinicaltrials.gov/api/v2/studies?format=json",
            headers=headers,
            params=params,
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        studies = data.get("studies", [])
        # Return a summary for each study
        results = []
        for s in studies:
            protocol = s.get("protocolSection", {})
            identification = protocol.get("identificationModule", {})
            status = protocol.get("statusModule", {})
            design = protocol.get("designModule", {})
            results.append({
                "nctId": identification.get("nctId"),
                "title": identification.get("officialTitle"),
                "status": status.get("overallStatus"),
                "phase": design.get("phaseList", {}).get("phases"),
            })
        return {
            "parsed_query_params": params,
            "results": results
        }
    except Exception as e:
        return {"error": str(e)} 