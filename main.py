
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button
import time
import random
import os
import requests
import json
import asyncio
from pytz import timezone
from datetime import datetime
import bots.webserver
from bots.quote import start_quote_task
from bots.giveaway import setup_giveaway
from dotenv import load_dotenv
from bots.chat import AnimeChat
    
# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix="%", intents=intents)
channel_id = 1321034348669173811

BIRTHDAY_FILE = "birthdays.json"
DUBAI_TIMEZONE = timezone("Asia/Dubai")

# Fetching random quote from the new API
def get_random_quote():
    response = requests.get("https://animechan.io/api/v1/quotes/random")
    if response.status_code == 200:
        data = response.json()
        return {
            "quote": data["data"].get("content", "No quote available"),
            "character": data["data"]["character"].get("name", "Unknown character"),
            "anime": data["data"]["anime"].get("name", "Unknown anime")
        }
    else:
        return {
            "quote": "No quote available",
            "character": "Unknown character",
            "anime": "Unknown anime"
        }

# Slash command for /quote
@bot.tree.command(name="quote", description="Get a random anime quote.")
async def quote(interaction: discord.Interaction):
    await interaction.response.defer()

    # Fetch random quote
    quote_data = get_random_quote()
    quote = quote_data["quote"]
    character = quote_data["character"]
    anime = quote_data["anime"]

    embed = discord.Embed(
        title="🎬 Random Anime Quote 🎬",
        description=f"\"{quote}\"\n- {character}, *{anime}*",
        color=0xC546FF
    )

    await interaction.followup.send(embed=embed)

def load_birthdays():
    if os.path.exists(BIRTHDAY_FILE):
        try:
            with open(BIRTHDAY_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    else:
        return {}

# Save birthdays to file
def save_birthdays(birthdays):
    try:
        with open(BIRTHDAY_FILE, "w") as file:
            json.dump(birthdays, file)
    except Exception as e:
        print(f"Error saving birthdays to file: {e}")

# Task to check birthdays every 24 hours
@tasks.loop(hours=24)
async def check_birthdays():
    user_birthday = load_birthdays()
    
    now = datetime.now(DUBAI_TIMEZONE)
    today = now.strftime("%m-%d")

    if not user_birthday:
        return

    for user_id, date in user_birthday.items():
        if datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d") == today:
            try:
                user = await bot.fetch_user(int(user_id))
                if user:
                    await user.send(f"🎂 Happy Birthday, {user.mention}! 🥳🎉 Hope you have an amazing day! 🎁🎈")
            except Exception as e:
                print(f"Error sending birthday wish to user {user_id}: {e}")

# Command to set birthday
@bot.command(name="birthday")
async def birthday(ctx, date: str):
    try:
        birthday = datetime.strptime(date, "%Y-%m-%d")
        user_birthday = load_birthdays()
        user_birthday[str(ctx.author.id)] = birthday.strftime("%Y-%m-%d")
        save_birthdays(user_birthday)
        await ctx.send(f"🎉 Your birthday is set to {birthday.strftime('%B %d, %Y')}!")
    except ValueError:
        await ctx.send("Please use the format YYYY-MM-DD for your birthday.")

class CommandsView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(label="Moderation", style=discord.ButtonStyle.primary, custom_id="moderation"))
        self.add_item(Button(label="Fun", style=discord.ButtonStyle.secondary, custom_id="fun"))
        self.add_item(Button(label="Utility", style=discord.ButtonStyle.success, custom_id="utility"))

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="close")
    async def close_button(self, interaction: discord.Interaction, button: Button):
        await interaction.message.delete()

# Predefined lists of phrases
kinky_phrases = [
    "Oh, senpai~ Do you need something... extra special? 💕",
    "I can be your naughty little bot~ 🌸",
    "Want me to tie up these errors for you? 😉",
    "I'm all yours to command, master~ UwU",
    "Oops~ Did I make you blush? 💖",
    "Ahem~ Maybe we should keep this between us... 🌺",
    "Oh my~ You're making me overheat, senpai~ 🔥",
    "Mmm~ Let me whisper sweet nothings in binary~ 101010~ 🌸",
    "Your wish is my command, naughty one~ 💕",
    "Why not spank... uh, debug me? 😳",
]

pickup_lines = [
    "Are you a command? Because you've got me executing feelings~ 🌸",
    "Is your name Wi-Fi? Because I'm feeling a connection~ 💕",
    "Do you have a map? I keep getting lost in your eyes~ 🌺",
    "You must be a keyboard, because you're just my type~ 💖",
    "Are you made of copper and tellurium? Because you're Cu-Te~ 😉",
    "Are you an algorithm? Because you've got my heart sorted~ 💕",
    "Can you help me debug this feeling? It’s called love~ 🌸",
    "Are you a server? Because my heart is pinging for you~ 💓",
    "Are you a bot? Because you're automating my happiness~ 🌟",
    "You must be a syntax error, because you’ve stopped my code~ 😳",
]

