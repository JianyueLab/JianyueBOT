import discord
from discord import app_commands
from .script import checkWhois, add_domain_monitor, remove_domain_monitor, list_monitored_domains, check_expiring_domains
from datetime import datetime
import json


async def whois_command(interaction: discord.Interaction, domain: str):
    """Handle whois command to get domain information."""
    await interaction.response.defer()
    
    try:
        result = checkWhois(domain)
        if not result:
            await interaction.followup.send(f"❌ Cannot get information of {domain}")
            return
            
        embed = discord.Embed(
            title=f"🔍 Domain Information - {result['domain']}",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Domain",
            value=result['domain'],
            inline=True
        )
        
        embed.add_field(
            name="Registrar",
            value=result['registrar'] or "Unknown",
            inline=True
        )
        
        if result['expiration_date']:
            try:
                # Parse the expiration date
                exp_date = datetime.fromisoformat(result['expiration_date'].replace('Z', '+00:00'))
                days_until_expiry = (exp_date - datetime.now(exp_date.tzinfo)).days
                
                embed.add_field(
                    name="Expiration Date",
                    value=f"{exp_date.strftime('%Y-%m-%d %H:%M:%S')} UTC",
                    inline=False
                )
                
                embed.add_field(
                    name="Remaining Days",
                    value=f"{days_until_expiry} days",
                    inline=True
                )
                
                if days_until_expiry <= 7:
                    embed.color = 0xff0000
                    embed.set_footer(text="⚠️ Domain is about to expire!")
                elif days_until_expiry <= 30:
                    embed.color = 0xffa500
                    embed.set_footer(text="⚠️ Domain will expire in one month")
                    
            except Exception as e:
                embed.add_field(
                    name="Expiration Date",
                    value=result['expiration_date'],
                    inline=False
                )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting domain information: {str(e)}")


async def add_monitor_command(interaction: discord.Interaction, domain: str):
    """Add a domain to monitoring list."""
    await interaction.response.defer()
    
    try:
        # First get domain info
        domain_info = checkWhois(domain)
        if not domain_info:
            await interaction.followup.send(f"❌ Cannot get information of {domain}, cannot add monitor")
            return
            
        success = add_domain_monitor(domain, interaction.user.id, domain_info)
        
        if success:
            embed = discord.Embed(
                title="✅ Domain Monitor Added",
                description=f"Domain **{domain}** has been added to the monitor list",
                color=0x00ff00
            )
            
            if domain_info['expiration_date']:
                try:
                    exp_date = datetime.fromisoformat(domain_info['expiration_date'].replace('Z', '+00:00'))
                    days_until_expiry = (exp_date - datetime.now(exp_date.tzinfo)).days
                    
                    embed.add_field(
                        name="Expiration Date",
                        value=f"{exp_date.strftime('%Y-%m-%d')}",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Remaining Days",
                        value=f"{days_until_expiry} days",
                        inline=True
                    )
                except:
                    pass
                    
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ Domain {domain} is already in the monitor list")
            
    except Exception as e:
        await interaction.followup.send(f"❌ Error adding domain monitor: {str(e)}")


async def remove_monitor_command(interaction: discord.Interaction, domain: str):
    """Remove a domain from monitoring list."""
    await interaction.response.defer()
    
    try:
        success = remove_domain_monitor(domain, interaction.user.id)
        
        if success:
            embed = discord.Embed(
                title="✅ Domain Monitor Removed",
                description=f"Domain **{domain}** has been removed from the monitor list",
                color=0x00ff00
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ Domain {domain} is not in your monitor list")
            
    except Exception as e:
        await interaction.followup.send(f"❌ Error removing domain monitor: {str(e)}")


async def list_monitors_command(interaction: discord.Interaction):
    """List all monitored domains for the user."""
    await interaction.response.defer()
    
    try:
        domains = list_monitored_domains(interaction.user.id)
        
        if not domains:
            await interaction.followup.send("📋 You are not monitoring any domain")
            return
            
        embed = discord.Embed(
            title=f"📋 Your Domain Monitor List ({len(domains)} domains)",
            color=0x0099ff
        )
        
        for i, domain_data in enumerate(domains, 1):
            domain = domain_data['domain']
            exp_date_str = domain_data.get('expiration_date', 'Unknown')
            
            if exp_date_str and exp_date_str != 'Unknown':
                try:
                    exp_date = datetime.fromisoformat(exp_date_str.replace('Z', '+00:00'))
                    days_until_expiry = (exp_date - datetime.now(exp_date.tzinfo)).days
                    
                    status_emoji = "🟢"  # Green
                    if days_until_expiry <= 7:
                        status_emoji = "🔴"  # Red
                    elif days_until_expiry <= 30:
                        status_emoji = "🟡"  # Yellow
                        
                    embed.add_field(
                        name=f"{status_emoji} {domain}",
                        value=f"Expiration Date: {exp_date.strftime('%Y-%m-%d')}\nRemaining Days: {days_until_expiry} days",
                        inline=True
                    )
                except:
                    embed.add_field(
                        name=f"⚪ {domain}",
                        value=f"Expiration Date: {exp_date_str}",
                        inline=True
                    )
            else:
                embed.add_field(
                    name=f"⚪ {domain}",
                    value="Expiration Date: Unknown",
                    inline=True
                )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting monitor list: {str(e)}") 