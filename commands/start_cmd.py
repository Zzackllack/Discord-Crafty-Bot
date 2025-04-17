import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import re
from utils.api_helper import server_action, get_server_logs, get_server_stats, get_server_info

class StartCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="start", description="Start a server by providing its server ID."
    )
    async def start(self, interaction: discord.Interaction, server_id: str):
        try:
            # Check if server exists and get its name
            server_name = f"Server {server_id}"
            try:
                server_info = get_server_info(server_id)
                if server_info.get("status") == "ok":
                    server_data = server_info.get("data", {})
                    server_name = server_data.get("server_name", f"Server {server_id}")
            except Exception as e:
                print(f"Error getting server info: {e}")
            
            # Initial response with loading animation
            loading_embed = discord.Embed(
                title="🚀 Server Starting",
                description=f"Starting {server_name}, please wait...",
                color=discord.Color.blue()
            )
            
            await interaction.response.send_message(embed=loading_embed)

            # Check if server is already running
            already_running = False
            try:
                stats_data = get_server_stats(server_id)
                if stats_data.get("status") == "ok":
                    stats = stats_data.get("data", {})
                    already_running = stats.get("running", False)
            except Exception as e:
                print(f"Error checking server status: {e}")

            if already_running:
                already_running_embed = discord.Embed(
                    title="ℹ️ Server Already Running",
                    description=f"{server_name} is already online.",
                    color=discord.Color.green()
                )
                await interaction.edit_original_response(embed=already_running_embed)
                return
                
            # Start the server
            data = server_action(server_id, "start_server")

            if data.get("status") != "ok":
                # If there's an error, update the message immediately
                error_embed = discord.Embed(
                    title="❌ Error Starting Server",
                    description=f"Failed to start {server_name}. Error: {data.get('message', 'Unknown error')}",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=error_embed)
                return

            # Wait a bit for server to begin startup process
            await asyncio.sleep(2)

            # Pattern to look for in logs to determine if server is fully started
            done_pattern = re.compile(r"\[.*?\] \[.*?INFO\].*?Done \(.*?\)! For help, type \"help\"")
            server_fully_started = False
            
            # Update the message every 5 seconds until server is fully started or max retries reached
            max_updates = 12  # 60 seconds maximum wait time
            for i in range(max_updates):
                try:
                    # Get server logs
                    logs_data = get_server_logs(server_id)

                    # Check server status to determine embed color and state
                    is_running = False
                    embed_color = discord.Color.gold()  # Default yellow for starting
                    
                    try:
                        stats_data = get_server_stats(server_id)
                        if stats_data.get("status") == "ok":
                            stats = stats_data.get("data", {})
                            is_running = stats.get("running", False)
                            if is_running:
                                embed_color = discord.Color.green()  # Green if running
                            else:
                                embed_color = discord.Color.gold()   # Yellow if still starting
                    except Exception as e:
                        print(f"Error checking server status: {e}")
                    
                    # Create updated embed
                    status_text = "🔄 Starting..." if not server_fully_started else "✅ Started"
                    log_embed = discord.Embed(
                        title=f"🚀 {server_name} - {status_text}",
                        description=f"Update {i+1}/{max_updates}: Server is {status_text.lower()}",
                        color=embed_color
                    )

                    # Add logs if available and scan for "Done" message
                    log_text = ""
                    if logs_data.get("status") == "ok":
                        log_lines = logs_data.get("data", [])
                        if log_lines:
                            # Scan logs for the "Done" message
                            for line in log_lines:
                                if done_pattern.search(line):
                                    server_fully_started = True
                                    log_embed.color = discord.Color.green()
                                    status_text = "✅ Started and Ready!"
                                    log_embed.title = f"🚀 {server_name} - {status_text}"
                                    log_embed.description = f"The server has fully started and is ready to use!"
                                    break
                                    
                            # Show the last 10 lines of logs
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

                    # Add server status field
                    if server_fully_started:
                        log_embed.add_field(
                            name="Status",
                            value="✅ Ready to use",
                            inline=True
                        )
                    elif is_running:
                        log_embed.add_field(
                            name="Status",
                            value="🟢 Online (Starting up...)",
                            inline=True
                        )
                    else:
                        log_embed.add_field(
                            name="Status",
                            value="🔄 Starting...",
                            inline=True
                        )

                    # Add info about players if server is running
                    if is_running and stats_data.get("status") == "ok":
                        stats = stats_data.get("data", {})
                        player_count = f"{stats.get('online', 0)}/{stats.get('max', 0)}"
                        log_embed.add_field(
                            name="Players",
                            value=player_count,
                            inline=True
                        )

                    # Update footer with remaining updates info or success message
                    if server_fully_started:
                        log_embed.set_footer(text="Server is fully started and ready to use")
                    else:
                        log_embed.set_footer(text=f"Updates remaining: {max_updates-i-1}")

                    # Edit the original message with the new embed
                    await interaction.edit_original_response(embed=log_embed)
                    
                    # If server is fully started, break the loop
                    if server_fully_started:
                        break
                    
                    # Wait 5 seconds between updates (except after the last one)
                    if i < max_updates - 1:
                        await asyncio.sleep(5)

                except Exception as e:
                    # If an update fails, continue to the next one after logging the error
                    print(f"Error updating startup status: {e}")
                    await asyncio.sleep(5)
                    continue
                    
            # Final message if we hit the timeout but server is still starting
            if not server_fully_started and i == max_updates - 1:
                timeout_embed = discord.Embed(
                    title=f"⚠️ {server_name} - Start Timeout",
                    description="The server is still starting up but taking longer than expected. It may need more time to fully initialize.",
                    color=discord.Color.gold()
                )
                timeout_embed.add_field(
                    name="Status",
                    value="🔄 Starting (taking longer than expected)",
                    inline=True
                )
                timeout_embed.set_footer(text="You can check status with /serverinfo or /logs commands")
                await interaction.edit_original_response(embed=timeout_embed)

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
