import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from discord.ui import View, Button
from utils.api_helper import server_action, get_server_stats, get_server_info

class ConfirmBackupView(View):
    def __init__(self, server_id, server_name):
        super().__init__(timeout=60)  # 60 second timeout
        self.server_id = server_id
        self.server_name = server_name
        self.value = None
        self.message = None
    
    @discord.ui.button(label="Yes, Continue", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        self.value = True
        # Disable all buttons after clicking
        for item in self.children:
            item.disabled = True
        
        backup_embed = discord.Embed(
            title="💾 Backup Attempt",
            description=f"Sending backup request for {self.server_name}...",
            color=discord.Color.blue()
        )
        
        await interaction.response.edit_message(embed=backup_embed, view=self)
        self.stop()
    
    @discord.ui.button(label="No, Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        self.value = False
        # Disable all buttons after clicking
        for item in self.children:
            item.disabled = True
        
        cancel_embed = discord.Embed(
            title="❌ Backup Cancelled",
            description=f"Backup request for {self.server_name} has been cancelled.",
            color=discord.Color.red()
        )
        
        await interaction.response.edit_message(embed=cancel_embed, view=self)
        self.stop()
    
    async def on_timeout(self):
        # If the user doesn't respond in time
        timeout_embed = discord.Embed(
            title="⏱️ Timed Out",
            description="Backup confirmation timed out. Please try again.",
            color=discord.Color.dark_gray()
        )
        
        # Try to update the message with timeout info
        # This might fail if the original message was deleted
        try:
            if self.message:
                for item in self.children:
                    item.disabled = True
                await self.message.edit(embed=timeout_embed, view=self)
        except:
            pass

class BackupCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="backup", description="Backup a server by providing its server ID.")
    async def backup(self, interaction: discord.Interaction, server_id: str):
        # Defer the response immediately to prevent interaction timeouts
        await interaction.response.defer(ephemeral=False, thinking=True)
        
        try:
            # Check if server exists and get its name and additional metadata
            server_name = f"Server {server_id}"
            server_type = "Unknown"
            backup_path = "Unknown"
            server_executable = "Unknown"
            server_stats = None
            
            try:
                server_info = get_server_info(server_id)
                if server_info.get("status") == "ok":
                    server_data = server_info.get("data", {})
                    server_name = server_data.get("server_name", f"Server {server_id}")
                    server_type = server_data.get("type", "Unknown")
                    backup_path = server_data.get("backup_path", "Unknown")
                    server_executable = server_data.get("executable", "Unknown")
                    
                    # Get additional stats if available
                    try:
                        stats_data = get_server_stats(server_id)
                        if stats_data.get("status") == "ok":
                            server_stats = stats_data.get("data", {})
                    except Exception as stats_e:
                        print(f"Error getting server stats: {stats_e}")
            except Exception as e:
                print(f"Error getting server info: {e}")
            
            # Initial response with warning embed
            warning_embed = discord.Embed(
                title="⚠️ Warning: Backup Feature - Known Issue Detected",
                description="**IMPORTANT:** The backup feature is currently broken in the Crafty API. This is a bug in Crafty Controller itself, not in this bot.",
                color=discord.Color.red()
            )
            
            # Add server metadata to the warning embed
            if server_type != "Unknown" or backup_path != "Unknown":
                server_meta = f"**Name:** {server_name}\n**Type:** {server_type}\n**Backup Path:** `{backup_path}`"
                if server_stats:
                    world_size = server_stats.get("world_size", "Unknown")
                    server_meta += f"\n**World Size:** {world_size}"
                    
                warning_embed.add_field(
                    name="Server Information",
                    value=server_meta,
                    inline=False
                )
            
            warning_embed.add_field(
                name="Technical Details",
                value="The API is trying to create a backup but encounters a `BackupsDoesNotExist` error because the backup configuration is missing in the database. The SQL query is attempting to find a backup with ID: `None`.",
                inline=False
            )
            
            warning_embed.add_field(
                name="Alternative Options",
                value="1. Use the Crafty Controller web interface to create and configure backups first\n2. Use server-specific backup plugins/mods\n3. Set up a scheduled backup task directly on the server",
                inline=False
            )
            
            warning_embed.add_field(
                name="Want to try anyway?",
                value=f"You can still attempt to back up {server_name}, but it will likely fail with the error shown in your logs.",
                inline=False
            )
            
            # Create the view containing our buttons
            view = ConfirmBackupView(server_id, server_name)
            
            # Send the initial message with buttons (using followup instead of response)
            message = await interaction.followup.send(embed=warning_embed, view=view, wait=True)
            
            # Store the message in the view for timeout handling
            view.message = message
            
            # Wait for the user to interact with the buttons
            timeout = await view.wait()
            
            # If it timed out, the on_timeout handler will have updated the message
            if timeout or view.value is None:
                return
                
            # If user clicked "No", the cancel button handler will have updated the message
            if view.value is False:
                return
                
            # If user confirmed, proceed with the backup
            if view.value is True:
                # Update the message to show we're attempting the backup
                backup_embed = discord.Embed(
                    title="💾 Backup Attempt",
                    description=f"Sending backup request for {server_name}...",
                    color=discord.Color.blue()
                )
                
                try:
                    await message.edit(embed=backup_embed, view=None)
                except Exception as edit_error:
                    print(f"Error updating message: {edit_error}")
                
                # Send backup command to server
                data = server_action(server_id, "backup_server")

                if data.get("status") != "ok":
                    # If there's an error, update the message
                    error_embed = discord.Embed(
                        title="❌ Error Requesting Backup",
                        description=f"Failed to request backup for {server_name}. Error: {data.get('message', 'Unknown error')}",
                        color=discord.Color.red()
                    )
                    
                    try:
                        await message.edit(embed=error_embed)
                    except Exception as edit_error:
                        print(f"Error updating message: {edit_error}")
                    return
                
                # Fetch current metadata for final response
                server_metadata = {}
                try:
                    stats_after_data = get_server_stats(server_id)
                    if stats_after_data.get("status") == "ok":
                        server_metadata = stats_after_data.get("data", {})
                except Exception as stats_e:
                    print(f"Error getting server stats after backup: {stats_e}")

                # Final response on successful API call
                final_embed = discord.Embed(
                    title="✅ Backup Request Sent (But Likely Failed)",
                    description=f"Backup request for {server_name} was sent to the Crafty Controller API, but likely failed due to the issue with Crafty's backup system.",
                    color=discord.Color.gold()
                )
                
                # Add server metadata to the final embed
                metadata_field = f"**Server Type:** {server_type}\n**Executable:** `{server_executable}`\n**Backup Path:** `{backup_path}`"
                
                # Add stats if available
                if server_metadata:
                    if "world_size" in server_metadata:
                        metadata_field += f"\n**World Size:** {server_metadata.get('world_size', 'Unknown')}"
                    if "server_port" in server_metadata:
                        metadata_field += f"\n**Port:** {server_metadata.get('server_port', 'Unknown')}"
                    if "version" in server_metadata:
                        metadata_field += f"\n**Version:** {server_metadata.get('version', 'Unknown')}"
                    if "running" in server_metadata:
                        status = "🟢 Online" if server_metadata.get("running") else "🔴 Offline"
                        metadata_field += f"\n**Status:** {status}"
                
                final_embed.add_field(
                    name="Server Information",
                    value=metadata_field,
                    inline=False
                )
                
                # Add timestamp for the backup attempt
                final_embed.add_field(
                    name="Backup Details",
                    value=f"**Attempt Time:** {discord.utils.format_dt(discord.utils.utcnow(), 'F')}\n**Backup Type:** Full Server Backup",
                    inline=False
                )
                
                final_embed.add_field(
                    name="Expected Error in Logs",
                    value="```\nBackupsDoesNotExist: <Model: Backups> instance matching query does not exist\nParams: [None, 1, 0]\n```",
                    inline=False
                )
                
                final_embed.add_field(
                    name="How to Fix",
                    value="1. Create at least one backup configuration in the Crafty Controller web interface\n2. Try using the web interface backup buttons directly\n3. Check the Crafty Controller issue tracker for updates on this bug",
                    inline=False
                )
                
                final_embed.set_footer(text="This is an issue with Crafty Controller's API backup functionality")
                
                try:
                    await message.edit(embed=final_embed)
                except Exception as edit_error:
                    print(f"Error updating final message: {edit_error}")
                
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Error",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )

            # Safely attempt to send or edit message
            try:
                await interaction.followup.send(embed=embed)
            except Exception as send_error:
                print(f"Error sending error message: {send_error}")
                try:
                    # Fallback to create a new message
                    channel = interaction.channel
                    if channel:
                        await channel.send(embed=embed)
                except Exception as channel_error:
                    print(f"Failed to send error message to channel: {channel_error}")

async def setup(bot):
    await bot.add_cog(BackupCommand(bot))
