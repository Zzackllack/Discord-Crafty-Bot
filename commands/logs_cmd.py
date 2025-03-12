import discord
from discord.ext import commands
from discord import app_commands
from utils.api_helper import get_server_logs

class LogsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="logs",
        description="Display the last few lines of a server's logs by providing its server ID.",
    )
    async def logs(self, interaction: discord.Interaction, server_id: str, lines: int = 15):
        try:
            # Get the logs
            data = get_server_logs(server_id)
            
            # Create embed
            embed = discord.Embed(
                title=f"📜 Logs for Server {server_id}",
                color=discord.Color.blue()
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
                    embed.description = "No logs available for this server."
                    embed.color = discord.Color.light_gray()
            else:
                embed.description = f"Failed to retrieve logs for server `{server_id}`."
                embed.color = discord.Color.red()
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Error Retrieving Logs",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LogsCommand(bot))
