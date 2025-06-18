import requests
from typing import Optional, Dict, Any


def minecraftServer(server_type: Any, server_ip: str) -> Optional[Dict[str, Any]]:
  server_type_value = server_type.value if hasattr(server_type, 'value') else str(server_type)
  
  if server_type_value == 'java':
    base = f"https://api.mcsrvstat.us/3/{server_ip}"
  elif server_type_value == 'bedrock':
    base = f"https://api.mcsrvstat.us/bedrock/3/{server_ip}"
  else:
    return None
  
  try:
    response = requests.get(base)
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