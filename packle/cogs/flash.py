# -*- coding: utf-8 -*-


# standard library modules
import asyncio

# third party modules - discord related
import discord
from discord.ext import commands


class FlashCog(commands.Cog, name="flash"):
    """
    cog for flashcard commands and related
    """

    def __init__(self, bot: commands.Bot):
        """
        initializer
        """

        self.bot = bot
        self.accepted_attachment_types = {
            'text/csv; charset=utf-8',
            'text/plain; charset=utf-8',
        }

        # default separators if not otherwise specified
        self.default_qa_sep = ','
        self.default_line_sep = '\n'


    @commands.command()
    async def test(self, ctx: commands.Context):
        flashcards = [
            ['What does the Jim say?', 'This duck sucks', 1],
            ['q01', 'a01', 1],
            ['q02', 'a02', 1],
            ['q03', 'a03', 1],
            ['q04', 'a04', 1],
            ['q05', 'a05', 1],
            ['q06', 'a06', 1],
            ['q07', 'a07', 1],
            ['q08', 'a08', 1],
            ['q09', 'a09', 1],
            ['q10', 'a10', 1],
            ['q11', 'a11', 1],
            ['q12', 'a12', 1],
            ['q13', 'a13', 1],
            ['q14', 'a14', 1],
            ['q15', 'a15', 1],
            ['q16', 'a16', 1],
            ['q17', 'a17', 1],
            ['q18', 'a18', 1],
            ['q19', 'a19', 1],
        ]


        question, answer, box = flashcards[0]

        embed = discord.Embed(title=question,
                              colour=0xefa607)
        embed.add_field(name='Answer', value=f'||{answer}||')

        msg: discord.Message = await ctx.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        def check(reaction, user):
            if msg != reaction.message or user != ctx.author:
                return

            if str(reaction.emoji) in '✅❌':
                return reaction, user

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            await ctx.send('success')
        except asyncio.TimeoutError:
            await ctx.send('timed out waiting for reaction')


    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
    #     pass
    #     # role, user = self.parse_reaction_payload(payload)
    #     # if role is not None and user is not None:
    #     #     await user.add_roles(role, reason="ReactionRole")


    # @commands.Cog.listener()
    # async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
    #     pass
    #     # role, user = self.parse_reaction_payload(payload)
    #     # if role is not None and user is not None:
    #     #     await user.remove_roles(role, reason="ReactionRole")

    # async def parse_payload(self):
    #     pass
    # # user = await client.fetch...


    @commands.command(aliases=['quiz', 'cards', 'flashcards'])
    async def flash(self, ctx: commands.Context, *, csv_text: str) -> None:
        """
        base command for a flash card quiz which will fork depending on ctx type
        """

        # check if there is any viable csv text in the message text itself
        csv_lines = await self.parse_text(csv_text)

        # check if there is viable csv in any of the message attachments, and add that to what if any we already have
        attachment_lines = await self.parse_attachments(ctx.message)

        if attachment_lines:
            csv_lines.extend(attachment_lines)

        # if no viable q/a csv can found in message text or attachments, command fails and stops
        if not csv_lines:
            return await ctx.send('`Error: no viable question,answer csv data in message text or attachments`')

        # send csv data to be forked between the two different variations of the quiz
        return await self.fork_flash(ctx, csv_lines)


    @flash.error
    async def flash_handler(self, ctx: commands.Context, error: Exception) -> None:
        """
        error handler for flash command
        """

        # if no questions/answers given in text form then check attachments
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'csv_text':

                # check if the message has an attached cvs file to use
                csv_lines = await self.parse_attachments(ctx.message)

                # if no questions/answers can be obtained from any attachments either, command fails and stops
                if not csv_lines:
                    return await ctx.send('`Error: no viable question,answer csv data in message text or attachments`')

                # send viable csv data to the fork which will choose which game mode to play
                return await self.fork_flash(ctx, csv_lines)


    async def fork_flash(self, ctx: commands.Context, csv_lines: list):
        """
        determine which version of the the app is going to be used
        """

        # if ctx.guild is not None, fork to the multiplayer flash quiz mode
        if ctx.guild:
            return await self.flash_guild(ctx, csv_lines)

        # otherwise use the more helpful flash quiz mode that focuses on weak points
        else:
            return await self.flash_dm(ctx, csv_lines)


    async def flash_guild(self, ctx: commands.Context, csv_lines: list):
        """
        multiplayer guild (server) flash quiz mode
        """

        # testing
        await ctx.send('\n'.join(csv_lines))


    async def flash_dm(self, ctx: commands.Context, csv_lines: list):
        """
        single player (DM) flash quiz mode that focuses on weak points
        """

        # testing
        await ctx.send('\n'.join(csv_lines))


    async def parse_attachments(self, message: discord.Message, sep: str = None, line_sep: str = None):
        """
        check all attachments on the command message for viable question,answer csv data
        """

        # use default question,answer separator if sep is None
        if sep is None:
            sep = self.default_qa_sep

        # use default line separator if line_sep is None
        if line_sep is None:
            line_sep = self.default_line_sep

        # typehinting for intellisense convenience
        attachment: discord.Attachment

        # initialize empty list to append any attachment text lines to
        lines = []

        # iterate attachments
        for attachment in message.attachments:

            # check if the attachment has an accepted content_type
            if attachment.content_type not in self.accepted_attachment_types:
                continue

            # attempt to get a utf-8 string from the attachment
            attachment_text = ''
            try:

                # read the attachment into a standard library builtins bytes type variable
                attachment_bytes: bytes = await attachment.read()

                # attempt to decode it into a standard library builtins str type variable
                attachment_text: str = attachment_bytes.decode('utf-8')
            except:

                # just do nothing if it can't be decoded into a str
                pass

            # continue to next attachment if we couldn't get a str from the attachment
            if not attachment_text:
                continue

            # parse attachment text for viable csv data
            attachment_lines = await self.parse_text(attachment_text, sep=sep, line_sep=line_sep)

            # add it to current csv data if any is found, with in-place list modification
            if attachment_lines:
                lines.extend(attachment_lines)

        return lines


    async def parse_text(self, text: str, sep: str = None, line_sep: str = None):
        """
        parse text for viable question,answer csv data
        """

        # use default question,answer separator if sep is None
        if sep is None:
            sep = self.default_qa_sep

        # use default line separator if line_sep is None
        if line_sep is None:
            line_sep = self.default_line_sep

        lines = []

        # iterate through the lines of text to check for viability
        for line in text.split(line_sep):

            # strip leading and trailing whitespace
            line = line.strip()

            # continue if it's not possible for the line to have a question, answer, and separator
            if len(line) < 3:
                continue

            # make an iterator for the line (string), which will iterator through the characters
            it = iter(line)

            # continue if the first character is the separator
            x = next(it)
            if x == sep:
                continue

            # determine if the line is viable
            viable = False
            for i, x in enumerate(it, 2):
                if x == sep:

                    # if the first instance of separator isn't the last character in the string
                    if i != len(line):
                        viable = True
                    break

            # if it's viable add it to existing viable csv data
            if viable:
                lines.append(line)

        return lines


    # @commands.command(name='embeds')
    # @commands.guild_only()
    # async def example_embed(self, ctx):
    #     """A simple command which showcases the use of embeds.

    #     Have a play around and visit the Visualizer."""

    #     embed = discord.Embed(title='Example Embed',
    #                           description='Showcasing the use of Embeds...\nSee the visualizer for more info.',
    #                           colour=0x98FB98)
    #     embed.set_author(name='MysterialPy',
    #                      url='https://gist.github.com/MysterialPy/public',
    #                      icon_url='http://i.imgur.com/ko5A30P.png')
    #     embed.set_image(url='https://cdn.discordapp.com/attachments/84319995256905728/252292324967710721/embed.png')

    #     embed.add_field(name='Embed Visualizer', value='[Click Here!](https://leovoel.github.io/embed-visualizer/)')
    #     embed.add_field(name='Command Invoker', value=ctx.author.mention)
    #     embed.set_footer(text='Made in Python with discord.py@rewrite', icon_url='http://i.imgur.com/5BFecvA.png')

    #     await ctx.send(content='**A simple Embed for discord.py@rewrite in cogs.**', embed=embed)


def setup(bot: commands.Bot) -> None:
    """
    function a commands.Bot method uses to load this cog
    """

    bot.add_cog(FlashCog(bot))
