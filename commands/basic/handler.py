import discord
from discord import app_commands
import random


async def say_command(interaction: discord.Interaction, things_to_say: str):
    """Make the bot say something."""
    await interaction.response.send_message(things_to_say)


async def status_command(interaction: discord.Interaction, choices: app_commands.Choice[str], custom_status_message: str, bot):
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
    await bot.change_presence(status=new_status, activity=activity)
    await interaction.response.send_message("Status updated!", ephemeral=True)


async def roll_command(interaction: discord.Interaction):
    """Roll a six-sided dice."""
    number = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 Rolled: {number}")


async def info_command(interaction: discord.Interaction, bot_version: str, bot_build: str, setting_version: str, bot_type: str):
    """Display bot information and credits."""
    await interaction.response.send_message(
        "## 🤖 JianyueBot\n"
        "This bot was developed by [JianyueLab](https://jianyuelab.org).\n"
        "If you have any questions or require assistance, please contact @jianyuehugo.\n\n"
        f"- **GitHub Repo**: https://github.com/jianyuelab/jianyuebot\n"
        f"- **Bot Version**: {bot_version}\n"
        f"- **Bot Build**: {bot_build}\n"
        f"- **Settings Version**: {setting_version}\n"
        f"- **Build Type**: {bot_type}",
        ephemeral=True
    ) 