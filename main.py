import discord
from discord.ext import commands, tasks
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio

TOKEN = 'YOUR-BOT-TOKEN'

intents = discord.Intents.default()
intents.typing = False
intents.message_content = True
intents.presences = False

bot = commands.Bot(command_prefix='', intents=intents)

activity_price = None

UNISWAP_SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3' # UniswapV3 Mainnet Subgraph
transport = AIOHTTPTransport(url=UNISWAP_SUBGRAPH_URL)
client = Client(transport=transport)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=activity_price)

async def update_price():
    await bot.wait_until_ready()
    while not bot.is_closed():
        query = gql('''
        {
          pool(id: "0x3470447f3cecffac709d3e783a307790b0208d60") {
            token1Price
          }
        }
        ''')

        result = await client.execute_async(query)
        token1Price = round(float(result['pool']['token1Price']), 3)

        global activity_price
        activity_price = discord.Activity(type=discord.ActivityType.watching, name=f'{token1Price} USDT')
        await bot.change_presence(activity=activity_price)

        await asyncio.sleep(60)

@bot.event
async def on_connect():
    bot.loop.create_task(update_price())

bot.run(TOKEN)
