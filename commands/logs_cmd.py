import discord
from discord.ext import commands
from discord import app_commands
from utils.api_helper import get_server_logs, get_server_stats, get_server_info

class LogsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="logs",
        description="Display the last few lines of a server's logs by providing its server ID.",
    )
    async def logs(self, interaction: discord.Interaction, server_id: str, lines: int = 15):
        # Defer the response to prevent timeout issues
        await interaction.response.defer(thinking=True)
        
        try:
            # First check if the server exists and is online
            server_exists = False
            server_online = False
            server_name = f"Server {server_id}"
            
            # Verify the server exists
            try:
                server_info = get_server_info(server_id)
                if server_info.get("status") == "ok":
                    server_exists = True
                    server_name = server_info.get("data", {}).get("server_name", f"Server {server_id}")
            except Exception as e:
                print(f"Error checking server existence: {e}")
            
            # Check if the server is online
            if server_exists:
                try:
                    stats_data = get_server_stats(server_id)
                    if stats_data.get("status") == "ok":
                        stats = stats_data.get("data", {})
                        server_online = stats.get("running", False)
                except Exception as e:
                    print(f"Error checking server status: {e}")
            
            # If server doesn't exist, return an error
            if not server_exists:
                error_embed = discord.Embed(
                    title="❌ Server Not Found",
                    description=f"Could not find a server with ID `{server_id}`.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=error_embed)
                return
                
            # If server is not online, return an appropriate message
            if not server_online:
                offline_embed = discord.Embed(
                    title="❌ Server Offline",
                    description=f"Server `{server_name}` (ID: `{server_id}`) is currently offline. Logs are only available for online servers.",
                    color=discord.Color.red()
                )
                offline_embed.set_footer(text="Use /start command to start the server first")
                await interaction.followup.send(embed=offline_embed)
                return
            
            # Server exists and is online, get the logs
            data = get_server_logs(server_id)
            
            # Determine color based on server status (should be green since we already checked it's online)
            embed_color = discord.Color.green()
            
            # Create embed
            embed = discord.Embed(
                title=f"📜 Logs for {server_name}",
                color=embed_color
            )
            
            if data.get("status") == "ok":
                log_lines = data.get("data", [])
                if log_lines:
                    # Show the specified number of lines (default 15)
                    log_text = "\n".join(log_lines[-lines:])
                    # Truncate if too long for Discord embed (max 4096 characters)
                    if len(log_text) > 4000:
                        log_text = log_text[-4000:]
                        log_text = "...(truncated)...\n" + log_text
                    
                    embed.description = f"```{log_text}```"
                    embed.set_footer(text=f"Showing last {min(lines, len(log_lines))} lines")
                else:
                    embed.description = "No logs available for this server even though it's online. This may happen if the server just started or if there's an issue with the log system."
                    embed.color = discord.Color.gold()
            else:
                embed.description = f"Failed to retrieve logs for server `{server_id}`. Error: {data.get('message', 'Unknown error')}"
                embed.color = discord.Color.red()
                
            await interaction.followup.send(embed=embed)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="⚠️ Error Retrieving Logs",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            
            # Try to send the error message
            try:
                await interaction.followup.send(embed=error_embed)
            except Exception as followup_error:
                print(f"Failed to send error message: {followup_error}")

async def setup(bot):
    await bot.add_cog(LogsCommand(bot))
