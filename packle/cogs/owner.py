# -*- coding: utf-8 -*-


# third party modules - discord related
from discord.ext import commands


class OwnerCog(commands.Cog, name="owner"):
    """
    owner commands concerning cogs
    """

    def __init__(self, bot: commands.Bot):
        """
        initializer
        """

        self.bot = bot


    @commands.command(name='load', hidden=True)
    # @commands.is_owner()
    async def load_cog(self, ctx: commands.Context, *, cog: str) -> None:
        """
        load a cog module
        ex: $load cogs.flash
        """

        try:
            self.bot.load_extension(cog)
        except Exception as e:  # pylint: disable=broad-except
            await ctx.send(f'`Error: {type(e).__name__} - {e}`')
        else:
            await ctx.send('`Success: loaded cog`')


    @commands.command(name='unload', hidden=True)
    # @commands.is_owner()
    async def unload_cog(self, ctx: commands.Context, *, cog: str) -> None:  # pylint: disable=arguments-differ
        """
        unload a cog module
        ex: $unload cogs.flash
        """

        try:
            self.bot.unload_extension(cog)
        except Exception as e:  # pylint: disable=broad-except
            await ctx.send(f'`Error: {type(e).__name__} - {e}`')
        else:
            await ctx.send('`Success: unloaded cog`')


    @commands.command(name='reload', hidden=True)
    # @commands.is_owner()
    async def reload_cog(self, ctx: commands.Context, *, cog: str) -> None:
        """
        reload a cog module
        ex: $reload cogs.flash
        """

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:  # pylint: disable=broad-except
            await ctx.send(f'`Error: {type(e).__name__} - {e}`')
        else:
            await ctx.send('`Success: reloaded cog`')


def setup(bot: commands.Bot) -> None:
    """
    function a commands.Bot method uses to load this cog
    """

    bot.add_cog(OwnerCog(bot))
