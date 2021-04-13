import os
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands

from Modules import printer

bot = discord.Client()

Channels = {}

@bot.event
async def on_ready():
    print('Bot Ready')

@bot.event
async def on_message(Msg):
    if Msg.author.bot:
        return

    if Msg.channel.id not in Channels:
        Channels[Msg.channel.id] = printer.Queue(Msg.channel.name,Testing=True)

    Channels[Msg.channel.id].Add(Msg.content,Msg.created_at,Msg.author.name)

bot.run(os.getenv('TOKEN'))