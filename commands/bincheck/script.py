import requests
from typing import Optional, Dict, Any
from ..utils import *


def binCheckRequest(bin_code: int) -> Optional[Dict[str, Any]]:
  if not BINCHECK_API_KEY:
    print("BIN check API key not configured")
    return None
  
  base = "https://bin-ip-checker.p.rapidapi.com/"
  payload = {"  bin": [bin_code]}
  headers = {
    "x-rapidapi-key": BINCHECK_API_KEY,
    "x-rapidapi-host": "bin-ip-checker.p.rapidapi.com",
    "Content-Type": "application/json"
  }
  
  try:
    response = requests.post(base, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    if data.get("code") == 200 and "BIN" in data:
      bin_data = data["BIN"]
      result = {
        "valid": bin_data.get("valid", "Unknown"),
        "brand": bin_data.get("brand", "Unknown"),
        "type": bin_data.get("type", "Unknown"),
        "level": bin_data.get("level", "Unknown"),
        "is_commercial": trueFalseJudgement(bin_data.get("is_commercial", "")),
        "is_prepaid": trueFalseJudgement(bin_data.get("is_prepaid", "")),
        "currency": bin_data.get("currency", "Unknown"),
        "issuer": bin_data.get("issuer", {}).get("name", "Unknown"),
        "country": bin_data.get("country", {}).get("name", "Unknown"),
        "flag": bin_data.get("country", {}).get("flag", "")
      }
      return result
    
    return None
    
  except requests.exceptions.RequestException as e:
    print(f"Error in BIN check API request: {e}")
    return None
  except KeyError as e:
    print(f"Error parsing BIN check API response: {e}")
    return None
