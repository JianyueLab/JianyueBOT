# Discord Bot - JianyueBot
"""
A Discord bot with various utility commands including IP lookup, domain search,
Minecraft server status, and more.
"""

import os
import random
from dotenv import load_dotenv

import discord
from discord import app_commands
from discord.ext import commands

from scripts import *

# Load environment variables
load_dotenv('.env')

# Configuration
TOKEN = os.getenv('TOKEN')
DEFAULT_CUSTOM_STATUS = os.getenv('default_custom_status')
DEFAULT_STATUS = os.getenv('default_status')
DEFAULT_VERSION = os.getenv('default_version')
SETTING_VERSION = os.getenv('setting_version')

# Bot information
BOT_VERSION = "v0.1.4"
BOT_BUILD = "1"
BOT_TYPE = "Release Build"

# Bot setup
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)


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


@client.tree.command(name="say", description="Let bot say something.")
@app_commands.describe(things_to_say="What should I say?")
async def say(interaction: discord.Interaction, things_to_say: str):
  """Make the bot say something."""
  await interaction.response.send_message(things_to_say)


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
  status_map = {
    "online": discord.Status.online,
    "idle": discord.Status.idle,
    "dnd": discord.Status.dnd
  }
  
  new_status = status_map.get(choices.value)
  if not new_status:
    await interaction.response.send_message(
      "Unknown status. Please specify 'online', 'idle', or 'dnd'",
      ephemeral=True
    )
    return

  activity = discord.Game(custom_status_message)
  await client.change_presence(status=new_status, activity=activity)
  await interaction.response.send_message("Status updated!", ephemeral=True)


@client.tree.command(name='roll', description='Roll a dice.')
async def roll(interaction: discord.Interaction):
  """Roll a six-sided dice."""
  number = random.randint(1, 6)
  await interaction.response.send_message(f"🎲 Rolled: {number}")


@client.tree.command(name='zipcode', description='Search address from zipcode')
@app_commands.choices(
  country=[
    app_commands.Choice(name='Japan', value='JP'),
  ]
)
async def zipcode(interaction: discord.Interaction, country: app_commands.Choice[str], zipcodes: str):
  """Search for address information using a zipcode."""
  await interaction.response.defer(ephemeral=True)
  
  if country.value == 'JP':
    result = search_zipcode_jp(zipcodes)
    if result is None:
      await interaction.followup.send("Invalid zipcode.")
    else:
      await interaction.followup.send(
        f"**Prefecture 都道府県:** {result['address1']} {result['kana1']}\n"
        f"**City 市区町村:** {result['address2']} {result['kana2']}\n"
        f"**Town 町域:** {result['address3']} {result['kana3']}"
      )
  else:
    await interaction.followup.send("Invalid country.")


@client.tree.command(name='ipdetail', description="Show details from IP address")
async def ipdetail(interaction: discord.Interaction, ipaddress: str):
  """Get detailed information about an IP address."""
  await interaction.response.defer(ephemeral=True)
  
  result = ipdetails(ipaddress)
  if result is None:
    await interaction.followup.send("Invalid IP address or internal error")
    return

  embed = discord.Embed(
    colour=discord.Colour.blue(),
    title="IP Details",
    description=f"Information for {ipaddress}"
  )
  
  fields = [
    ('IP Address', result['ip']),
    ('IP Number', result['ip_number']),
    ('IP Version', result['ip_version']),
    ('Country', result['country_name']),
    ('Country Code', result['country_code2']),
    ('ISP', result['isp']),
    ('Response Code', result['response_code']),
    ('Response Message', result['response_message'])
  ]
  
  for name, value in fields:
    embed.add_field(name=name, value=value, inline=True)

  await interaction.followup.send(embed=embed)


