# Raid Finder Bot - Discord Bot
# Copyright (C) 2025 Jake Anderson
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

# Per-server state
searching_servers = {}

# Channel name identifiers
TARGET_CHANNEL_RAID = "raid-codes"
TARGET_CHANNEL_COOP = "co-op-codes"

# Multilingual detection keywords
RAID_KEYWORDS = ["raid", "レイド", "레이드", "incursion"]
COOP_KEYWORDS = ["co-op", "協力", "협동", "cooperativo"]

# Store channels per guild
raid_channels = {}
coop_channels = {}

# Recent code memory
seen_codes = deque(maxlen=100)

@bot.event
async def on_ready():
    print(f"Bot is online! Logged in as {bot.user}")
    print("Commands:")
    print("!go     - Start raid scanning")
    print("!stop   - Stop raid scanning")
    print("!status - Show scan status")

    for guild in bot.guilds:
        for channel in guild.text_channels:
            name = channel.name.lower()
            if TARGET_CHANNEL_RAID in name:
                raid_channels[guild.id] = channel
                print("Found RAID channel in", guild.name)
            elif TARGET_CHANNEL_COOP in name:
                coop_channels[guild.id] = channel
                print("Found CO-OP channel in", guild.name)

        if guild.id not in raid_channels:
            print(f"Warning: Could not find 'raid-codes' channel in {guild.name}")
        if guild.id not in coop_channels:
            print(f"Warning: Could not find 'co-op-codes' channel in {guild.name}")

@bot.command()
async def go(ctx):
    searching_servers[ctx.guild.id] = True
    await ctx.send("Scanning for raid codes has started.")

@bot.command()
async def stop(ctx):
    searching_servers[ctx.guild.id] = False
    await ctx.send("Raid scanning has been stopped.")

@bot.command()
async def status(ctx):
    state = "ON" if searching_servers.get(ctx.guild.id, False) else "OFF"
    await ctx.send(f"Raid scanning is currently: {state}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.guild and searching_servers.get(message.guild.id, False):
        match = re.search(r"\b[A-Z0-9]{8}\b", message.content)
        if match:
            code = match.group(0)

            if code in seen_codes:
                return  # already handled

            seen_codes.append(code)
            timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
            output = f"Code found: {code} from {message.guild.name}#{message.channel.name} at {timestamp}"

            lower_channel = message.channel.name.lower()
            lower_msg = message.content.lower()

            if any(keyword in lower_channel for keyword in COOP_KEYWORDS) or any(keyword in lower_msg for keyword in COOP_KEYWORDS):
                coop_channel = coop_channels.get(message.guild.id)
                if coop_channel:
                    await coop_channel.send(output)

            elif any(keyword in lower_channel for keyword in RAID_KEYWORDS) or any(keyword in lower_msg for keyword in RAID_KEYWORDS):
                raid_channel = raid_channels.get(message.guild.id)
                if raid_channel:
                    await raid_channel.send(output)

    await bot.process_commands(message)

# Run the bot
bot.run(os.getenv("DISCORD_BOT_TOKEN"))

