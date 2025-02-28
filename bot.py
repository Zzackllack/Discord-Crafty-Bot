import discord
from discord.ext import commands
import requests
import json
import urllib3

# Disable insecure warnings (if using self-signed certificates)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

DISCORD_TOKEN = config.get("discord_token")
CRAFTY_API_TOKEN = config.get("crafty_api_token")
CRAFTY_API_URL = config.get("crafty_api_url", "https://localhost:8443/api/v2")

# Common headers for API calls
HEADERS = {
    "Authorization": f"Bearer {CRAFTY_API_TOKEN}",
    "Content-Type": "application/json",
}

# Set up the bot with default intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# When the bot is ready, sync slash commands
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


# -----------------------------
# Slash Command: List Servers
# -----------------------------
@bot.tree.command(name="servers", description="List all available Minecraft servers")
async def servers(interaction: discord.Interaction):
    try:
        response = requests.get(
            f"{CRAFTY_API_URL}/servers", headers=HEADERS, verify=False
        )
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
    await interaction.response.send_message(message)


# -----------------------------
# Slash Command: Server Info
# -----------------------------
@bot.tree.command(
    name="serverinfo", description="Get details of a server. Provide the server ID."
)
async def serverinfo(interaction: discord.Interaction, server_id: str):
    try:
        response = requests.get(
            f"{CRAFTY_API_URL}/servers/{server_id}", headers=HEADERS, verify=False
        )
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
            message = f"Failed to retrieve information for server ID `{server_id}`."
    except Exception as e:
        message = f"Error: {str(e)}"
    await interaction.response.send_message(message)


# -----------------------------
# Slash Command: Start Server
# -----------------------------
@bot.tree.command(
    name="start", description="Start a server by providing its server ID."
)
async def start(interaction: discord.Interaction, server_id: str):
    try:
        response = requests.post(
            f"{CRAFTY_API_URL}/servers/{server_id}/action/start_server",
            headers=HEADERS,
            verify=False,
        )
        data = response.json()
        if data.get("status") == "ok":
            message = f"Server **{server_id}** is starting."
        else:
            message = f"Failed to start server **{server_id}**."
    except Exception as e:
        message = f"Error: {str(e)}"
    await interaction.response.send_message(message)


# -----------------------------
# Slash Command: Stop Server
# -----------------------------
@bot.tree.command(name="stop", description="Stop a server by providing its server ID.")
async def stop(interaction: discord.Interaction, server_id: str):
    try:
        response = requests.post(
            f"{CRAFTY_API_URL}/servers/{server_id}/action/stop_server",
            headers=HEADERS,
            verify=False,
        )
        data = response.json()
        if data.get("status") == "ok":
            message = f"Server **{server_id}** is stopping."
        else:
            message = f"Failed to stop server **{server_id}**."
    except Exception as e:
        message = f"Error: {str(e)}"
    await interaction.response.send_message(message)


# -----------------------------
# Slash Command: Get Server Logs
# -----------------------------
@bot.tree.command(
    name="logs",
    description="Display the last few lines of a server's logs by providing its server ID.",
)
async def logs(interaction: discord.Interaction, server_id: str):
    try:
        # Adjust query parameters as needed
        params = {"raw": "true", "file": "true"}
        response = requests.get(
            f"{CRAFTY_API_URL}/servers/{server_id}/logs",
            headers=HEADERS,
            params=params,
            verify=False,
        )
        data = response.json()
        if data.get("status") == "ok":
            log_lines = data.get("data", [])
            if log_lines:
                # Show only the last 10 lines to avoid message limits
                log_text = "\n".join(log_lines[-10:])
                message = f"**Logs for server {server_id}:**\n```{log_text}```"
            else:
                message = "No logs available for this server."
        else:
            message = f"Failed to retrieve logs for server `{server_id}`."
    except Exception as e:
        message = f"Error: {str(e)}"
    await interaction.response.send_message(message)


# Run the bot
bot.run(DISCORD_TOKEN)
