import discord
from discord.ext import commands
import requests
import json
import os
import urllib3

# Suppress insecure request warnings if you use self-signed certificates.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load configuration from config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

DISCORD_TOKEN = config.get("discord_token")
CRAFTY_API_TOKEN = config.get("crafty_api_token")
CRAFTY_API_URL = config.get("crafty_api_url", "https://localhost:8443/api/v2")

# Prepare default headers for API calls
HEADERS = {
    "Authorization": f"Bearer {CRAFTY_API_TOKEN}",
    "Content-Type": "application/json"
}

# Set up Discord bot with command prefix !
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents, description="Crafty Controller Bot")

# -----------------------------
# Command: List All Servers
# -----------------------------
@bot.command(name="servers", help="List all available Minecraft servers")
async def list_servers(ctx):
    try:
        response = requests.get(f"{CRAFTY_API_URL}/servers", headers=HEADERS, verify=False)
        data = response.json()
        if data.get("status") == "ok":
            servers = data.get("data", [])
            if servers:
                message = "**Available Servers:**\n"
                for server in servers:
                    message += f"• **ID:** {server.get('server_id')}, **Name:** {server.get('server_name')}, **Type:** {server.get('type')}\n"
            else:
                message = "No servers found."
        else:
            message = "Failed to retrieve servers."
    except Exception as e:
        message = f"Error retrieving servers: {str(e)}"
    await ctx.send(message)

# -----------------------------
# Command: Get Server Information
# -----------------------------
@bot.command(name="serverinfo", help="Get details of a server. Usage: !serverinfo <server_id>")
async def server_info(ctx, server_id: str):
    try:
        response = requests.get(f"{CRAFTY_API_URL}/servers/{server_id}", headers=HEADERS, verify=False)
        data = response.json()
        if data.get("status") == "ok":
            server = data.get("data", {})
            message = (
                f"**Server Information:**\n"
                f"• **ID:** {server.get('server_id')}\n"
                f"• **Name:** {server.get('server_name')}\n"
                f"• **Type:** {server.get('type')}\n"
                f"• **IP:** {server.get('server_ip')}\n"
                f"• **Port:** {server.get('server_port')}\n"
            )
        else:
            message = f"Failed to retrieve information for server ID {server_id}."
    except Exception as e:
        message = f"Error: {str(e)}"
    await ctx.send(message)

# -----------------------------
# Command: Start a Server
# -----------------------------
@bot.command(name="start", help="Start a server. Usage: !start <server_id>")
async def start_server(ctx, server_id: str):
    try:
        response = requests.post(f"{CRAFTY_API_URL}/servers/{server_id}/action/start_server", headers=HEADERS, verify=False)
        data = response.json()
        if data.get("status") == "ok":
            message = f"Server **{server_id}** is starting."
        else:
            message = f"Failed to start server **{server_id}**."
    except Exception as e:
        message = f"Error: {str(e)}"
    await ctx.send(message)

# -----------------------------
# Command: Stop a Server
# -----------------------------
@bot.command(name="stop", help="Stop a server. Usage: !stop <server_id>")
async def stop_server(ctx, server_id: str):
    try:
        response = requests.post(f"{CRAFTY_API_URL}/servers/{server_id}/action/stop_server", headers=HEADERS, verify=False)
        data = response.json()
        if data.get("status") == "ok":
            message = f"Server **{server_id}** is stopping."
        else:
            message = f"Failed to stop server **{server_id}**."
    except Exception as e:
        message = f"Error: {str(e)}"
    await ctx.send(message)

# -----------------------------
# Command: Get Server Logs
# -----------------------------
@bot.command(name="logs", help="Get the last few lines of a server's logs. Usage: !logs <server_id>")
async def get_logs(ctx, server_id: str):
    try:
        # Use query parameters to get raw log file data (adjust as needed)
        params = {"raw": "true", "file": "true"}
        response = requests.get(f"{CRAFTY_API_URL}/servers/{server_id}/logs", headers=HEADERS, params=params, verify=False)
        data = response.json()
        if data.get("status") == "ok":
            logs = data.get("data", [])
            if logs:
                # To avoid hitting Discord's message limit, only show the last 10 lines
                log_text = "\n".join(logs[-10:])
                message = f"**Logs for server {server_id}:**\n```{log_text}```"
            else:
                message = "No logs available for this server."
        else:
            message = f"Failed to retrieve logs for server {server_id}."
    except Exception as e:
        message = f"Error: {str(e)}"
    await ctx.send(message)

# -----------------------------
# Bot Ready Event
# -----------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Crafty Controller Bot is now running!")

# Run the bot using the Discord token from config.json
bot.run(DISCORD_TOKEN)
