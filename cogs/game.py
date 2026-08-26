"""
Game cog containing the unified master command for Charon Simulator.
Theme: Bleak, solemn, poetic Underworld.
"""

import discord
from discord.ext import commands
from discord import app_commands
import database
import config
from config import TOTAL_HUMAN_SOULS, format_number
from cogs.ui import CharonDashboardView, ResetConfirmationView


class GameCog(commands.Cog, name="Game"):
    """Master game cog running the unified Charon Simulator interface."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_clean(self, ctx: commands.Context, *args, **kwargs) -> discord.Message:
        """Deletes user's prefix command and previous bot response to keep the channel clean."""
        # 1. Delete previous bot response for this user in this channel
        key = (ctx.channel.id, ctx.author.id)
        if not hasattr(self.bot, "last_user_responses"):
            self.bot.last_user_responses = {}

        prev_msg = self.bot.last_user_responses.get(key)
        if prev_msg:
            try:
                await prev_msg.delete()
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                pass

        # 2. Delete user's prefix command message (e.g. !charon, !ferry)
        if ctx.interaction is None and ctx.message:
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                pass

        # 3. Send new response and store it
        msg = await ctx.send(*args, **kwargs)
        self.bot.last_user_responses[key] = msg
        return msg

    @commands.hybrid_command(
        name="charon",
        description="Take the helm of Charon's skiff and navigate all Underworld realms."
    )
    @app_commands.describe(realm="Initial Underworld realm to open (optional)")
    @app_commands.choices(realm=[
        app_commands.Choice(name="🌊 Shore of Acheron (Ferry & Perils)", value="river"),
        app_commands.Choice(name="🛒 Market of the Dead (Vessels & Upgrades)", value="shop"),
        app_commands.Choice(name="🗺️ River Expeditions (Voyages)", value="voyages"),
        app_commands.Choice(name="🎲 Thanatos' Loom & Bones (Dice & Fate)", value="gamble"),
        app_commands.Choice(name="📜 Decrees of Hades (Bounties)", value="bounties"),
        app_commands.Choice(name="🏛️ Sanctuary of Mythic Relics", value="artifacts"),
        app_commands.Choice(name="📊 Ferryman Record & Rankings", value="profile")
    ])
    async def charon_cmd(self, ctx: commands.Context, realm: str = "river"):
        """Master command opening the unified interactive dashboard."""
        initial_realm = realm.lower().strip() if realm else "river"
        if initial_realm not in ["river", "shop", "voyages", "gamble", "bounties", "artifacts", "profile"]:
            initial_realm = "river"

        view = CharonDashboardView(ctx.author.id, initial_realm=initial_realm)
        embed = view.get_embed()
        await self.send_clean(ctx, embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(GameCog(bot))
