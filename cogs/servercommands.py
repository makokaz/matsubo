"""Server Commands Cog

Simple discord bot cog that defines basic commands on a server for a bot:
- managing roles
- testing
- fun activites
- ... and more!
"""

import discord
from discord.ext import commands

class ServerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """TODO: Write member they should choose their university"""
        print(f'{member} has joined the server.')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter, *, reason=None):
        """Kicks specified member from server"""
        await member.kick(reason=reason)
        await ctx.send(f"{member} was kicked from the server.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.MemberConverter, *, reason=None):
        """Bans specified member from server"""
        await member.ban(reason=reason)
        await ctx.send(f"{member} was banned from the server.")
    
    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        """Unbans specified member from server"""
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator)==(member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"{user.mention} was unbanned.")
                return
        

    @commands.command(aliases=['test'])
    async def ping(self, ctx):
        """Test command to check if bot has not frozen && discord API is still working"""
        await ctx.send(f'pong! [{round(self.bot.latency * 1000)}ms]')

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount : int):
        """Bulk clears the last #amount messages in the channel"""
        #await ctx.send(f'The last {amount} messages will be deleted.')
        await ctx.channel.purge(limit=amount)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Gets called when an error happens due to a false command by a user"""
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'You forgot to specify a few arguments.\nType: `{self.bot.command_prefix}help <command>` to see the required arguments.')
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f"I don't know this command... sorry 🙈\nType:\n   - `{self.bot.command_prefix}help` for general help\n   - `{self.bot.command_prefix}help <COMMAND>` to get specific help for this command")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Too much power, this command for you has, {ctx.message.author.display_name} 😬")
        else:
            await ctx.send(f"Something went wrong... 🙈\n   - Type `{self.bot.command_prefix}help` for general help\n   - Tag the admins with `@Admin` to ask for their help!")


def setup(bot):
    bot.add_cog(ServerCommands(bot))