@client.tree.command(name='iplocation', description="Show geolocation from IP address")
async def iplocation(interaction: discord.Interaction, ipaddress: str):
  """Get geolocation information for an IP address."""
  await interaction.response.defer(ephemeral=True)
  
  result = iplocations(ipaddress)
  if result is None:
    await interaction.followup.send("Invalid IP address or internal error")
    return

  embed = discord.Embed(
    colour=discord.Colour.blue(),
    title="IP Location",
    description=f"Location information for {ipaddress}"
  )
  
  fields = [
    ('Query', result['query']),
    ('Timezone', result['timezone']),
    ('Country', result['country']),
    ('City', result['city']),
    ('ISP', result['isp']),
    ('Organization', result['org']),
    ('ASN', result['as'])
  ]
  
  for name, value in fields:
    embed.add_field(name=name, value=value, inline=True)

  await interaction.followup.send(embed=embed)


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
  await interaction.response.defer(ephemeral=True)
  
  result = cheapest(tld, order.value)
  if result is None:
    await interaction.followup.send("Invalid input or internal error")
    return

  def format_registrar_info(num: str) -> str:
    """Format registrar information for display."""
    return (
      f"### {num}:\n"
      f"- **Registrar**: {result[f'reg_{num}']}\n"
      f"- **Currency**: {result[f'currency_{num}']}\n"
      f"- **New**: {result[f'new_{num}']}\n"
      f"- **Renew**: {result[f'renew_{num}']}\n"
      f"- **Transfer**: {result[f'transfer_{num}']}\n"
      f"- **Website**: {result[f'reg_web_{num}']}\n"
    )

  message = (
    f"## Domain Registrar Comparison\n"
    f"**TLD**: {result['domain']} | **Order**: {result['order']}\n\n"
    f"{format_registrar_info('1st')}"
    f"{format_registrar_info('2nd')}"
    f"{format_registrar_info('3rd')}"
    f"{format_registrar_info('4th')}"
    f"{format_registrar_info('5th')}"
  )

  await interaction.followup.send(message)


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
  await interaction.response.defer(ephemeral=True)
  
  result = registrar_search(registrar, order)
  if result is None:
    await interaction.followup.send("Invalid input or internal error")
    return

  def format_domain_info(num: str) -> str:
    """Format domain information for display."""
    return (
      f"### {num}:\n"
      f"**Domain**: {result[f'domain_{num}']}\n"
      f"**New**: {result[f'new_{num}']}\n"
      f"**Renew**: {result[f'renew_{num}']}\n"
      f"**Transfer**: {result[f'transfer_{num}']}\n"
      f"**Currency**: {result[f'currency_{num}']}\n"
    )

  message = (
    f"## Domain Prices by Registrar\n"
    f"**Registrar**: {result['reg']} | **Website**: {result['reg_web']} | **Order**: {result['order']}\n\n"
    f"{format_domain_info('1st')}"
    f"{format_domain_info('2nd')}"
    f"{format_domain_info('3rd')}"
    f"{format_domain_info('4th')}"
    f"{format_domain_info('5th')}"
  )

  await interaction.followup.send(message)


@client.tree.command(name='mcserver', description='Get details of a Minecraft server')
@app_commands.choices(
  server_type=[
    app_commands.Choice(name='Java', value='java'),
    app_commands.Choice(name='Bedrock', value='bedrock'),
  ]
)
async def mcserver(interaction: discord.Interaction, server_type: app_commands.Choice[str], ipaddress: str):
  """Get information about a Minecraft server."""
  await interaction.response.defer(ephemeral=True)
  
  result = minecraftServer(server_type, ipaddress)
  if result is None:
    await interaction.followup.send("Invalid input or server type")
    return

  embed = discord.Embed(
    colour=discord.Colour.dark_grey(),
    title="🎮 Minecraft Server Info",
    description=f"Server information for {ipaddress}"
  )
  
  fields = [
    ('IP Address', result['ip']),
    ('Port', result['port']),
    ('Hostname', result['hostname']),
    ('Version', result['version']),
    ('MOTD', result['motd']),
    ('Ping', f"{result['ping']}ms"),
    ('SRV Record', result['srv']),
    ('Players', f"{result['player']} / {result['maxPlayer']}")
  ]
  
  for name, value in fields:
    embed.add_field(name=name, value=value, inline=True)

  await interaction.followup.send(embed=embed)


@client.tree.command(name='bincheck', description="Check card issuer and country from BIN")
async def bincheck(interaction: discord.Interaction, bin_code: int):
  """Check card information from BIN (Bank Identification Number)."""
  await interaction.response.defer(ephemeral=True)
  
  result = bin_check_request(bin_code)
  if result is None:
    await interaction.followup.send("Request error or BIN code doesn't exist")
    return

  embed = discord.Embed(
    colour=discord.Colour.dark_grey(),
    title="💳 BIN Check Results",
    description=f"Card information for BIN: {bin_code}"
  )
  
  fields = [
    ('Valid', result['valid']),
    ('Brand', result['brand']),
    ('Type', result['type']),
    ('Level', result['level']),
    ('Commercial', result['is_commercial']),
    ('Prepaid', result['is_prepaid']),
    ('Currency', result['currency']),
    ('Country', result['country']),
    ('Flag', result['flag']),
    ('Issuer', result['issuer'])
  ]
  
  for name, value in fields:
    embed.add_field(name=name, value=value, inline=True)

  await interaction.followup.send(embed=embed, ephemeral=True)


@client.tree.command(name='info', description="Information about this bot")
async def info(interaction: discord.Interaction):
  """Display bot information and credits."""
  await interaction.response.send_message(
    "## 🤖 JianyueBot\n"
    "This bot was developed by [JianyueLab](https://awa.ms).\n"
    "If you have any questions or require assistance, please contact @jianyuehugo.\n\n"
    f"- **GitHub Repo**: https://github.com/jianyuelab/jianyuebot\n"
    f"- **Bot Version**: {BOT_VERSION}\n"
    f"- **Bot Build**: {BOT_BUILD}\n"
    f"- **Settings Version**: {SETTING_VERSION}\n"
    f"- **Build Type**: {BOT_TYPE}",
    ephemeral=True
  )


if __name__ == "__main__":
  client.run(TOKEN)
