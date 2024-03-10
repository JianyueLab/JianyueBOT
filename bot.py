# imports
import discord
from discord.ext import commands
from discord import app_commands
from settings import TOKEN, default_custom_status, default_status, setting_version
import random
from scripts.zipcode import search_zipcode_jp
from scripts.ipdetails import ipdetails
from scripts.iplocations import iplocations
from scripts.domainreg import cheapest

# 固定不变
intents = discord.Intents.all() 
client = commands.Bot(command_prefix='!', intents=intents)

# 版本号
bot_version = "v0.1.2"
bot_build = "1"
bot_type = "Dev Build"

# 启动之后
@client.event
async def on_ready():
    # 终端输出
    print("Bot is ready for use!")
    # 从配置文件中获取设定的状态
    if default_status == 'idle':
        edit_status = discord.Status.idle
    elif default_status == 'online':
        edit_status = discord.Status.online
    elif default_status == 'do_not_disturb':
        edit_status = discord.Status.dnd
    else:
        print("unknown Status")  
        edit_status = discord.Status.online
    # 自定义状态的内容
    game = discord.Game(default_custom_status)
    await client.change_presence(status=edit_status, activity=game)
    #同步命令 并输出
    try:
        synced = await client.tree.sync()
        print(f"synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    
# /say [things_to_say]
@client.tree.command(name="say", description="Let bot say something.")
@app_commands.describe(things_to_say = "What should I say?")
async def say(interaction: discord.Interaction, things_to_say: str):
    await interaction.response.send_message(f"{things_to_say}")

# /status [choice] [custom]
@client.tree.command(name="status", description="Change the status")
@app_commands.choices(choices=[
    app_commands.Choice(name="Online", value="online"),
    app_commands.Choice(name="idle", value="idle"),
    app_commands.Choice(name="Do Not Disturb", value="dnd"),
])
async def status(interaction: discord.Interaction, choices: app_commands.Choice[str], *, custom_status_message: str):
        if choices.value == "online":
            changed_status = discord.Status.online
        elif choices.value == "idle":
            changed_status = discord.Status.idle
        elif choices.value == "dnd":
            changed_status = discord.Status.dnd
        else:
            await interaction.response.send_message(f"Unknown Status. Please specify 'online', 'idle', 'Do Not Disturb'", ephemeral=True)
            return
        
        game = discord.Game(custom_status_message)
        await client.change_presence(status=changed_status, activity=game)
        await interaction.response.send_message(f"Status Updated!", ephemeral=True)

# /roll 
@client.tree.command(name='roll', description='Roll a dice.')
async def roll(interaction: discord.Interaction):
    number = random.randint(1, 6)
    await interaction.response.send_message(f"Number is {number}")

# /zipcode [country] [zipcode]
@client.tree.command(name='zipcode', description='search address from zipcode')
@app_commands.choices(country=[
    app_commands.Choice(name='Japan', value='JP'),
])
async def zipcode(interaction: discord.Interaction, country: app_commands.Choice[str], zipcode: str):
    await interaction.response.defer(ephemeral=True)
    if country.value == 'JP':
        result = search_zipcode_jp(zipcode)
        if result is None:
            await interaction.followup.send(f"Invalid Zipcode.")
            return
        else:
            await interaction.followup.send(f"**Prefecture 都道府県:** {result['address1']} {result['kana1']}\n**City 市区町村:** {result['address2']} {result['kana2']}\n**Town 町域:** {result['address3']} {result['kana3']}")
            return
    if country.value == 'CN':
        result = "Unavaliable"
        if result is None:
            await interaction.followup.send(f"Invalid Zipcode.")
            return
        else:
            await interaction.followup.send(f"Address: {result}")
            return
    else: 
        await interaction.followup.send(f'Invalid Country.')
        
# /ipdetails
@client.tree.command(name='ipdetail', description="Show the details from IP address")
async def ipdetail(interaction: discord.Interaction, ipaddress: str):
    await interaction.response.defer(ephemeral=True)
    result = ipdetails(ipaddress)
    if result is None:
        await interaction.followup.send(f"Invalid IP address or Inter Error")
        return
    else:
        embed = discord.Embed(
            colour=discord.Colour.blue(),
            title="IP Detail",
            description=(f"This is the Result of {ipaddress}")
        )
        embed.add_field(name='IP address', value=result['ip'])
        embed.add_field(name='IP number', value=result['ip_number'])
        embed.add_field(name='IP version', value=result['ip_version'])
        embed.add_field(name='IP country name', value=result['country_name'])
        embed.add_field(name='IP country code', value=result['country_code2'])
        embed.add_field(name='IP ISP', value=result['isp'])
        embed.add_field(name='IP response_code', value=result['response_code'])
        embed.add_field(name='IP response_message', value=result['response_message'])
        
        await interaction.followup.send(embed=embed)
        return
    
# /iplocation
@client.tree.command(name='iplocation', description="Show the Geolocation from IP address")
async def iplocation(interaction: discord.Interaction, ipaddress: str):
    await interaction.response.defer(ephemeral=True)
    result = iplocations(ipaddress)
    if result is None:
        await interaction.followup.send(f"Invalid IP address or Inter Error")
        return
    else:
        embed = discord.Embed(
            colour=discord.Colour.blue(),
            title="IP Location",
            description=(f"This is the Result of {ipaddress}")
        )
        embed.add_field(name='Query', value=result['query'])
        embed.add_field(name='Timezone', value=result['timezone'])
        embed.add_field(name='Country', value=result['country'])
        embed.add_field(name='City', value=result['city'])
        embed.add_field(name='ISP', value=result['isp'])
        embed.add_field(name='org', value=result['org'])
        embed.add_field(name='ASN', value=result['as'])

        await interaction.followup.send(embed=embed)
        return

# /domain
@client.tree.command(name='domain', description='Find the cheapest domain registrar')
@app_commands.choices(
    order=[
    app_commands.Choice(name='New', value='new'),
    app_commands.Choice(name='Renew', value='renew'),
    app_commands.Choice(name='Transfer', value='transfer'),
    ]
)
async def domain(interaction: discord.Interaction, tld: str, order: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    result = cheapest(tld, str(order))
    if result is None:
        await interaction.followup.send(f"Invalid input or Inter Error")
        return
    else:
        await interaction.followup.send(
            "## Domain Registrar"
            f"\n**TLD**: {result['domain']} **| Order**: {result['order']}"
            "\n### 1st: "
            f"\n- **Registrar**: {result['reg_1']}"
            f"\n- **Currency**: {result['currency_1']}"
            f"\n- **New**: {result['new_1']}"
            f"\n- **Renew**: {result['renew_1']}"
            f"\n- **Transfer**: {result['transfer_1']}"
            f"\n- **Registrar Website**: {result['reg_web_1']}"
            "\n### 2nd: "
            f"\n- **Registrar**: {result['reg_2']}"
            f"\n- **Currency**: {result['currency_2']}"
            f"\n- **New**: {result['new_2']}"
            f"\n- **Renew**: {result['renew_2']}"
            f"\n- **Transfer**: {result['transfer_2']}"
            f"\n- **Registrar Website**: {result['reg_web_2']}"
            "\n### 3rd: "
            f"\n- **Registrar**: {result['reg_3']}"
            f"\n- **Currency**: {result['currency_3']}"
            f"\n- **New**: {result['new_3']}"
            f"\n- **Renew**: {result['renew_3']}"
            f"\n- **Transfer**: {result['transfer_3']}"
            f"\n- **Registrar Website**: {result['reg_web_3']}"
            "\n### 4th: "
            f"\n- **Registrar**: {result['reg_4']}"
            f"\n- **Currency**: {result['currency_4']}"
            f"\n- **New**: {result['new_4']}"
            f"\n- **Renew**: {result['renew_4']}"
            f"\n- **Transfer**: {result['transfer_4']}"
            f"\n- **Registrar Website**: {result['reg_web_4']}"
            "\n### 5th: "
            f"\n- **Registrar**: {result['reg_4']}"
            f"\n- **Currency**: {result['currency_4']}"
            f"\n- **New**: {result['new_4']}"
            f"\n- **Renew**: {result['renew_4']}"
            f"\n- **Transfer**: {result['transfer_4']}"
            f"\n- **Registrar Website**: {result['reg_web_4']}"
            )
        return
    
# /registrars
@client.tree.command(name='registrars', description='Find the cheapest domain registrar')
@app_commands.choices(
    order=[
        app_commands.Choice(name='New', value='new'),
        app_commands.Choice(name='Renew', value='renew'),
        app_commands.Choice(name='Transfer', value='transfer'),
    ],
    registrar=[
        app_commands.Choice(name='阿里云', value='aliyun'),
        app_commands.Choice(name='爱名网', value='22cn'),
        app_commands.Choice(name='百度智能云', value='baidu'),
        app_commands.Choice(name='华为云', value='huawei'),
        app_commands.Choice(name='火山引擎', value='volcengine'),
        app_commands.Choice(name='具名网', value='juming'),
        app_commands.Choice(name='趣域网', value='quyu'),
        app_commands.Choice(name='腾讯云', value='tencent'),
        app_commands.Choice(name='西部数码', value='west'),
        app_commands.Choice(name='西部数码国际', value='363hk'),
        app_commands.Choice(name='新网', value='xinnet'),
        app_commands.Choice(name='易名', value='ename'),
        app_commands.Choice(name='中资源', value='zzy'),
        app_commands.Choice(name='101domain', value='101domain'),
        app_commands.Choice(name='Afriregister', value='afriregister'),
        app_commands.Choice(name='Alibaba Cloud', value='alibaba'),
        app_commands.Choice(name='ALLDomains', value='alldomains'),
        app_commands.Choice(name='CanSpace', value='canspace'),
        app_commands.Choice(name='Cloudflare', value='cloudflare'),
        app_commands.Choice(name='Cosmotown', value='cosmotown'),
        app_commands.Choice(name='DDD.com', value='ddd'),
        app_commands.Choice(name='Directnic', value='directnic'),
        app_commands.Choice(name='Domain.com', value='domaincom'),
        app_commands.Choice(name='domgate', value='domgate'),
        app_commands.Choice(name='dotology', value='dotology'),
        app_commands.Choice(name='DreamHost', value='dreamhost'),
        app_commands.Choice(name='Dynadot', value='dynadot'),
        app_commands.Choice(name='EnCirca', value='encirca'),
        app_commands.Choice(name='Enom', value='enom'),
        app_commands.Choice(name='Epik', value='epik'),
        app_commands.Choice(name='gandi.net', value='gandi'),
        app_commands.Choice(name='Globalhost', value='globalhost'),
        app_commands.Choice(name='GNAME', value='gname'),
        app_commands.Choice(name='GoDaddy', value='godaddy'),
        app_commands.Choice(name='Google Domains', value='google'),
        app_commands.Choice(name='Google Domains TR', value='googletr'),
        app_commands.Choice(name='HEXONET', value='hexonet'),
        app_commands.Choice(name='hover', value='hover'),
        app_commands.Choice(name='InnovaHost', value='innovahost'),
        app_commands.Choice(name='internet.bs', value='internetbs'),
        app_commands.Choice(name='INWX', value='inwx'),
        app_commands.Choice(name='Marcaria', value='marcaria'),
        app_commands.Choice(name='MrDomain', value='mrdomain'),
        app_commands.Choice(name='Name.com', value='namecom'),
        app_commands.Choice(name='namecheap', value='namecheap'),
        app_commands.Choice(name='NameSilo', value='namesilo'),
        app_commands.Choice(name='netim', value='netim'),
        app_commands.Choice(name='one.com', value='onecom'),
        app_commands.Choice(name='OnlyDomains', value='onlydomains'),
        app_commands.Choice(name='OpenSRS', value='opensrs'),
        app_commands.Choice(name='OVHcloud', value='ovh'),
        app_commands.Choice(name='Pananames', value='pananames'),
        app_commands.Choice(name='porkbun', value='porkbun'),
        app_commands.Choice(name='Rebel', value='rebel'),
        app_commands.Choice(name='Regery', value='regery'),
        app_commands.Choice(name='regtons', value='regtons'),
        app_commands.Choice(name='Sav', value='sav'),
        app_commands.Choice(name='Spaceship', value='spaceship'),
        app_commands.Choice(name='TFhost', value='tfhost'),
        app_commands.Choice(name='Truehost', value='truehost'),
        app_commands.Choice(name='west.xyz', value='west.xyz'),
        app_commands.Choice(name='WordPress.com', value='wordpress'),
        app_commands.Choice(name='Zone', value='zone'),
    ]
)
async def registrars(interaction: discord.Interaction, registrar: str, order: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    result = cheapest(registrar, str(order))
    if result is None:
        await interaction.followup.send(f"Invalid input or Inter Error")
        return
    else:
        await interaction.followup.send(
            "## Domain Registrar"
            f"\n**Registrar**: {result['reg']} **Registrar Website**: {result['reg_web']} **| Order**: {result['order']}"
            "\n### 1st: "
            f"\n**Domain**: {result['domain_1']}"
            f"\n**New**: {result['new_1']}"
            f"\n**Renew**: {result['renew_1']}"
            f"\n**Transfer**: {result['transfer_1']}"
            f"\n**Currency**: {result['currency_1']}"
            "\n### 2nd: "
            f"\n**Domain**: {result['domain_2']}"
            f"\n**New**: {result['new_2']}"
            f"\n**Renew**: {result['renew_2']}"
            f"\n**Transfer**: {result['transfer_2']}"
            f"\n**Currency**: {result['currency_2']}"
            "\n### 3rd: "
            f"\n**Domain**: {result['domain_3']}"
            f"\n**New**: {result['new_3']}"
            f"\n**Renew**: {result['renew_3']}"
            f"\n**Transfer**: {result['transfer_3']}"
            f"\n**Currency**: {result['currency_3']}"
            "\n### 4th: "
            f"\n**Domain**: {result['domain_4']}"
            f"\n**New**: {result['new_4']}"
            f"\n**Renew**: {result['renew_4']}"
            f"\n**Transfer**: {result['transfer_4']}"
            f"\n**Currency**: {result['currency_4']}"
            "\n### 5th: "
            f"\n**Domain**: {result['domain_5']}"
            f"\n**New**: {result['new_5']}"
            f"\n**Renew**: {result['renew_5']}"
            f"\n**Transfer**: {result['transfer_5']}"
            f"\n**Currency**: {result['currency_5']}"
        )
        return

# /info
@client.tree.command(name='info', description="Some information about this bot")
async def version(interaction: discord.Interaction):
    await interaction.response.send_message(
        "## JianyueBot"
        "This bot was developed by [JianyueLab](https://eke.vin). If you have any questions or require assistance, please contact @jianyuehugo."
        "**Github Repo**: https://github.com/jianyuelab/jianyuebot"
        f"**Bot Version:** {bot_version}\n**Bot Build:** {bot_build}\n**Settings Version:** {setting_version}\n**Build Type:** {bot_type}"
        , ephemeral=True)

client.run(TOKEN)
