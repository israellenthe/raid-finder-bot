
# Raid Finder Bot - Discord Bot
# Copyright (C) 2025 [Your Name or Server Name]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, with the following additional restriction:
#
#     → This software may NOT be used for commercial purposes.
#
# This means you cannot sell, license, or profit from this code or any
# modified versions of it, including hosting it behind a paywall or using it
# in a monetized environment. It is intended for public, non-commercial community use only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU AGPL along with this program.
# If not, see <https://www.gnu.org/licenses/>.
#
# A copy of the full AGPL v3 license is available here:
# https://www.gnu.org/licenses/agpl-3.0.txt

import os
import datetime
import discord
from discord.ext import commands
import re
from collections import deque

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# Create bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Global state
searching_for_raids = False
TARGET_THREAD_RAID = "raid-codes"
TARGET_THREAD_COOP = "co-op-codes"
raid_thread = None
coop_thread = None
seen_codes = deque(maxlen=100)

# Multilingual detection keywords
RAID_KEYWORDS = ["raid", "レイド", "레이드", "incursion"]
COOP_KEYWORDS = ["co-op", "協力", "협동", "cooperativo"]

@bot.event
async def on_ready():
    global raid_thread, coop_thread

    print(f"Bot is online! Logged in as {bot.user}")
    print("Commands:")
    print("!go     - Start raid scanning")
    print("!stop   - Stop raid scanning")
    print("!status - Show scan status")

    for guild in bot.guilds:
        for thread in guild.threads:
            name = thread.name.lower()
            if TARGET_THREAD_RAID in name:
                raid_thread = thread
                print("Found RAID thread in", guild.name)
            elif TARGET_THREAD_COOP in name:
                coop_thread = thread
                print("Found CO-OP thread in", guild.name)

    if not raid_thread:
        print("Warning: Could not find 'raid-codes' thread.")
    if not coop_thread:
        print("Warning: Could not find 'co-op-codes' thread.")

@bot.command()
async def go(ctx):
    global searching_for_raids
    searching_for_raids = True
    await ctx.send("Scanning for raid codes has started.")

@bot.command()
async def stop(ctx):
    global searching_for_raids
    searching_for_raids = False
    await ctx.send("Raid scanning has been stopped.")

@bot.command()
async def status(ctx):
    state = "ON" if searching_for_raids else "OFF"
    await ctx.send(f"Raid scanning is currently: {state}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if searching_for_raids and message.guild:
        match = re.search(r"\b[A-Z0-9]{8}\b", message.content)
        if match:
            code = match.group(0)

            if code in seen_codes:
                return

            seen_codes.append(code)
            timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
            output = f"Code found: {code} from {message.guild.name}#{message.channel.name} at {timestamp}"

            channel_name = message.channel.name.lower()
            message_lower = message.content.lower()

            if any(keyword in channel_name for keyword in COOP_KEYWORDS) or any(keyword in message_lower for keyword in COOP_KEYWORDS):
                if coop_thread:
                    await coop_thread.send(output)
            elif any(keyword in channel_name for keyword in RAID_KEYWORDS) or any(keyword in message_lower for keyword in RAID_KEYWORDS):
                if raid_thread:
                    await raid_thread.send(output)

    await bot.process_commands(message)

# Run the bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))

