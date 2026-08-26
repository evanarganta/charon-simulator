"""
Main bot entry point for Charon Simulator.
"""

import os
import sys
import asyncio
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

import database

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("CharonBot")

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN", "MY_BOT_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")

# Set intents
intents = discord.Intents.default()
intents.message_content = True


class CharonBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(PREFIX),
            intents=intents,
            help_command=None
        )
        self.last_user_responses = {}

    async def setup_hook(self):
        # Initialize SQLite database
        database.init_db()
        logger.info("Database initialized.")

        # Load Game cog
        await self.load_extension("cogs.game")
        logger.info("Loaded extension: cogs.game")

    async def on_ready(self):
        logger.info("==========================================")
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        logger.info(f"Prefix: {PREFIX} | Slash Commands Active")
        logger.info("==========================================")

        # Sync Slash commands with Discord (clear guild-specific duplicates and sync globally)
        try:
            for guild in self.guilds:
                self.tree.clear_commands(guild=guild)
                await self.tree.sync(guild=guild)
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s) globally without duplicates!")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")

        # Set playing status
        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name="https://github.com/evanarganta/acheron-simulator"
        )
        await self.change_presence(activity=activity)


    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            return

        # Delete user's prefix command if prefix was used
        if ctx.interaction is None and ctx.message:
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound, discord.HTTPException):
                pass

        async def report(message: str):
            """Report safely whether a slash interaction was acknowledged or not."""
            try:
                if ctx.interaction is not None and ctx.interaction.response.is_done():
                    await ctx.interaction.followup.send(message, ephemeral=True)
                else:
                    await ctx.send(message, delete_after=10)
            except (discord.NotFound, discord.HTTPException):
                # The original failure may already be an expired interaction.
                logger.warning("Could not report command error: interaction expired or was already handled.")

        if isinstance(error, commands.MissingRequiredArgument):
            await report(f"Missing argument: `{error.param.name}`. Consult `/help` for guidance.")
            return
        
        logger.error(f"Command error in {ctx.command}: {error}", exc_info=error)
        await report(f"An error occurred: `{str(error)}`")



def main():
    if not TOKEN or TOKEN == "MY_BOT_TOKEN" or TOKEN == "your_bot_token_here":
        print("\n" + "="*60)
        print(" ⚠️  DISCORD TOKEN NOT SET!")
        print(" Please create a file named '.env' in this directory with:")
        print(" DISCORD_TOKEN=your_actual_discord_bot_token")
        print(" See README.md for instructions on how to get a token.")
        print("="*60 + "\n")
        sys.exit(1)

    bot = CharonBot()
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
