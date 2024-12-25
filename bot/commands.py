import discord
import requests
from discord.ext import commands
import random
from datetime import datetime
import time

bot = commands.Bot(command_prefix='%')
user_birthday = {}
start_time = time.time()

async def meme(ctx):
    meme_url = get_meme()
    await ctx.send(meme_url)

@bot.command()
async def cat(ctx):
    cat_url = get_cat()
    await ctx.send(cat_url)

@bot.command()
async def dog(ctx):
    dog_url = get_dog()
    await ctx.send(dog_url)

def get_meme():
    response = requests.get("https://some-random-api.ml/meme")
    if response.status_code == 200:
        meme_data = response.json()
        meme_url = meme_data['image']
        return meme_url
    else:
        return "Could not fetch meme."

@bot.command(name="8ball")
async def _8ball(ctx, *, question):
    responses = [
        'Yes', 'No', 'Maybe', 'Definitely', 'Not likely', 'Ask again later', 'Definitely not'
    ]
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

def get_cat():
    response = requests.get("https://aws.random.cat/meow")
    if response.status_code == 200:
        cat_data = response.json()
        cat_url = cat_data['file']
        return cat_url
    else:
        return "Could not fetch cat image."

def get_dog():
    response = requests.get("https://random.dog/woof.json")
    if response.status_code == 200:
        dog_data = response.json()
        dog_url = dog_data['url']
        return dog_url
    else:
        return "Could not fetch dog image."

@bot.command(name="rps")
async def rps(ctx, choice):
    choices = ['rock', 'paper', 'scissors']
    bot_choice = random.choice(choices)
    if choice not in choices:
        await ctx.send("Please choose 'rock', 'paper', or 'scissors'.")
        return
    if choice == bot_choice:
        result = "It's a tie!"
    elif (choice == 'rock' and bot_choice == 'scissors') or (choice == 'paper' and bot_choice == 'rock') or (choice == 'scissors' and bot_choice == 'paper'):
        result = f"You win! {choice} beats {bot_choice}."
    else:
        result = f"You lose! {bot_choice} beats {choice}."
    await ctx.send(result)

@bot.command(name="uptime")
async def uptime(ctx):
    uptime = time.time() - start_time
    minutes = uptime // 60
    seconds = uptime % 60
    await ctx.send(f"Bot uptime: {int(minutes)} minutes and {int(seconds)} seconds.")

@bot.command(name="serverinfo")
async def serverinfo(ctx):
    guild = ctx.guild
    server_info = f"Server name: {guild.name}\nTotal members: {guild.member_count}\nServer region: {guild.region}"
    await ctx.send(server_info)

@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latency is {latency}ms.")

@bot.command(name="userinfo")
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    user_info = f"User name: {member.name}\nJoined at: {member.joined_at}\nID: {member.id}"
    await ctx.send(user_info)

@bot.command(name="birthday")
async def birthday(ctx, date: str):
    try:
        birthday = datetime.strptime(date, "%Y-%m-%d")
        user_birthday[ctx.author.id] = birthday
        await ctx.send(f"Your birthday is set to {birthday.strftime('%B %d, %Y')}")
    except ValueError:
        await ctx.send("Please use the format YYYY-MM-DD for your birthday.")

@bot.command(name="polladd")
async def polladd(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.send("Please provide at least two options.")
        return

    poll = f"**{question}**\n"
    reactions = ['🇦', '🇧', '🇨', '🇩', '🇪']
    for i, option in enumerate(options):
        poll += f"{reactions[i]} {option}\n"

    message = await ctx.send(poll)
    for i in range(len(options)):
        await message.add_reaction(reactions[i])
