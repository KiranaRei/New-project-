import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.permissions import check_admin_permissions

class RulesCommands(commands.Cog):
    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager

    @app_commands.command(name="rules", description="Display server rules")
    async def rules(self, interaction: discord.Interaction):
        try:
            guild_id = str(interaction.guild.id)
            config = self.config_manager.get_server_config(guild_id)
            
            embed = discord.Embed(
                title="Peraturan Server",
                color=0x3498db,
                description="Harap ikuti peraturan ini untuk menjaga komunitas yang nyaman:"
            )
            
            # Default rules if not configured
            rules_list = config.get('rules', [
                "Be respectful to all members",
                "No spam or excessive self-promotion",
                "Keep conversations appropriate and family-friendly",
                "Use channels for their intended purpose",
                "No harassment, hate speech, or discrimination",
                "Follow Discord Terms of Service",
                "Listen to moderators and administrators"
            ])
            
            rules_text = ""
            for i, rule in enumerate(rules_list, 1):
                rules_text += f"{i}. {rule}\n"
            
            embed.add_field(name="Peraturan", value=rules_text, inline=False)
            
            # Add custom image if configured
            rules_image = config.get('rules_image')
            if rules_image:
                embed.set_image(url=rules_image)
            
            embed.set_footer(text="Terima kasih telah membantu menjaga server kami tetap aman dan nyaman!")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while displaying the rules. Please try again later.",
                ephemeral=True
            )
            print(f"Error in rules command: {e}")

    @app_commands.command(name="set-rules", description="Set custom rules for the server")
    @app_commands.describe(rules="Rules separated by semicolons (;)")
    async def set_rules(self, interaction: discord.Interaction, rules: str):
        if not check_admin_permissions(interaction.user, interaction.guild):
            await interaction.response.send_message(
                "You need administrator permissions to use this command.",
                ephemeral=True
            )
            return
        
        try:
            guild_id = str(interaction.guild.id)
            rules_list = [rule.strip() for rule in rules.split(';') if rule.strip()]
            
            if len(rules_list) == 0:
                await interaction.response.send_message(
                    "Please provide at least one rule.",
                    ephemeral=True
                )
                return
            
            self.config_manager.update_server_config(guild_id, {'rules': rules_list})
            
            await interaction.response.send_message(
                f"Successfully updated server rules with {len(rules_list)} rules.",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while setting the rules. Please try again later.",
                ephemeral=True
            )
            print(f"Error in set-rules command: {e}")

    @app_commands.command(name="set-rules-image", description="Set image for rules display")
    @app_commands.describe(image="Image to display with rules")
    async def set_rules_image(self, interaction: discord.Interaction, image: discord.Attachment):
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
            self.config_manager.update_server_config(guild_id, {'rules_image': image.url})
            
            await interaction.response.send_message(
                "Successfully updated rules image.",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                "An error occurred while setting the rules image. Please try again later.",
                ephemeral=True
            )
            print(f"Error in set-rules-image command: {e}")
