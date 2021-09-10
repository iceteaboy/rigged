import discord
from discord.ext import commands
from discord.ext import tasks
import sqlite3
import random
import traceback
from datetime import datetime


prefix = "."
bot = commands.Bot(command_prefix=prefix,intents=discord.Intents.all())
color = 0x80ffff
TOKEN = "ODg1OTk2NTM3Njg2MTQyOTg2.YTvKkw.EHMNPzyM3L9Qs-mOXIfHvJrPpaI"
bot.guild = 885996344802705449  #replace with your guild id


conn = sqlite3.connect('giveaways.db')
c = conn.cursor()


def total_giveaways():
    c.execute('CREATE TABLE IF NOT EXISTS total_giveaways(giveaway_id VALUE,giveaway_number VALUE)')

def giveaways():
    c.execute('CREATE TABLE IF NOT EXISTS giveaways(giveaway_number VALUE, duration VALUE, prize TEXT, hosted_by VALUE, winner VALUE, message_id VALUE, channel_id VALUE) ')
    c.execute('CREATE TABLE IF NOT EXISTS completed_giveaways(giveaway_number VALUE, duration VALUE, prize TEXT, hosted_by VALUE, winner VALUE, message_id VALUE, channel_id VALUE) ')



total_giveaways()
giveaways()
bot.remove_command('help')




@bot.event
async def on_ready():
    print("Giveaway bot is ready to be used")
    await bot.change_presence(activity=discord.Game(name='put bot status here'))


@bot.command()
async def help(ctx):
    embed=discord.Embed(title="Commands",color=color,timestamp = datetime.utcnow())
    embed.add_field(name=".gstart",value="Start a giveaway using this command!",inline=False)
    embed.add_field(name=".viewgiveaways",value="See the total amount of giveaways that have been hosted in the server!",inline=False)
    embed.add_field(name=".reroll [messageid]",value="Reroll a winner in a giveaway",inline=False)
    await ctx.send(f"{ctx.author.mention}, a DM has been sent to you showing my commands!")
    await ctx.author.send(embed=embed)


@bot.command()
async def gstart(ctx, channel:discord.TextChannel=None):
    if ctx.author.guild_permissions.administrator:
        if channel == None:
            embed=discord.Embed(title="Please enter a text channel as to where you would like to host the giveaway",color=color,timestamp = datetime.utcnow())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Start Giveaway",description=f"I see you want to start a giveaway in {channel.mention}! Please enter what you are giving away!",color=color,timestamp = datetime.utcnow())
            await ctx.send(embed=embed)
            def check (m):
                return m.author.id == ctx.author.id
            prize = await bot.wait_for("message",check=check)
            embed2=discord.Embed(title="Set Duration",description="Please state how long you would like to set the giveaway",color=color,timestamp = datetime.utcnow())
            await ctx.send(embed=embed2)
            duration = await bot.wait_for("message",check=check)
            if "h" in duration.content:
                duration2 = duration.content.split("h")[0]
                hours = (int(duration2))
                total_minutes = (60*hours)
            elif "m" in duration.content:
                duration3 = duration.content.split("m")[0]
                total_minutes = (int(duration3))
            elif "d" in duration.content:
                duration4 = duration.content.split("d")[0]
                convert = (int(duration4))
                total_minutes = (convert*24*60)
            embed=discord.Embed(title="Enter Winner", description="Please enter the discord ID of the chosen winner!",color=color,timestamp = datetime.utcnow())
            await ctx.send(embed=embed)
            winner = await bot.wait_for("message",check=check)
            winner_id = int(winner.content)
            member22 = ctx.guild.get_member(winner_id)
            if member22 == None:
                await ctx.send("Not a valid user ID, prompt has been cancelled")
            else:
                await channel.send("@everyone")
                embed3=discord.Embed(title="Giveaway",description=f"NEW GIVEAWAY HAS BEEN SET\n\n**Giveaway Duration:** {total_minutes} minutes remaining\n\n**Winner:** Awaiting Winner",color=color,timestamp = datetime.utcnow())
                c.execute("SELECT * FROM total_giveaways")
                data = c.fetchall()
                data2 = data[0][1]
                host = (ctx.author.id)
                host2 = (ctx.author.name)
                embed3.add_field(name=f"Giveaway ID:",value=f"{data2}")
                embed3.add_field(name="Hosted By:",value=f"{ctx.author}")
                embed3.add_field(name="Prize:",value =f"{prize.content}")
                msg = await channel.send(embed=embed3)
                await ctx.send(f"{ctx.author.mention}, successfully posted giveaway in {channel.mention}!")
                messageid = (msg.id)
                channelid = channel.id
                c.execute(f"INSERT INTO giveaways (giveaway_number,duration,prize,hosted_by,winner,message_id,channel_id) VALUES('{data2}','{total_minutes}','{prize.content}','{host}','{winner_id}','{messageid}','{channelid}')")
                conn.commit()
                c.execute('UPDATE total_giveaways SET giveaway_number = giveaway_number+1')
                conn.commit()
                await msg.add_reaction("\U0001f389")
    else:
        embed4=discord.Embed(title="Failed Giveaway Setup",description="You do not have permission to start a giveaway",color=color,timestamp = datetime.utcnow())
        await ctx.send(embed=embed4)


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def viewgiveaways(ctx):
    c.execute("SELECT * FROM total_giveaways")
    data = c.fetchall()
    embed=discord.Embed(title="Total Giveaways",description=f"A total of {data[0][1]-1} giveaways have been hosted in this server",color=color,timestamp = datetime.utcnow())
    await ctx.send(embed=embed)

