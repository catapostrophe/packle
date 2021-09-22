# -*- coding: utf-8 -*-


# third-party packages - discord related
from discord.ext import commands


class Packle(commands.Bot):
    def __init__(self, *args, **kwargs) -> None:
        """initializer"""

        super().__init__(*args, **kwargs)

        # storage for each user's FlashCard CardPacks
        self.packs = {}
