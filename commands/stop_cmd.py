import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.api_helper import server_action, get_server_stats, get_server_info, get_server_logs

class StopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stop", description="Stop a server by providing its server ID.")
    async def stop(self, interaction: discord.Interaction, server_id: str):
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
                title="🛑 Server Stopping",
                description=f"Stopping {server_name}, please wait...",
                color=discord.Color.gold()
            )
            
            await interaction.response.send_message(embed=loading_embed)

            # Send stop command to server
            data = server_action(server_id, "stop_server")

            if data.get("status") != "ok":
                # If there's an error, update the message immediately
                error_embed = discord.Embed(
                    title="❌ Error Stopping Server",
                    description=f"Failed to stop {server_name}. Error: {data.get('message', 'Unknown error')}",
                    color=discord.Color.red()
                )
                await interaction.edit_original_response(embed=error_embed)
                return

            # Wait a bit for server to begin shutdown process
            await asyncio.sleep(2)

            # Check if the server was running before we attempt updates
            server_was_running = False
            try:
                stats_data = get_server_stats(server_id)
                if stats_data.get("status") == "ok":
                    stats = stats_data.get("data", {})
                    server_was_running = stats.get("running", False)
            except Exception as e:
                print(f"Error checking initial server status: {e}")
                
            # If server wasn't running, show an appropriate message and exit
            if not server_was_running:
                already_stopped_embed = discord.Embed(
                    title="ℹ️ Server Already Stopped",
                    description=f"{server_name} was already offline.",
                    color=discord.Color.blue()
                )
                await interaction.edit_original_response(embed=already_stopped_embed)
                return

            # Update the message every 5 seconds, up to 8 times (40 seconds total)
            max_updates = 8
            for i in range(max_updates):
                try:
                    # Get server status
                    is_running = False
                    try:
                        stats_data = get_server_stats(server_id)
                        if stats_data.get("status") == "ok":
                            stats = stats_data.get("data", {})
                            is_running = stats.get("running", False)
                    except Exception as e:
                        print(f"Error checking server status: {e}")
                        
                    # Try to get logs if the server is still running
                    log_text = ""
                    if is_running:
                        try:
                            logs_data = get_server_logs(server_id)
                            if logs_data.get("status") == "ok":
                                log_lines = logs_data.get("data", [])
                                if log_lines:
                                    # Show the last 5 lines
                                    log_text = "\n".join(log_lines[-5:])
                                    if len(log_text) > 1000:
                                        log_text = "...(truncated)...\n" + log_text[-1000:]
                        except Exception as e:
                            print(f"Error getting logs: {e}")
                    
                    # Create updated embed
                    status_color = discord.Color.gold() if is_running else discord.Color.green()
                    status_text = "🔄 Stopping..." if is_running else "✅ Stopped"
                    
                    update_embed = discord.Embed(
                        title=f"🛑 {server_name} - {status_text}",
                        description=f"Update {i+1}/{max_updates}: Server is {status_text.lower()}",
                        color=status_color
                    )
                    
                    # Add logs if available
                    if log_text:
                        update_embed.add_field(
                            name="📜 Latest Logs",
                            value=f"```{log_text}```",
                            inline=False
                        )
                    
                    # Add status field
                    update_embed.add_field(
                        name="Status",
                        value=status_text,
                        inline=True
                    )
                    
                    # Update footer with remaining updates info if still running
                    if is_running:
                        update_embed.set_footer(text=f"Updates remaining: {max_updates-i-1}")
                    else:
                        update_embed.set_footer(text="Server has fully stopped")
                    
                    # Edit the original message with the new embed
                    await interaction.edit_original_response(embed=update_embed)
                    
                    # If server is stopped, break the loop
                    if not is_running:
                        break
                    
                    # Wait 5 seconds between updates (except after the last one)
                    if i < max_updates - 1:
                        await asyncio.sleep(5)
                        
                except Exception as e:
                    print(f"Error updating stop status: {e}")
                    await asyncio.sleep(5)
                    continue
                    
            # Final update if we exited the loop because of timeout
            if i == max_updates - 1:
                timeout_embed = discord.Embed(
                    title=f"⚠️ {server_name} - Stop Timeout",
                    description="The server is taking longer than expected to stop. It may still be shutting down in the background.",
                    color=discord.Color.red()
                )
                timeout_embed.set_footer(text="You can check status with /serverinfo command")
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
    await bot.add_cog(StopCommand(bot))