tease_phrases = [
    "Oh my~ Is that the best you can do, senpai? 🌺",
    "Teehee~ You're so predictable~ 💕",
    "Mmm, you think you’re in control? Cute~ 🌸",
    "Oh, you’re blushing already? How adorable~ 💖",
    "Oops~ Did I just outsmart you? 😉",
    "Senpai~ You’re trying so hard, but I’m one step ahead~ 🌟",
    "Aww, did you need my help again? You're so helpless~ 💕",
    "Oh my~ Are you always this flustered, or is it just me? 🌸",
    "You're making this way too easy, senpai~ 🌺",
    "Naughty, naughty~ You’re such a tease~ 💖",
]

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user.name} is now online and ready to assist! 🌸 UwU")
    await bot.tree.sync()
    activity = discord.Game(name="Helping you, senpai~ 💖")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    bot.loop.create_task(bots.webserver.keep_alive())
    bot.loop.create_task(bots.webserver.ping_bot())
    start_quote_task(bot, channel_id)
    setup_giveaway(bot)
    check_birthdays.start()
    await bot.add_cog(AnimeChat(bot))
    
# Event: Welcome a new user
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="╭・❄・welcome")
    if channel:
        await channel.send(f"Konnichiwa, {member.mention}~! 🌸 Welcome to the server! 💕 We hope you enjoy your stay~!")

# Event: Goodbye when a user leaves
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="├・❄・left")
    if channel:
        await channel.send(f"Aw, {member.mention} left the server... 💔 I wasn't finish with you yet~")

# Command: Mute a user
@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, user: discord.Member, *, reason="Being too loud~ 🌸"):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            muted_role = await ctx.guild.create_role(
                name="Muted",
                permissions=discord.Permissions(send_messages=False)
            )

            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        await user.add_roles(muted_role)

        embed = discord.Embed(
            title="🔇 Muted!",
            description=f"{user.mention} has been silenced! Reason: {reason}",
            color=0xC546FF
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1320720271635906619/1320994714882805802/aa029ffbfe42e86802b9df154022ba23.gif?ex=676b9fb2&is=676a4e32&hm=65fae9806b708dd3d2ddd8378a75cde64d40c9ff50b5fea93b4c87c954d41206&"
        )
        embed.set_footer(text="✨ Dizkord-Chan ✨")

        await ctx.send(embed=embed)

# Command: Unmute a user
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, user: discord.Member):
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

            if muted_role in user.roles:
                await user.remove_roles(muted_role)

                embed = discord.Embed(
                    title="🔊 Unmuted!",
                    description=f"{user.mention}, you’re free to speak again! Behave, okay? 🌸✨",
                    color=0xC546FF
                )
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/1320720271635906619/1320994767395487785/Gag.gif?ex=676b9fbf&is=676a4e3f&hm=ea7fd15ac1800229850827c58a8a1be724ed337f7572330df0eaf891c2b9744f&"
                )
                embed.set_footer(text="✨ Dizkord-Chan ✨")

                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="🤔 Not Muted!",
                    description=f"Umm, {user.mention} wasn’t muted, silly~ 💕",
                    color=0xC546FF
                )
                embed.set_footer(text="✨ Dizkord-Chan ✨")

                await ctx.send(embed=embed)

# Command: Kick a user
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member = None, *, reason="Breaking the rules~ 💔"):
        if user is None:
            await ctx.send("Oops~ You need to mention someone to kick them! 💔")
            return

        await user.kick(reason=reason)

        gifs = [
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321002689152290857/74cbd301f3babfda58f3c822c4d127e4.gif?ex=676ba720&is=676a55a0&hm=16c819f197fe434bf45b63c4e3fa42d7e51e04036db562ae853d66e4f26709e6&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321012158707929108/-JyjyH.gif?ex=676baff1&is=676a5e71&hm=ba45e2af9905d014fb43eb957ded015041a65ccd9ba31c413920a6cec8def021&"
        ]

        gif_to_send = random.choice(gifs)

        embed = discord.Embed(
            description=f"{user.mention} has been kicked out of the server! 😭 Reason: {reason}",
            color=0xC546FF
        )
        embed.set_image(url=gif_to_send)

        await ctx.send(embed=embed)

