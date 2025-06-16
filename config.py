import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.permissions import check_admin_permissions

class ConfigCommands(commands.Cog):
    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager

    @app_commands.command(name="set-welcome-channel", description="Set the channel for welcome messages")
    @app_commands.describe(channel="The channel where welcome messages will be sent")
    async def set_welcome_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
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

            if not channel_permissions.send_messages or not channel_permissions.attach_files:
                await interaction.response.send_message(
                    "I don't have permission to send messages or attach files in that channel.",
                    ephemeral=True
                )
                return

            self.config_manager.update_server_config(guild_id, {'welcome_channel': str(channel.id)})

            await interaction.response.send_message(
                f"Welcome channel set to {channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while setting the welcome channel. Please try again later.",
                ephemeral=True
            )
            print(f"Error in set-welcome-channel command: {e}")

    @app_commands.command(name="set-welcome-message", description="Set the welcome message text")
    @app_commands.describe(message="Welcome message (use {user} for mention, {server} for server name)")
    async def set_welcome_message(self, interaction: discord.Interaction, message: str):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return

        try:
            guild_id = str(interaction.guild.id)
            self.config_manager.update_server_config(guild_id, {'welcome_message': message})

            await interaction.response.send_message(
                "Welcome message updated successfully.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while setting the welcome message. Please try again later.",
                ephemeral=True
            )
            print(f"Error in set-welcome-message command: {e}")

    @app_commands.command(name="set-welcome-image", description="Set the background image for welcome messages")
    @app_commands.describe(image="Background image for welcome messages")
    async def set_welcome_image(self, interaction: discord.Interaction, image: discord.Attachment):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return

        try:
            if not image.content_type.startswith('image/'):
                await interaction.response.send_message(
                    "Please upload a valid image file.",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)
            self.config_manager.update_server_config(guild_id, {'welcome_bg_image': image.url})

            await interaction.response.send_message(
                "Welcome background image updated successfully.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while setting the welcome image. Please try again later.",
                ephemeral=True
            )
            print(f"Error in set-welcome-image command: {e}")

    @app_commands.command(name="set-mod-log-channel", description="Set the channel for moderation logs")
    @app_commands.describe(channel="The channel where moderation logs will be sent")
    async def set_mod_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
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

            self.config_manager.update_server_config(guild_id, {'mod_log_channel': str(channel.id)})

            await interaction.response.send_message(
                f"Moderation log channel set to {channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while setting the moderation log channel. Please try again later.",
                ephemeral=True
            )
            print(f"Error in set-mod-log-channel command: {e}")

    @app_commands.command(name="config", description="View current server configuration")
    async def config(self, interaction: discord.Interaction):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return

        try:
            guild_id = str(interaction.guild.id)
            config = self.config_manager.get_server_config(guild_id)

            embed = discord.Embed(
                title="Server Configuration",
                color=0x3498db
            )

            # Welcome settings
            welcome_channel = config.get('welcome_channel')
            if welcome_channel:
                channel = self.bot.get_channel(int(welcome_channel))
                embed.add_field(
                    name="Welcome Channel",
                    value=channel.mention if channel else "Channel not found",
                    inline=False
                )
            else:
                embed.add_field(name="Welcome Channel", value="Not set", inline=False)

            welcome_message = config.get('welcome_message', 'Not set')
            embed.add_field(name="Welcome Message", value=welcome_message[:100] + "..." if len(welcome_message) > 100 else welcome_message, inline=False)

            # Announcement settings
            announcement_channel = config.get('announcement_channel')
            if announcement_channel:
                channel = self.bot.get_channel(int(announcement_channel))
                embed.add_field(
                    name="Announcement Channel",
                    value=channel.mention if channel else "Channel not found",
                    inline=False
                )
            else:
                embed.add_field(name="Announcement Channel", value="Not set", inline=False)

            # Moderation settings
            mod_log_channel = config.get('mod_log_channel')
            if mod_log_channel:
                channel = self.bot.get_channel(int(mod_log_channel))
                embed.add_field(
                    name="Moderation Log Channel",
                    value=channel.mention if channel else "Channel not found",
                    inline=False
                )
            else:
                embed.add_field(name="Moderation Log Channel", value="Not set", inline=False)

            # Rules settings
            rules_count = len(config.get('rules', []))
            embed.add_field(name="Custom Rules", value=f"{rules_count} rules set" if rules_count > 0 else "Using default rules", inline=False)

            rules_image = config.get('rules_image')
            embed.add_field(name="Rules Image", value="Set" if rules_image else "Not set", inline=False)

            welcome_bg = config.get('welcome_bg_image')
            embed.add_field(name="Welcome Background", value="Set" if welcome_bg else "Not set", inline=False)

            # Auto roles settings
            auto_roles = config.get('auto_roles', [])
            if auto_roles:
                role_names = []
                for role_id in auto_roles:
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        role_names.append(role.name)
                    else:
                        role_names.append(f"Unknown (ID: {role_id})")
                embed.add_field(
                    name="Auto Roles",
                    value=", ".join(role_names) if role_names else "No valid roles",
                    inline=False
                )
            else:
                embed.add_field(name="Auto Roles", value="Not set", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while retrieving the configuration. Please try again later.",
                ephemeral=True
            )
            print(f"Error in config command: {e}")

    @app_commands.command(name="set-auto-roles", description="Set roles to automatically assign to new members")
    @app_commands.describe(roles="Roles to automatically assign (separate multiple roles with spaces)")
    async def set_auto_roles(self, interaction: discord.Interaction, roles: str):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return

        try:
            guild_id = str(interaction.guild.id)
            
            # Parse role mentions and names
            role_ids = []
            role_names = []
            
            # Split roles by space and process each
            role_parts = roles.split()
            for part in role_parts:
                # Check if it's a role mention
                if part.startswith('<@&') and part.endswith('>'):
                    role_id = part[3:-1]
                    role = interaction.guild.get_role(int(role_id))
                    if role:
                        role_ids.append(str(role.id))
                        role_names.append(role.name)
                else:
                    # Try to find role by name
                    role = discord.utils.get(interaction.guild.roles, name=part)
                    if role:
                        role_ids.append(str(role.id))
                        role_names.append(role.name)
            
            if not role_ids:
                await interaction.response.send_message(
                    "No valid roles found. Please mention roles or use exact role names.",
                    ephemeral=True
                )
                return
            
            # Check if bot can assign these roles
            bot_member = interaction.guild.get_member(self.bot.user.id)
            valid_roles = []
            invalid_roles = []
            
            for role_id in role_ids:
                role = interaction.guild.get_role(int(role_id))
                if role and role < bot_member.top_role:
                    valid_roles.append(role_id)
                else:
                    invalid_roles.append(role.name if role else f"ID: {role_id}")
            
            if not valid_roles:
                await interaction.response.send_message(
                    "I cannot assign any of these roles. Make sure my role is higher than the roles you want to auto-assign.",
                    ephemeral=True
                )
                return
            
            # Save configuration
            self.config_manager.update_server_config(guild_id, {'auto_roles': valid_roles})
            
            valid_role_names = [interaction.guild.get_role(int(rid)).name for rid in valid_roles]
            response = f"Auto roles set: {', '.join(valid_role_names)}"
            
            if invalid_roles:
                response += f"\n⚠️ Cannot assign: {', '.join(invalid_roles)} (insufficient permissions)"
            
            await interaction.response.send_message(response, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while setting auto roles. Please try again later.",
                ephemeral=True
            )
            print(f"Error in set-auto-roles command: {e}")

    @app_commands.command(name="remove-auto-roles", description="Remove all auto roles")
    async def remove_auto_roles(self, interaction: discord.Interaction):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return

        try:
            guild_id = str(interaction.guild.id)
            self.config_manager.update_server_config(guild_id, {'auto_roles': []})
            
            await interaction.response.send_message(
                "All auto roles have been removed.",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while removing auto roles. Please try again later.",
                ephemeral=True
            )
            print(f"Error in remove-auto-roles command: {e}")

    @app_commands.command(name="view-auto-roles", description="View currently configured auto roles")
    async def view_auto_roles(self, interaction: discord.Interaction):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return

        try:
            guild_id = str(interaction.guild.id)
            config = self.config_manager.get_server_config(guild_id)
            auto_roles = config.get('auto_roles', [])
            
            if not auto_roles:
                await interaction.response.send_message(
                    "No auto roles are currently configured.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="Auto Roles Configuration",
                color=0x3498db
            )
            
            role_list = []
            for role_id in auto_roles:
                role = interaction.guild.get_role(int(role_id))
                if role:
                    role_list.append(f"• {role.name}")
                else:
                    role_list.append(f"• Unknown Role (ID: {role_id})")
            
            embed.add_field(
                name="Roles assigned to new members:",
                value="\n".join(role_list) if role_list else "None",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while viewing auto roles. Please try again later.",
                ephemeral=True
            )
            print(f"Error in view-auto-roles command: {e}")