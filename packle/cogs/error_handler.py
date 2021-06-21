# -*- coding: utf-8 -*-


# standard library modules
import traceback
import sys

# third party modules - discord related
from discord.ext import commands


class CommandErrorHandler(commands.Cog):
    """
    cog for handling errors in commands that don't have their own handler
    """

    def __init__(self, bot: commands.Bot):
        """
        initializer
        """

        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """
        triggered when an exception is raised during command invocation
        """

        # ignore exceptions that have their own error (exception) handler
        if hasattr(ctx.command, 'on_error'):
            return

        # specific types of exceptions to ignore
        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        # handle specific types of exceptions
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'`Error: {ctx.command} has been disabled`')
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f"`Error: {ctx.command} can't be used in DMs`")
            except:
                pass
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                return await ctx.send('`Error: member not found`')

        # print traceback to terminal if exception wasn't already taken care of
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot: commands.Bot):
    """
    function a commands.Bot method uses to load this cog
    """

    bot.add_cog(CommandErrorHandler(bot))
