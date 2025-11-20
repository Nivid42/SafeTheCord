import discord
from discord.ext import commands
from urllib.parse import urlparse
import re
import logging
import os

logger = logging.getLogger("Moderation")
logger.setLevel(logging.INFO)

class Moderation(commands.Cog):
    """
    Cog für Moderation von Nachrichten.

    Filtert Nachrichten mit URLs, die nicht auf der Whitelist stehen.
    Löscht diese Nachrichten, sendet sie an den Moderations-Channel
    und erlaubt die Freigabe per Reaktion.
    """

    def __init__(self, bot):
        self.bot = bot

        # Whitelist laden
        raw_whitelist = ""
        if hasattr(bot, "config") and "whitelist" in bot.config["DEFAULT"]:
            raw_whitelist = bot.config["DEFAULT"].get("whitelist", "")
        else:
            raw_whitelist = os.getenv("WHITELIST", "")

        self.allowed = {d.strip().lower() for d in raw_whitelist.split(",") if d.strip()}
        self.url_regex = r"https?://\S+"
        self.pending = {}

        # Moderations-Channel ID laden
        self.mod_channel_id = None
        if hasattr(bot, "config"):
            self.mod_channel_id = int(bot.config["DEFAULT"].get("modchannel", 0))
        if not self.mod_channel_id and os.getenv("MODCHANNEL"):
            self.mod_channel_id = int(os.getenv("MODCHANNEL"))

        logger.info(f"Using moderation channel ID: {self.mod_channel_id}")

    async def get_mod_channel(self):
        """
        Holt den Mod-Channel zuverlässig via Cache oder API.
        """
        if not self.mod_channel_id:
            logger.warning("Moderation channel ID not set!")
            return None
        mod_channel = self.bot.get_channel(self.mod_channel_id)
        if mod_channel is None:
            try:
                mod_channel = await self.bot.fetch_channel(self.mod_channel_id)
            except Exception as e:
                logger.error(f"Failed to fetch moderation channel: {e}")
                return None
        logger.info(f"Got channel: {mod_channel.name} (ID: {mod_channel.id})")
        return mod_channel

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        urls = re.findall(self.url_regex, message.content)
        if not urls:
            return

        for url in urls:
            domain = urlparse(url).netloc.lower()
            if domain in self.allowed or any(domain.endswith("." + w) for w in self.allowed):
                continue  # URL ist erlaubt

            try:
                await message.delete()
                logger.info(f"Deleted message from {message.author} containing {url}")
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")

            mod_channel = await self.get_mod_channel()
            if not mod_channel:
                return

            try:
                # Nachricht im Moderations-Channel posten
                m = await mod_channel.send(
                    f"🔍 Verdächtige Nachricht von {message.author.mention} "
                    f"in {message.channel.mention}:\n> {message.content}"
                )
                await m.add_reaction("✅")

                # Nachricht für Freigabe speichern
                self.pending[m.id] = {
                    "channel": message.channel,
                    "author": message.author,
                    "content": message.content
                }
                logger.info(f"Message posted to moderation channel: {m.id}")
            except Exception as e:
                logger.error(f"Failed to send message to moderation channel: {e}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user == self.bot.user:
            return

        msg = reaction.message
        if msg.id not in self.pending:
            return

        if str(reaction.emoji) != "✅":
            return

        data = self.pending.pop(msg.id)
        try:
            await data["channel"].send(f"✅ Freigegeben:\n{data['content']}")
            logger.info(f"Message released to {data['channel'].name}: {data['content']}")
        except Exception as e:
            logger.error(f"Failed to release message: {e}")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
