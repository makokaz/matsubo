"""Event Listener Cog

Discord Bot Cog that scraps the web for events, and then posts them on defined channels.
"""

import discord
from discord.ext import commands, tasks
from itertools import cycle
import datetime, pytz
from cogs.utils import database as db
from cogs.utils.event import Event

SLEEP_STATUS = cycle([f"Counting 🐑... {i} {'💤' if i%2 else ''}" for i in range(1, 10)])
POST_TIMES = [datetime.time(hour=10, minute=0, second=0, tzinfo=pytz.timezone('Asia/Tokyo')), 
              datetime.time(hour=20, minute=0, second=0, tzinfo=pytz.timezone('Asia/Tokyo'))]


class EventListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop_scrapNotify.start()
        self.countingSheeps.start()

    @tasks.loop(seconds=10)
    async def countingSheeps(self):
        """Counts sheeps. Very handy, because it shows the bot is still running."""
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(next(SLEEP_STATUS)))
    def cog_unload(self):
        self.countingSheeps.cancel()
    @countingSheeps.before_loop
    async def before_countingSheeps(self):
        await self.bot.wait_until_ready()
    @countingSheeps.after_loop
    async def on_countingSheeps_cancel(self):
        if self.countingSheeps.is_being_cancelled():
            await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name='Internet', type=discord.ActivityType.listening))
    
    # @tasks.loop(seconds=10)
    # async def scrappingEvents(self):
    #     """Scraps the events and puts them into the database"""
    #     print('Running: scrappingEvents()')
    #     currentTime = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo'))
    #     dt = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).replace(hour=POST_TIMES[0].hour, minute=POST_TIMES[0].minute, second=POST_TIMES[0].second) + datetime.timedelta(days=1) - currentTime
    #     for time in POST_TIMES:
    #         postTime = datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).replace(hour=time.hour, minute=time.minute, second=time.second)
    #         if postTime > currentTime:     
    #             dt = postTime - currentTime
    #             break
    #     print(f"Next Loop: {dt.seconds}s")
    #     self.scrappingEvents.change_interval(seconds=dt.seconds)
    # @scrappingEvents.before_loop
    # async def before_scrappingEvents(self):
    #     await self.bot.wait_until_ready()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def scrap(self, ctx):
        """(ADMIN ONLY) Searches the web for new events, and posts updates to all subscibed channels."""
        await ctx.send(f"Scanning the web... this might take a while. Come back later again.")
        await self.scrapEvents()
        await self.notifyAllChannels()

    async def scrapEvents(self):
        """Searches the web for new events, and puts them into the database"""
        #TODO
        pass

    async def notifyAllChannels(self):
        """Notify all subscribed channels of new events"""
        chvs = db.discordDB.getChannelWithVisibility()
        for chv in chvs:
            guild_id = chv[0]
            channel_id = chv[1]
            visibility = chv[2]
            events = db.eventDB.getEvents(visibility=visibility, from_date=datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo')).date())
            #channel = self.bot.get_channel(channel_id)
            self.notifyChannel(channel_id, events)

    async def notifyChannel(self, channel : commands.TextChannelConverter, events : list[Event]):
        """Notify channel of new events"""
        #TODO
        #channel.send()
        print(f"Called notifiyChannel with arguments: {channel}")
        pass

    @tasks.loop(hours=1)
    async def loop_scrapNotify(self):
        """[Background task] Scraps web at specified times and notifies all subscribed channels."""
        #TODO
        pass
    @loop_scrapNotify.before_loop
    async def before_loop_scrapNotify(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def subscribe(self, ctx, *, visibility):
        """Subscribes channel the message was sent in. Will post events to this channel."""
        channel_id = ctx.channel.id
        # TODO
        print(f"Called function with arguments: {visibility}")
        await ctx.send(f"Called function with {len(visibility)} arguments: {visibility}")
        pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unsubscribe(self, ctx, *, visibility):
        """Unsubscribes topics from the channel the message was sent in. If no topics are given, the entire channel will be unsubscribed."""
        channel_id = ctx.channel.id
        #TODO
        print(f"Called function with arguments: {visibility}")
        await ctx.send(f"Called function with {len(visibility)} arguments: {visibility}")
        await self.notifyChannel(channel_id, None)
        pass

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def getSubscribedTopics(self, ctx):
        """Returns topics this channel is subscribed to."""
        channel_id = ctx.channel.id
        #TODO
        print(f"Called function. Channel-ID: {channel_id}")
        await ctx.send(f"Called function. Channel-ID: {channel_id}")
        pass


def setup(bot):
    bot.add_cog(EventListener(bot))
