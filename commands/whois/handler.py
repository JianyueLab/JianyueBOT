import discord
from discord import app_commands
from .script import checkWhois, add_domain_monitor, remove_domain_monitor, list_monitored_domains, check_expiring_domains
from datetime import datetime
import json


async def whois_command(interaction: discord.Interaction, domain: str):
    """Handle whois command to get domain information."""
    await interaction.response.defer()
    
    try:
        # Import validation functions
        from .script import validate_domain, normalize_domain
        
        # Normalize and validate domain
        normalized_domain = normalize_domain(domain)
        
        if not validate_domain(normalized_domain):
            embed = discord.Embed(
                title="❌ Invalid Domain Format",
                description=f"The domain `{domain}` has an invalid format.",
                color=0xff0000
            )
            embed.add_field(
                name="Valid Domain Examples",
                value="• example.com\n• sub.example.com\n• my-domain.org\n• test123.net",
                inline=False
            )
            embed.add_field(
                name="Domain Rules",
                value="• Only letters, numbers, and hyphens\n• Cannot start or end with hyphen\n• Max 253 characters total\n• Each label max 63 characters",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return
        
        result = checkWhois(domain)
        if not result:
            embed = discord.Embed(
                title="❌ Domain Information Unavailable",
                description=f"Could not retrieve information for `{normalized_domain}`",
                color=0xff0000
            )
            embed.add_field(
                name="Possible Reasons",
                value="• Domain doesn't exist\n• Domain is not registered\n• API service unavailable\n• Domain format not supported",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return
            
        embed = discord.Embed(
            title=f"🔍 Domain Information - {result['domain']}",
            color=0x00ff00
        )
        
        # Basic Information
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
        
        # Dates Information
        if result.get('creation_date'):
            try:
                creation_date = datetime.fromisoformat(result['creation_date'].replace('Z', '+00:00'))
                embed.add_field(
                    name="Creation Date",
                    value=f"{creation_date.strftime('%Y-%m-%d')}",
                    inline=True
                )
            except:
                embed.add_field(
                    name="Creation Date",
                    value=result['creation_date'],
                    inline=True
                )
        
        if result.get('updated_date'):
            try:
                updated_date = datetime.fromisoformat(result['updated_date'].replace('Z', '+00:00'))
                embed.add_field(
                    name="Last Updated",
                    value=f"{updated_date.strftime('%Y-%m-%d')}",
                    inline=True
                )
            except:
                embed.add_field(
                    name="Last Updated",
                    value=result['updated_date'],
                    inline=True
                )
        
        if result.get('expiration_date'):
            try:
                # Parse the expiration date (ISO 8601 format)
                exp_date = datetime.fromisoformat(result['expiration_date'].replace('Z', '+00:00'))
                days_until_expiry = (exp_date - datetime.now(exp_date.tzinfo)).days
                
                embed.add_field(
                    name="Expiration Date",
                    value=f"{exp_date.strftime('%Y-%m-%d')}",
                    inline=True
                )
                
                embed.add_field(
                    name="Days Left",
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
                    inline=True
                )
        
        # Registrant Information
        if result.get('registrant_organization') or result.get('registrant_name'):
            registrant_info = []
            if result.get('registrant_organization'):
                registrant_info.append(f"**Org:** {result['registrant_organization']}")
            if result.get('registrant_name'):
                registrant_info.append(f"**Name:** {result['registrant_name']}")
            if result.get('registrant_country'):
                registrant_info.append(f"**Country:** {result['registrant_country']}")
            
            if registrant_info:
                embed.add_field(
                    name="Registrant Information",
                    value="\n".join(registrant_info),
                    inline=False
                )
        
        # Contact Information
        contact_info = []
        if result.get('registrant_email'):
            contact_info.append(f"**Registrant:** {result['registrant_email']}")
        if result.get('admin_email'):
            contact_info.append(f"**Admin:** {result['admin_email']}")
        if result.get('tech_email'):
            contact_info.append(f"**Tech:** {result['tech_email']}")
        if result.get('billing_email'):
            contact_info.append(f"**Billing:** {result['billing_email']}")
        
        if contact_info:
            embed.add_field(
                name="Contact Information",
                value="\n".join(contact_info),
                inline=False
            )
        
        # Name Servers
        if result.get('name_servers'):
            name_servers = result['name_servers']
            if isinstance(name_servers, list):
                ns_text = "\n".join([f"• {ns}" for ns in name_servers[:3]])  # Show first 3
                if len(name_servers) > 3:
                    ns_text += f"\n• ... and {len(name_servers) - 3} more"
            else:
                ns_text = str(name_servers)
            
            embed.add_field(
                name="Name Servers",
                value=ns_text,
                inline=False
            )
        
        # Status and DNSSEC
        status_info = []
        if result.get('status'):
            if isinstance(result['status'], list):
                status_info.extend([f"• {status}" for status in result['status'][:3]])
                if len(result['status']) > 3:
                    status_info.append(f"• ... and {len(result['status']) - 3} more")
            else:
                status_info.append(f"• {result['status']}")
        
        if result.get('dnssec'):
            status_info.append(f"• DNSSEC: {result['dnssec']}")
        
        if status_info:
            embed.add_field(
                name="Status & Security",
                value="\n".join(status_info),
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting domain information: {str(e)}")


async def add_monitor_command(interaction: discord.Interaction, domain: str):
    """Add a domain to monitoring list."""
    await interaction.response.defer()
    
    try:
        # Import validation functions
        from .script import validate_domain, normalize_domain
        
        # Normalize and validate domain
        normalized_domain = normalize_domain(domain)
        
        if not validate_domain(normalized_domain):
            embed = discord.Embed(
                title="❌ Invalid Domain Format",
                description=f"The domain `{domain}` has an invalid format and cannot be added to monitoring.",
                color=0xff0000
            )
            embed.add_field(
                name="Valid Domain Examples",
                value="• example.com\n• sub.example.com\n• my-domain.org\n• test123.net",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return
        
        # First get domain info
        domain_info = checkWhois(domain)
        if not domain_info:
            embed = discord.Embed(
                title="❌ Cannot Add Domain to Monitoring",
                description=f"Could not retrieve information for `{normalized_domain}`",
                color=0xff0000
            )
            embed.add_field(
                name="Possible Reasons",
                value="• Domain doesn't exist\n• Domain is not registered\n• API service unavailable\n• Domain format not supported",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return
            
        success = add_domain_monitor(domain, interaction.user.id, domain_info)
        
        if success:
            embed = discord.Embed(
                title="✅ Domain Monitor Added",
                description=f"Domain **{domain_info['domain']}** has been added to the monitor list",
                color=0x00ff00
            )
            
            if domain_info.get('expiration_date'):
                try:
                    exp_date = datetime.fromisoformat(domain_info['expiration_date'].replace('Z', '+00:00'))
                    days_until_expiry = (exp_date - datetime.now(exp_date.tzinfo)).days
                    
                    embed.add_field(
                        name="Expiration Date",
                        value=f"{exp_date.strftime('%Y-%m-%d')}",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Days Left",
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
        # Import validation functions
        from .script import normalize_domain
        
        # Normalize domain for comparison
        normalized_domain = normalize_domain(domain)
        
        success = remove_domain_monitor(domain, interaction.user.id)
        
        if success:
            embed = discord.Embed(
                title="✅ Domain Monitor Removed",
                description=f"Domain **{normalized_domain}** has been removed from the monitor list",
                color=0x00ff00
            )
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Domain Not Found",
                description=f"Domain **{normalized_domain}** is not in your monitor list",
                color=0xff0000
            )
            embed.add_field(
                name="Tip",
                value="Use `/domain-monitor-list` to see your monitored domains",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            
    except Exception as e:
        await interaction.followup.send(f"❌ Error removing domain monitor: {str(e)}")


async def list_monitors_command(interaction: discord.Interaction):
    """List all monitored domains for the user."""
    await interaction.response.defer()
    
    try:
        domains = list_monitored_domains(interaction.user.id)
        
        if not domains:
            await interaction.followup.send("📋 You are not monitoring any domains")
            return
            
        embed = discord.Embed(
            title=f"📋 Your Domain Monitor List ({len(domains)} domains)",
            color=0x0099ff
        )
        
        for i, domain_data in enumerate(domains, 1):
            domain = domain_data['domain']
            expiration_date = domain_data.get('expiration_date', 'Unknown')
            registrar = domain_data.get('registrar', 'Unknown')
            registrant_org = domain_data.get('registrant_organization', 'Unknown')
            
            if expiration_date and expiration_date != 'Unknown':
                try:
                    exp_date = datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
                    days_until_expiry = (exp_date - datetime.now(exp_date.tzinfo)).days
                    
                    status_emoji = "🟢"  # Green
                    if days_until_expiry <= 7:
                        status_emoji = "🔴"  # Red
                    elif days_until_expiry <= 30:
                        status_emoji = "🟡"  # Yellow
                    
                    # Create detailed info
                    domain_info = f"**Expires:** {exp_date.strftime('%Y-%m-%d')}\n"
                    domain_info += f"**Days Left:** {days_until_expiry}\n"
                    domain_info += f"**Registrar:** {registrar}\n"
                    if registrant_org and registrant_org != 'Unknown':
                        domain_info += f"**Organization:** {registrant_org}"
                        
                    embed.add_field(
                        name=f"{status_emoji} {domain}",
                        value=domain_info,
                        inline=True
                    )
                except:
                    embed.add_field(
                        name=f"⚪ {domain}",
                        value=f"Expiration Date: {expiration_date}\nRegistrar: {registrar}",
                        inline=True
                    )
            else:
                embed.add_field(
                    name=f"⚪ {domain}",
                    value=f"Expiration Date: Unknown\nRegistrar: {registrar}",
                    inline=True
                )
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error getting monitor list: {str(e)}")


async def check_domains_now_command(interaction: discord.Interaction):
    """Manually check all monitored domains for the user."""
    await interaction.response.defer()
    
    try:
        from .script import get_expiring_domains_without_update, get_all_monitored_domains
        
        # Get all monitored domains
        all_monitors = get_all_monitored_domains()
        user_id_str = str(interaction.user.id)
        
        if user_id_str not in all_monitors or not all_monitors[user_id_str]:
            await interaction.followup.send("📋 You are not monitoring any domains")
            return
        
        # Check for expiring domains without updating data
        expiring_domains = get_expiring_domains_without_update()
        user_expiring = expiring_domains.get(user_id_str, [])
        
        if not user_expiring:
            embed = discord.Embed(
                title="✅ Domain Check Complete",
                description="All your monitored domains are safe!",
                color=0x00ff00
            )
            embed.add_field(
                name="Status",
                value="No domains expiring in the next 7 days",
                inline=False
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Send notification for expiring domains
        embed = discord.Embed(
            title="⚠️ Manual Domain Check - Expiry Found",
            description="The following domains will expire in 7 days:",
            color=0xff0000
        )
        
        for domain_data in user_expiring:
            domain = domain_data['domain']
            days_left = domain_data.get('days_until_expiry', 0)
            registrar = domain_data.get('registrar', 'Unknown')
            
            if days_left <= 1:
                status_emoji = "🚨"
            elif days_left <= 3:
                status_emoji = "🔴"
            else:
                status_emoji = "🟡"
            
            embed.add_field(
                name=f"{status_emoji} {domain}",
                value=f"Remaining time: **{days_left}** days\nRegistrar: {registrar}",
                inline=True
            )
        
        embed.set_footer(text=f"Manual check time: {datetime.now().strftime('%Y-%m-%d')}")
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error checking domains: {str(e)}") 