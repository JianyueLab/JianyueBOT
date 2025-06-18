# Import all command handlers
from .basic.handler import say_command, status_command, roll_command, info_command
from .bincheck.handler import bincheck_command
from .domain.handler import domain_command, registrars_command
from .ipaddress.handler import ipdetail_command, iplocation_command
from .minecraft.handler import mcserver_command
from .zipcode.handler import zipcode_command
from .whois.handler import whois_command, add_monitor_command, remove_monitor_command, list_monitors_command

# Import all script functions for compatibility
from .bincheck.script import binCheckRequest as bin_check_request
from .domain.script import cheapest, registrarSearch as registrar_search
from .ipaddress.script import ipdetails, iplocations
from .minecraft.script import minecraftServer
from .zipcode.script import searchZipCodeJP as search_zipcode_jp
from .whois.script import checkWhois

__all__ = [
    # Command handlers
    'say_command',
    'status_command', 
    'roll_command',
    'info_command',
    'bincheck_command',
    'domain_command',
    'registrars_command',
    'ipdetail_command',
    'iplocation_command',
    'mcserver_command',
    'zipcode_command',
    'whois_command',
    'add_monitor_command',
    'remove_monitor_command',
    'list_monitors_command',
    
    # Script functions (for compatibility)
    'bin_check_request',
    'cheapest',
    'registrar_search',
    'ipdetails',
    'iplocations',
    'minecraftServer',
    'search_zipcode_jp',
    'checkWhois'
]
