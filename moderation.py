import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.permissions import check_mod_permissions
import asyncio
from datetime import datetime, timedelta

class ModerationCommands(commands.Cog):
    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(
        member="The member to kick",
        reason="Reason for the kick"
    )
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if not check_mod_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need moderation permissions to use this command.",
                ephemeral=True
            )
            return
        
        try:
            if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
                await interaction.response.send_message(
                    "You cannot kick someone with an equal or higher role.",
                    ephemeral=True
                )
                return
            
            if member == interaction.guild.owner:
                await interaction.response.send_message(
                    "Cannot kick the server owner.",
                    ephemeral=True
                )
                return
            
            # Log the action
            await self._log_moderation_action(interaction.guild, "Kick", member, interaction.user, reason)
            
            # Try to DM the user
            try:
                embed = discord.Embed(
                    title="You have been kicked",
                    description=f"You were kicked from {interaction.guild.name}",
                    color=0xe67e22
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await member.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            await member.kick(reason=f"Kicked by {interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="Member Kicked",
                description=f"{member.mention} has been kicked from the server",
                color=0xe67e22
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while kicking the member. Please check my permissions and try again.",
                ephemeral=True
            )
            print(f"Error in kick command: {e}")

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(
        member="The member to ban",
        reason="Reason for the ban",
        delete_days="Days of messages to delete (0-7)"
    )
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided", delete_days: int = 0):
        if not check_mod_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need moderation permissions to use this command.",
                ephemeral=True
            )
            return
        
        try:
            if delete_days < 0 or delete_days > 7:
                await interaction.response.send_message(
                    "Delete days must be between 0 and 7.",
                    ephemeral=True
                )
                return
            
            if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
                await interaction.response.send_message(
                    "You cannot ban someone with an equal or higher role.",
                    ephemeral=True
                )
                return
            
            if member == interaction.guild.owner:
                await interaction.response.send_message(
                    "Cannot ban the server owner.",
                    ephemeral=True
                )
                return
            
            # Log the action
            await self._log_moderation_action(interaction.guild, "Ban", member, interaction.user, reason)
            
            # Try to DM the user
            try:
                embed = discord.Embed(
                    title="You have been banned",
                    description=f"You were banned from {interaction.guild.name}",
                    color=0xe74c3c
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                await member.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            await member.ban(reason=f"Banned by {interaction.user}: {reason}", delete_message_days=delete_days)
            
            embed = discord.Embed(
                title="Member Banned",
                description=f"{member.mention} has been banned from the server",
                color=0xe74c3c
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while banning the member. Please check my permissions and try again.",
                ephemeral=True
            )
            print(f"Error in ban command: {e}")

    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The ID of the user to unban",
        reason="Reason for the unban"
    )
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        if not check_mod_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need moderation permissions to use this command.",
                ephemeral=True
            )
            return
        
        try:
            user_id = int(user_id)
            user = await self.bot.fetch_user(user_id)
            
            await interaction.guild.unban(user, reason=f"Unbanned by {interaction.user}: {reason}")
            
            # Log the action
            await self._log_moderation_action(interaction.guild, "Unban", user, interaction.user, reason)
            
            embed = discord.Embed(
                title="User Unbanned",
                description=f"{user.mention} has been unbanned from the server",
                color=0x2ecc71
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.NotFound:
            await interaction.response.send_message(
                "User not found or not banned.",
                ephemeral=True
            )
        except ValueError:
            await interaction.response.send_message(
                "Invalid user ID provided.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while unbanning the user. Please check my permissions and try again.",
                ephemeral=True
            )
            print(f"Error in unban command: {e}")

    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(
        member="The member to timeout",
        duration="Duration in minutes",
        reason="Reason for the timeout"
    )
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "No reason provided"):
        if not check_mod_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need moderation permissions to use this command.",
                ephemeral=True
            )
            return
        
        try:
            if duration <= 0 or duration > 40320:  # Max 28 days
                await interaction.response.send_message(
                    "Duration must be between 1 and 40320 minutes (28 days).",
                    ephemeral=True
                )
                return
            
            if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
                await interaction.response.send_message(
                    "You cannot timeout someone with an equal or higher role.",
                    ephemeral=True
                )
                return
            
            timeout_until = discord.utils.utcnow() + timedelta(minutes=duration)
            await member.timeout(timeout_until, reason=f"Timed out by {interaction.user}: {reason}")
            
            # Log the action
            await self._log_moderation_action(interaction.guild, "Timeout", member, interaction.user, f"{reason} (Duration: {duration} minutes)")
            
            embed = discord.Embed(
                title="Member Timed Out",
                description=f"{member.mention} has been timed out for {duration} minutes",
                color=0xf39c12
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            embed.add_field(name="Ends At", value=f"<t:{int(timeout_until.timestamp())}:F>", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while timing out the member. Please check my permissions and try again.",
                ephemeral=True
            )
            print(f"Error in timeout command: {e}")

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(
        member="The member to warn",
        reason="Reason for the warning"
    )
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if not check_mod_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need moderation permissions to use this command.",
                ephemeral=True
            )
            return
        
        try:
            # Store warning in config
            guild_id = str(interaction.guild.id)
            config = self.config_manager.get_server_config(guild_id)
            
            if 'warnings' not in config:
                config['warnings'] = {}
            
            user_id = str(member.id)
            if user_id not in config['warnings']:
                config['warnings'][user_id] = []
            
            warning = {
                'reason': reason,
                'moderator': str(interaction.user.id),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            config['warnings'][user_id].append(warning)
            self.config_manager.update_server_config(guild_id, config)
            
            # Log the action
            await self._log_moderation_action(interaction.guild, "Warning", member, interaction.user, reason)
            
            warning_count = len(config['warnings'][user_id])
            
            # Try to DM the user
            try:
                embed = discord.Embed(
                    title="You have been warned",
                    description=f"You received a warning in {interaction.guild.name}",
                    color=0xf39c12
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
                embed.add_field(name="Total Warnings", value=str(warning_count), inline=False)
                await member.send(embed=embed)
            except:
                pass  # User has DMs disabled
            
            embed = discord.Embed(
                title="Member Warned",
                description=f"{member.mention} has been warned",
                color=0xf39c12
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            embed.add_field(name="Total Warnings", value=str(warning_count), inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while warning the member. Please try again later.",
                ephemeral=True
            )
            print(f"Error in warn command: {e}")

    async def _log_moderation_action(self, guild, action, target, moderator, reason):
        """Log moderation actions to the configured log channel"""
        try:
            guild_id = str(guild.id)
            config = self.config_manager.get_server_config(guild_id)
            
            log_channel_id = config.get('mod_log_channel')
            if not log_channel_id:
                return
            
            channel = self.bot.get_channel(int(log_channel_id))
            if not channel:
                return
            
            embed = discord.Embed(
                title=f"Moderation Action: {action}",
                color=0x34495e,
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="Target", value=f"{target.mention} ({target})", inline=False)
            embed.add_field(name="Moderator", value=f"{moderator.mention} ({moderator})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error logging moderation action: {e}")
