import discord
from discord.ext import commands
from discord import app_commands

class SyncCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="sync", description="Sync all slash commands with Discord (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction):
        """Sync all slash commands with Discord. Only server administrators can use this command."""
        
        # Defer the response to show that the bot is working on it
        await interaction.response.defer(ephemeral=False, thinking=True)
        
        try:
            # Create an initial embed showing that sync is in progress
            sync_progress_embed = discord.Embed(
                title="⏳ Syncing Commands",
                description="Syncing slash commands with Discord. This may take a moment...",
                color=discord.Color.blue()
            )
            
            # Send the initial response
            await interaction.followup.send(embed=sync_progress_embed)
            
            # Attempt to sync the commands
            synced = await self.bot.tree.sync()
            
            # Create success embed
            success_embed = discord.Embed(
                title="✅ Commands Synced Successfully",
                description=f"Successfully synced {len(synced)} commands!",
                color=discord.Color.green()
            )
            
            # Add field with the list of synced commands
            if len(synced) > 0:
                command_list = "\n".join([f"• `/{cmd.name}` - {cmd.description}" for cmd in synced])
                success_embed.add_field(
                    name="Synced Commands",
                    value=command_list,
                    inline=False
                )
            else:
                success_embed.add_field(
                    name="Note",
                    value="No commands were synced. This might happen if there were no changes since the last sync.",
                    inline=False
                )
            
            # Add a timestamp
            success_embed.set_footer(text=f"Synced at {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
            
            # Edit the original message with the success embed
            await interaction.edit_original_response(embed=success_embed)
            
        except Exception as e:
            # Create error embed if something goes wrong
            error_embed = discord.Embed(
                title="❌ Sync Failed",
                description=f"An error occurred while syncing commands: ```{str(e)}```",
                color=discord.Color.red()
            )
            
            # Add troubleshooting info
            error_embed.add_field(
                name="Troubleshooting",
                value=(
                    "• Check if the bot has the necessary permissions\n"
                    "• Ensure the bot is properly connected to Discord\n"
                    "• Check that all command files are free of syntax errors\n"
                    "• Try restarting the bot before syncing again"
                ),
                inline=False
            )
            
            # Edit the original message with the error embed
            await interaction.edit_original_response(embed=error_embed)

    @sync.error
    async def sync_error(self, interaction: discord.Interaction, error):
        # Handle permission error specifically
        if isinstance(error, app_commands.errors.MissingPermissions):
            permission_error = discord.Embed(
                title="❌ Permission Denied",
                description="You need administrator permissions to use this command.",
                color=discord.Color.red()
            )
            
            # Try to respond or edit original response
            try:
                await interaction.response.send_message(embed=permission_error, ephemeral=True)
            except:
                await interaction.followup.send(embed=permission_error, ephemeral=True)
        else:
            # Handle other errors
            unknown_error = discord.Embed(
                title="❌ Error",
                description=f"An unexpected error occurred: {str(error)}",
                color=discord.Color.red()
            )
            
            # Try to respond or edit original response
            try:
                await interaction.response.send_message(embed=unknown_error, ephemeral=True)
            except:
                await interaction.followup.send(embed=unknown_error, ephemeral=True)

async def setup(bot):
    await bot.add_cog(SyncCommand(bot))
