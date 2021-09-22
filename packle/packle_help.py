# -*- coding: utf-8 -*-


# standard library modules - typing
from typing import Mapping, Optional, List

# third-party packages - discord related
import discord
from discord.ext import commands

# local modules
from constants import Colors


class PackleHelp(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping: Mapping[Optional[commands.Cog], List[commands.Command]]) -> None:
        pack_cmds = ('__Packs__', [])
        practice_cmds = ('__Practice__', [])
        help_command = None
        for cog, cmds in mapping.items():
            if cog is None:
                for cmd in cmds:
                    if cmd.name == 'help':
                        help_command = cmd
            elif cog.qualified_name == 'packs':
                pack_cmds[1].extend(cmds)
            else:
                practice_cmds[1].extend(cmds)

        description = (
            f'Use `{self.get_command_signature(help_command)}` for more '
            'detailed help about a specific command. Any text such as pack names with spaces should be wrapped with quotes\"like so\"\n\u200b'
        )

        embed = discord.Embed(
            color=Colors.embed,
            title='Packle Help',
            description=description,
        )
        for i, (group_name, cmds) in enumerate([practice_cmds, pack_cmds]):
            names = ''
            descriptions = ''
            cmd: commands.Command
            for cmd in cmds:
                if cmd.hidden:
                    continue
                names += f'{cmd.name}\n'
                descriptions += f'{cmd.description}\n'
            names = '```\n' + names + '```'
            descriptions = '```\n' + descriptions + '```'
            if i == 0:
                name = '__Details__'
            else:
                name = '\u200b'
            embed.add_field(name=group_name, value=names, inline=True)
            embed.add_field(name=name, value=descriptions, inline=True)
            if i == 0:
                embed.add_field(name='\u200b', value='\u200b', inline=False)

        name = '\u200b\nSupport Server'
        value = ':link: https://discord.gg/V2TXDrAfZs'
        embed.add_field(name=name, value=value, inline=False)

        dest = self.get_destination()
        await dest.send(embed=embed)


    async def send_command_help(self, command: commands.Command) -> None:
        if command.hidden:
            return

        embed = discord.Embed(
            color=Colors.embed,
        )
        embed.title = f'Packle Help - {command.name} command'
        name = '\u200b\nDescription'
        value = f'{command.help}'
        embed.add_field(name=name, value=value, inline=False)

        name = '\u200b\nUsage'
        value = f'`{self.get_command_signature(command)}`'
        embed.add_field(name=name, value=value, inline=False)

        name = '\u200b\nSupport Server'
        value = ':link: https://discord.gg/V2TXDrAfZs'
        embed.add_field(name=name, value=value, inline=False)

        dest = self.get_destination()
        await dest.send(embed=embed)


    async def send_cog_help(self, cog):
        pass


    async def send_group_help(self, group):
        pass
