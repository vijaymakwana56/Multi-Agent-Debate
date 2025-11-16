import re
import json

def extract_json(text: str):
    """Extract the first valid JSON object from an LLM response."""
    match = re.search(r"\{[\s\S]*?\}", text)
    if not match:
        return None
    
    try:
        return json.loads(match.group())
    except:
        return None
