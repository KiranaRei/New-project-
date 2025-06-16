import discord
from discord.ext import commands
import asyncio
import json
import os
from aiohttp import web
from bot.commands.rules import RulesCommands
from bot.commands.announcement import AnnouncementCommands
from bot.commands.moderation import ModerationCommands
from bot.commands.config import ConfigCommands

from bot.events.welcome import WelcomeHandler
from bot.utils.config_manager import ConfigManager

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize components
config_manager = ConfigManager()
welcome_handler = WelcomeHandler(bot, config_manager)

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user}')
    
    # Set bot status with Discord invite link
    activity = discord.Activity(
        type=discord.ActivityType.playing,
        name="🎮 Join: discord.gg/ZFM8pCt4"
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)
    
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_member_join(member):
    await welcome_handler.handle_member_join(member)

@bot.command(name='welcome')
async def test_welcome(ctx):
    """Test welcome message (for testing purposes)"""
    await welcome_handler.handle_member_join(ctx.author)

# Web server untuk keep alive
async def health_check(request):
    return web.Response(text="Akari Bot is running! Status: Online")

async def bot_status(request):
    total_users = 0
    for guild in bot.guilds:
        if guild.member_count:
            total_users += guild.member_count
    
    return web.json_response({
        "status": "online",
        "bot_name": "Akari",
        "servers": len(bot.guilds),
        "users": total_users
    })

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/status', bot_status)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 5000)
    await site.start()
    print("Web server started on port 5000 - Keep alive active!")

async def main():
    # Start web server untuk keep alive
    await start_web_server()
    
    # Add command cogs
    await bot.add_cog(RulesCommands(bot, config_manager))
    await bot.add_cog(AnnouncementCommands(bot, config_manager))
    await bot.add_cog(ModerationCommands(bot, config_manager))
    await bot.add_cog(ConfigCommands(bot, config_manager))
    from bot.commands.translate import SayCommands
    await bot.add_cog(SayCommands(bot, config_manager))
    
    # Get bot token from environment
    token = os.getenv('DISCORD_BOT_TOKEN', 'your_bot_token_here')
    await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