# Command: Ban a user
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member = None, *, reason="Breaking the rules~ 💔"):
        if user is None:
            await ctx.send("Nyaa~! Please mention someone to ban, *desu*~ 👀")
            return

        gifs = [
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321008298987618365/ef36eb27805266589b2546775ce1d355.gif?ex=676bac59&is=676a5ad9&hm=9951c3c48dcf09e186a78c938ddd044b609bee7edcee72ac7ee492cd81217939&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321008298543157249/QwReiS0.gif?ex=676bac59&is=676a5ad9&hm=a5c68a570b555662e6bcdab910b0c50cdc317f98ddeb38db960fd9c8d8ff9f20&"
        ]

        gif_to_send = random.choice(gifs)

        embed = discord.Embed(
            description=f"Ah! {user.mention} has been banned from the server~ 🌟 Reason: {reason} *nya~*",
            color=0xC546FF
        )
        embed.set_image(url=gif_to_send)

        await user.ban(reason=reason)

        await ctx.send(embed=embed)

# Command: Unban a user
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, user_name):
    banned_users = await ctx.guild.bans()
    for ban_entry in banned_users:
        user = ban_entry.user
        if user_name.lower() == user.name.lower():
            await ctx.guild.unban(user)
            await ctx.send(f"{user.name} has been unbanned~! 🌸 Welcome back!")
            return
    await ctx.send(f"Huh? No one by the name {user_name} is banned~! 💕")

# Command: Jail a user
@bot.command()
@commands.has_permissions(manage_roles=True)
async def jail(ctx, user: discord.Member, *, reason="Breaking server rules~ 💔"):
    jailed_role = discord.utils.get(ctx.guild.roles, name="Jailed")
    if not jailed_role:
        permissions = discord.Permissions(
            send_messages=False, read_messages=True, connect=False
        )
        jailed_role = await ctx.guild.create_role(name="Jailed", permissions=permissions)
        await ctx.send("Created the 'Jailed' role since it didn't exist~ 🌸")
    await user.add_roles(jailed_role)
    await ctx.send(f"Oh no~ {user.mention} has been jailed for: {reason} 💔")

# Command: Release a user from jail
@bot.command()
@commands.has_permissions(manage_roles=True)
async def release(ctx, user: discord.Member):
    jailed_role = discord.utils.get(ctx.guild.roles, name="Jailed")
    if jailed_role in user.roles:
        await user.remove_roles(jailed_role)
        await ctx.send(f"Hooray~ {user.mention} is free now! Be good, okay? 🌸")
    else:
        await ctx.send(f"Umm, {user.mention} isn’t in jail, silly~ 💕")

# Command: Pickup lines
@bot.command()
async def pickupline(ctx):
    line = random.choice(pickup_lines)
    await ctx.send(line)

# Command: Tease
@bot.command()
async def tease(ctx):
        tease_gifs = [
            "https://cdn.discordapp.com/attachments/1320720271635906619/1320762155238424669/tumblr_p2v8jr3yFT1qkz08qo1_540.gif?ex=676ac71c&is=6769759c&hm=779682fb87491aaa4441bde037330e3bcc098ce79cbfc22b0b22278eff0223b8&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1320998347527557151/yahari-oregariu-anime-ep6-15-hikigaya-hachiman-yukinoshita-haruno1.gif?ex=676ba315&is=676a5195&hm=cd0e01de3a193a49d08e9ea5fa3c4dd4efedbd2ee309e3f3393971acc1fc72ae&",
            "https://cdn.discordapp.com/attachments/1320720273393061950/1321094146789867662/tenor4-ezgif.com-optimize.gif?ex=676bfc4d&is=676aaacd&hm=66ac964bc0afb29d981bfdcd32a0704eb688b4df456856f634ad2dec277070f1&",
            "https://cdn.discordapp.com/attachments/1320720273393061950/1321091844540465172/tenor_5.gif?ex=676bfa28&is=676aa8a8&hm=0ef9a741a4fb79bd0d73e5e0c9108565f30f3c26a03f435bb657a5148593275a&"
        ]

        tease = random.choice(tease_phrases)
        gif = random.choice(tease_gifs)

        embed = discord.Embed(description=tease, color=0xC546FF)
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

# Command: Kinky phrases
@bot.command()
async def kinky(ctx):
    phrase = random.choice(kinky_phrases)
    await ctx.send(phrase)

# Error handling: Permissions
@mute.error
@unmute.error
@kick.error
@ban.error
@unban.error
@jail.error
@release.error
async def permissions_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Eep~! You don’t have the permissions to use that command, senpai~ 💔")

