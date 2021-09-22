# -*- coding: utf-8 -*-


# standard library modules
import asyncio

# third-party packages - discord related
import discord
from discord.ext import commands
import dpymenus
from dpymenus import ButtonMenu

# local modules
from utils import send_error_msg
from cardpack import CardPack
from packlebot import Packle
from ui import make_card_page
from constants import Colors, Emojis


class Quiz(commands.Cog, name='quiz_mode'):

    def __init__(self, bot: Packle) -> None:
        """initializer"""

        self.bot = bot

        # quiz mode logic specific
        self.quiz_sessions_by_user_id = {}
        self.quiz_messages_by_id = {}
        self.quiz_interval_default = 10


    @commands.command(
        description='multiplayer quiz mode',
        help=(
            'This is a multiplayer quiz mode where anyone can join in. '
            'Just answer the question and then reveal the spoiler to see if you were '
            'correct, react with the check mark if you were, and the cross if not. '
            'Questions will automatically keep changing based on either the default '
            'interval or a custom one you set when you start the quiz '
            '(min 5 seconds, max 60 seconds). '
            'Scores for all players will be displayed at the end.'
        ),
    )
    @commands.guild_only()
    async def quiz(
            self,
            ctx: commands.Context,
            pack_name: str = None,
            interval: float = None,
    ) -> None:
        """
        multiplayer quiz mode (server channels only)
        """

        # check for missing pack_name and handle it
        if pack_name is None:
            msg = 'Missing required argument `<pack_name>`'
            return await send_error_msg(ctx, msg)

        if interval is None:
            interval = self.quiz_interval_default
        else:
            interval = min(60.0, interval)
            interval = max(5.0, interval)

        # send error message and return if they already have a quiz session
        if ctx.author.id in self.quiz_sessions_by_user_id:
            msg = "You're already running a Quiz session"
            return await send_error_msg(ctx, msg)

        # send error message and return if pack doesn't exist
        if (
            ctx.author.id not in self.bot.packs
            or pack_name not in self.bot.packs[ctx.author.id]
        ):
            msg = 'pack not found'
            return await send_error_msg(ctx, msg)

        # send error message and return if the pack doesn't exist
        if ctx.author.id not in self.bot.packs or pack_name not in self.bot.packs[ctx.author.id]:
            msg = 'Pack not found'
            return await send_error_msg(ctx, msg)

        # get the pack
        pack = self.bot.packs[ctx.author.id][pack_name]

        # start the quiz
        return await self._quiz(ctx, pack, interval)


    @quiz.after_invoke
    async def quiz_after_invoke(self, ctx: commands.Context):
        """
        handle cleaning up the mp quiz session dicts even if there is an error
        """

        if ctx.author.id in self.quiz_sessions_by_user_id:
            message_id = self.quiz_sessions_by_user_id[ctx.author.id]['message'].id
            if message_id in self.quiz_messages_by_id:
                self.quiz_messages_by_id.pop(message_id, None)
            self.quiz_sessions_by_user_id.pop(ctx.author.id, None)


    async def _quiz(self, ctx: commands.Context, pack: CardPack, interval: float):
        """
        backend for quiz command
        """

        pack = CardPack(
            (card for card in pack),
            dm_channel=None,
            name=pack.name,
            author=pack.author,
            category=pack.category,
            difficulty=pack.difficulty,
        )

        # create initial page
        page = await make_card_page(pack, 0, quiz_mode=True)

        # initialize and configure menu
        menu = ButtonMenu(ctx)
        menu.persist_on_close()
        menu.set_timeout(0)
        menu.show_command_message()
        menu.add_pages([page])

        # hook callback clear reaction buttons after session has ended
        async def clear_reaction_buttons():
            nonlocal menu
            if menu.output and menu.output.guild:
                message: discord.Message = menu.output

                # this might throw an exception if missing permissions to clear reactions
                await message.clear_reactions()

        # menu timeout hook
        menu.add_hook(
            when=dpymenus.hooks.AFTER,
            event=dpymenus.hooks.TIMEOUT,
            callback=clear_reaction_buttons
        )

        # menu close hook
        menu.add_hook(
            when=dpymenus.hooks.AFTER,
            event=dpymenus.hooks.CLOSE,
            callback=clear_reaction_buttons
        )

        # run this flashcard mode
        await menu.open()
        message: discord.Message = menu.output

        # create a dict that stores the game information, scores, the message
        # that the game is being played in, the players, whether or not the 
        # game creator wants to exit
        self.quiz_sessions_by_user_id.update({
            ctx.author.id: {
                'message': message,
                'players': {ctx.author: 0},
                'configuring': False,
                'exit': False,
            }
        })
        self.quiz_messages_by_id.update({message.id: message})

        # each iteration of this loop is a quiz flashcard
        for index, _ in enumerate(pack):

            # clear the reactions so they're fresh for the next card
            await message.clear_reactions()

            # if the person who started the quiz clicked exit, we break the loop
            if self.quiz_sessions_by_user_id[ctx.author.id]['exit']:
                break

            # we already made the first card so we skip making it
            if index != 0:
                page = await make_card_page(pack, index, quiz_mode=True)
                await menu.output.edit(embed=page.as_safe_embed())

            # re-add the buttons
            await message.add_reaction(Emojis.check)
            await message.add_reaction(Emojis.cross)
            await message.add_reaction(Emojis.exit)

            # sleep for the set interval
            await asyncio.sleep(interval)

            # check to see answered correctly, 
            # since answering incorrectly doesn't change anything
            await self._quiz_update_scores(ctx, message)

        # make scoreboard embed
        embed = discord.Embed(
            title='SCOREBOARD',
            color=Colors.embed,
        )

        # create rank/name/score columns
        players = self.quiz_sessions_by_user_id[ctx.author.id]['players']
        scores = ''
        names = ''
        ranks = ''
        prev = -1
        rank = 0
        name_score = sorted(players.items(), key=lambda x: x[0].display_name)
        for player, score in sorted(name_score, key=lambda x: x[1], reverse=True):
            if score != prev:
                rank += 1
            scores += f'{Emojis.blank}{score}\n'
            names += f'{player.display_name}{Emojis.blank}\n'
            emoji_medal = Emojis.medals.get(rank, Emojis.blank)
            ranks += f'{emoji_medal} {rank}{Emojis.blank}\n'
            prev = score

        name = '__Rank__'
        embed.add_field(name=name, value=ranks, inline=True)

        name = '__Name__'
        embed.add_field(name=name, value=names, inline=True)

        name = '__Score__'
        embed.add_field(name=name, value=scores, inline=True)

        embed.set_author(name=pack.name)
        embed.set_footer(text=f'Pack by {ctx.author.display_name}')

        await message.clear_reactions()
        await message.edit(embed=embed)


    async def _quiz_update_scores(self, ctx: commands.Context, message: discord.Message):
        """
        updates the scores for a current quiz session
        """

        message = await ctx.channel.fetch_message(message.id)
        reaction: discord.Reaction = discord.utils.get(message.reactions, emoji=Emojis.check)
        reactors = await reaction.users().flatten()
        for reactor in reactors:

            # exclude the bot
            if reactor.id == self.bot.user.id:
                continue

            if reactor in self.quiz_sessions_by_user_id[ctx.author.id]['players']:
                self.quiz_sessions_by_user_id[ctx.author.id]['players'][reactor] += 1
            else:
                self.quiz_sessions_by_user_id[ctx.author.id]['players'][reactor] = 1


    @commands.Cog.listener(name='on_raw_reaction_add')
    async def _quiz_add_reaction_listener(
            self,
            payload: discord.RawReactionActionEvent
    ) -> None:
        """
        listener for reactions on messages that are in the multiplayer session dicts
        """

        # ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return

        # ignore reactions to messages that aren't in the session dicts
        if payload.message_id not in self.quiz_messages_by_id:
            return

        message: discord.Message = self.quiz_messages_by_id[payload.message_id]

        # remove user's x reaction if they just reacted with a check
        if str(payload.emoji) == Emojis.check:
            try:
                user = await self.bot.fetch_user(payload.user_id)
                await message.remove_reaction(Emojis.cross, user)
            except discord.NotFound:
                pass

        # remove user's check reaction if they just reacted with an x
        elif str(payload.emoji) == Emojis.cross:
            try:
                user = await self.bot.fetch_user(payload.user_id)
                await message.remove_reaction(Emojis.check, user)
            except discord.NotFound:
                pass

        # check for quiz cancellation
        elif str(payload.emoji) == Emojis.exit:
            if payload.user_id in self.quiz_sessions_by_user_id:
                if payload.message_id == self.quiz_sessions_by_user_id[payload.user_id]['message'].id:
                    self.quiz_sessions_by_user_id[payload.user_id]['exit'] = True


def setup(bot: Packle) -> None:
    """function the bot uses to load this cog"""

    bot.add_cog(Quiz(bot))
