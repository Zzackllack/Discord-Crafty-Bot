import discord
from discord.ext import commands
from discord import app_commands
from utils.api_helper import get_all_servers, get_server_stats

class ServersCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="servers", description="List all available Minecraft servers")
    async def servers(self, interaction: discord.Interaction):
        try:
            data = get_all_servers()
            
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
                            stats_data = get_server_stats(server_id)
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

async def setup(bot):
    await bot.add_cog(ServersCommand(bot))
