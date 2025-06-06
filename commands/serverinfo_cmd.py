import discord
from discord.ext import commands
from discord import app_commands
from utils.api_helper import get_server_info, get_server_stats

class ServerInfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(
        name="serverinfo", description="Get details of a server. Provide the server ID."
    )
    async def serverinfo(self, interaction: discord.Interaction, server_id: str):
        # Defer the response to prevent timeout
        await interaction.response.defer(thinking=True)
        
        try:
            # Get server info
            data = get_server_info(server_id)

            if data.get("status") == "ok":
                server = data.get("data", {})

                # Get server status
                status = "⚠️ Unknown"
                embed_color = discord.Color.gold()  
                # Default to yellow/gold for unknown
                try:
                    stats_data = get_server_stats(server_id)
                    if stats_data.get("status") == "ok":
                        stats = stats_data.get("data", {})
                        if stats.get("running", False):
                            status = "🟢 Online"
                            embed_color = discord.Color.green()
                        else:
                            status = "🔴 Offline"
                            embed_color = discord.Color.red()
                except:
                    status = "⚠️ Status Unavailable"
                    embed_color = discord.Color.gold()

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
                    color=embed_color
                )

                # Add fields
                embed.add_field(name="🆔 Server ID", value=server.get('server_id'), inline=True)
                embed.add_field(name="🏷️ Server Type", value=server.get('type'), inline=True)
                embed.add_field(name="🔌 Status", value=status, inline=True)
                if public_server_ip == "Failed to retrieve public IP address":
                    embed.add_field(
                        name="🌐 Internal IP Address", value=internal_server_ip, inline=True
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

                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"Failed to retrieve information for server ID `{server_id}`.")
        except Exception as e:
            await interaction.followup.send(f"Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(ServerInfoCommand(bot))