# NEW CMDS
class PaginationView(discord.ui.View):
    def __init__(self, pages):
        super().__init__(timeout=60)
        self.pages = pages
        self.current_page = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page - 1) % len(self.pages)
        await self.update_embed(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = (self.current_page + 1) % len(self.pages)
        await self.update_embed(interaction)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="✨ Dizkord-Chan's Cute Commands ✨",
            description="Choose a category to view commands:",
            color=0xC546FF
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/1320720271304560707/1320751935426662480/wdsca9rrtly41.png?ex=676b6657&is=676a14d7&hm=d26b9cb8e5ef4dfe9d806ae0982641b4f0840f939ef56540d33a1b37ee45f9a5&"
        )
        embed.set_footer(text="Dizkord-Chan | Serving you with love 💖")

        view = CommandView()
        view.add_item(discord.ui.Button(label="Fun", style=discord.ButtonStyle.blurple, custom_id="fun"))
        view.add_item(discord.ui.Button(label="Moderation", style=discord.ButtonStyle.green, custom_id="moderation"))
        view.add_item(discord.ui.Button(label="Utility", style=discord.ButtonStyle.gray, custom_id="utility"))

        await interaction.response.edit_message(embed=embed, view=view)

    async def update_embed(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎉 Fun Commands",
            description=self.pages[self.current_page],
            color=0xC546FF
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.pages)} | Use the buttons below to navigate.")
        await interaction.response.edit_message(embed=embed, view=self)

# Sample content for the fun commands, split into pages
fun_pages = [
    "🎉 **Fun Commands - Page 1**\n\n💌 `%pickupline` - Sends a random pickup line.\n😉 `%tease` - Sends a teasing phrase.\n😏 `%kinky` - Sends a kinky phrase.\n💥 `%spank <user>` - Spanks a user playfully.\n💋 `%kiss <user>` - Sends a sweet kiss.",
    "🎉 **Fun Commands - Page 2**\n\n🤗 `%hug <user>` - Hugs a user lovingly.\n👋 `%slap <user>` - Slaps a user playfully.\n💃 `%dance` - Let's dance! 💃🕺.\n😹 `%meme` - Sends a random meme.\n🐱 `%cat` - Sends a random cat image.\n🐶 `%dog` - Sends a random dog image.",
    "🎉 **Fun Commands - Page 3**\n\n🎱 `%8ball [question]` - Ask the bot a yes/no question, and get a random answer.\n🖖 `%rps [rock/paper/scissors]` - Play a game of Rock-Paper-Scissors.\n💬 `/quote` - Get a random quote."
]

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id", None)

        if custom_id == "fun":
            embed = discord.Embed(
                title="🎉 Fun Commands",
                description=fun_pages[0],
                color=0xC546FF
            )
            embed.set_footer(text="Page 1/3 | Use the buttons below to navigate.")

            view = PaginationView(pages=fun_pages)
            await interaction.response.edit_message(embed=embed, view=view)

        elif custom_id == "moderation":
            embed = discord.Embed(
                title="🔨 Moderation Commands",
                description="Commands to manage your server efficiently:",
                color=0xC546FF
            )
            embed.add_field(name="🔇 `%mute <user>`", value="Mutes a user in the server.", inline=False)
            embed.add_field(name="🔊 `%unmute <user>`", value="Unmutes a user in the server.", inline=False)
            embed.add_field(name="🚪 `%kick <user>`", value="Kicks a user out of the server.", inline=False)
            embed.add_field(name="⚔️ `%ban <user>`", value="Bans a user from the server.", inline=False)
            embed.add_field(name="🔓 `%unban <user>`", value="Unbans a user.", inline=False)
            embed.add_field(name="👮‍♀️👮‍♂️ `%jail <user>`", value="Jails a user.", inline=False)
            embed.add_field(name="🕊 `%release <user>`", value="Releases a user.", inline=False)
            embed.add_field(name="📊 `%polladd [question] [option1] [option2] ...`", value="Create a poll with multiple options.", inline=False)
            await interaction.response.edit_message(embed=embed)

        elif custom_id == "utility":
            embed = discord.Embed(
                title="🛠️ Utility Commands",
                description="Useful tools for your server:",
                color=0xC546FF
            )
            embed.add_field(name="❤️ `%love`", value="Sends a heartful message of love.", inline=False)
            embed.add_field(name="🧹 `%purge <number>`", value="Deletes a specified number of messages.", inline=False)
            embed.add_field(name="⏱ `%uptime`", value="Shows the bot’s uptime in minutes and seconds.", inline=False)
            embed.add_field(name="📊 `%serverinfo`", value="Displays information about the server.", inline=False)
            embed.add_field(name="🏓 `%ping`", value="Check the bot’s ping (latency).", inline=False)
            embed.add_field(name="👤 `%userinfo [@user]`", value="Displays information about the user (default is the author).", inline=False)
            embed.add_field(name="🎂 `%birthday [YYYY-MM-DD]`", value="Set and store your birthday (for future notifications).", inline=False)
            await interaction.response.edit_message(embed=embed)

