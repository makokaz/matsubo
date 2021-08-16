"""Example Cog file

Simple example file to help understand how to add more functionality to this bot.

This cog defines the following discord commands:
- clear
- ping

It also defines special behaviour when a member has joined the server:
- on_member_join

Refer to the Discord Docs to learn the basic functionality of a discord bot:
https://discordpy.readthedocs.io/en/stable/
"""

import discord
from discord.ext import commands


class ExampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ##############
    # Add here your functions
    ##############

    # EXAMPLE: Whenever somebody joins this server, this function will be called
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Whenever somebody joins this server, this function will be called.
        Currently, it only prints to the console that somebody has joined this server.
        """
        print(f'{member} has joined the server.')

    # EXAMPLE: If you write `.ping` in a discord message, the bot will respond with the ping in ms
    @commands.command(aliases=['test'])
    async def ping(self, ctx):
        """Returns with a `pong"!` message and the ping"""
        await ctx.send(f'pong! [{round(self.bot.latency * 1000)}ms]')

    # EXAMPLE: If you write `.clear 5`, the bot will delete the 5 last messages in this channel.
    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Bulk clears the last #amount messages in the channel"""
        await ctx.channel.purge(limit=amount)


# This function will register this cog as a module to the bot, so the bot receives the functionality you defined above
def setup(bot):
    bot.add_cog(ExampleCog(bot))
