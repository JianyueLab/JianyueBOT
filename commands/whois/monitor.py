import asyncio
import discord
from discord.ext import tasks
from .script import check_expiring_domains, get_expiring_domains_without_update
from ..utils import CHANNEL_ID
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DomainMonitor:
    def __init__(self, bot):
        self.bot = bot
        self.sent_notifications = set()  # Track sent notifications to prevent duplicates
        # Don't start immediately, wait for bot to be ready
    
    def start_monitoring(self):
        """Start the monitoring task."""
        if not self.check_expiring.is_running():
            self.check_expiring.start()
    
    def cog_unload(self):
        self.check_expiring.cancel()
    
    def _get_notification_key(self, user_id: str, domain: str, days_left: int) -> str:
        """Generate a unique key for notification tracking."""
        return f"{user_id}:{domain}:{days_left}"
    
    async def check_on_startup(self):
        """Check domains immediately when bot starts."""
        try:
            logger.info("Performing startup domain check...")
            expiring_domains = get_expiring_domains_without_update()
            
            if not expiring_domains:
                logger.info("No expiring domains found on startup")
                return
            
            # Send notifications to users via DM
            for user_id, domains in expiring_domains.items():
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    if user:
                        await self.send_expiry_notification(user, domains, is_startup=True)
                except Exception as e:
                    logger.error(f"Failed to send startup notification for user {user_id}: {e}")
            
            logger.info(f"Sent startup notifications to {len(expiring_domains)} users")
            
        except Exception as e:
            logger.error(f"Error in startup domain check: {e}")
    
    @tasks.loop(hours=12)  # 每12小时检查一次
    async def check_expiring(self):
        """Check for expiring domains and send notifications."""
        try:
            logger.info("Checking for expiring domains...")
            expiring_domains = check_expiring_domains()
            
            if not expiring_domains:
                logger.info("No expiring domains found")
                return
            
            # Send notifications to users via DM
            for user_id, domains in expiring_domains.items():
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    if user:
                        await self.send_expiry_notification(user, domains)
                except Exception as e:
                    logger.error(f"Failed to send notification for user {user_id}: {e}")
            
            logger.info(f"Sent DM notifications to {len(expiring_domains)} users")
            
        except Exception as e:
            logger.error(f"Error in domain monitoring task: {e}")
    
    @check_expiring.before_loop
    async def before_check_expiring(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()
    
    async def send_expiry_notification(self, user: discord.User, domains: list, is_startup=False):
        """Send expiry notification to user via DM."""
        try:
            title = "⚠️ Domain Expiry Reminder"
            if is_startup:
                title = "🚀 Startup Domain Check - Expiry Reminder"
                
            embed = discord.Embed(
                title=title,
                description="The following domains will expire in 7 days:",
                color=0xff0000
            )
            
            # Filter out domains that we've already notified about recently
            new_domains = []
            for domain_data in domains:
                domain = domain_data['domain']
                days_left = domain_data.get('days_until_expiry', 0)
                notification_key = self._get_notification_key(str(user.id), domain, days_left)
                
                # Only send notification if we haven't sent it recently
                if notification_key not in self.sent_notifications:
                    new_domains.append(domain_data)
                    self.sent_notifications.add(notification_key)
            
            if not new_domains:
                logger.info(f"No new notifications to send to {user.name}")
                return
            
            for domain_data in new_domains:
                domain = domain_data['domain']
                days_left = domain_data.get('days_until_expiry', 0)
                registrar = domain_data.get('registrar', 'Unknown')
                registrant_org = domain_data.get('registrant_organization', 'Unknown')
                creation_date = domain_data.get('creation_date', 'Unknown')
                
                if days_left <= 1:
                    status_emoji = "🚨"  # Emergency
                elif days_left <= 3:
                    status_emoji = "🔴"  # Critical
                else:
                    status_emoji = "🟡"  # Warning
                
                # Create detailed domain info
                domain_info = f"**Remaining time:** {days_left} days\n"
                domain_info += f"**Registrar:** {registrar}\n"
                if registrant_org and registrant_org != 'Unknown':
                    domain_info += f"**Organization:** {registrant_org}\n"
                if creation_date and creation_date != 'Unknown':
                    try:
                        creation_dt = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                        domain_info += f"**Created:** {creation_dt.strftime('%Y-%m-%d')}"
                    except:
                        pass
                
                embed.add_field(
                    name=f"{status_emoji} {domain}",
                    value=domain_info,
                    inline=True
                )
            
            footer_text = f"Check time: {datetime.now().strftime('%Y-%m-%d')}"
            if is_startup:
                footer_text += " (Startup Check)"
            embed.set_footer(text=footer_text)
            
            # Try to send DM first
            try:
                await user.send(embed=embed)
                logger.info(f"Sent {'startup ' if is_startup else ''}DM notification to {user.name}")
            except discord.Forbidden:
                logger.warning(f"Cannot send DM to {user.name}, user has DMs disabled")
                # If user has DMs disabled, mention them in channel
                await self.send_channel_notification(user, new_domains, is_startup)
                
        except Exception as e:
            logger.error(f"Error sending notification to {user.name}: {e}")
    
    async def send_channel_notification(self, user: discord.User, domains: list, is_startup=False):
        """Send notification to channel when DM fails."""
        if not CHANNEL_ID:
            logger.error("CHANNEL_ID not configured, cannot send channel notification")
            return
            
        try:
            channel = await self.bot.fetch_channel(int(CHANNEL_ID))
            if not channel:
                logger.error(f"Could not find channel with ID: {CHANNEL_ID}")
                return
                
            title = "⚠️ Domain Expiry Reminder"
            if is_startup:
                title = "🚀 Startup Domain Check - Expiry Reminder"
                
            embed = discord.Embed(
                title=title,
                description=f"{user.mention} The following domains will expire in 7 days:",
                color=0xff0000
            )
            
            for domain_data in domains:
                domain = domain_data['domain']
                days_left = domain_data.get('days_until_expiry', 0)
                registrar = domain_data.get('registrar', 'Unknown')
                registrant_org = domain_data.get('registrant_organization', 'Unknown')
                creation_date = domain_data.get('creation_date', 'Unknown')
                
                if days_left <= 1:
                    status_emoji = "🚨"
                elif days_left <= 3:
                    status_emoji = "🔴"
                else:
                    status_emoji = "🟡"
                
                # Create detailed domain info
                domain_info = f"**Remaining time:** {days_left} days\n"
                domain_info += f"**Registrar:** {registrar}\n"
                if registrant_org and registrant_org != 'Unknown':
                    domain_info += f"**Organization:** {registrant_org}\n"
                if creation_date and creation_date != 'Unknown':
                    try:
                        creation_dt = datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
                        domain_info += f"**Created:** {creation_dt.strftime('%Y-%m-%d')}"
                    except:
                        pass
                
                embed.add_field(
                    name=f"{status_emoji} {domain}",
                    value=domain_info,
                    inline=True
                )
            
            footer_text = f"Check time: {datetime.now().strftime('%Y-%m-%d')}"
            if is_startup:
                footer_text += " (Startup Check)"
            embed.set_footer(text=footer_text)
            
            await channel.send(embed=embed)
            logger.info(f"Sent {'startup ' if is_startup else ''}channel notification for {user.name}")
            
        except Exception as e:
            logger.error(f"Error sending channel notification for {user.name}: {e}")


def setup_domain_monitor(bot):
    """Setup domain monitoring for the bot."""
    monitor = DomainMonitor(bot)
    monitor.start_monitoring()
    return monitor 