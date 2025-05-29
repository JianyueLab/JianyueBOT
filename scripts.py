# API Scripts for JianyueBot
"""
Collection of API utility functions for various services including
domain registrar search, IP lookup, zipcode search, Minecraft server status,
and BIN checking.
"""

import os
from typing import Dict, Optional, Any

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')
BINCHECK_API_KEY = os.getenv('bincheck_apikey')


def true_false_judgement(data: str) -> Optional[str]:
  """Convert string boolean to emoji representation."""
  if data == 'true':
    return '✅'
  elif data == 'false':
    return '❌'
  else:
    return None


def cheapest(tld: str, order: str) -> Optional[Dict[str, Any]]:
  """
  Find the cheapest domain registrar for a given TLD.
  
  Args:
    tld: Top-level domain (e.g., 'com', 'net')
    order: Order type ('new', 'renew', 'transfer')
    
  Returns:
    Dictionary with registrar pricing information or None if error
  """
  url = "https://www.nazhumi.com/api/v1"
  params = {"domain": tld, "order": order}
  
  try:
    response = requests.get(url, params=params)
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
    
    return None
    
  except requests.exceptions.RequestException as e:
    print(f"Error in cheapest API request: {e}")
    return None
  except (KeyError, IndexError) as e:
    print(f"Error parsing cheapest API response: {e}")
    return None


def registrar_search(registrar: str, order: Any) -> Optional[Dict[str, Any]]:
  """
  Search for domain prices from a specific registrar.
  
  Args:
    registrar: Name of the registrar
    order: Order type (Choice object or string)
    
  Returns:
    Dictionary with domain pricing information or None if error
  """
  url = "https://www.nazhumi.com/api/v1"
  order_value = order.value if hasattr(order, 'value') else str(order)
  params = {"registrar": registrar, "order": order_value}
  
  try:
    response = requests.get(url, params=params)
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


def ipdetails(ipaddress: str) -> Optional[Dict[str, str]]:
  """
  Get detailed information about an IP address.
  
  Args:
    ipaddress: IP address to lookup
    
  Returns:
    Dictionary with IP details or None if error
  """
  url = "https://api.iplocation.net/"
  params = {"ip": ipaddress}
  
  try:
    response = requests.get(url, params=params)
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
  """
  Get geolocation information for an IP address.
  
  Args:
    ipaddress: IP address to lookup
    
  Returns:
    Dictionary with location details or None if error
  """
  url = f"http://ip-api.com/json/{ipaddress}"
  
  try:
    response = requests.get(url)
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


def search_zipcode_jp(zipcode: str) -> Optional[Dict[str, str]]:
  """
  Search Japanese address information by zipcode.
  
  Args:
    zipcode: Japanese postal code
    
  Returns:
    Dictionary with address information or None if error
  """
  url = "https://zipcloud.ibsnet.co.jp/api/search"
  params = {"zipcode": zipcode}
  
  try:
    response = requests.get(url, params=params)
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
    return None


def minecraftServer(server_type: Any, server_ip: str) -> Optional[Dict[str, Any]]:
  """
  Get Minecraft server information.
  
  Args:
    server_type: Server type (Choice object with 'java' or 'bedrock' value)
    server_ip: Server IP address or hostname
    
  Returns:
    Dictionary with server information or None if error
  """
  server_type_value = server_type.value if hasattr(server_type, 'value') else str(server_type)
  
  if server_type_value == 'java':
    url = f"https://api.mcsrvstat.us/3/{server_ip}"
  elif server_type_value == 'bedrock':
    url = f"https://api.mcsrvstat.us/bedrock/3/{server_ip}"
  else:
    return None
  
  try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    if data.get("online"):
      result = {
        "ip": data["ip"],
        "port": data["port"],
        "hostname": data.get("hostname", "N/A"),
        "version": data.get("protocol", {}).get("name", "Unknown"),
        "motd": data.get("motd", {}).get("clean", "N/A"),
        "ping": data.get("debug", {}).get("ping", "N/A"),
        "srv": data.get("debug", {}).get("srv", "N/A"),
        "player": data.get("players", {}).get("online", 0),
        "maxPlayer": data.get("players", {}).get("max", 0)
      }
      return result
    
    return None
    
  except requests.exceptions.RequestException as e:
    print(f"Error in Minecraft server API request: {e}")
    return None
  except KeyError as e:
    print(f"Error parsing Minecraft server API response: {e}")
    return None


def bin_check_request(bin_code: int) -> Optional[Dict[str, Any]]:
  """
  Check BIN (Bank Identification Number) information.
  
  Args:
    bin_code: Bank identification number
    
  Returns:
    Dictionary with card information or None if error
  """
  if not BINCHECK_API_KEY:
    print("BIN check API key not configured")
    return None
  
  url = "https://bin-ip-checker.p.rapidapi.com/"
  payload = {"bin": [bin_code]}
  headers = {
    "x-rapidapi-key": BINCHECK_API_KEY,
    "x-rapidapi-host": "bin-ip-checker.p.rapidapi.com",
    "Content-Type": "application/json"
  }
  
  try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    
    if data.get("code") == 200 and "BIN" in data:
      bin_data = data["BIN"]
      result = {
        "valid": bin_data.get("valid", "Unknown"),
        "brand": bin_data.get("brand", "Unknown"),
        "type": bin_data.get("type", "Unknown"),
        "level": bin_data.get("level", "Unknown"),
        "is_commercial": true_false_judgement(bin_data.get("is_commercial", "")),
        "is_prepaid": true_false_judgement(bin_data.get("is_prepaid", "")),
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
