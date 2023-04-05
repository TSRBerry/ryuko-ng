import json
import os

import discord
from discord.ext import commands
from discord.ext.commands import Cog

from robocop_ng.helpers.checks import check_if_collaborator


class Invites(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invites_json_path = os.path.join(self.bot.state_dir, "data/invites.json")

    @commands.command()
    @commands.guild_only()
    @commands.check(check_if_collaborator)
    async def invite(self, ctx):
        welcome_channel = self.bot.get_channel(self.bot.config.welcome_channel)
        author = ctx.message.author
        reason = f"Created by {str(author)} ({author.id})"
        invite = await welcome_channel.create_invite(
            max_age=0, max_uses=1, temporary=True, unique=True, reason=reason
        )

        with open(self.invites_json_path, "r") as f:
            invites = json.load(f)

        invites[invite.id] = {
            "uses": 0,
            "url": invite.url,
            "max_uses": 1,
            "code": invite.code,
        }

        with open(self.invites_json_path, "w") as f:
            f.write(json.dumps(invites))

        await ctx.message.add_reaction("🆗")
        try:
            await ctx.author.send(f"Created single-use invite {invite.url}")
        except discord.errors.Forbidden:
            await ctx.send(
                f"{ctx.author.mention} I could not send you the \
                             invite. Send me a DM so I can reply to you."
            )


async def setup(bot):
    await bot.add_cog(Invites(bot))
