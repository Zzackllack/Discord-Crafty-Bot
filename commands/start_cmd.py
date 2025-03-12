import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.api_helper import server_action, get_server_logs, get_server_stats

class StartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="start", description="Start a server by providing its server ID."
    )
    async def start(self, interaction: discord.Interaction, server_id: str):
        try:
            # Initial response with loading animation
            loading_embed = discord.Embed(
                title="🚀 Server Starting",
                description="Starting server, please wait...",
                color=discord.Color.blue()
            )
            
            await interaction.response.send_message(embed=loading_embed)

            # Start the server
            data = server_action(server_id, "start_server")

            if data.get("status") != "ok":
                # If there's an error, update the message immediately
                error_embed = discord.Embed(
                    title="❌ Error Starting Server",
                    description=f"Failed to start server **{server_id}**.",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=error_embed)
                return

            # Wait a bit for server to begin startup process
            await asyncio.sleep(5)

            # Update the message with logs 5 times, every 10 seconds
            for i in range(5):
                try:
                    # Get server logs
                    logs_data = get_server_logs(server_id)

                    # Create updated embed with logs
                    log_embed = discord.Embed(
                        title=f"🚀 Server {server_id} Starting - Update {i+1}/5",
                        description="Server is starting up. Here are the latest logs:",
                        color=discord.Color.green()
                    )

                    if logs_data.get("status") == "ok":
                        log_lines = logs_data.get("data", [])
                        if log_lines:
                            # Show the last 10 lines
                            log_text = "\n".join(log_lines[-10:])
                            # Truncate if too long
                            if len(log_text) > 1000:
                                log_text = "...(truncated)...\n" + log_text[-1000:]

                            log_embed.add_field(
                                name="📜 Latest Logs",
                                value=f"```{log_text}```",
                                inline=False
                            )
                        else:
                            log_embed.add_field(
                                name="📜 Logs",
                                value="No logs available yet.",
                                inline=False
                            )
                    else:
                        log_embed.add_field(
                            name="📜 Logs",
                            value="Failed to retrieve logs.",
                            inline=False
                        )

                    # Add server status check
                    try:
                        stats_data = get_server_stats(server_id)
                        if stats_data.get("status") == "ok":
                            stats = stats_data.get("data", {})
                            status = "🟢 Online" if stats.get("running", False) else "🔄 Starting..."
                            log_embed.add_field(
                                name="Status",
                                value=status,
                                inline=True
                            )
                    except Exception as e:
                        log_embed.add_field(
                            name="Status",
                            value="⚠️ Unknown",
                            inline=True
                        )

                    # Update footer with remaining updates info
                    log_embed.set_footer(text=f"Updates remaining: {5-i-1}")

                    # Edit the original message with the new embed
                    await interaction.edit_original_response(embed=log_embed)

                    # Wait 5 seconds between updates (except after the last one)
                    if i < 4:
                        await asyncio.sleep(5)

                except Exception as e:
                    # If an update fails, continue to the next one after logging the error
                    print(f"Error updating logs: {str(e)}")
                    await asyncio.sleep(5)
                    continue

        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Error",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )

            # Check if we've already responded
            try:
                await interaction.edit_original_response(embed=embed)
            except:
                await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(StartCommand(bot))
