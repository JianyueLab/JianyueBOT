from ..utils import *
from cloudflare import Cloudflare
from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime, timedelta

client = Cloudflare(
    api_token=CLOUDFLARE_API_TOKEN
)

# 监控数据文件路径
MONITOR_FILE = "domain_monitors.json"

def checkWhois(domain: str) -> Optional[Dict[str, Any]]:
    """Get whois information for a domain."""
    try:
        whois = client.intel.whois.get(
            account_id=CLOUDFLARE_ACCOUNT_ID,
            domain=domain
        )
        
        return {
            "domain": whois.domain,
            "expiration_date": whois.expiration_date_raw,
            "registrar": whois.registrar,
        }
    except Exception as e:
        print(f"Error checking whois for {domain}: {e}")
        return None


def load_monitors() -> Dict[str, List[Dict]]:
    """Load domain monitors from file."""
    if not os.path.exists(MONITOR_FILE):
        return {}
    
    try:
        with open(MONITOR_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def save_monitors(monitors: Dict[str, List[Dict]]):
    """Save domain monitors to file."""
    try:
        with open(MONITOR_FILE, 'w', encoding='utf-8') as f:
            json.dump(monitors, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving monitors: {e}")


def add_domain_monitor(domain: str, user_id: int, domain_info: Dict[str, Any]) -> bool:
    """Add a domain to monitoring list for a user."""
    monitors = load_monitors()
    user_id_str = str(user_id)
    
    if user_id_str not in monitors:
        monitors[user_id_str] = []
    
    # Check if domain already exists for this user
    for existing_domain in monitors[user_id_str]:
        if existing_domain['domain'].lower() == domain.lower():
            return False  # Domain already exists
    
    # Add new domain
    monitor_data = {
        "domain": domain,
        "added_date": datetime.now().isoformat(),
        "expiration_date": domain_info.get('expiration_date'),
        "registrar": domain_info.get('registrar'),
        "last_checked": datetime.now().isoformat()
    }
    
    monitors[user_id_str].append(monitor_data)
    save_monitors(monitors)
    return True


def remove_domain_monitor(domain: str, user_id: int) -> bool:
    """Remove a domain from monitoring list for a user."""
    monitors = load_monitors()
    user_id_str = str(user_id)
    
    if user_id_str not in monitors:
        return False
    
    original_length = len(monitors[user_id_str])
    monitors[user_id_str] = [
        d for d in monitors[user_id_str] 
        if d['domain'].lower() != domain.lower()
    ]
    
    if len(monitors[user_id_str]) < original_length:
        save_monitors(monitors)
        return True
    
    return False


def list_monitored_domains(user_id: int) -> List[Dict[str, Any]]:
    """Get all monitored domains for a user."""
    monitors = load_monitors()
    user_id_str = str(user_id)
    
    return monitors.get(user_id_str, [])


def update_domain_info(domain_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update domain information by checking whois."""
    domain = domain_data['domain']
    fresh_info = checkWhois(domain)
    
    if fresh_info:
        domain_data['expiration_date'] = fresh_info.get('expiration_date')
        domain_data['registrar'] = fresh_info.get('registrar')
        domain_data['last_checked'] = datetime.now().isoformat()
    
    return domain_data


def check_expiring_domains() -> Dict[str, List[Dict[str, Any]]]:
    """Check for domains expiring in the next 7 days."""
    monitors = load_monitors()
    expiring_domains = {}
    current_time = datetime.now()
    
    for user_id, domains in monitors.items():
        user_expiring = []
        
        for domain_data in domains:
            # Update domain info if it's been more than 24 hours since last check
            try:
                last_checked = datetime.fromisoformat(domain_data['last_checked'])
                if (current_time - last_checked).days >= 1:
                    domain_data = update_domain_info(domain_data)
            except:
                domain_data = update_domain_info(domain_data)
            
            exp_date_str = domain_data.get('expiration_date')
            if exp_date_str:
                try:
                    exp_date = datetime.fromisoformat(exp_date_str.replace('Z', '+00:00'))
                    # Remove timezone info for comparison
                    exp_date_naive = exp_date.replace(tzinfo=None)
                    days_until_expiry = (exp_date_naive - current_time).days
                    
                    if 0 <= days_until_expiry <= 7:
                        domain_data['days_until_expiry'] = days_until_expiry
                        user_expiring.append(domain_data)
                except Exception as e:
                    print(f"Error parsing expiration date for {domain_data['domain']}: {e}")
        
        if user_expiring:
            expiring_domains[user_id] = user_expiring
    
    # Save updated monitor data
    save_monitors(monitors)
    return expiring_domains


def get_all_monitored_domains() -> Dict[str, List[Dict[str, Any]]]:
    """Get all monitored domains across all users."""
    return load_monitors()


def refresh_domain_info(domain: str, user_id: int) -> bool:
    """Refresh domain information for a specific domain."""
    monitors = load_monitors()
    user_id_str = str(user_id)
    
    if user_id_str not in monitors:
        return False
    
    for i, domain_data in enumerate(monitors[user_id_str]):
        if domain_data['domain'].lower() == domain.lower():
            monitors[user_id_str][i] = update_domain_info(domain_data)
            save_monitors(monitors)
            return True
    
    return False
