# -*- coding: utf-8 -*-


# third-party packages - discord related
from dpymenus import Page

# local modules
from cardpack import CardPack, FlashCard
from constants import Colors, Emojis


U200B = '\u200b'


async def make_card_page(
        pack: CardPack,
        index: int,
        quiz_mode: bool = False,
) -> Page:
    """
    create a dpymenus.Page for a FlashCard
    """

    # get card
    if quiz_mode:
        card: FlashCard = pack[index]
    else:
        card: FlashCard = pack.round[index]

    # initialize page
    page = Page(
        title=f'{pack.name} ({pack.category})',
        description='Click the answer to reveal it and choose the tick or cross based on your self assessment',
        colour=Colors.embed,
    )

    # add question
    page.add_field(name='Question', value=card.question, inline=True)

    # add answer, spoilering if in multiplayer mode, or no results in single player mode
    if quiz_mode or card.result == FlashCard.Result.UNANSWERED:
        answer = f'||{card.answer}||'
    else:
        answer = card.answer
    page.add_field(name='Answer', value=answer, inline=True)

    # add result field if requested, for single player only
    if not quiz_mode:

        # add whitespace
        page.add_field(name=U200B, value=U200B, inline=False)

        # add proficiency level
        page.add_field(name='Proficiency', value=f'{card.proficiency}', inline=False)

        # add whitespace
        page.add_field(name=U200B, value=U200B, inline=False)

        # add result field and minor whitespace beneath it
        if card.result == FlashCard.Result.CORRECT:
            result_text = f'{Emojis.check} Correct\n{U200B}'
        elif card.result == FlashCard.Result.INCORRECT:
            result_text = f'{Emojis.cross} Incorrect\n{U200B}'
        else:
            result_text = f'{Emojis.box} Unanswered\n{U200B}'
        page.add_field(name='Result', value=result_text, inline=False)

    # add current card position in deck for current round
    if quiz_mode:

        # amount of cards in the whole CardPack
        size = len(pack)
    else:

        # amount of cards just for this Round
        size = len(pack.round)
    page.set_author(name=f'card {index + 1} of {size}')

    # add pack author
    page.set_footer(text=f'pack creator: {pack.author}')

    return page
