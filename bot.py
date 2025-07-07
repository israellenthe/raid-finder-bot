# Raid Finder Bot - Discord Bot
# Copyright (C) 2025
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License (AGPL) as
# published by the Free Software Foundation, either version 3 of the License,
# with the additional restriction:
#
# This software may NOT be used for commercial purposes.
#
# This means you cannot sell, license, or profit from this code or any
# modified versions of it, including hosting it behind a paywall or using
# it in a monetized environment.
#
# You should have received a copy of the GNU AGPL along with this program.
# If not, see <https://www.gnu.org/licenses/>.

import datetime
import os
import discord
from discord.ext import commands
import re
from collections import deque

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

# Create the bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Track raid searching state
searching_for_raids = False

# Server and channel names
TARGET_CHANNEL_RAID = "raid-codes"
TARGET_CHANNEL_COOP = "co-op-codes"
raid_channel = None
coop_channel = None

# Track recent codes
seen_codes = deque(maxlen=100)

@bot.event
async def on_ready():
    global raid_thread, coop_thread

    print(f"Bot is online! Logged in as {bot.user}")
    print("Commands:")
    print("!go     - Start raid scanning")
    print("!stop   - Stop raid scanning")
    print("!status - Show scan status")

    # Scan all servers the bot is in
    for guild in bot.guilds:
        for thread in guild.threads:
            name = thread.name.lower()
            if TARGET_THREAD_RAID in name:
                raid_thread = thread
                print("Found RAID thread in", guild.name + ": " + thread.name)
            elif TARGET_THREAD_COOP in name:
                coop_thread = thread
                print("Found CO-OP thread in", guild.name + ": " + thread.name)

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
    await ctx.send("Scanning for raid codes has stopped.")

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
                return  # Duplicate

            seen_codes.append(code)
            timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            output = f"Code found: `{code}` from **{message.guild.name}#{message.channel.name}** at {timestamp}"

            if "co-op" in message.channel.name.lower() and coop_channel:
                await coop_channel.send(output)
            elif raid_channel:
                await raid_channel.send(output)

    await bot.process_commands(message)

# Final run command with environment variable
bot.run(os.getenv("DISCORD_BOT_TOKEN"))

