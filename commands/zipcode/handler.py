import discord
from discord import app_commands
from .script import searchZipCodeJP as search_zipcode_jp


async def zipcode_command(interaction: discord.Interaction, country: app_commands.Choice[str], zipcodes: str):
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