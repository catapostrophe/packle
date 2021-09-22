# -*- coding: utf-8 -*-


# third-party modules - discord related
import discord
from discord.ext import commands

# local modules
from constants import Colors


async def delete_context_message(ctx: commands.Context):

    # return if the message doesn't exist
    message: discord.Message = ctx.message
    if not message:
        return

    # delete the message if we sent it
    if ctx.author.id == ctx.me.id:
        return await ctx.message.delete()

    # return if the message is in a DM
    guild: discord.Guild = ctx.guild
    if not guild:
        return

    # return if we don't have permission to delete the message
    author: discord.Member = ctx.author
    permissions = author.permissions_in(ctx.channel)
    if not permissions.manage_messages:
        return

    # delete the message
    return await message.delete()


async def send_error_msg(ctx: commands.Context, msg: str) -> discord.Message:
    embed = discord.Embed(
        color=Colors.error,
    )
    embed.add_field(
        name='Error',
        value=msg,
    )
    embed.add_field(
        name='\u200b\nNeed Help?',
        value='Use the command `$help <command>` for more information',
        inline=False,
    )
    return await ctx.send(embed=embed)


async def send_success_msg(ctx: commands.Context, msg: str) -> discord.Message:
    embed = discord.Embed(
        color=Colors.success,
    )
    embed.add_field(
        name='Success',
        value=msg,
    )
    return await ctx.send(embed=embed)


async def send_info_msg(ctx: commands.Context, msg: str) -> discord.Message:
    embed = discord.Embed(
        color=Colors.info,
        description=msg,
    )
    return await ctx.send(embed=embed)
