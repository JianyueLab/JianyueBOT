from ..utils import *
from cloudflare import Cloudflare
from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime, timedelta, timezone
import re
from urllib.parse import quote

client = Cloudflare(
    api_token=CLOUDFLARE_API_TOKEN
)

# 监控数据文件路径
MONITOR_FILE = "domain_monitors.json"


def parse_iso_datetime(date_string):
    """
    Parse ISO 8601 datetime string with various formats.
    Supports formats like:
    - 2024-01-15T10:30:00Z
    - 2024-01-15T10:30:00.123Z
    - 2024-01-15T10:30:00+00:00
    - 2024-01-15T10:30:00.123456+00:00
    """
    if not date_string:
        return None
    
    try:
        # Handle 'Z' suffix (UTC timezone)
        if date_string.endswith('Z'):
            date_string = date_string[:-1] + '+00:00'
        
        # Parse the datetime
        # Try with fromisoformat first (Python 3.7+)
        try:
            return datetime.fromisoformat(date_string)
        except ValueError:
            # Fallback for edge cases
            # Remove microseconds if they have more than 6 digits
            date_string = re.sub(r'\.(\d{6})\d+', r'.\1', date_string)
            return datetime.fromisoformat(date_string)
            
    except (ValueError, AttributeError) as e:
        # If parsing fails, try alternative parsing methods
        try:
            # Try parsing without timezone info and assume UTC
            if '+' in date_string or date_string.endswith('Z'):
                # Strip timezone info and parse as UTC
                clean_date = re.sub(r'[+\-]\d{2}:\d{2}$|Z$', '', date_string)
                dt = datetime.fromisoformat(clean_date)
                return dt.replace(tzinfo=timezone.utc)
            else:
                # Parse as-is and assume UTC
                dt = datetime.fromisoformat(date_string)
                return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
        except:
            return None


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def validate_domain(domain: str) -> bool:
    """Validate domain name format."""
    # Remove any leading/trailing whitespace
    domain = domain.strip().lower()
    
    # Basic domain pattern
    pattern = r'^[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9\-]{0,61}[a-z0-9])?)*$'
    
    # Check if domain matches pattern
    if not re.match(pattern, domain):
        return False
    
    # Check domain length (max 253 characters)
    if len(domain) > 253:
        return False
    
    # Check each label length (max 63 characters)
    labels = domain.split('.')
    for label in labels:
        if len(label) > 63:
            return False
    
    return True


def normalize_domain(domain: str) -> str:
    """Normalize domain name for API calls."""
    # Remove any leading/trailing whitespace and convert to lowercase
    domain = domain.strip().lower()
    
    # Remove any protocol prefixes
    if domain.startswith(('http://', 'https://', 'www.')):
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
    
    # Remove trailing slash
    domain = domain.rstrip('/')
    
    return domain


