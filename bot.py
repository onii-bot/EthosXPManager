import os
import discord
from discord.ext import commands, tasks
import requests
import time
from pymongo import MongoClient

# Intents
intents = discord.Intents.all()
intents.members = True

client = commands.Bot(intents=intents, command_prefix='..')

# Importing Database
cluster = MongoClient(os.environ['MONGO_TOKEN'])
db = cluster["discord"]
collection = db["ethos_xp_data"]

# Variables
ethos_customized_bot_ch = 1046353571001667617
ethos_dc = 1039314094081183824
ethos_reaction_ch = 1046331199628509204
ethos_priv_log_ch = 1046331887964143667
ethos_pub_logs_ch = 1047132047275208745
ethos_xp_manager = 1046367188421976074


# Events
@client.event
async def on_raw_reaction_add(payload):
    if payload.guild_id == ethos_dc:
        if payload.channel_id == ethos_reaction_ch:
            guild = client.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if message.author.id == ethos_xp_manager:
                if str(payload.emoji) == "👾":
                    try:
                        already_got_xp_users = collection.find().distinct('_id')
                        if payload.member.id not in already_got_xp_users:
                            if payload.member.id != ethos_xp_manager:
                                post = {"_id": payload.member.id}
                                collection.insert_one(post)
                                xp_pass = discord.utils.get(payload.guild.roles, id=1047154419696926783)
                                queen = discord.utils.get(payload.guild.roles, id=1045274556379701259)
                                king = discord.utils.get(payload.guild.roles, id=1045274429141299250)
                                if king in payload.author.roles or queen in payload.author.roles:
                                    xp = 500
                                    await xp_giver(payload.member.id, xp)
                                elif xp_pass in payload.author.roles:
                                    xp = 250
                                    await xp_giver(payload.member.id, xp)
                                else:
                                    xp = 100
                                    await xp_giver(payload.member.id, xp)
                                channelbot = client.get_channel(ethos_pub_logs_ch)
                                embed = discord.Embed(colour=discord.Colour.green())
                                embed.set_author(name=f"You received {xp}xp 👾")
                                await channelbot.send(f"{payload.member.mention}", embed=embed)
                        else:
                            channelbot = client.get_channel(ethos_pub_logs_ch)
                            embed = discord.Embed(colour=discord.Colour.red())
                            embed.set_author(name=f"You already claimed your daily XP 👾")
                            await channelbot.send(f"{payload.member.mention}", embed=embed)
                    except Exception as e:
                        print("Error")


@client.event
async def on_ready():
    print("bot:user ready == {0.user}".format(client))
    taskcheck.start()


# Functions
async def xp_giver(user_id, xp):
    word = f"!give-xp <@{user_id}> {xp}"
    channel_id = ethos_priv_log_ch
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    payload = {
        'content': word
    }
    header = {
        'authorization': os.environ['ICHIGO_TOKEN']
    }
    requests.post(url, data=payload, headers=header)


async def time_check():
    time_unix = int(time.time())
    target = collection.find_one({"_id": "target"})['time']
    if time_unix > target:
        print("its time")
        await new_day()


@client.command()
async def check(ctx):
    await ctx.send("Working :cat:")


async def new_day():
    target = collection.find_one({"_id": "target"})['time']
    collection.delete_many({})
    target = target + 86400
    post = {"_id": "target", "time": target}
    collection.insert_one(post)
    guild = client.get_guild(ethos_dc)
    channel = guild.get_channel(ethos_reaction_ch)
    await channel.purge(limit=1)
    # Embed
    embed = discord.Embed(colour=discord.Colour.blue())
    embed.add_field(name="Daily XPs", value="React to this text with 👾 to claim your daily xp", inline=True)
    msg = await channel.send("<@&1047154419696926783>", embed=embed)
    emoji = "👾"
    await msg.add_reaction(emoji)


# Tasks
@tasks.loop(seconds=30)
async def taskcheck():
    await time_check()


client.run(os.environ['DISCORD_TOKEN'])
