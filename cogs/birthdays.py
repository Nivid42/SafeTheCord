import discord
from discord.ext import commands, tasks
from discord import app_commands
import csv
import os
from datetime import datetime
import logging

logger = logging.getLogger("Birthdays")
logger.setLevel(logging.INFO)

class Birthdays(commands.Cog):
    """
    Cog für Geburtstagsmanagement.

    Ermöglicht es Nutzern, ihre Geburtstage zu speichern und 
    sendet automatisch Geburtstagsgrüße im festgelegten Channel.
    """

    def __init__(self, bot):
        """
        Initialisiert die Birthdays-Cog.

        Args:
            bot (commands.Bot): Der Hauptbot.
        """
        self.bot = bot
        self.file = "data/birthdays.csv"  # Pfad zur CSV-Datei
        self.check_birthdays.start()  # Startet den wiederkehrenden Task

    def save_birthday(self, user_id: int, name: str, birthday: str):
        """
        Speichert oder aktualisiert einen Geburtstag in der CSV-Datei.

        Args:
            user_id (int): Discord-ID des Nutzers.
            name (str): Name des Nutzers.
            birthday (str): Geburtstag im Format TT.MM.JJJJ.
        """
        file_exists = os.path.isfile(self.file)

        # Lese existierende Einträge
        entries = {}
        if file_exists:
            with open(self.file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    entries[row["user_id"]] = row

        # Update oder füge neuen Eintrag hinzu
        entries[str(user_id)] = {
            "user_id": str(user_id),
            "name": name,
            "birthday": birthday
        }

        # Schreibe alle Einträge zurück
        os.makedirs(os.path.dirname(self.file), exist_ok=True)
        with open(self.file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "name", "birthday"])
            writer.writeheader()
            for e in entries.values():
                writer.writerow(e)

        logger.info(f"Birthday saved: {name} ({birthday}) for user {user_id}")

    @tasks.loop(minutes=1)
    async def check_birthdays(self):
        """
        Task, der regelmäßig Geburtstage überprüft und Nachrichten sendet.

        Prüft jeden Tag um 09:00 Uhr, ob Nutzer Geburtstag haben, 
        und sendet einen Geburtstagsgruß in den angegebenen Channel.
        """
        now = datetime.now()
        if now.hour != 9 or now.minute != 0:
            return

        if not os.path.isfile(self.file):
            return

        today = now.strftime("%d.%m")

        with open(self.file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["birthday"].startswith(today):
                    channel_id = int(self.bot.config["DEFAULT"]["birthdaychannel"])
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        try:
                            user = await self.bot.fetch_user(int(row["user_id"]))
                            await channel.send(
                                f"🎉🎂 Alles Gute zum Geburtstag, {user.mention} ({row['name']})! 🎂🎉"
                            )
                            logger.info(f"Birthday sent for {row['name']} ({row['user_id']})")
                        except Exception as e:
                            logger.error(f"Failed to send birthday message: {e}")

    @app_commands.command(
        name="addbirthday",
        description="Speichere deinen Geburtstag im Format TT.MM.JJJJ."
    )
    async def add_birthday(self, interaction: discord.Interaction, name: str, date: str):
        """
        Slash-Command, um den Geburtstag eines Nutzers zu speichern.

        Args:
            interaction (discord.Interaction): Interaktion des Nutzers.
            Name (str): Name des Nutzers.
            Datum (str): Geburtstag im Format TT.MM.JJJJ.
        """
        try:
            datetime.strptime(date, "%d.%m.%Y")
        except ValueError:
            await interaction.response.send_message(
                "❌ Bitte verwende das Format TT.MM.JJJJ", ephemeral=True
            )
            return

        self.save_birthday(interaction.user.id, name, date)

        await interaction.response.send_message(
            f"✅ Geburtstag gespeichert: **{name}**, {date}",
            ephemeral=True
        )

async def setup(bot):
    """
    Lädt die Birthdays-Cog in den Bot.

    Args:
        bot (commands.Bot): Der Hauptbot.
    """
    await bot.add_cog(Birthdays(bot))