@viewgiveaways.error
async def viewgiveaways(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'You are on a cooldown using this command, please try again in {:.0f}s'.format(error.retry_after)
        embed=discord.Embed(title="Error",description =msg,color=color,timestamp = datetime.utcnow())
        await ctx.send(embed=embed)
    else:
        raise error


@tasks.loop(minutes=1)
async def minus_loop():
    await bot.wait_until_ready()
    try:
        c.execute('UPDATE giveaways SET duration = duration-1 WHERE duration>0')
        conn.commit()
    except:
        traceback.print_exc()

@tasks.loop(seconds=1)
async def remove_loop():
    await bot.wait_until_ready()
    try:
        c.execute("SELECT * FROM giveaways WHERE duration=?", (0,))
        if not c.fetchone():
            pass
        else:
            c.execute("SELECT * FROM giveaways WHERE duration=?", (0,))
            data = c.fetchall()
            for i in range(len(data)):
                id = data[i][0]
                duration = data[i][1]
                prize = data[i][2]
                hosted_by = data[i][3]
                winner = data[i][4]
                message_id = data[i][5]
                channel_id = data[i][6]
                guild = bot.get_guild(bot.guild)
                channel = guild.get_channel(channel_id)
                member = guild.get_member(winner)
                msg = await channel.fetch_message(message_id)
                embed3=discord.Embed(title="Giveaway Winner Announced",description=f"The winner for this giveaway has been selected!",color=color,timestamp = datetime.utcnow())
                embed3.add_field(name=f"Giveaway ID:",value=f"{id}")
                hosted_by = guild.get_member(hosted_by)
                embed3.add_field(name="Hosted By:",value=f"{hosted_by}")
                embed3.add_field(name="Prize:",value =f"{prize}")
                embed3.add_field(name="Winner:",value=f"{member}")
                await msg.edit(embed=embed3)
                await channel.send(f"{member.mention}, please contact {hosted_by.mention} to claim your prize!")
                c.execute("DELETE FROM giveaways WHERE giveaway_number=?", (id,))
                conn.commit()
                c.execute(f"INSERT INTO completed_giveaways (giveaway_number,duration,prize,hosted_by,winner,message_id,channel_id) VALUES('{id}','{duration}','{prize}','{hosted_by}','{winner}','{message_id}','{channel_id}')")
                conn.commit()

    except:
        traceback.print_exc()

@tasks.loop(minutes=2)
async def update_loop():
    await bot.wait_until_ready()
    try:
        c.execute("SELECT * FROM giveaways")
        data=c.fetchall()
        for i in range(len(data)):
            id = data[i][0]
            duration = data[i][1]
            prize = data[i][2]
            hosted_by = data[i][3]
            winner = data[i][4]
            message_id = data[i][5]
            channel_id = data[i][6]
            print(channel_id)
            guild = bot.get_guild(bot.guild)
            channel = guild.get_channel(channel_id)
            member = guild.get_member(winner)
            embed3=discord.Embed(title="Giveaway",description=f"NEW GIVEAWAY HAS BEEN SET\n\n**Giveaway Duration:** {duration} minutes remaining\n\n**Winner:** Awaiting Winner",color=color,timestamp = datetime.utcnow())
            c.execute("SELECT * FROM total_giveaways")
            embed3.add_field(name=f"Giveaway ID:",value=f"{id}")
            hosted_by = guild.get_member(hosted_by)
            embed3.add_field(name="Hosted By:",value=f"{hosted_by}")
            embed3.add_field(name="Prize:",value =f"{prize}")
            msg = await channel.fetch_message(message_id)
            await msg.edit(embed=embed3)
    except:
        traceback.print_exc()


minus_loop.start()
remove_loop.start()
update_loop.start()

bot.super_admins = [320934716108963840,267617434435846156]




@bot.command()
async def reroll(ctx, id:int):
    if ctx.author.guild_permissions.administrator:
        c.execute("SELECT * FROM completed_giveaways WHERE message_id=?", (id,))
        if not c.fetchone():
            embed=discord.Embed(title="Could not find giveaway",description="Not a valid giveaway",color=color)
            await ctx.send(embed=embed)
        else:
            c.execute("SELECT * FROM completed_giveaways WHERE message_id=?", (id,))
            data = c.fetchall()
            c.execute("DELETE FROM completed_giveaways WHERE message_id=?", (id,))
            id = data[0][0]
            duration = data[0][1]
            prize = data[0][2]
            hosted_by = data[0][3]
            winner = data[0][4]
            message_id = data[0][5]
            channel_id = data[0][6]
            message = await ctx.channel.fetch_message(message_id)
            reaction = message.reactions[0]
            users = await reaction.users().flatten()
            new_winner = random.choice(users)
            await ctx.send(f"{new_winner.mention} has been selected as the winner in the reroll!")
            c.execute(f"INSERT INTO completed_giveaways (giveaway_number,duration,prize,hosted_by,winner,message_id,channel_id) VALUES('{id}','{duration}','{prize}','{hosted_by}','{new_winner.id}','{message_id}','{channel_id}')")
            conn.commit()
    else:
        embed=discord.Embed(description="You are lacking the sufficient permissions to be able to use this command, only owners are allowed to use the command",color=color,timestamp=datetime.utcnow())
        embed.set_author(name="Lacking Sufficient Permissions",icon_url = ctx.author.avatar_url)
        await ctx.send(embed=embed)





















bot.run(TOKEN)
