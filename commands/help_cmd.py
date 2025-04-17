import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

class HelpView(View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
        self.current_page = "main"
        self.message = None
    
    async def on_timeout(self):
        # Disable all buttons when the view times out
        for item in self.children:
            item.disabled = True
        
        # Update the message with disabled buttons if possible
        if self.message:
            try:
                timeout_embed = discord.Embed(
                    title="⏱️ Help Session Expired",
                    description="This help session has expired. Please use the `/help` command again if needed.",
                    color=discord.Color.dark_gray()
                )
                await self.message.edit(embed=timeout_embed, view=self)
            except Exception as e:
                print(f"Error updating timed out help message: {e}")
    
    @discord.ui.button(label="📚 Commands", style=discord.ButtonStyle.primary)
    async def commands_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        self.current_page = "commands"
        
        embed = discord.Embed(
            title="📚 Available Commands",
            description="Here's a list of all available commands in the Discord Crafty Bot:",
            color=discord.Color.blue()
        )
        
        # Server Information Commands
        embed.add_field(
            name="🔍 Server Information",
            value=(
                "`/servers` - List all available Minecraft servers\n"
                "`/serverinfo <server_id>` - Get detailed info about a server\n"
                "`/logs <server_id> [lines]` - Display the last few lines of logs"
            ),
            inline=False
        )
        
        # Server Control Commands
        embed.add_field(
            name="🎮 Server Control",
            value=(
                "`/start <server_id>` - Start a Minecraft server\n"
                "`/stop <server_id>` - Stop a Minecraft server\n"
                "`/backup <server_id>` - Create a server backup (Note: Currently limited by Crafty API)"
            ),
            inline=False
        )
        
        # Help and Utility Commands
        embed.add_field(
            name="❓ Help & Utility",
            value=(
                "`/help` - Show this help message"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use the buttons below to navigate through different help sections")
        
        await self.message.edit(embed=embed, view=self)
    
    @discord.ui.button(label="🔧 Setup Guide", style=discord.ButtonStyle.primary)
    async def setup_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        self.current_page = "setup"
        
        embed = discord.Embed(
            title="🔧 Bot Setup Guide",
            description="Follow these steps to set up the Discord Crafty Bot:",
            color=discord.Color.green()
        )
        
        # Installation Steps
        embed.add_field(
            name="Step 1: Installation",
            value=(
                "1. Clone the repository: `git clone https://github.com/zzackllack/Discord-Crafty-Bot.git`\n"
                "2. Navigate to the directory: `cd Discord-Crafty-Bot`\n"
                "3. Install dependencies: `pip install -r requirements.txt`"
            ),
            inline=False
        )
        
        # Configuration Steps
        embed.add_field(
            name="Step 2: Configuration",
            value=(
                "1. Copy `config.example.json` to `config.json`\n"
                "2. Edit `config.json` and set the following values:\n"
                "   - `discord_token`: Your Discord bot token\n"
                "   - `crafty_api_token`: Your Crafty Controller API token\n"
                "   - `crafty_api_url`: URL to your Crafty Controller API (e.g., `https://crafty.example.com/api/v2`)"
            ),
            inline=False
        )
        
        # Bot Startup
        embed.add_field(
            name="Step 3: Start the Bot",
            value=(
                "1. Run the bot: `python main.py`\n"
                "2. The bot should connect to Discord and log in\n"
                "3. You should see a message indicating successful connection"
            ),
            inline=False
        )
        
        # Discord Bot Setup
        embed.add_field(
            name="Discord Bot Creation",
            value=(
                "If you need to create a Discord bot token:\n"
                "1. Go to [Discord Developer Portal](https://discord.com/developers/applications)\n"
                "2. Create a New Application\n"
                "3. Navigate to the Bot section\n"
                "4. Click 'Add Bot'\n"
                "5. Under 'Privileged Gateway Intents', enable 'Message Content Intent'\n"
                "6. Copy the token for use in your config.json"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use the buttons below to navigate through different help sections")
        
        await self.message.edit(embed=embed, view=self)
    
    @discord.ui.button(label="⚠️ Troubleshooting", style=discord.ButtonStyle.primary)
    async def troubleshoot_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        self.current_page = "troubleshoot"
        
        embed = discord.Embed(
            title="⚠️ Troubleshooting",
            description="Common issues and their solutions:",
            color=discord.Color.gold()
        )
        
        # Connection Issues
        embed.add_field(
            name="🔌 Connection Issues",
            value=(
                "**Bot doesn't connect to Discord:**\n"
                "• Verify your Discord token is correct\n"
                "• Check your internet connection\n"
                "• Ensure the bot has appropriate intents enabled\n\n"
                "**Bot can't connect to Crafty Controller:**\n"
                "• Verify the Crafty API URL is correct\n"
                "• Check if the Crafty API token is valid\n"
                "• Ensure Crafty Controller is running\n"
                "• Check if there are any SSL/certificate issues"
            ),
            inline=False
        )
        
        # Command Issues
        embed.add_field(
            name="⌨️ Command Issues",
            value=(
                "**Slash commands not showing up:**\n"
                "• Reinvite the bot with the application.commands scope\n"
                "• Try using `/help` to sync commands\n"
                "• Restart the bot\n\n"
                "**Commands return errors:**\n"
                "• Check the bot's console for specific error messages\n"
                "• Verify the server ID is correct\n"
                "• Ensure the user has appropriate permissions"
            ),
            inline=False
        )
        
        # Server Operation Issues
        embed.add_field(
            name="🖥️ Server Operation Issues",
            value=(
                "**Start/Stop commands not working:**\n"
                "• Verify your Crafty API permissions\n"
                "• Check if the server exists and is accessible\n"
                "• Look for error messages in Crafty Controller logs\n\n"
                "**Backup command issues:**\n"
                "• Known issue with Crafty Controller API\n"
                "• Configure backups in Crafty web interface first\n"
                "• Consider server-specific backup plugins"
            ),
            inline=False
        )
        
        embed.set_footer(text="Use the buttons below to navigate through different help sections")
        
        await self.message.edit(embed=embed, view=self)
    
    @discord.ui.button(label="🔄 About", style=discord.ButtonStyle.primary)
    async def about_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        self.current_page = "about"
        
        embed = discord.Embed(
            title="ℹ️ About Discord Crafty Bot",
            description="A Discord bot for managing Minecraft servers through Crafty Controller",
            color=discord.Color.purple()
        )
        
        # Bot Information
        embed.add_field(
            name="🤖 Bot Information",
            value=(
                "**Version:** 1.0.0\n"
                "**Developer:** Zacklack\n"
                "**Repository:** [GitHub](https://github.com/zzackllack/Discord-Crafty-Bot)\n"
                "**License:** BSD 3-Clause"
            ),
            inline=False
        )
        
        # Features
        embed.add_field(
            name="✨ Features",
            value=(
                "• Manage Minecraft servers directly from Discord\n"
                "• View server information and statistics\n"
                "• Start, stop, and monitor servers\n"
                "• View logs and create backups\n"
                "• Easy-to-use slash commands"
            ),
            inline=False
        )
        
        # Requirements
        embed.add_field(
            name="📋 Requirements",
            value=(
                "• Python 3.10+\n"
                "• discord.py 2.5.0+\n"
                "• A running Crafty Controller instance\n"
                "• Discord bot token\n"
                "• Crafty Controller API token"
            ),
            inline=False
        )
        
        embed.set_footer(text="Thanks for using Discord Crafty Bot!")
        
        await self.message.edit(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Main Menu", style=discord.ButtonStyle.success)
    async def main_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        self.current_page = "main"
        
        embed = discord.Embed(
            title="🔰 Discord Crafty Bot Help",
            description="Welcome to the Discord Crafty Bot help system! Use the buttons below to navigate through different help sections.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📚 Commands",
            value="View all available commands and their usage",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Setup Guide",
            value="Learn how to set up and configure the bot",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Troubleshooting",
            value="Common issues and their solutions",
            inline=True
        )
        
        embed.add_field(
            name="🔄 About",
            value="Information about the bot and its features",
            inline=True
        )
        
        embed.set_footer(text="Bot by Zacklack • https://github.com/zzackllack/Discord-Crafty-Bot")
        
        await self.message.edit(embed=embed, view=self)

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show help information about the bot")
    async def help(self, interaction: discord.Interaction):
        """Display help information about the bot and its commands"""
        
        # Create the initial help embed
        embed = discord.Embed(
            title="🔰 Discord Crafty Bot Help",
            description="Welcome to the Discord Crafty Bot help system! Use the buttons below to navigate through different help sections.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📚 Commands",
            value="View all available commands and their usage",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Setup Guide",
            value="Learn how to set up and configure the bot",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Troubleshooting",
            value="Common issues and their solutions",
            inline=True
        )
        
        embed.add_field(
            name="🔄 About",
            value="Information about the bot and its features",
            inline=True
        )
        
        embed.set_footer(text="Bot by Zacklack • https://github.com/zzackllack/Discord-Crafty-Bot")
        
        # Create the view with buttons
        view = HelpView()
        
        # Send the message with the view
        await interaction.response.send_message(embed=embed, view=view)
        
        # Store the message reference in the view for timeout handling
        message = await interaction.original_response()
        view.message = message

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
