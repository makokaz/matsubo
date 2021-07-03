"""Discord bot

Scraps events and posts them onto discord.
"""

# import event
# import event_scrapper
# import database
# import asyncio
import discord
from discord.ext import commands
import datetime
import pytz
import os

# Bot setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    """Gets called when bot is ready. Change presence and other setup of the bot."""
    await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name='Internet', type=discord.ActivityType.listening))
    print(f'[{getJSTtime()}] Hello peeps! Matsubo is online ⚡')

@bot.command()
async def load(ctx, extension : str):
    """Loads bot cogs during execution"""
    bot.load_extension(f'cogs.{extension}')
    string = f"Successfully loaded bot-extension '{extension}'.\nType `{bot.command_prefix}help` for an explanation of my new abilities!"
    print(string)
    await ctx.send(string)

@bot.command()
async def unload(ctx, extension : str):
    """Unloads bot cogs during execution"""
    bot.unload_extension(f'cogs.{extension}')
    string = f"Successfully unloaded bot-extension '{extension}'"
    print(string)
    await ctx.send(string)

@bot.command()
async def reload(ctx, extension : str):
    """Reloads bot cogs during execution"""
    if extension.lower() == 'all':
        for cog in getAllCogs():
            if cog:
                bot.reload_extension(f'cogs.{cog}')
        string = f"Successfully reloaded all active bot-extensions.\nType `{bot.command_prefix}help` for an explanation of my abilities!"
    else:
        bot.reload_extension(f'cogs.{extension}')
        string = f"Successfully reloaded bot-extension '{extension}'.\nType `{bot.command_prefix}help` for an explanation of my new abilities!"
    print(string)
    await ctx.send(string)

@bot.event
async def on_guild_join(guild):
    """Gets called when this bot joins a server"""
    print(f"Joined new server: {guild.id}")

@bot.event
async def on_guild_remove(guild):
    """Gets called when this bot is removed from a server"""
    print(f"Got kicked from server: {guild.id}")


def getJSTtime():
    return datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).strftime('%Y-%m-%d %H:%M:%S')

def getAllCogs():
    return [filename[:-3] if filename.endswith('.py') else '' for filename in os.listdir('./src/cogs')]


for cog in getAllCogs():
    if cog:
        bot.load_extension(f'cogs.{cog}')
        print(f"Successfully loaded bot-extension '{cog}'")

if __name__ == "__main__":
    bot.run(BOT_TOKEN)
    print('Running.')