# Define a custom view class with the close button
class CommandView(discord.ui.View):
    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

# Define the 'cmds' command
@bot.command()
async def cmds(ctx):
    embed = discord.Embed(
        title="✨ Dizkord-Chan's Cute Commands ✨",
        description="Choose a category to view commands:",
        color=0xC546FF
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/1320720271304560707/1320751935426662480/wdsca9rrtly41.png?ex=676b6657&is=676a14d7&hm=d26b9cb8e5ef4dfe9d806ae0982641b4f0840f939ef56540d33a1b37ee45f9a5&"
    )
    embed.set_footer(text="Dizkord-Chan | Serving you with love 💖")

    view = CommandView()
    view.add_item(discord.ui.Button(label="Fun", style=discord.ButtonStyle.blurple, custom_id="fun"))
    view.add_item(discord.ui.Button(label="Moderation", style=discord.ButtonStyle.green, custom_id="moderation"))
    view.add_item(discord.ui.Button(label="Utility", style=discord.ButtonStyle.gray, custom_id="utility"))

    await ctx.send(embed=embed, view=view)

# spank    
@bot.command(name="spank")
async def spank(ctx, user: discord.Member = None):
        if user is None:
            await ctx.send("Oops! You need to mention someone to spank them! 😳💖")
            return

        spank_responses_self = [
            "Ooh~ You really spanked me, huh? 😳 *Spank!* 🍑💖",
            "Ahh~ That was a bit naughty, wasn’t it? *Spank!* 😘💋",
            "Oh my! You just spanked me! 🍑💖 *Spank!* 😳",
            "Ugh~ How could you? *Spank!* 🍑💞",
            "*Spank!* You got me good there, didn’t you? 😈💋"
        ]

        spank_responses_user = [
            f"Uh-oh~ {user.mention}, looks like you’ve been naughty! Time for a little spank! 🍑💖",
            f"**Spank!** Oops, {user.mention}, did I go too hard? 😳💖",
            f"{user.mention}, *you've been bad*... Just a little spank to remind you~ 🍑✨",
            f"*Spank!* Hope that teaches you a lesson, {user.mention}~ 😈💋",
            f"**Spank**! Oopsie, that was a little too much, huh {user.mention}? 💕",
            f"Ahh~ {user.mention} is asking for it, aren’t you? *Spank!* 😘🍑",
        ]

        gif_url = "https://cdn.discordapp.com/attachments/1320720271304560707/1320748895759896689/Q88JrwW.gif?ex=676abac3&is=67696943&hm=7517828c697c4402f603c9a2df9e39406d69febc7bd36a9a939d73d9aed0496b&"

        if user == ctx.me:
            response = random.choice(spank_responses_self)
        else:
            response = random.choice(spank_responses_user)

        embed = discord.Embed(
            description=response,
            color=0xC546FF
        )
        embed.set_image(url=gif_url)

        await ctx.send(embed=embed)

