import discord
from discord import app_commands
from .script import minecraftServer


async def mcserver_command(interaction: discord.Interaction, server_type: app_commands.Choice[str], ipaddress: str):
    """Get information about a Minecraft server."""
    await interaction.response.defer(ephemeral=True)
    
    result = minecraftServer(server_type.value, ipaddress)
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