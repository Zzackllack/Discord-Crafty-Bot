import discord
from discord.ext import commands
from discord import app_commands
from utils.api_helper import server_action

class StopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stop", description="Stop a server by providing its server ID.")
    async def stop(self, interaction: discord.Interaction, server_id: str):
        try:
            data = server_action(server_id, "stop_server")
            
            embed = discord.Embed(
                color=discord.Color.green() if data.get("status") == "ok" else discord.Color.red()
            )
            
            if data.get("status") == "ok":
                embed.title = "🛑 Server Stopping"
                embed.description = f"Server **{server_id}** is stopping."
            else:
                embed.title = "❌ Error Stopping Server"
                embed.description = f"Failed to stop server **{server_id}**."
            
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Error",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(StopCommand(bot))