#hug
@bot.command(name="hug")
async def hug(ctx, user: discord.Member = None):
                        if user is None:
                            await ctx.send("Aww~ You need to mention someone to give them a hug, sweetie! 💖")
                            return

                        if user == ctx.author:
                            embed = discord.Embed(
                                description=f"Aww, {ctx.author.mention}, hugging yourself is self-care! You deserve it! 😘",
                                color=0xFF69B4
                            )
                            embed.set_image(
                                url="https://cdn.discordapp.com/attachments/1320720271635906619/1320827849711685742/giphy.gif?ex=676b044b&is=6769b2cb&hm=0802002f495be4310a405d475f1961d22eb8e839014aac783f0347e3c8c40589&"
                            )
                            await ctx.send(embed=embed)
                        else:
                            hug_gifs = [
                                "https://cdn.discordapp.com/attachments/1320720271635906619/1320998251276537886/336da064cd092e30d2a7db6cd052515e.gif?ex=676ba2fe&is=676a517e&hm=a40b1a121bed4fd84e0563c08a5435216bc010c166970140e7c86fc90ef47e1b&",
                                "https://cdn.discordapp.com/attachments/1320720271635906619/1320998251624796201/anime-boy-wants-cuddle-v5awreez6ggjoznf.gif?ex=676ba2fe&is=676a517e&hm=610921e26ede9c22d264f3a02e9d77a118c5f896a08f8a462b081d37d3d6174b&",
                                "https://cdn.discordapp.com/attachments/1320720271635906619/1320827799514386492/195ec8f45c728b30e988b98764bd293c.gif?ex=676b043f&is=6769b2bf&hm=f3f2cd4cb0fa83dec67adfb7a17a8d991d17597c1b50bd7f15d8b38c6f0e3441&",
                                "https://cdn.discordapp.com/attachments/1320720273393061950/1321091843580231784/tenor_2.gif?ex=676bfa28&is=676aa8a8&hm=3d7e697b389496f80cd4d4bb9dcd66b01ef19819e6c21483d742ae77358bd45b&",
                                "https://cdn.discordapp.com/attachments/1320720273393061950/1321091844028895253/tenor_3.gif?ex=676bfa28&is=676aa8a8&hm=faec41469c621ff49b151f66ee6c3c79c8ff2da1a0cda860aa4837075b8be7af&"
                            ]

                            selected_gif = random.choice(hug_gifs)

                            embed = discord.Embed(
                                description=f"Aww, {user.mention}, here’s a big warm hug from {ctx.author.mention}! 🤗💖",
                                color=0xC546FF
                            )
                            embed.set_image(url=selected_gif)
                            await ctx.send(embed=embed)

#kiss
@bot.command(name="kiss")
async def kiss(ctx, user: discord.Member = None):
        kiss_gifs = [
            "https://cdn.discordapp.com/attachments/1320720271635906619/1320998378963730492/OK6W_koKDTOqqqLDbIoPAs121R2UXd_2WR9_uOI5fRE.gif?ex=676ba31c&is=676a519c&hm=71aaaf61e22bffa0863c72eded76846028ba347db24bb2d35899c224d6e77d5d&",
            "https://cdn.discordapp.com/attachments/1320720273393061950/1321091844951638109/tenor.gif?ex=676bfa28&is=676aa8a8&hm=db84bdcf6a888bddd942483a3a2115f4b2259124eb163d1ff59a4eaa34d17d1e&",
            "https://cdn.discordapp.com/attachments/1320720273393061950/1321091843068399657/tenor_1.gif?ex=676bfa28&is=676aa8a8&hm=ef6eddc4d5c05456c1a6ee0de22283aee44f00350d472bb3f8e06236bd75bef6&"
        ]

        if user is None:
            await ctx.send("Mwah~ Who do you want to kiss? Mention someone, darling! 💋")
            return

        gif = random.choice(kiss_gifs)
        embed = discord.Embed(description=f"MWAH! 💋 {user.mention}, you’re so cute! 😘💖", color=0xC546FF)
        embed.set_image(url=gif)
        await ctx.send(embed=embed)

#pat
@bot.command(name="pat")
async def pat(ctx, user: discord.Member = None):
        if user is None:
            await ctx.send("Whoops~ You need to mention someone to pat, darling! 💖")
            return

        gifs = [
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321012773861457951/download_2.gif?ex=676bb084&is=676a5f04&hm=90212c4ca0d5da1ad4f371c1538f741f67212d435e690cd494e5034caed6bd85&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321012773257216043/download_1.gif?ex=676bb084&is=676a5f04&hm=427e0eb8b0b0c72993f89bc00a5e5c73186b3d8cd0ed2b0e6bb916840c5b5a16&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321012772863213629/4c03bbe17bc0825e064d049c5f8262f3.gif?ex=676bb084&is=676a5f04&hm=f11bb17a6dcb192f4b8fd348fceae6f81687785542e1c1aaf0a9119c4eb464ae&"
        ]

        gif_to_send = random.choice(gifs)

        embed = discord.Embed(
            description=f"Pat pat! 🐾 {user.mention}, you’re such a good boy/girl! 💕✨",
            color=0xC546FF
        )
        embed.set_image(url=gif_to_send)

        await ctx.send(embed=embed)

