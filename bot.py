# Discord Bot - JianyueBot
"""
A Discord bot with various utility commands including IP lookup, domain search,
Minecraft server status, and more.
"""

import os
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

# Import command handlers
from commands import (
  say_command, status_command, roll_command, info_command,
  bincheck_command, domain_command, registrars_command,
  ipdetail_command, iplocation_command, mcserver_command,
  zipcode_command, whois_command, add_monitor_command, 
  remove_monitor_command, list_monitors_command
)

# Load environment variables
load_dotenv('.env')

# Configuration
TOKEN = os.getenv('TOKEN')
DEFAULT_CUSTOM_STATUS = os.getenv('default_custom_status')
DEFAULT_STATUS = os.getenv('default_status')
DEFAULT_VERSION = os.getenv('default_version')
SETTING_VERSION = os.getenv('setting_version')

# Bot information
BOT_VERSION = "v1.0.0"
BOT_BUILD = "1"
BOT_TYPE = "Release Build"

# Bot setup
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

# Global variable for domain monitor
domain_monitor = None


def get_status_from_string(status_string: str) -> discord.Status:
    """Convert string status to Discord Status enum."""
    status_map = {
        'idle': discord.Status.idle,
        'online': discord.Status.online,
        'do_not_disturb': discord.Status.dnd
    }
    return status_map.get(status_string, discord.Status.online)


@client.event
async def on_ready():
    """Event handler for when the bot is ready."""
    global domain_monitor
    
    print("Bot is ready for use!")
    
    # Set bot status
    status = get_status_from_string(DEFAULT_STATUS)
    activity = discord.Game(DEFAULT_CUSTOM_STATUS)
    await client.change_presence(status=status, activity=activity)
    
    # Sync slash commands
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Setup domain monitoring after bot is ready
    try:
        from commands.whois.monitor import setup_domain_monitor
        domain_monitor = setup_domain_monitor(client)
        print("Domain monitoring system initialized")
    except Exception as e:
        print(f"Failed to initialize domain monitoring: {e}")


@client.tree.command(name="say", description="Let bot say something.")
@app_commands.describe(things_to_say="What should I say?")
async def say(interaction: discord.Interaction, things_to_say: str):
    """Make the bot say something."""
    await say_command(interaction, things_to_say)


@client.tree.command(name="status", description="Change the bot's status")
@app_commands.choices(
    choices=[
        app_commands.Choice(name="Online", value="online"),
        app_commands.Choice(name="Idle", value="idle"),
        app_commands.Choice(name="Do Not Disturb", value="dnd"),
    ]
)
async def status(interaction: discord.Interaction, choices: app_commands.Choice[str], *, custom_status_message: str):
    """Change the bot's status and custom message."""
    await status_command(interaction, choices, custom_status_message, client)


@client.tree.command(name='roll', description='Roll a dice.')
async def roll(interaction: discord.Interaction):
    """Roll a six-sided dice."""
    await roll_command(interaction)


@client.tree.command(name='zipcode', description='Search address from zipcode')
@app_commands.choices(
    country=[
        app_commands.Choice(name='Japan', value='JP'),
    ]
)
async def zipcode(interaction: discord.Interaction, country: app_commands.Choice[str], zipcodes: str):
    """Search for address information using a zipcode."""
    await zipcode_command(interaction, country, zipcodes)


@client.tree.command(name='ipdetail', description="Show details from IP address")
async def ipdetail(interaction: discord.Interaction, ipaddress: str):
    """Get detailed information about an IP address."""
    await ipdetail_command(interaction, ipaddress)


@client.tree.command(name='iplocation', description="Show geolocation from IP address")
async def iplocation(interaction: discord.Interaction, ipaddress: str):
    """Get geolocation information for an IP address."""
    await iplocation_command(interaction, ipaddress)


@client.tree.command(name='domain', description='Find the cheapest domain registrar')
@app_commands.choices(
    order=[
        app_commands.Choice(name='New', value='new'),
        app_commands.Choice(name='Renew', value='renew'),
        app_commands.Choice(name='Transfer', value='transfer'),
    ]
)
async def domain(interaction: discord.Interaction, tld: str, order: app_commands.Choice[str]):
    """Find the cheapest domain registrar for a given TLD."""
    await domain_command(interaction, tld, order)


@client.tree.command(name='registrars', description='Search domains by registrar')
@app_commands.choices(
    order=[
        app_commands.Choice(name='New', value='new'),
        app_commands.Choice(name='Renew', value='renew'),
        app_commands.Choice(name='Transfer', value='transfer'),
    ],
)
async def registrars(interaction: discord.Interaction, registrar: str, order: app_commands.Choice[str]):
    """Search for domain prices from a specific registrar."""
    await registrars_command(interaction, registrar, order)


@client.tree.command(name='mcserver', description='Get details of a Minecraft server')
@app_commands.choices(
    server_type=[
        app_commands.Choice(name='Java', value='java'),
        app_commands.Choice(name='Bedrock', value='bedrock'),
    ]
)
async def mcserver(interaction: discord.Interaction, server_type: app_commands.Choice[str], ipaddress: str):
    """Get information about a Minecraft server."""
    await mcserver_command(interaction, server_type, ipaddress)


@client.tree.command(name='bincheck', description="Check card issuer and country from BIN")
async def bincheck(interaction: discord.Interaction, bin_code: int):
    """Check card information from BIN (Bank Identification Number)."""
    await bincheck_command(interaction, bin_code)


@client.tree.command(name='info', description="Information about this bot")
async def info(interaction: discord.Interaction):
    """Display bot information and credits."""
    await info_command(interaction, BOT_VERSION, BOT_BUILD, SETTING_VERSION, BOT_TYPE)


@client.tree.command(name='whois', description='Get domain whois information')
async def whois(interaction: discord.Interaction, domain: str):
    """Get whois information for a domain."""
    await whois_command(interaction, domain)


@client.tree.command(name='domain-monitor-add', description='Add a domain to monitoring list')
async def domain_monitor_add(interaction: discord.Interaction, domain: str):
    """Add a domain to your monitoring list."""
    await add_monitor_command(interaction, domain)


@client.tree.command(name='domain-monitor-remove', description='Remove a domain from monitoring list')
async def domain_monitor_remove(interaction: discord.Interaction, domain: str):
    """Remove a domain from your monitoring list."""
    await remove_monitor_command(interaction, domain)


@client.tree.command(name='domain-monitor-list', description='List your monitored domains')
async def domain_monitor_list(interaction: discord.Interaction):
    """List all your monitored domains."""
    await list_monitors_command(interaction)


if __name__ == "__main__":
    client.run(TOKEN)
