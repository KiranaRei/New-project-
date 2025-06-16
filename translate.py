import discord
from discord.ext import commands
from discord import app_commands
from bot.utils.permissions import check_admin_permissions
import asyncio

class SayCommands(commands.Cog):
    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager

    @commands.command(name="say")
    async def say_command(self, ctx, *, message: str = None):
        """Bot akan mengirim pesan dan menghapus command message"""
        try:
            # Hapus command message dalam waktu kurang dari 1 detik
            asyncio.create_task(self.delete_command_message(ctx.message))

            if not message:
                # Kirim pesan sementara yang akan dihapus
                temp_msg = await ctx.send("Gunakan: `!say <pesan>` untuk mengirim pesan!")
                await asyncio.sleep(3)
                await temp_msg.delete()
                return

            # Kirim pesan sebagai bot
            await ctx.send(message)

        except Exception as e:
            print(f"Error in say command: {e}")

    @commands.command(name="reply")
    async def reply_command(self, ctx, *, message: str = None):
        """Bot akan reply pesan yang di-reply user dan hapus command message"""
        try:
            # Hapus command message dalam waktu kurang dari 1 detik
            asyncio.create_task(self.delete_command_message(ctx.message))

            if not message:
                # Kirim pesan sementara yang akan dihapus
                temp_msg = await ctx.send("Reply pesan orang lain terus gunakan: `!reply <pesan>`")
                await asyncio.sleep(3)
                await temp_msg.delete()
                return

            # Cek apakah command ini adalah reply ke pesan lain
            if ctx.message.reference and ctx.message.reference.message_id:
                try:
                    # Ambil pesan yang di-reply
                    referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

                    # Reply ke pesan tersebut
                    await referenced_message.reply(message, mention_author=False)

                except discord.NotFound:
                    await ctx.send("Pesan yang mau di-reply ga ditemukan!")
                except Exception as e:
                    await ctx.send(f"Error pas reply pesan: {str(e)}")
            else:
                # Kalau bukan reply, kirim pesan biasa
                await ctx.send(f"**Reply:** {message}")

        except Exception as e:
            print(f"Error in reply command: {e}")

    @app_commands.command(name="say", description="Bot kirim pesan (slash command)")
    @app_commands.describe(message="Pesan yang mau dikirim bot")
    async def say_slash(self, interaction: discord.Interaction, message: str):
        """Slash command version of say"""
        try:
            await interaction.response.send_message(message)
        except Exception as e:
            await interaction.response.send_message(
                "Error pas kirim pesan. Coba lagi nanti.",
                ephemeral=True
            )
            print(f"Error in say slash command: {e}")

    async def delete_command_message(self, message):
        """Hapus command message dengan delay minimal"""
        try:
            await asyncio.sleep(0.5)  # Delay 0.5 detik (kurang dari 1 detik)
            await message.delete()
        except discord.NotFound:
            pass  # Pesan udah dihapus
        except discord.Forbidden:
            pass  # Bot ga punya permission delete
        except Exception as e:
            print(f"Error deleting command message: {e}")

async def setup(bot):
    await bot.add_cog(SayCommands(bot))