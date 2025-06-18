import requests
from typing import Optional, Dict, Any


def cheapest(tld: str, order: str) -> Optional[Dict[str, Any]]:
  base = "https://www.nazhumi.com/api/v1"
  params = {"domain": tld, "order": order}

  try:
    response = requests.get(base, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get("code") == 100 and "data" in data and "price" in data["data"]:
      prices = data["data"]["price"]
      if len(prices) >= 5:
        result = {
          "domain": data["data"]["domain"],
          "order": data["data"]["order"]
        }
        
        # Add pricing data for top 5 registrars
        for i in range(5):
          num = ["1st", "2nd", "3rd", "4th", "5th"][i]
          price_data = prices[i]
          result.update({
            f"reg_{num}": price_data["registrar"],
            f"new_{num}": price_data["new"],
            f"renew_{num}": price_data["renew"],
            f"transfer_{num}": price_data["transfer"],
            f"currency_{num}": price_data["currency"],
            f"reg_web_{num}": price_data["registrarweb"]
          })
        return result
      else:
        return None
    else:
      return None
  except requests.exceptions.RequestException as e:
    print(f"Error in cheapest API request: {e}")
    return None
  except (KeyError, IndexError) as e:
    print(f"Error parsing cheapest API response: {e}")
    
def registrarSearch(registrar: str, order: str) -> Optional[Dict[str, Any]]:
  base = "https://www.nazhumi.com/api/v1"
  params = {"registrar": registrar, "order": order}

  try:
    response = requests.get(base, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get("code") == 100 and "data" in data and "price" in data["data"]:
      prices = data["data"]["price"]
      if len(prices) >= 5:
        result = {
          "reg": data["data"]["registrar"],
          "order": data["data"]["order"],
          "reg_web": data["data"]["registrarweb"]
        }
        
        # Add domain pricing data for top 5 results
        for i in range(5):
          num = ["1st", "2nd", "3rd", "4th", "5th"][i]
          price_data = prices[i]
          result.update({
            f"domain_{num}": price_data["domain"],
            f"new_{num}": price_data["new"],
            f"renew_{num}": price_data["renew"],
            f"transfer_{num}": price_data["transfer"],
            f"currency_{num}": price_data["currency"]
          })
        
        return result
    
    return None
    
  except requests.exceptions.RequestException as e:
    print(f"Error in registrar search API request: {e}")
    return None
  except (KeyError, IndexError) as e:
    print(f"Error parsing registrar search API response: {e}")
    return None