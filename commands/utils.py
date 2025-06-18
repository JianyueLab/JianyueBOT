import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv('.env')

BINCHECK_API_KEY = os.getenv('BINCHECK_API_KEY')
CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_API_TOKEN')
CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
CHANNEL_ID = os.getenv('CHANNEL_ID')

def trueFalseJudgement(data: str) -> Optional[str]:
  """Convert string boolean to emoji representation."""
  if data == 'true':
    return '✅'
  elif data == 'false':
    return '❌'
  else:
    return None

