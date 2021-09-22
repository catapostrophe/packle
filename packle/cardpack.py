# -*- coding: utf-8 -*-


# standard library modules - typing
from __future__ import annotations  # fixes some typehinting issues
from typing import TYPE_CHECKING  # fixes some typehinting issues
from typing import Union, List

# standard library modules
import enum
import random

# third-party packages - discord related
import discord


class FlashCard:
    """
    class for storing information for a specific flashcard
    """

    class Result(enum.Enum):
        UNANSWERED = enum.auto()
        CORRECT = enum.auto()
        INCORRECT = enum.auto()

    def __init__(
            self,
            question: str,
            answer: str,
            proficiency: int = 1
    ):
        """initializer"""

        self.question = str(question)
        self.answer = str(answer)
        self.proficiency = int(proficiency)
        self.result = FlashCard.Result.UNANSWERED


class CardPack:
    """
    class for holding and using flashcards
    """

    class Round:

        # spaced repetition proficiency levels by round
        ROUNDS = (
            (1,),
            (1,),
            (1, 2),
            (1,),
            (1,),
            (1,),
            (1, 2, 3),
        )

        def __init__(
                self,
                pack: CardPack,
        ):
            """initializer"""

            self.pack = pack
            self.active = True
            self._indexes = []
            self.setup_round()


        @property
        def unstudied(self) -> int:
            cnt = 0
            for card in self:
                if card.result == FlashCard.Result.UNANSWERED:
                    cnt += 1
            return cnt


        @property
        def completed(self) -> bool:
            """
            checks if all FlashCards in this round have been answered
            """

            for card in self:
                if card.result == FlashCard.Result.UNANSWERED:
                    return False
            return True


        def setup_round(self):
            """
            adds all FlashCards matching the current round's proficiency levels
            then randomizes their order
            """

            self._indexes.clear()
            cur_round = self.ROUNDS[self.pack.round_index]
            for index, card in enumerate(self.pack):
                if card.proficiency in cur_round:
                    self._indexes.append(index)
            self.shuffle()


        def __getitem__(self, i: int) -> FlashCard:
            """
            overloads the index operator for this class
            used for indexing and iteration
            """

            if not isinstance(i, int):
                raise TypeError('i must be of type int')

            return self.pack[self._indexes[i]]


        def __len__(self):
            """
            sets the length/size of this class,
            used for iteration, truthiness, len function, etc
            """

            return len(self._indexes)


        def shuffle(self):
            """
            in-place order randomization of the FlashCards in this round
            """

            random.shuffle(self._indexes)


    def __init__(
            self,
            cards,
            name: str,
            author: Union[discord.Member, discord.User],
            dm_channel: discord.DMChannel,
            category: str = 'No Category',
            difficulty: str = 'No Difficulty',
    ):
        """initializer"""

        self.__cards: List[FlashCard] = []

        # current round
        self.__round_index = 0
        self.round = CardPack.Round(self)

        # full pack
        self.index = 0
        self.extend(cards)
        self.name = name
        self.author = author
        self.category = category
        self.difficulty = difficulty

        # reminders
        self.reminder = None
        self.dm_channel = dm_channel
        self.remind_channel = self.dm_channel


    @property
    def round_index(self):
        """
        "immutable" round_index property
        """

        return self.__round_index


    @property
    def mastered(self):
        """
        returns whether or not all cards are at proficiency level 4 (mastered)
        """

        for card in self:
            if card.proficiency < 4:
                return False
        return True


    def next_round(self):
        """
        cleans up current round and then sets up a new one
        """

        # set new proficiencies for the current cards before advancing rounds
        for card in self.__cards:
            if card.result == FlashCard.Result.CORRECT:
                card.proficiency += 1
                card.result = FlashCard.Result.UNANSWERED
            elif card.result == FlashCard.Result.INCORRECT:
                card.proficiency -= 1
                if card.proficiency < 1:
                    card.proficiency = 1
                card.result = FlashCard.Result.UNANSWERED

        # increment the round index, wrapping around to 0 when required
        self.__round_index += 1
        if self.__round_index == len(CardPack.Round.ROUNDS):
            self.__round_index = 0
        self.round.setup_round()


    def reset(self):
        """
        resets the card proficiencies and round index
        """

        for card in self.__cards:
            card.proficiency = 1
        self.__round_index = 0
        self.round.setup_round()


    def __getitem__(self, s: Union[int, slice]):
        """
        overloads the index operator for this class
        used for indexing, slicing, and iteration
        """

        if isinstance(s, int):
            return self.__cards[s]

        elif isinstance(s, slice):
            return CardPack(
                self.__cards[s],
                name=self.name,
                category=self.category,
                author=self.author,
                difficulty=self.difficulty,
            )

        else:
            raise TypeError('s must be of type int or slice')


    def __len__(self):
        """
        sets the length/size of this class,
        used for iteration, truthiness, len function, etc
        """

        return len(self.__cards)


    def __iadd__(self, card: FlashCard):
        """
        overloads the addition operator for this class
        """

        if isinstance(card, FlashCard):
            self.__cards += card
            self.round.setup_round()
            return
        raise TypeError('card must be type FlashCard')


    def pop(self, i):
        """
        removes the FlashCard at index i and returns it
        """

        card = self.__cards.pop(i)
        self.round.setup_round()
        return card


    def append(self, card: FlashCard):
        """
        adds on FlashCard into this pack
        """

        return self.__iadd__(card)


    def extend(self, cards):
        """
        extends this pack with an iterable of FlashCards
        """

        for card in cards:
            if isinstance(card, FlashCard):
                self.__cards.append(card)
            else:
                self.__cards.append(FlashCard(*card))
        self.round.setup_round()
