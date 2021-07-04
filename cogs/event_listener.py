"""Event Listener Cog

Discord Bot Cog that scraps the web for events, and then posts them on defined channels.
"""

import discord
from discord.ext import commands, tasks
from itertools import cycle

status = cycle([f"Counting 🐑... {i} {'💤' if i%2 else ''}" for i in range(1, 10)])

class EventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.countingSheeps.start()

    @tasks.loop(seconds=10)
    async def countingSheeps(self):
        """Counts sheeps. Very handy, because it shows the bot is still running."""
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(next(status)))
    def cog_unload(self):
        self.countingSheeps.cancel()
    @countingSheeps.before_loop
    async def before_countingSheeps(self):
        await self.bot.wait_until_ready()
    @countingSheeps.after_loop
    async def on_countingSheeps_cancel(self):
        if self.countingSheeps.is_being_cancelled():
            await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name='Internet', type=discord.ActivityType.listening))


def setup(bot):
    bot.add_cog(EventListener(bot))
