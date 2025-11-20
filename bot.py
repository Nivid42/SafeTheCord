import discord
from discord.ext import commands
from discord import app_commands
import configparser
import os
from dotenv import load_dotenv
import logging

# --- Logging Setup ---
os.makedirs("data", exist_ok=True)  # sicherstellen, dass der Ordner existiert
logging.basicConfig(
    filename='data/bot.log',
    filemode='a',
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("SafeTheCord")

# --- Load env variables ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Load config.ini ---
config = configparser.ConfigParser()
config.read("config.ini")

# Optional: Channels auch aus env laden, fallback auf config.ini
MOD_CHANNEL = int(os.getenv("MODCHANNEL", config["DEFAULT"]["modchannel"]))
BIRTHDAY_CHANNEL = int(os.getenv("BIRTHDAY_CHANNEL", config["DEFAULT"]["birthdaychannel"]))

class SafeTheCord(commands.Bot):
    """
    Haupt-Botklasse für SafeTheCord.
    Lädt automatisch alle Cogs und synchronisiert Slash Commands.
    """

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        intents.messages = True

        super().__init__(command_prefix="!", intents=intents)

        # Config allen Cogs zur Verfügung stellen
        self.config = config

    async def setup_hook(self):
        """
        Lädt alle Cogs und synchronisiert die Slash-Commands.
        """
        await self.load_extension("cogs.birthdays")
        await self.load_extension("cogs.moderation")

        await self.tree.sync()
        logger.info("Slash Commands synchronisiert")

    async def on_ready(self):
        """
        Event: Bot ist bereit und eingeloggt.
        """
        logger.info(f"Eingeloggt als {self.user}")
        print(f"✅ Eingeloggt als {self.user}")

# --- Bot starten ---
bot = SafeTheCord()
bot.run(TOKEN)

