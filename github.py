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
ethos_log_ch = 1046331887964143667
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
                                await xp_giver(payload.member.id)
                        else:
                            await client.get_channel(ethos_log_ch).send(f"{payload.member.mention}You already claimed your daily XP 👾")
                    except Exception as e:
                        print("Error")


@client.event
async def on_ready():
    print("bot:user ready == {0.user}".format(client))
    taskcheck.start()


# Functions
async def xp_giver(user_id):
    word = f"!give-xp <@{user_id}> 200"
    channel_id = ethos_log_ch
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
        target = target + 86400
        collection.update_one({"_id": "target"}, {"$set": {"time": target}})
        await new_day()


@client.command()
async def check(ctx):
    await ctx.send("Working :cat:")


async def new_day():
    collection.delete_many({})
    guild = client.get_guild(ethos_dc)
    channel = guild.get_channel(ethos_reaction_ch)
    await channel.purge(limit=1)
    embed = discord.Embed(colour=discord.Colour.blue())
    embed.add_field(name="Daily XPs", value="React to this text with 👾 to claim your daily xp", inline=True)
    msg = await channel.send(embed=embed)
    emoji = "👾"
    await msg.add_reaction(emoji)


# Tasks
@tasks.loop(seconds=30)
async def taskcheck():
    await time_check()


client.run(os.environ['DISCORD_TOKEN'])

