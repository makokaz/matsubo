"""Event Listener Cog

Discord Bot Cog that scraps the web for events, and then posts them on subscribed channels.
"""

import os
import discord
import asyncio
import datetime
import pytz

from discord.ext import commands, tasks
from itertools import cycle
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .utils import utils
from .utils import database as db
from .utils.event import Event
from .utils.event_scrapper import getEvents


#########################
# Global variables
#########################
# Note: The time variables below are in UNIX CRON format:
#           *    *        *         *       *
#          min  hour  dayOfMonth  month  weekday
#       For example: "Every 2nd hour at minute 0 on Monday to Thursday every month"
#                    -> 0 0-23/2 * * 0-3

# Local timezone
LOCAL_TZ = pytz.timezone('Asia/Tokyo')

# Times when the web-scrapper should run
SCRAP_TIMES = '0 15 * * *'  # Every day at 15:00

# Times when new events shall be posted to subscribed channels
POST_TIMES = '0 20 * * 5-6'  # Every Saturday & Sunday at 20:00
# POST_TIMES = '0-59/2 * * * *'  # for DEBUGGING

# Time when it shall be reminded of events happening today/tomorrow/...
# REMIND_TIMES = '* 10 * * *'  # Every day at 10:00
REMIND_TIMES = '0-59 * * * *'  # for DEBUGGING
REMIND_BEFORE_DAYS = 0  # how many days before the reminder should be done

# Define (logo, thumbnail, footer) for all sources that are scrapped
SCRAP_SOURCES = {
    'Web:TokyoCheapo': {
        'footer': 'TOKYO CHEAPO',
        'icon': 'https://community.tokyocheapo.com/uploads/db1536/original/1X/91a0a0ee35d00aaa338a0415496d40f3a5cb298e.png',
        'thumbnail': 'https://cdn.cheapoguides.com/wp-content/themes/cheapo_theme/assets/img/logos/tokyocheapo/logo.png'
    },
    'Web:JapanCheapo': {
        'footer': 'JAPAN CHEAPO',
        'icon': 'https://pbs.twimg.com/profile_images/1199468429553455104/GdCZbc-R_400x400.png',
        'thumbnail': 'https://cdn.cheapoguides.com/wp-content/themes/cheapo_theme/assets/img/logos/japancheapo/logo.png'
    }
}

# Sleep status messages that will be iterated through
SLEEP_STATUS = [f"Counting 🐑... {i} {'💤' if i%2 else ''}" for i in range(1, 10)]

# How many past messages are checked per channel for event searching
SEARCH_DEPTH = 10


#########################
# Classes & Functions
#########################

