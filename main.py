from discord.abc import User
from discord.channel import TextChannel
from discord.ext.commands import Bot
from discord.flags import Intents
from datetime import datetime
import discord
from discord.member import Member
import requests
import json
intents = Intents.all()
color = 0x73ff00
log_id = 883367883210629200 #logging channel id here
bot_cmd = 883815284585164870 #bot command channel id here
bot = Bot(intents=intents,command_prefix="+")
@bot.command()
async def claim(ctx):
    if ctx.message.channel.id == bot_cmd:
        log =  await bot.fetch_channel(log_id)
        embed=discord.Embed(description="Sent, please check your DMs",color=color,timestamp=datetime.utcnow())
        embed.set_author(name="Sent!",icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        embed=discord.Embed(description=f"User {ctx.author} ran +check command!",color=color,timestamp=datetime.utcnow())
        embed.set_author(name=f"{ctx.author}",icon_url=ctx.author.avatar_url)
        await log.send(embed=embed)
        embed=discord.Embed(description=f"Thanks for running the command you ({ctx.author}) are in queue now!",color=color,timestamp=datetime.utcnow())
        embed.set_author(name=f"In queue",icon_url=ctx.author.avatar_url)
        await ctx.author.send(embed=embed)
    else:
        await ctx.message.delete()
@bot.command()
async def lookup(ctx,id):
    r = requests.get(f"https://api.blox.link/v1/user/{id}")
    try:
        user = await bot.fetch_user(id)
        uid = json.loads(r.text)["primaryAccount"]
    except KeyError:        
            embed=discord.Embed(description=f"The user you requested ({user}) did not link their roblox profile",color=0xFF0000,timestamp=datetime.utcnow())
            embed.set_author(name=f"Not found!",icon_url=user.avatar_url)
            await ctx.channel.send(embed=embed)
    else:
        user = await bot.fetch_user(id)
        embed=discord.Embed(description=f"The user you requested ({user}) is found!",color=color,timestamp=datetime.utcnow())
        embed.set_author(name=f"Found!",icon_url=user.avatar_url)
        await ctx.channel.send(embed=embed)
        uid = json.loads(r.text)["primaryAccount"]
        await ctx.channel.send(f"https://roblox.com/users/{uid}")
@bot.event
async def on_message(message):
    if str(message.content) == "+claim" or str(message.content).startswith("+lookup"):
        await bot.process_commands(message)
    else:
        if message.author.id != bot.user.id and message.channel.id == bot_cmd:
            await message.delete()
bot.run("ODgzMzM4ODM4MTU4NzQ5NzE2.YTIfZg.DRUineO9rHFx5O3bnlApCRbLx3g")
