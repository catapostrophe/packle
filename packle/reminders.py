# -*- coding: utf-8 -*-


# standard library modules
import asyncio
import itertools

# third-party packages - discord related
import discord
from discord.ext import tasks

# local modules
from cardpack import CardPack
from constants import Colors


async def create_reminder(
        pack: CardPack,
        seconds: float = 0.0,
        minutes: float = 0.0,
        hours: float = 24.0,
        count: int = None,  # infinite
        reconnect: bool = True,
        loop: asyncio.AbstractEventLoop = None,
):

    @tasks.loop(
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        count=count,
        reconnect=reconnect,
        loop=loop,
    )
    async def reminder() -> None:
        """
        sends spaced repetition reminder to practice specified CardPack
        """

        r: tasks.Loop = pack.reminder
        if r.current_loop == 0:
            return

        # if the last round wasn't completed
        if pack.round.active:

            # skips it and sets up the next one
            pack.next_round()

        # otherwise current round was setup when the previous one was completed
        else:

            # activates current round
            pack.round.active = True

        # format proficiency the levels of the round
        proficiency_levels = [str(x) for x in CardPack.Round.ROUNDS[pack.round_index]]
        if len(proficiency_levels) > 2:
            start = ', '.join(itertools.islice(proficiency_levels, len(proficiency_levels) - 1))
            proficiency_levels = f'{start}, and {proficiency_levels[-1]}'
        else:
            proficiency_levels = ' and '.join(proficiency_levels)

        # create the embed
        title = 'Flashcard Reminder'
        embed = discord.Embed(
            color=Colors.embed,
            title=title
        )

        name = pack.name
        value = f"It's time to practice your flashcard pack {repr(pack.name)}"
        embed.add_field(name=name, value=value, inline=False)

        name = 'Round'
        value = str(pack.round_index + 1)
        embed.add_field(name=name, value=value)

        name = 'Proficiency Level(s)'
        value = proficiency_levels
        embed.add_field(name=name, value=value)

        name = 'Cards'
        value = len(pack.round)
        embed.add_field(name=name, value=value)

        # add information field if the round has no cards
        if not pack.round:
            name = 'Notice'
            value = (
                'You have already mastered all proficiencies included in '
                f"this round, your may add more cards or use the `$next_round <pack_name>` "
                'command to manually advance the pack to the next non-empty round'
            )
            embed.add_field(name=name, value=value, inline=False)

        # send the reminder
        await pack.remind_channel.send(embed=embed)


    return reminder
