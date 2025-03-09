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

# Set up the bot with required intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
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
                # Create a nicr embed for the servers
                embed = discord.Embed(
                    title="Available Minecraft Servers",
                    description="Here are all available servers from Crafty Controller:",
                    color=discord.Color.blue()
                )

                # Add server information to embed
                for server in servers:
                    server_name = server.get('server_name')
                    server_id = server.get('server_id')
                    server_type = server.get('type')

                    # Get server status if possible (running or offline or unk)
                    status = "Unknown"
                    try:
                        stats_response = requests.get(
                            f"{CRAFTY_API_URL}/servers/{server_id}/stats", 
                            headers=HEADERS, 
                            verify=False
                        )
                        stats_data = stats_response.json()
                        if stats_data.get("status") == "ok":
                            stats = stats_data.get("data", {})
                            status = "🟢 Online" if stats.get("running", False) else "🔴 Offline"
                    except:
                        status = "⚠️ Status Unavailable, is the Server unloaded?"

                    # Add field for each server
                    embed.add_field(
                        name=f"Name: {server_name} | ID: *{server_id}*",
                        value=f"**Type:** {server_type}\n**Status:** {status}",
                        inline=False,
                    )

                embed.set_footer(text="Use /serverinfo <id> for more details")
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message("No servers found.")
        else:
            await interaction.response.send_message("Failed to retrieve servers.")
    except Exception as e:
        await interaction.response.send_message(f"Error retrieving servers: {str(e)}")


# -----------------------------
# Slash Command: Server Info
# -----------------------------
@bot.tree.command(
    name="serverinfo", description="Get details of a server. Provide the server ID."
)
async def serverinfo(interaction: discord.Interaction, server_id: str):
    try:
        # Get server info
        response = requests.get(
            f"{CRAFTY_API_URL}/servers/{server_id}", headers=HEADERS, verify=False
        )
        data = response.json()

        if data.get("status") == "ok":
            server = data.get("data", {})

            # Get server status
            status = "⚠️ Unknown"
            try:
                stats_response = requests.get(
                    f"{CRAFTY_API_URL}/servers/{server_id}/stats", 
                    headers=HEADERS, 
                    verify=False
                )
                stats_data = stats_response.json()
                if stats_data.get("status") == "ok":
                    stats = stats_data.get("data", {})
                    status = "🟢 Online" if stats.get("running", False) else "🔴 Offline"
            except:
                status = "⚠️ Status Unavailable"

            # Get public server IP address
            public_server_ip = server.get('server_ip')
            if (
                public_server_ip == "127.0.0.1"
                or public_server_ip == "localhost"
                or public_server_ip == "docker_internal"
            ):
                public_server_ip = "Failed to retrieve public IP address"

            # Get internal server IP address
            if public_server_ip == "Failed to retrieve public IP address":
                internal_server_ip = server.get('server_ip')

            # Create embed
            embed = discord.Embed(
                title=f"Server Information: {server.get('server_name')}",
                description="Detailed information about this Minecraft server:",
                color=discord.Color.blue()
            )

            # Add fields
            embed.add_field(name="🆔 Server ID", value=server.get('server_id'), inline=True)
            embed.add_field(name="🏷️ Server Type", value=server.get('type'), inline=True)
            embed.add_field(name="🔌 Status", value=status, inline=True)
            if public_server_ip == "Failed to retrieve public IP address":
                embed.add_field(
                    name="🌐 Internal  IP Address", value=internal_server_ip, inline=True
                )
                embed.add_field(
                    name="🌐 Public IP Address", value="Failed to retrieve public IP address", inline=True
                )
            else:
                embed.add_field(
                    name="🌐 Public IP Address", value=public_server_ip, inline=True
                )
                embed.add_field(
                    name="🌐 Internal IP Address", value="Cannot get Internal IP!", inline=True
                )
            embed.add_field(name="🔢 Port", value=server.get('server_port'), inline=True)

            embed.set_footer(text="Use /start or /stop to control this server")

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"Failed to retrieve information for server ID `{server_id}`.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {str(e)}")


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
        
        embed = discord.Embed(
            color=discord.Color.green() if data.get("status") == "ok" else discord.Color.red()
        )
        
        if data.get("status") == "ok":
            embed.title = "🚀 Server Starting"
            embed.description = f"Server **{server_id}** is starting."
        else:
            embed.title = "❌ Error Starting Server"
            embed.description = f"Failed to start server **{server_id}**."
        
    except Exception as e:
        embed = discord.Embed(
            title="⚠️ Error",
            description=f"Error: {str(e)}",
            color=discord.Color.red()
        )
    
    await interaction.response.send_message(embed=embed)


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
