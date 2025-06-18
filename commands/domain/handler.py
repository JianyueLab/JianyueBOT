import discord
from discord import app_commands
from .script import cheapest, registrarSearch as registrar_search


async def domain_command(interaction: discord.Interaction, tld: str, order: app_commands.Choice[str]):
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


async def registrars_command(interaction: discord.Interaction, registrar: str, order: app_commands.Choice[str]):
    """Search for domain prices from a specific registrar."""
    await interaction.response.defer(ephemeral=True)
    
    result = registrar_search(registrar, order.value)
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