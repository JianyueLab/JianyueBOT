from dotenv import load_dotenv
from commands.utils import *
from cloudflare import Cloudflare
from typing import Optional, Dict, Any

load_dotenv('.env')

CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')

client = Cloudflare(
    api_token=CLOUDFLARE_API_TOKEN
)

def checkWhois(domain: str) -> Optional[Dict[str, Any]]:
  whois = client.intel.whois.get(
    account_id=CLOUDFLARE_ACCOUNT_ID,
    domain=domain
  )
  
  return {
    "domain": whois.domain,
    "expiration_date": whois.expiration_date_raw,
    "registrar": whois.registrar,
  }
  
print(checkWhois("awa.ms"))