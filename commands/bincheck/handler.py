import discord
from discord import app_commands
from .script import binCheckRequest


async def bincheck_command(interaction: discord.Interaction, bin_code: int):
    """Check card information from BIN (Bank Identification Number)."""
    await interaction.response.defer(ephemeral=True)
    
    result = binCheckRequest(bin_code)
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
