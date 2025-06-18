import requests
from typing import Optional, Dict


def searchZipCodeJP(zipcode: str) -> Optional[Dict[str, str]]:
  base = "https://zipcloud.ibsnet.co.jp/api/search"
  params = {"zipcode": zipcode}

  try:
    response = requests.get(base, params=params)
    response.raise_for_status()
    data = response.json()
    
    if data.get("status") == 200 and data.get("results"):
      result_data = data["results"][0]
      result = {
        "address1": result_data["address1"],
        "address2": result_data["address2"],
        "address3": result_data["address3"],
        "kana1": result_data["kana1"],
        "kana2": result_data["kana2"],
        "kana3": result_data["kana3"]
      }
      return result
    
    return None
    
  except requests.exceptions.RequestException as e:
    print(f"Error in zipcode API request: {e}")
    return None
  except (KeyError, IndexError) as e:
    print(f"Error parsing zipcode API response: {e}")