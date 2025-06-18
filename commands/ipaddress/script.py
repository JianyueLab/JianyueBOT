import requests
from typing import Optional, Dict


def ipdetails(ipaddress: str) -> Optional[Dict[str, str]]:
  base = "https://api.iplocation.net/"
  params = {"ip": ipaddress}
  
  try:
    response = requests.get(base, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get("response_code") == '200':
      result = {
        "ip": data["ip"],
        "ip_number": data["ip_number"],
        "ip_version": data["ip_version"],
        "country_name": data["country_name"],
        "country_code2": data["country_code2"],
        "isp": data["isp"],
        "response_code": data["response_code"],
        "response_message": data["response_message"]
      }
      return result
    
    return None
    
  except requests.exceptions.RequestException as e:
    print(f"Error in IP details API request: {e}")
    return None
  except KeyError as e:
    print(f"Error parsing IP details API response: {e}")
    return None
  
def iplocations(ipaddress: str) -> Optional[Dict[str, str]]:
  base = f"http://ip-api.com/json/{ipaddress}"
  
  try:
    response = requests.get(base)
    response.raise_for_status()
    data = response.json()
    
    if data.get("status") == "success":
      result = {
        "query": data["query"],
        "country": data["country"],
        "city": data["city"],
        "zip": data.get("zip", "N/A"),
        "isp": data["isp"],
        "org": data["org"],
        "timezone": data["timezone"],
        "as": data["as"]
      }
      return result
    
    return None
    
  except requests.exceptions.RequestException as e:
    print(f"Error in IP location API request: {e}")
    return None
  except KeyError as e:
    print(f"Error parsing IP location API response: {e}")
    return None
  
