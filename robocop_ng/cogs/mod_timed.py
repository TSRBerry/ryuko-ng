from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from discord.ext.commands import Cog

from robocop_ng.helpers.checks import check_if_staff
from robocop_ng.helpers.restrictions import add_restriction
from robocop_ng.helpers.robocronp import add_job
from robocop_ng.helpers.userlogs import userlog


class ModTimed(Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_if_target_is_staff(self, target):
        return any(r.id in self.bot.config.staff_role_ids for r in target.roles)

    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check(check_if_staff)
    @commands.command()
    async def timeban(
        self, ctx, target: Optional[discord.Member], duration: str, *, reason: str = ""
    ):
        """Bans a user for a specified amount of time, staff only."""
        if target is None and ctx.message.reference is None:
            return await ctx.send(
                f"I'm sorry {ctx.author.mention}, I'm afraid I can't do that."
            )
        else:
            if ctx.message.reference is not None:
                if target is not None:
                    duration = str(target) + duration
                target = (
                    await ctx.channel.fetch_message(ctx.message.reference.message_id)
                ).author
        # Hedge-proofing the code
        if target == ctx.author:
            return await ctx.send("You can't do mod actions on yourself.")
        elif self.check_if_target_is_staff(target):
            return await ctx.send("I can't ban this user as they're a member of staff.")

        expiry_timestamp = self.bot.parse_time(duration)
        expiry_datetime = datetime.utcfromtimestamp(expiry_timestamp)
        duration_text = self.bot.get_relative_timestamp(
            time_to=expiry_datetime, include_to=True, humanized=True
        )

        userlog(
            self.bot,
            target.id,
            ctx.author,
            f"{reason} (Timed, until " f"{duration_text})",
            "bans",
            target.name,
        )

        safe_name = await commands.clean_content(escape_markdown=True).convert(
            ctx, str(target)
        )

        dm_message = f"You were banned from {ctx.guild.name}."
        if reason:
            dm_message += f' The given reason is: "{reason}".'
        dm_message += f"\n\nThis ban will expire {duration_text}."

        try:
            await target.send(dm_message)
        except discord.errors.Forbidden:
            # Prevents ban issues in cases where user blocked bot
            # or has DMs disabled
            pass

        await target.ban(
            reason=f"{ctx.author}, reason: {reason}", delete_message_days=0
        )
        chan_message = (
            f"⛔ **Timed Ban**: {ctx.author.mention} banned "
            f"{target.mention} for {duration_text} | {safe_name}\n"
            f"🏷 __User ID__: {target.id}\n"
        )
        if reason:
            chan_message += f'✏️ __Reason__: "{reason}"'
        else:
            chan_message += (
                "Please add an explanation below. In the future"
                ", it is recommended to use `.ban <user> [reason]`"
                " as the reason is automatically sent to the user."
            )

        add_job(self.bot, "unban", target.id, {"guild": ctx.guild.id}, expiry_timestamp)

        log_channel = self.bot.get_channel(self.bot.config.log_channel)
        await log_channel.send(chan_message)
        await ctx.send(f"{safe_name} is now b&. " f"It will expire {duration_text}. 👍")

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command()
    async def timemute(
        self, ctx, target: Optional[discord.Member], duration: str, *, reason: str = ""
    ):
        """Mutes a user for a specified amount of time, staff only."""
        if target is None and ctx.message.reference is None:
            return await ctx.send(
                f"I'm sorry {ctx.author.mention}, I'm afraid I can't do that."
            )
        else:
            if ctx.message.reference is not None:
                if target is not None:
                    duration = str(target) + duration
                target = (
                    await ctx.channel.fetch_message(ctx.message.reference.message_id)
                ).author
        # Hedge-proofing the code
        if target == ctx.author:
            return await ctx.send("You can't do mod actions on yourself.")
        elif self.check_if_target_is_staff(target):
            return await ctx.send(
                "I can't mute this user as they're a member of staff."
            )

        expiry_timestamp = self.bot.parse_time(duration)
        expiry_datetime = datetime.utcfromtimestamp(expiry_timestamp)
        duration_text = self.bot.get_relative_timestamp(
            time_to=expiry_datetime, include_to=True, humanized=True
        )

        userlog(
            self.bot,
            target.id,
            ctx.author,
            f"{reason} (Timed, until " f"{duration_text})",
            "mutes",
            target.name,
        )

        safe_name = await commands.clean_content(escape_markdown=True).convert(
            ctx, str(target)
        )

        dm_message = f"You were muted!"
        if reason:
            dm_message += f' The given reason is: "{reason}".'
        dm_message += f"\n\nThis mute will expire {duration_text}."

        try:
            await target.send(dm_message)
        except discord.errors.Forbidden:
            # Prevents kick issues in cases where user blocked bot
            # or has DMs disabled
            pass

        mute_role = ctx.guild.get_role(self.bot.config.mute_role)

        await target.add_roles(mute_role, reason=str(ctx.author))

        chan_message = (
            f"🔇 **Timed Mute**: {ctx.author.mention} muted "
            f"{target.mention} for {duration_text} | {safe_name}\n"
            f"🏷 __User ID__: {target.id}\n"
        )
        if reason:
            chan_message += f'✏️ __Reason__: "{reason}"'
        else:
            chan_message += (
                "Please add an explanation below. In the future, "
                "it is recommended to use `.mute <user> [reason]`"
                " as the reason is automatically sent to the user."
            )

        add_job(
            self.bot, "unmute", target.id, {"guild": ctx.guild.id}, expiry_timestamp
        )

        log_channel = self.bot.get_channel(self.bot.config.log_channel)
        await log_channel.send(chan_message)
        await ctx.send(
            f"{target.mention} can no longer speak. " f"It will expire {duration_text}."
        )
        add_restriction(self.bot, target.id, self.bot.config.mute_role)


async def setup(bot):
    await bot.add_cog(ModTimed(bot))
