# -*- coding: utf-8 -*-


# standard library modules
import os
import sys
import traceback

# third party modules
from dotenv import load_dotenv

# third party modules - discord related
import discord
from discord.ext import commands


def main(bot: commands.Bot, indent: int = 4, underline: bool = True) -> None:
    """
    main function to launch the bot
    """

    # load token into system environment from .env file
    load_dotenv()

    # get token from system environment
    token = os.getenv('DISCORD_TOKEN')

    # cogs that are loaded by default
    default_cogs = [
        'cogs.error_handler',
        'cogs.flash',
        'cogs.owner',
    ]

    # load the default cogs
    title = 'loading cogs'
    print(title)
    if underline:
        print(f"{'-' * len(title)}")
    for cog in default_cogs:
        try:
            bot.load_extension(cog)
            print(f"{' ' * indent}{cog}")
        except:

            # print traceback and continue loading remaining cogs
            print(f'`Error: failed to load extension {cog}`', file=sys.stderr)
            traceback.print_exc()
    print()

    # run the bot
    bot.run(token, bot=True, reconnect=True)


# makes it so the code doesn't automatically run if this file is imported into another python file
if __name__ == '__main__':

    # text formatting variables
    indent = 4
    underline = True

    # intialize the bot
    bot = commands.Bot(command_prefix='$', description='flash card bot')

    # add/override on_ready method to bot
    @bot.event
    async def on_ready():
        """
        called when the bot logs in (usually)
        prints some useful status info to the terminal
        """

        print('--- startup complete ---\n')

        # print information about the bot
        bot_info = [
            ['bot username', f"'{bot.user.name}#{bot.user.discriminator}'"],
            ['bot id', bot.user.id],
            ['server count', len(bot.guilds)],
            ['discord.py version', discord.__version__],
        ]
        title = 'bot information'
        print(title)
        if underline:
            print(f"{'-' * len(title)}")

        # find the length of the longest title in bot_info for padding purposes (+1 for colon)
        sz = max((len(name) for name, _ in bot_info), default=0) + 1

        # iterate through info and print the titles and values
        for name, value in bot_info:
            print(f"{' ' * indent}{name + ':':<{sz}} {value}")
        print()

        # print information about the servers the bot is a member of
        title = 'current server names and ids'
        print(title)
        if underline:
            print(f"{'-' * len(title)}")

        # find the length of the longest Guild.name in bot.guilds for padding purposes (+3 for colon and quotes)
        sz = max((len(guild.name) for guild in bot.guilds), default=0) + 3

        # iterate through info and print the titles and values
        for guild in bot.guilds:
            print(f"{' ' * indent}{guild.name.__repr__() + ':':<{sz}} {guild.id}")

        # print newline and flush the buffer to make sure everything is printed in a timely fashion
        print(flush=True)

    # run the bot
    main(bot, indent=indent, underline=underline)