class EventListener(commands.Cog):
    """Discord Cog, Bot Addon.

    This cog gives the bot the ability to scrap for events in the web and post them in subscribed channels.
    """
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone=LOCAL_TZ)
        self.scheduler.start()

        # Start scheduled tasks
        self.scheduler.add_job(self.loop_scrap, CronTrigger.from_crontab(SCRAP_TIMES), id='scrap')
        self.scheduler.add_job(self.loop_post, CronTrigger.from_crontab(POST_TIMES), id='post')
        self.scheduler.add_job(self.loop_remind, CronTrigger.from_crontab(REMIND_TIMES), id='remind')

        # Print next run times of scheduled tasks
        print('Next run time of scheduled tasks:')
        print(f"  > {self.scheduler.get_job('scrap').func.__name__.upper()}:  {self.scheduler.get_job('scrap').next_run_time}")
        print(f"  > {self.scheduler.get_job('post').func.__name__.upper()}:   {self.scheduler.get_job('post').next_run_time}")
        print(f"  > {self.scheduler.get_job('remind').func.__name__.upper()}: {self.scheduler.get_job('remind').next_run_time}")

        # Start other loops
        self.countingSheeps.start()


    @tasks.loop(seconds=10)
    async def countingSheeps(self):
        """Counts sheeps. Very handy, because it shows the bot is still running."""
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(next(self.status_cycle)))
    def cog_unload(self):
        self.countingSheeps.cancel()
    @countingSheeps.before_loop
    async def before_countingSheeps(self):
        await self.bot.wait_until_ready()
        self.status_cycle = cycle(SLEEP_STATUS)
    @countingSheeps.after_loop
    async def on_countingSheeps_cancel(self):
        # if self.countingSheeps.is_being_cancelled():
        #     await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(name='Internet', type=discord.ActivityType.listening))
        pass

    @utils.log_call
    async def loop_scrap(self):
        """[Background task] Scraps web at specified times for new events."""
        await self.bot.wait_until_ready()
        self.countingSheeps.cancel()
        await asyncio.sleep(1) #bugfix: wait before change_presence is called too fast!
        await self.scrap()
        await asyncio.sleep(1) #bugfix: wait before change_presence is called too fast!
        self.countingSheeps.start()
        print(f"Next run time of LOOP_SCRAP():  {self.scheduler.get_job('scrap').next_run_time}")

    @utils.log_call
    async def loop_post(self):
        """[Background task] Notifies all subscribed channels of new events."""
        await self.bot.wait_until_ready()
        self.countingSheeps.cancel()
        await asyncio.sleep(1) #bugfix: wait before change_presence is called too fast!
        await self.notify()
        await asyncio.sleep(1) #bugfix: wait before change_presence is called too fast!
        self.countingSheeps.start()
        print(f"Next run time of LOOP_POST():  {self.scheduler.get_job('post').next_run_time}")
    
    @utils.log_call
    async def loop_remind(self):
        """[Background task] Reminds subscribed channels of when events are happening (today, tomorrow, ...).
        
        The global variable `REMIND_BEFORE_DAYS`` defines how many days prior to the start of the event the reminder will be issued.
        """
        await self.bot.wait_until_ready()
        self.countingSheeps.cancel()
        await asyncio.sleep(1) #bugfix: wait before change_presence is called too fast!
        await self.remind()
        await asyncio.sleep(1) #bugfix: wait before change_presence is called too fast!
        self.countingSheeps.start()
        print(f"Next run time of LOOP_REMIND():  {self.scheduler.get_job('remind').next_run_time}")
    
    async def scrap(self):
        """Searches the web for new events, and puts them into the database"""
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('Scrapping the web...'))

        # Scrap events
        print("Scrapping events...")
        events = getEvents()
        # print("Found the following events:")
        # for event in events:
        #    print(event)

        # Insert events into database
        db.eventDB.insertEvents(events)

        print("Finished scrapping events!")
        pass
    
    async def notify(self, channels:list[commands.TextChannelConverter]=None):
        """Notifies given channels of new events.

        If no list of channels are given, it defaults to notifying every channel.

        Parameters
        ------------
        channels: Optional[:class:`list`[:class:`commands.TextChannelConverter`]]
            The channels to be notified, ``None`` if all channels shall be notified.
        """
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('Notifying channels...'))

        # Extract subscribed topics per channel from database
        if channels:
            chvs = [[channel.id, db.discordDB.getChannelVisibility(channel.id)] for channel in channels]
            print(f'### Notifying channels {channels} of new events')
        else:
            chvs = db.discordDB.getAllChannelVisibility()
            print('### Notifying all channels of new events')

        # Loop over every channel
        for chv in chvs:
            channel = self.bot.get_channel(chv[0])
            topics = chv[1]
            #print(f"Channel-ID: {channel.id};  Topics: {topics}")

            # Obtain all events in database from today until 1 week of topics this channel has subscribed to
            events = db.eventDB.getEvents(
                visibility=topics,
                from_date=datetime.datetime.now(tz=LOCAL_TZ).date(),
                until_date=datetime.datetime.now(tz=LOCAL_TZ).date()+datetime.timedelta(weeks=1)
            )

            ################
            # Notify channel
            ################
            print(f"-> Notifying channel #{channel}:{channel.id} of new events")

            # Find messages of events that have already been posted to discord
            messages, idx = await self.findEventMessages(channel, events)

            # Loop over every event
            for i, event in enumerate(events):
                if i in idx:  # If event has already been posted before, update it with new details (if any)
                    message = messages[idx.index(i)]
                    # Only edit if embed has changed
                    if self.embedsAreEqual(message.embeds[0], self.getEmbed(event)):
                        continue
                    # Edit message
                    await message.edit(embed=self.getEmbed(event))
                    print(f'Edited event in message: {event.name} [{event.id}] -> Message-ID:{message.id}')
                    pass
                else:  # Post NEW event
                    if event.status.lower() in ['cancelled','canceled']:
                        continue # Only post if event has not been cancelled in the first place
                    await channel.send(content=f'***{event.name} [{event.id}]***', embed=self.getEmbed(event))
                    print(f'Posted event to channel: {event.name} [{event.id}] -> #{channel}:{channel.id}')
                await asyncio.sleep(2) #bugfix: sleep for some time before new event is posted
        
        print("### Notified all channels!")

    async def remind(self, channels:list[commands.TextChannelConverter]=None):
        """Reminds given channels of events that are happening soon.
        
        If no list of channels are given, it defaults to reminding every channel.

        The global variable `REMIND_BEFORE_DAYS`` defines how many days prior to the start of the event the reminder will be issued.

        Parameters
        ------------
        channels: Optional[:class:`list`[:class:`commands.TextChannelConverter`]]
            The channels to be notified, ``None`` if all channels shall be notified.
        """
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('Checking for reminders...'))

        # Extract subscribed topics per channel from database
        if channels:
            chvs = [[channel.id, db.discordDB.getChannelVisibility(channel.id)] for channel in channels]
            print(f'### Reminding channels {channels} of current events')
        else:
            chvs = db.discordDB.getAllChannelVisibility()
            print('### Reminding all channels of current events')
        
        # Loop over every channel
        for chv in chvs:
            channel = self.bot.get_channel(chv[0])
            topics = chv[1]
            #print(f"Channel-ID: {channel.id};  Topics: {topics}")

            # Obtain all currently happening events in database of topics this channel has subscribed to
            events = db.eventDB.getEvents(
                visibility=topics,
                from_date=(datetime.datetime.now(tz=LOCAL_TZ)+datetime.timedelta(days=REMIND_BEFORE_DAYS)).date(),
                until_date=(datetime.datetime.now(tz=LOCAL_TZ)+datetime.timedelta(days=REMIND_BEFORE_DAYS)).date()
            )

            if not events:
                print(f"-> Channel #{channel}:{channel.id} has no currently happening events")
                return

            ################
            # Remind channel
            ################
            print(f"-> Reminding channel #{channel}:{channel.id} of currently happening events")
            for event in events:
                print(event)

            # Find reminder that has already been posted to Discord
            message = await self.findReminderMessage(channel, events)
            #TODO find all event embeds for the reminder, so the embed-URLs can be set as links in the reminder message

            if message:
                #TODO Edit reminder, in case they changed -> Or delete it, and send a new reminder?
                pass
            else:
                #TODO Construct reminder
                pass

        print('### Reminded all channels!')

    async def findReminderMessage(self, channel: commands.TextChannelConverter, events: list[Event]) -> discord.Message:
        """Finds latest reminder message of currently happening events.

        Parameters
        ------------
        channel: :class:`discord.TextChannel`
            The channel where to search for the reminder.
        events: :class:`list`[:class:`Event`]
            The events to check if they have all been mentioned in the reminder.
        """
        #TODO
        pass

    def getReminder(self, events:list[Event]) -> str:
        """Creates reminder message and returns as string.

        Parameters
        ------------
        events: :class:`list`[:class:`Event`]
            The list of currently happening events.
        """
        #TODO
        pass

    async def findEventMessages(self, channel: commands.TextChannelConverter, events: list[Event]) -> tuple[list[discord.Message],list[int]]:
        """Finds events that have already been posted to discord.

        Returns the messages and the indices of the events in the provided list.

        Parameters
        ------------
        channel: :class:`discord.TextChannel`
            The channel where to search for already posted events.
        events: :class:`list`[:class:`Event`]
            The events to check for if they have already been posted.
        """
        # Search results will be appended to these lists
        messages = []
        idx = []

        # Loop over every message
        async for message in channel.history(limit=SEARCH_DEPTH):
            if not len(message.embeds):
                continue
            if message.author != self.bot.user:
                continue

            # Find index in list events that matches the discord message event
            embed = message.embeds[0]
            datefield = next((field for field in embed.fields if field.value.startswith(':date:')))
            i = next((i for i,event in enumerate(events) if event.id==embed.footer.text.split()[-1] and f':date: ***{event.getDateRange()}***'==datefield.value), None)
            
            if i is None:
                continue

            # Append message and index to return-lists
            messages.append(message)
            idx.append(i)
        return messages, idx


    def getEmbed(self, event: Event) -> discord.Embed:
        """Returns discord.Embed object of given event

        Parameters
        ------------
        event: :class:`Event`
            The event.
        """
        embed = discord.Embed(
            title=event.name,
            colour=discord.Colour(0xd69d37),
            url=event.url,
            description=f"```{event.description}```\nFind out more [here]({event.url}).",
            timestamp=event.date_added if event.date_added else datetime.datetime.now(tz=pytz.timezone('Asia/Tokyo'))
        )

        # Set event image
        if event.img:
            embed.set_image(url=event.img)

        # Set author
        embed.set_author(
            name=os.getenv("BOT_NAME", 'Matsubo'),
            url=os.getenv("BOT_URL", 'https://github.com/makokaz/matsubo'),
            icon_url=os.getenv("BOT_ICON_URL", 'https://discord.com/assets/f9bb9c4af2b9c32a2c5ee0014661546d.png')
        )

        # Set footer & thumbnail
        if event.source in SCRAP_SOURCES.keys():
            embed.set_footer(
                text=f"{SCRAP_SOURCES[event.source]['footer']} • {event.id}",
                icon_url=SCRAP_SOURCES[event.source]['icon']
            )
            embed.set_thumbnail(url=SCRAP_SOURCES[event.source]['thumbnail'])
        else:
            embed.set_footer(text=[event.source])

        # Add field: CANCELLED
        if event.status.lower() in ['cancelled', 'canceled']:
            embed.add_field(name=':x: ***This event has been CANCELLED***', value='\u200B', inline=False)
        # Add field: Date
        embed.add_field(name='\u200B', value=f':date: ***{event.getDateRange()}***', inline=True)
        # Add field: Time
        embed.add_field(name='\u200B', value=f':clock10: ***{event.getTimeRange()}***', inline=True)
        # Add field: Cost
        embed.add_field(name='\u200B', value=f':coin: ***{event.cost}***', inline=True)
        # Add field: Location
        loc_string = ''
        if event.status.lower() == 'online':
            loc_string += f"[ONLINE]({event.url}), "
        for location in event.location.split(', '):
            loc_string += f"[{location}](https://www.google.com/maps/search/?api=1&query={location.replace(' ','%')}), "
        loc_string = loc_string.rstrip(', ')
        if loc_string == '':
            loc_string = '---'
        embed.add_field(name='\u200B', value=f":round_pushpin: ***{loc_string}***", inline=True)
        
        return embed

    def embedsAreEqual(self, embed1:discord.Embed, embed2:discord.Embed) -> bool:
        """Checks if two :class:`discord.Embed` representing two :class:`Event` are equal.

        Equality happens when their metadata (all fields in the embed) are equal.

        Parameters
        ------------
        embed1: :class:`discord.Embed`
            The embed of the first event.
        embed2: :class:`discord.Embed`
            The embed of the second event.
        """
        if embed1.title != embed2.title:
            return False
        if embed1.url != embed2.url:
            return False
        if embed1.description != embed2.description:
            return False
        if embed1.image.url != embed2.image.url:
            return False
        if embed1.footer.text != embed2.footer.text:
            return False
        if embed1.footer.icon_url != embed2.footer.icon_url:
            return False
        if embed1.thumbnail.url != embed2.thumbnail.url:
            return False

        # Check if fields are equal
        if len(embed1.fields) != len(embed2.fields):
            return False
        fieldsAreEqual = next((False for i in range(len(embed1.fields)) if
            embed1.fields[i].name   != embed2.fields[i].name   or
            embed1.fields[i].value  != embed2.fields[i].value  or
            embed1.fields[i].inline != embed2.fields[i].inline
        ), True)
        if not fieldsAreEqual:
            return False
        return True
    
    @commands.command(name='scrap')
    @commands.has_permissions(administrator=True)
    async def cmd_scrap(self, ctx):
        """Searches the web for new events, and posts updates to all subscibed channels."""
        self.countingSheeps.cancel()

        await ctx.send(f"Scanning the web... this might take a while :coffee:")
        await self.scrap()
        await self.notify()
        await ctx.send(f"That's all I could find :innocent:")

        await asyncio.sleep(2) #bugfix: wait before change_presence is called too fast!
        self.countingSheeps.start()

    @commands.command(name='subscribe')
    @commands.has_permissions(administrator=True)
    async def cmd_subscribe(self, ctx, *topics):
        """Subscribes channel the message was sent in. Will post events to this channel."""
        topics = set(topics)
        topics_all = topics | db.discordDB.getChannelVisibility(ctx.channel.id)
        db.discordDB.updateChannel(ctx.channel.id, list(topics_all))
        await ctx.send(f"Subscribed the following new topics: {topics}\nAll subscribed topics of this channel: {topics_all}")

    @commands.command(name='unsubscribe')
    @commands.has_permissions(administrator=True)
    async def cmd_unsubscribe(self, ctx, *topics):
        """Unsubscribes topics from the channel the message was sent in. If no topics are given, the entire channel will be unsubscribed."""
        if len(topics):
            topics = set(topics)
            topics_new = db.discordDB.getChannelVisibility(ctx.channel.id) - topics
        else:
            topics_new = None
        if topics_new:
            db.discordDB.updateChannel(ctx.channel.id, list(topics_new))
            await ctx.send(f"Unsubscribed the following topics: {topics}\nAll subscribed topics of this channel: {topics_new}")
        else:
            db.discordDB.removeChannel(ctx.channel.id)
            await ctx.send("Unsubscribed channel from all topics")

    @commands.command(name='getsubscribedtopics')
    @commands.has_permissions(administrator=True)
    async def cmd_getSubscribedTopics(self, ctx):
        """Returns topics this channel is subscribed to."""
        topics_all = db.discordDB.getChannelVisibility(ctx.channel.id)
        if topics_all:
            await ctx.send(f"All subscribed topics of this channel: {topics_all}")
        else:
            await ctx.send("This channel has no subscribtions")


def setup(bot):
    bot.add_cog(EventListener(bot))


# TODO:
# - One day before the event, remind that the event is starting
# - Implement command that returns which events are happening {currently; in given period; this month;  in this area; ...}
# - Extend sources of event scrapping
# - Add list of topics one can subscribe
