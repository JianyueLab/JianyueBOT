import discord
from discord import app_commands
from .script import ipdetails, iplocations


async def ipdetail_command(interaction: discord.Interaction, ipaddress: str):
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


async def iplocation_command(interaction: discord.Interaction, ipaddress: str):
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