import discord
from discord.ext import commands
import aiohttp
import io
from bot.utils.image_processor import ImageProcessor

class WelcomeHandler:
    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager
        self.image_processor = ImageProcessor()

    async def handle_member_join(self, member):
        """Handle when a member joins the server"""
        try:
            guild_id = str(member.guild.id)
            config = self.config_manager.get_server_config(guild_id)
            
            welcome_channel_id = config.get('welcome_channel')
            if not welcome_channel_id:
                return  # No welcome channel configured
            
            channel = self.bot.get_channel(int(welcome_channel_id))
            if not channel:
                return  # Channel not found
            
            # Get welcome message
            welcome_message = config.get('welcome_message', 'Welcome to {server}, {user}!')
            welcome_message = welcome_message.replace('{user}', member.mention)
            welcome_message = welcome_message.replace('{server}', member.guild.name)
            
            # Create welcome image
            welcome_image = await self._create_welcome_image(member, config)
            
            embed = discord.Embed(
                title="Welcome!",
                description=welcome_message,
                color=0x2ecc71
            )
            
            embed.set_author(
                name=member.display_name,
                icon_url=member.display_avatar.url
            )
            
            embed.add_field(
                name="Member Count",
                value=f"You are member #{member.guild.member_count}",
                inline=False
            )
            
            embed.timestamp = discord.utils.utcnow()
            
            # Auto assign roles
            await self._assign_auto_roles(member, config)
            
            if welcome_image:
                file = discord.File(welcome_image, filename="welcome.png")
                embed.set_image(url="attachment://welcome.png")
                await channel.send(embed=embed, file=file)
            else:
                await channel.send(embed=embed)
                
        except Exception as e:
            print(f"Error in welcome handler: {e}")

    async def _assign_auto_roles(self, member, config):
        """Assign auto roles to new member"""
        try:
            auto_roles = config.get('auto_roles', [])
            if not auto_roles:
                return
            
            for role_id in auto_roles:
                role = member.guild.get_role(int(role_id))
                if role and role < member.guild.me.top_role:
                    await member.add_roles(role, reason="Auto role assignment")
                    print(f"Assigned role {role.name} to {member.display_name}")
                elif role:
                    print(f"Cannot assign role {role.name} - insufficient permissions")
                else:
                    print(f"Role with ID {role_id} not found")
                    
        except Exception as e:
            print(f"Error assigning auto roles: {e}")

    async def _create_welcome_image(self, member, config):
        """Create a welcome image for the member"""
        try:
            # Get background image URL
            bg_image_url = config.get('welcome_bg_image')
            
            # Get member avatar
            avatar_url = str(member.display_avatar.url)
            
            # Create the welcome image
            image_buffer = await self.image_processor.create_welcome_image(
                member.display_name,
                member.guild.name,
                avatar_url,
                bg_image_url,
                member.guild.member_count
            )
            
            return image_buffer
            
        except Exception as e:
            print(f"Error creating welcome image: {e}")
            return None
