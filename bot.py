# Raid Finder Bot - Discord Bot
# Copyright (C) 2025 [Your Name or Server Name]
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
# If not, see https://www.gnu.org/licenses/

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
TARGET_SERVER_NAME = "Gran Blu Raid Scanner"
TARGET_THREAD_RAID = "raid-codes"
TARGET_THREAD_COOP = "co-op-codes"
raid_thread = None
coop_thread = None

# Keep track of recently posted codes (to avoid duplicates)
seen_codes = deque(maxlen=100)  # Stores the last 100 codes

@bot.event
async def on_ready():
    global raid_thread, coop_thread

    print(f"Bot is online! Logged in as {bot.user}")
    print("Hello! I'm your Raid Finder Bot.")
    print("Use these commands to control me:")
    print("- !go     Start raid notifications")
    print("- !stop   Stop raid notifications")
    print("- !status Check if I'm searching or not")

    # Search for threads in your server
    for guild in bot.guilds:
        if guild.name == TARGET_SERVER_NAME:
            for thread in guild.threads:
                name = thread.name.lower()
                if TARGET_THREAD_RAID in name:
                    raid_thread = thread
                    print(f"Found RAID thread: {thread.name}")
                elif TARGET_THREAD_COOP in name:
                    coop_thread = thread
                    print(f"Found CO-OP thread: {thread.name}")

    if not raid_thread:
        print("Could not find 'raid-codes' thread.")
    if not coop_thread:
        print("Could not find 'co-op-codes' thread.")

@bot.command()
async def go(ctx):
    global searching_for_raids
    searching_for_raids = True
    await ctx.send('Got it! I will start searching for raids now.\nIf you want me to stop, just say so.')

@bot.command()
async def stop(ctx):
    global searching_for_raids
    searching_for_raids = False
    await ctx.send('Alright, I have stopped looking for raids.\nIf you want me to go again, just say so.')

@bot.command()
async def status(ctx):
    state = "ON" if searching_for_raids else "OFF"
    await ctx.send(f'Raid searching is currently: {state}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if searching_for_raids and message.guild:
        match = re.search(r"\b[A-Z0-9]{8}\b", message.content)
        if match:
            code = match.group(0)

            if code in seen_codes:
                return  # Skip if this code was already posted

            seen_codes.append(code)  # Track it as seen
            formatted = f"Code found: `{code}` from {message.guild.name}#{message.channel.name}"

            if "co-op" in message.channel.name.lower() and coop_thread:
                await coop_thread.send(formatted)
            elif raid_thread:
                await raid_thread.send(formatted)

    await bot.process_commands(message)

# Final line — run with your bot token
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
x