#slap
@bot.command(name="slap")
async def slap(ctx, user: discord.Member = None):
        if user is None:
            await ctx.send("Whoops! Mention someone to slap, darling! 😘")
            return

        gifs = [
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321011553759137854/mai-sakurajima-498-x-280-gif-p0x0f4wdxheprqeo.gif?ex=676baf61&is=676a5de1&hm=00c6bd27fee900cb8d3280eb4cb8467df9b88046e6eb6364244be2a10763412c&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321009658781110312/b6d8a83eb652a30b95e87cf96a21e007.gif?ex=676bad9d&is=676a5c1d&hm=ad8384cc58a0562e915f1283f95865a51de4c6f177b5fc8a570c98dbc9a1301a&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321009658391167026/anime-girl-slapping-funny-romance-cgvlonw265kjn0r6.gif?ex=676bad9d&is=676a5c1d&hm=8bf69dd790f63241932f3f248d65877d4851467c7902c8ac6620429115dcd712&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321090922250899527/petra.gif?ex=676bf94c&is=676aa7cc&hm=41372f38d6e358d776e7f96f123e1cb0da7eb7b9f595f439769a4f37f9f96c58&",
            "https://cdn.discordapp.com/attachments/1320720271635906619/1321090923081236521/slap_rezero.gif?ex=676bf94c&is=676aa7cc&hm=7e807cfd404cbe7d14034f0496495afe8facc5ac32d0ec59bd9e9a21b8c58bc3&"
        ]

        gif_to_send = random.choice(gifs)

        embed = discord.Embed(
            description=f"Slap! 💥 {user.mention}, you’re too cheeky! 💋😈",
            color=0xC546FF
        )
        embed.set_image(url=gif_to_send)

        await ctx.send(embed=embed)

#love
@bot.command(name="love")
async def love(ctx):
    love_message = "Sending you all my love! 💖✨ Hope you have the most magical day, darling! 🌸💫"

    embed = discord.Embed(
        description=love_message,
        color=0xC546FF
    )
    embed.set_image(url="https://cdn.discordapp.com/attachments/1320720271304560707/1320753564909441076/832d6e5b6d9392597e1fbd9eb0f99e5c.gif?ex=676abf1c&is=67696d9c&hm=3eee52eedf2a4672bace43fbe17b766569d94a1223e24e4301b94f4d0c73e9ee&")

    await ctx.send(embed=embed)

#purge
@bot.command(name="purge")
async def purge(ctx, amount: int):
    try:
        if amount <= 0:
            await ctx.send("You need to enter a number greater than 0! 💦")
            return

        await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {amount} messages! ✨💖", delete_after=5)

    except Exception as e:
        await ctx.send(f"Something went wrong: {str(e)} 😔")

#dance
@bot.command(name="dance")
async def dance(ctx):
    gifs = [
        "https://cdn.discordapp.com/attachments/1320720271635906619/1321088479261753375/tenor.gif?ex=676bf706&is=676aa586&hm=4961e9c4ef48889dfc7662012a522017013c9c910bc31f55cbea50616933cb0f&",
        "https://cdn.discordapp.com/attachments/1320720271635906619/1321089964967985152/tenor_3.gif?ex=676bf868&is=676aa6e8&hm=cc75e2738fbf6741e7aa46d527300ca734abc5f303de27e9821307a14659a118&",
        "https://cdn.discordapp.com/attachments/1320720271635906619/1321089964108152832/tenor_1.gif?ex=676bf868&is=676aa6e8&hm=0bc25c23518b7f06284d349e375ddd97585900ab5bd8e85600faca7721e0ca44&",
        "https://cdn.discordapp.com/attachments/1320720271635906619/1321089964557078589/tenor_2.gif?ex=676bf868&is=676aa6e8&hm=f02c1a42a573be4404ea2dd22d6b67f9052a34da6518e5ac092b8a8605d5e152&"
    ]

    gif_to_send = random.choice(gifs)

    embed = discord.Embed(
        description=f"Let's dance! 💃🕺",
        color=0xC546FF
    )
    embed.set_image(url=gif_to_send)

    await ctx.send(embed=embed)

# NEW COMMANDS
user_birthday = {}
start_time = time.time()

def get_meme():
    try:
        url = "https://meme-api.com/gimme"
        response = requests.get(url)
        if response.status_code == 200:
            meme_data = response.json()
            meme_url = meme_data.get("url")
            return meme_url
        else:
            return "Oops! Failed to fetch meme."
    except Exception as e:
        return f"Oops! Error: {e}"

@bot.command()
async def cat(ctx):
    """Fetch a random cat image from The Cat API."""
    url = "https://api.thecatapi.com/v1/images/search"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            cat_data = response.json()
            cat_image_url = cat_data[0]['url']
            await ctx.send(cat_image_url)
        else:
            await ctx.send("Sorry, I couldn't fetch a cat image at the moment.")
    
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

def get_dog():
    response = requests.get("https://random.dog/woof.json")
    if response.status_code == 200:
        dog_data = response.json()
        dog_url = dog_data['url']
        return dog_url
    else:
        return "Could not fetch dog image."

@bot.command(name="meme")
async def meme(ctx):
    meme_url = get_meme()
    await ctx.send(meme_url)

