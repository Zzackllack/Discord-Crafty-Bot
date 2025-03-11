import discord
from discord.ext import commands
import os
import json
import urllib3
import asyncio
from utils.api_helper import load_config

# Disable insecure warnings (if using self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load configuration
config = load_config()
DISCORD_TOKEN = config.get("discord_token")

# Set up the bot with required intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
bot = commands.Bot(command_prefix="!", intents=intents)

# When the bot is ready, sync slash commands
@bot.event
async def on_ready():
    try:
        # Load all command modules
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                await bot.load_extension(f'commands.{filename[:-3]}')
        
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

# Run the bot
bot.run(DISCORD_TOKEN)
