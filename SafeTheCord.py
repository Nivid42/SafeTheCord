import discord
import configparser
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import re
import logging

logging.basicConfig(
    filename='example.log',
    filemode='a',
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("SafeTheCord")



class SafeTheCord(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger  # Nutze global definierten Logger
        self.config = configparser.ConfigParser()
        base_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_path, "config.ini")
        self.config.read(config_path) 
        self.moderation_channel_id = int(self.config['DEFAULT']['modchannel'])
        self.pending_messages = {}
        self.whitelisted_domains = {
                'vm.tiktok.com'
                                    }
        self.url_pattern = r'https?://[^\s]+'


    async def on_ready(self):

        print(f"✅ Eingeloggt als {self.user}")


    async def on_message(self, message):
        if message.author == self.user:
            return
        urls = re.findall(self.url_pattern, message.content, re.IGNORECASE)

        for url in urls:
            domain = url
            if not url.startswith(('http://', 'https://')):
                domain = 'http://' + url
            domain = urlparse(domain).netloc.lower()

            if any(domain == w or domain.endswith('.' + w) for w in self.whitelisted_domains):
                continue  # erlaubt

            await message.delete()
            mod_channel = await self.fetch_channel(self.moderation_channel_id)
            if not mod_channel:
                print(f"⚠️ Konnte Channel mit ID {self.moderation_channel_id} nicht finden!")
                return
            mod_message = await mod_channel.send(
                f"Neue verdächtige Nachricht von {message.author.mention} in {message.channel.mention}:\n"
                f"> {message.content}"
            )
            await mod_message.add_reaction("✅")
            self.pending_messages[mod_message.id] = {
                "original_channel": message.channel,
                "original_author": message.author,
                "content": message.content,
            }

    async def on_reaction_add(self, reaction, user):
        if user == self.user:
            return

        message = reaction.message
        if message.channel.id != self.moderation_channel_id:
            return

        if message.id not in self.pending_messages:
            return

        if str(reaction.emoji) == "✅":
            info = self.pending_messages.pop(message.id)
            try:
                await info["original_channel"].send(
                    f"Nachricht von {info['original_author'].mention} wurde freigegeben:\n{info['content']}"
                )
            except Exception as on_reaction_add_error:
                logging.error(f"Fehler beim wiederfreigeben von{info['original_author'].mention} wurde freigegeben:\n{info['content']}")



intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
client = SafeTheCord(intents=intents)

load_dotenv()  # lädt Variablen aus .env
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

client.run(DISCORD_TOKEN)