def checkWhois(domain: str) -> Optional[Dict[str, Any]]:
    """Get whois information for a domain."""
    try:
        # Normalize and validate domain
        normalized_domain = normalize_domain(domain)
        
        if not validate_domain(normalized_domain):
            print(f"Invalid domain format: {domain}")
            return None
        
        # URL encode the domain for API call
        encoded_domain = quote(normalized_domain)
        
        whois = client.intel.whois.get(
            account_id=CLOUDFLARE_ACCOUNT_ID,
            domain=encoded_domain
        )
        
        # Create result dict with safe attribute access
        result = {
            "domain": normalized_domain,  # Always use normalized domain as primary
            "registrar": getattr(whois, 'registrar', None),
        }
        
        # Try to get additional fields if they exist
        try:
            creation_date = getattr(whois, 'creation_date', None)
            result["creation_date"] = creation_date.isoformat() if creation_date else None
        except:
            result["creation_date"] = None
            
        try:
            updated_date = getattr(whois, 'updated_date', None)
            result["updated_date"] = updated_date.isoformat() if updated_date else None
        except:
            result["updated_date"] = None
            
        try:
            expiration_date = getattr(whois, 'expiration_date', None)
            result["expiration_date"] = expiration_date.isoformat() if expiration_date else None
        except:
            result["expiration_date"] = None
        
        try:
            result["registrant_organization"] = getattr(whois, 'registrant_organization', None)
        except:
            result["registrant_organization"] = None
            
        try:
            result["registrant_country"] = getattr(whois, 'registrant_country', None)
        except:
            result["registrant_country"] = None
            
        try:
            result["name_servers"] = getattr(whois, 'name_servers', None)
        except:
            result["name_servers"] = None
            
        try:
            result["status"] = getattr(whois, 'status', None)
        except:
            result["status"] = None
            
        try:
            result["dnssec"] = getattr(whois, 'dnssec', None)
        except:
            result["dnssec"] = None
            
        try:
            result["registrant_email"] = getattr(whois, 'registrant_email', None)
        except:
            result["registrant_email"] = None
            
        try:
            result["registrant_phone"] = getattr(whois, 'registrant_phone', None)
        except:
            result["registrant_phone"] = None
            
        try:
            result["registrant_name"] = getattr(whois, 'registrant_name', None)
        except:
            result["registrant_name"] = None
            
        try:
            result["registrant_address"] = getattr(whois, 'registrant_address', None)
        except:
            result["registrant_address"] = None
            
        try:
            result["registrant_city"] = getattr(whois, 'registrant_city', None)
        except:
            result["registrant_city"] = None
            
        try:
            result["registrant_state"] = getattr(whois, 'registrant_state', None)
        except:
            result["registrant_state"] = None
            
        try:
            result["registrant_postal_code"] = getattr(whois, 'registrant_postal_code', None)
        except:
            result["registrant_postal_code"] = None
            
        try:
            result["admin_email"] = getattr(whois, 'admin_email', None)
        except:
            result["admin_email"] = None
            
        try:
            result["tech_email"] = getattr(whois, 'tech_email', None)
        except:
            result["tech_email"] = None
            
        try:
            result["billing_email"] = getattr(whois, 'billing_email', None)
        except:
            result["billing_email"] = None
        
        return result
        
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
            json.dump(monitors, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
    except Exception as e:
        print(f"Error saving monitors: {e}")


def add_domain_monitor(domain: str, user_id: int, domain_info: Dict[str, Any]) -> bool:
    """Add a domain to monitoring list for a user."""
    monitors = load_monitors()
    user_id_str = str(user_id)
    
    if user_id_str not in monitors:
        monitors[user_id_str] = []
    
    # Normalize domain for consistent storage
    normalized_domain = normalize_domain(domain)
    
    # Check if domain already exists for this user
    for existing_domain in monitors[user_id_str]:
        if existing_domain['domain'].lower() == normalized_domain.lower():
            return False  # Domain already exists
    
    # Add new domain - ensure all datetime fields are strings
    monitor_data = {
        "domain": normalized_domain,  # Use normalized domain
        "added_date": datetime.now().isoformat(),
        "expiration_date": domain_info.get('expiration_date'),
        "creation_date": domain_info.get('creation_date'),
        "updated_date": domain_info.get('updated_date'),
        "registrar": domain_info.get('registrar'),
        "registrant_organization": domain_info.get('registrant_organization'),
        "registrant_country": domain_info.get('registrant_country'),
        "name_servers": domain_info.get('name_servers'),
        "status": domain_info.get('status'),
        "dnssec": domain_info.get('dnssec'),
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
    
    # Normalize domain for consistent comparison
    normalized_domain = normalize_domain(domain)
    
    original_length = len(monitors[user_id_str])
    monitors[user_id_str] = [
        d for d in monitors[user_id_str] 
        if d['domain'].lower() != normalized_domain.lower()
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
        domain_data['creation_date'] = fresh_info.get('creation_date')
        domain_data['updated_date'] = fresh_info.get('updated_date')
        domain_data['registrar'] = fresh_info.get('registrar')
        domain_data['registrant_organization'] = fresh_info.get('registrant_organization')
        domain_data['registrant_country'] = fresh_info.get('registrant_country')
        domain_data['name_servers'] = fresh_info.get('name_servers')
        domain_data['status'] = fresh_info.get('status')
        domain_data['dnssec'] = fresh_info.get('dnssec')
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
            
            expiration_date = domain_data.get('expiration_date')
            if expiration_date:
                parsed_date = parse_iso_datetime(expiration_date)
                if parsed_date:
                    try:
                        # Ensure both dates are timezone-aware for proper comparison
                        current_time_utc = current_time.replace(tzinfo=timezone.utc) if current_time.tzinfo is None else current_time
                        parsed_date_utc = parsed_date.replace(tzinfo=timezone.utc) if parsed_date.tzinfo is None else parsed_date
                        
                        days_until_expiry = (parsed_date_utc - current_time_utc).days
                        
                        if 0 <= days_until_expiry <= 7:
                            # Create a copy of domain_data and add days_until_expiry as integer
                            notification_data = domain_data.copy()
                            notification_data['days_until_expiry'] = days_until_expiry
                            user_expiring.append(notification_data)
                    except Exception as e:
                        print(f"Error calculating expiry days for {domain_data['domain']}: {e}")
                else:
                    print(f"Could not parse expiration date for {domain_data['domain']}: {expiration_date}")
        
        if user_expiring:
            expiring_domains[user_id] = user_expiring
    
    # Save updated monitor data
    save_monitors(monitors)
    return expiring_domains


def get_expiring_domains_without_update() -> Dict[str, List[Dict[str, Any]]]:
    """Get expiring domains without updating the data (for startup check)."""
    monitors = load_monitors()
    expiring_domains = {}
    current_time = datetime.now()
    
    for user_id, domains in monitors.items():
        user_expiring = []
        
        for domain_data in domains:
            expiration_date = domain_data.get('expiration_date')
            if expiration_date:
                parsed_date = parse_iso_datetime(expiration_date)
                if parsed_date:
                    try:
                        # Ensure both dates are timezone-aware for proper comparison
                        current_time_utc = current_time.replace(tzinfo=timezone.utc) if current_time.tzinfo is None else current_time
                        parsed_date_utc = parsed_date.replace(tzinfo=timezone.utc) if parsed_date.tzinfo is None else parsed_date
                        
                        days_until_expiry = (parsed_date_utc - current_time_utc).days
                        
                        if 0 <= days_until_expiry <= 7:
                            # Create a copy of domain_data and add days_until_expiry as integer
                            notification_data = domain_data.copy()
                            notification_data['days_until_expiry'] = days_until_expiry
                            user_expiring.append(notification_data)
                    except Exception as e:
                        print(f"Error calculating expiry days for {domain_data['domain']}: {e}")
                else:
                    print(f"Could not parse expiration date for {domain_data['domain']}: {expiration_date}")
        
        if user_expiring:
            expiring_domains[user_id] = user_expiring
    
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
