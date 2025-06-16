import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.permissions import check_admin_permissions

class AnnouncementCommands(commands.Cog):
    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager

    @app_commands.command(name="announcement", description="Send an announcement to the designated channel")
    @app_commands.describe(
        message="The announcement message",
        title="Optional title for the announcement"
    )
    async def announcement(self, interaction: discord.Interaction, message: str, title: str = None):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return
        
        try:
            guild_id = str(interaction.guild.id)
            config = self.config_manager.get_server_config(guild_id)
            
            announcement_channel_id = config.get('announcement_channel')
            if not announcement_channel_id:
                await interaction.response.send_message(
                    "No announcement channel has been set. Use /set-announcement-channel first.",
                    ephemeral=True
                )
                return
            
            channel = self.bot.get_channel(int(announcement_channel_id))
            if not channel:
                await interaction.response.send_message(
                    "The configured announcement channel no longer exists. Please set a new one.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=title or "Announcement",
                description=message,
                color=0xe74c3c
            )
            
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f"Announced in {interaction.guild.name}")
            
            await channel.send(embed=embed)
            await interaction.response.send_message(
                f"Announcement sent to {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while sending the announcement. Please try again later.",
                ephemeral=True
            )
            print(f"Error in announcement command: {e}")

    @app_commands.command(name="set-announcement-channel", description="Set the channel for announcements")
    @app_commands.describe(channel="The channel where announcements will be sent")
    async def set_announcement_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return
        
        try:
            guild_id = str(interaction.guild.id)
            
            # Check if bot has permissions to send messages in the channel
            bot_member = interaction.guild.get_member(self.bot.user.id)
            channel_permissions = channel.permissions_for(bot_member)
            
            if not channel_permissions.send_messages or not channel_permissions.embed_links:
                await interaction.response.send_message(
                    "I don't have permission to send messages or embed links in that channel.",
                    ephemeral=True
                )
                return
            
            self.config_manager.update_server_config(guild_id, {'announcement_channel': str(channel.id)})
            
            await interaction.response.send_message(
                f"Announcement channel set to {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while setting the announcement channel. Please try again later.",
                ephemeral=True
            )
            print(f"Error in set-announcement-channel command: {e}")

    @app_commands.command(name="get-announcement-channel", description="Get the current announcement channel")
    async def get_announcement_channel(self, interaction: discord.Interaction):
        try:
            guild_id = str(interaction.guild.id)
            config = self.config_manager.get_server_config(guild_id)
            
            announcement_channel_id = config.get('announcement_channel')
            if not announcement_channel_id:
                await interaction.response.send_message(
                    "No announcement channel has been set.",
                    ephemeral=True
                )
                return
            
            channel = self.bot.get_channel(int(announcement_channel_id))
            if not channel:
                await interaction.response.send_message(
                    "The configured announcement channel no longer exists.",
                    ephemeral=True
                )
                return
            
            await interaction.response.send_message(
                f"Current announcement channel: {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while getting the announcement channel. Please try again later.",
                ephemeral=True
            )
            print(f"Error in get-announcement-channel command: {e}")