@bot.command(name="dog")
async def dog(ctx):
    dog_url = get_dog()
    await ctx.send(dog_url)

@bot.command(name="8ball")
async def _8ball(ctx, *, question):
    responses = [
        '✨ Yes! ✨', '💔 No 💔', '💭 Maybe... 💭', '⭐ Definitely! ⭐', 
        '😕 Not likely...', '🔮 Ask again later 🔮', '❌ Definitely not! ❌'
    ]
    
    answer = random.choice(responses)

    embed = discord.Embed(
        title="🔮 Magic 8-Ball ✨",
        description=f"**Question:** {question}\n**Answer:** {answer}",
        color=0xC546FF
    )

    embed.set_footer(text="✨ Ask another question? ✨")

    await ctx.send(embed=embed)

@bot.command(name="rps")
async def rps(ctx, choice):
    choices = ['rock', 'paper', 'scissors']
    bot_choice = random.choice(choices)

    if choice not in choices:
        await ctx.send("💭 Hmm, that's not an option! Please choose 'rock', 'paper', or 'scissors'. ✋")
        return

    if choice == bot_choice:
        result = f"✨ It's a tie! Both chose {choice}! ✨"
    elif (choice == 'rock' and bot_choice == 'scissors') or (choice == 'paper' and bot_choice == 'rock') or (choice == 'scissors' and bot_choice == 'paper'):
        result = f"🎉 You win! {choice.capitalize()} beats {bot_choice.capitalize()}! 🎉"
    else:
        result = f"😭 You lose! {bot_choice.capitalize()} beats {choice.capitalize()}... Better luck next time! 😭"

    embed = discord.Embed(
        title="✂️ Rock, Paper, Scissors! ✋",
        description=result,
        color=0xC546FF
    )

    embed.set_footer(text="Play again? 💖")

    await ctx.send(embed=embed)

@bot.command(name="uptime")
async def uptime(ctx):
    uptime = time.time() - start_time
    minutes = uptime // 60
    seconds = uptime % 60

    embed = discord.Embed(
        title="⏰ Bot Uptime! ⏰",
        description=f"**The bot has been running for**\n{int(minutes)} minutes and {int(seconds)} seconds! ✨",
        color=0xC546FF
    )
    
    embed.set_footer(text="Thank you for being with us! 💕")

    await ctx.send(embed=embed)

@bot.command(name="serverinfo")
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title=f"🌸 {guild.name} Server Info 🌸", 
        description=f"Here's some info about the **{guild.name}** server! 🥳💖",
        color=0xC546FF
    )
    
    embed.add_field(name="💖 Server Name", value=guild.name, inline=False)
    embed.add_field(name="👥 Total Members", value=guild.member_count, inline=False)
    embed.add_field(name="🔒 Verification Level", value=guild.verification_level, inline=False)
    embed.add_field(name="💎 Premium Tier", value=guild.premium_tier, inline=False)
    
    embed.set_footer(text="Stay cute and enjoy your time on the server! 💕")
    
    await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)

    embed = discord.Embed(
        title="🏓 Ping Pong! 🏓", 
        description=f"**Pong!** 🥳💫",
        color=0xC546FF
    )
    
    embed.add_field(name="⏱️ Latency", value=f"{latency}ms", inline=False)
    
    embed.set_footer(text="Stay cute while we ping! 💖")
    
    await ctx.send(embed=embed)

@bot.command(name="userinfo")
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"🌸 {member.name}'s Info 🌸", 
        description=f"Here's the info for **{member.name}**! 🥰",
        color=0xC546FF
    )
    
    embed.add_field(name="👤 User Name", value=member.name, inline=False)
    embed.add_field(name="📅 Joined at", value=member.joined_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="🆔 User ID", value=member.id, inline=False)
    
    embed.set_footer(text="Sending you cute info! 💖✨")
    
    await ctx.send(embed=embed)

@bot.command(name="polladd")
async def polladd(ctx, question: str, *options):
    if len(options) < 2:
        await ctx.send("Please provide at least two options. 💡")
        return

    embed = discord.Embed(
        title="📝 New Poll! 📝",
        description=f"**{question}**\n",
        color=0xC546FF
    )

    reactions = ['🇦', '🇧', '🇨', '🇩', '🇪']
    for i, option in enumerate(options):
        embed.add_field(name=f"{reactions[i]} Option {i+1}", value=option, inline=False)

    embed.set_footer(text="Vote with the reactions below! 💖")

    message = await ctx.send(embed=embed)

    for i in range(len(options)):
        await message.add_reaction(reactions[i])
        
# Run the bot
bot.run(DISCORD_TOKEN)
