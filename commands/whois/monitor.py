import asyncio
import discord
from discord.ext import tasks
from .script import check_expiring_domains
from ..utils import CHANNEL_ID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DomainMonitor:
    def __init__(self, bot):
        self.bot = bot
        # Don't start immediately, wait for bot to be ready
    
    def start_monitoring(self):
        """Start the monitoring task."""
        if not self.check_expiring.is_running():
            self.check_expiring.start()
    
    def cog_unload(self):
        self.check_expiring.cancel()
    
    @tasks.loop(hours=12)  # 每12小时检查一次
    async def check_expiring(self):
        """Check for expiring domains and send notifications."""
        try:
            logger.info("Checking for expiring domains...")
            expiring_domains = check_expiring_domains()
            
            if not expiring_domains:
                logger.info("No expiring domains found")
                return
            
            # Get the notification channel
            if not CHANNEL_ID:
                logger.error("CHANNEL_ID not configured in environment variables")
                return
                
            try:
                channel = await self.bot.fetch_channel(int(CHANNEL_ID))
                if not channel:
                    logger.error(f"Could not find channel with ID: {CHANNEL_ID}")
                    return
            except Exception as e:
                logger.error(f"Error getting channel {CHANNEL_ID}: {e}")
                return
            
            # Send notifications for each user's expiring domains
            for user_id, domains in expiring_domains.items():
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    if user:
                        await self.send_expiry_notification(channel, user, domains)
                except Exception as e:
                    logger.error(f"Failed to send notification for user {user_id}: {e}")
            
            logger.info(f"Sent notifications to channel for {len(expiring_domains)} users")
            
        except Exception as e:
            logger.error(f"Error in domain monitoring task: {e}")
    
    @check_expiring.before_loop
    async def before_check_expiring(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()
    
    async def send_expiry_notification(self, channel: discord.TextChannel, user: discord.User, domains: list):
        """Send expiry notification to the specified channel."""
        try:
            embed = discord.Embed(
                title="⚠️ Domain Expiry Reminder",
                description=f"The following domains of {user.mention} will expire in 7 days:",
                color=0xff0000
            )
            
            for domain_data in domains:
                domain = domain_data['domain']
                days_left = domain_data.get('days_until_expiry', 0)
                registrar = domain_data.get('registrar', 'Unknown')
                
                if days_left <= 1:
                    status_emoji = "🚨"  # Emergency
                elif days_left <= 3:
                    status_emoji = "🔴"  # Critical
                else:
                    status_emoji = "🟡"  # Warning
                
                embed.add_field(
                    name=f"{status_emoji} {domain}",
                    value=f"Remaining time: **{days_left}** days\nRegistrar: {registrar}",
                    inline=True
                )
            
            embed.set_footer(text=f"Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1234567890123456789.png")  # 可选：添加警告图标
            
            await channel.send(embed=embed)
            logger.info(f"Sent notification to channel for {user.name}")
                
        except Exception as e:
            logger.error(f"Error sending notification for {user.name}: {e}")


def setup_domain_monitor(bot):
    """Setup domain monitoring for the bot."""
    monitor = DomainMonitor(bot)
    monitor.start_monitoring()
    return monitor 