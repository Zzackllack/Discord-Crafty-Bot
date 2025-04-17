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
            
            # Initial response with warning embed
            warning_embed = discord.Embed(
                title="⚠️ Warning: Backup Feature",
                description="**IMPORTANT:** The backup feature has shown reliability issues in testing. While the API call will be made, backups may not appear in the web UI or backup directory.",
                color=discord.Color.gold()
            )
            
            warning_embed.add_field(
                name="Alternative Options",
                value="1. Use the Crafty Controller web interface to create backups\n2. Use server-specific backup plugins/mods\n3. Set up a scheduled backup task directly on the server",
                inline=False
            )
            
            warning_embed.add_field(
                name="Confirmation Required",
                value=f"Do you want to proceed with the backup request for {server_name}?",
                inline=False
            )
            
            # Create the view containing our buttons
            view = ConfirmBackupView(server_id, server_name)
            
            # Send the initial message with buttons
            await interaction.response.send_message(embed=warning_embed, view=view)
            
            # Wait for the user to interact with the buttons
            timeout = await view.wait()
            
            # If it timed out, the on_timeout handler will have updated the message
            if timeout:
                return
                
            # If user clicked "No", the cancel button handler will have updated the message
            if view.value is False:
                return
                
            # If user confirmed, proceed with the backup
            if view.value is True:
                # Send backup command to server
                data = server_action(server_id, "backup_server")

                if data.get("status") != "ok":
                    # If there's an error, update the message immediately
                    error_embed = discord.Embed(
                        title="❌ Error Requesting Backup",
                        description=f"Failed to request backup for {server_name}. Error: {data.get('message', 'Unknown error')}",
                        color=discord.Color.red()
                    )
                    await interaction.edit_original_response(embed=error_embed, view=None)
                    return

                # Final response on successful API call
                final_embed = discord.Embed(
                    title="✅ Backup Request Sent",
                    description=f"Backup request for {server_name} has been sent to the Crafty Controller API.",
                    color=discord.Color.green()
                )
                
                final_embed.add_field(
                    name="Next Steps",
                    value="1. Check the Crafty Controller web interface to verify if the backup appears\n2. Verify directly in the backup directory on your server\n3. Check server logs for backup completion messages",
                    inline=False
                )
                
                final_embed.add_field(
                    name="⚠️ Important Note",
                    value="If the backup doesn't appear, please use the Crafty Controller web interface directly to perform backups.",
                    inline=False
                )
                
                final_embed.set_footer(text="The bot will not track backup progress due to API limitations")
                
                await interaction.edit_original_response(embed=final_embed, view=None)
                
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Error",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )

            # Check if we've already responded
            try:
                await interaction.edit_original_response(embed=embed, view=None)
            except:
                await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BackupCommand(bot))
