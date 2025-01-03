
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
from bots.poll import setup_poll
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
bot = commands.Bot(command_prefix=",", intents=intents)
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
    setup_poll(bot)
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
    "🎉 **Fun Commands - Page 1**\n\n💌 `,pickupline` - Sends a random pickup line.\n😉 `,tease` - Sends a teasing phrase.\n😏 `,kinky` - Sends a kinky phrase.\n💥 `,spank <user>` - Spanks a user playfully.\n💋 `,kiss <user>` - Sends a sweet kiss.",
    "🎉 **Fun Commands - Page 2**\n\n🤗 `,hug <user>` - Hugs a user lovingly.\n👋 `,slap <user>` - Slaps a user playfully.\n🐾 `,pat` - Pat a user lovingly.\n💃 `,dance` - Let's dance! 💃🕺.\n😹 `,meme` - Sends a random meme.\n🐱 `,cat` - Sends a random cat image.\n🐶 `,dog` - Sends a random dog image.",
    "🎉 **Fun Commands - Page 3**\n\n🎱 `,8ball [question]` - Ask the bot a yes/no question, and get a random answer.\n🖖 `,rps [rock/paper/scissors]` - Play a game of Rock-Paper-Scissors.\n💬 `/quote` - Get a random anime quote."
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
            embed.add_field(name="🔇 `,mute <user>`", value="Mutes a user in the server.", inline=False)
            embed.add_field(name="🔊 `,unmute <user>`", value="Unmutes a user in the server.", inline=False)
            embed.add_field(name="🚪 `,kick <user>`", value="Kicks a user out of the server.", inline=False)
            embed.add_field(name="⚔️ `,ban <user>`", value="Bans a user from the server.", inline=False)
            embed.add_field(name="🔓 `,unban <user>`", value="Unbans a user.", inline=False)
            embed.add_field(name="🎉 `,giveaway`", value="Starts a Giveaway in the desired channel.", inline=False)
            embed.add_field(name="👮‍♀️👮‍♂️ `,jail <user>`", value="Jails a user.", inline=False)
            embed.add_field(name="🕊 `,release <user>`", value="Releases a user.", inline=False)
            embed.add_field(name="📊 `,polladd <question> <duration> <option1> <option2> [<option3> <option4> ...]`", value="Create a poll with multiple options.", inline=False)
            await interaction.response.edit_message(embed=embed)

        elif custom_id == "utility":
            embed = discord.Embed(
                title="🛠️ Utility Commands",
                description="Useful tools for your server:",
                color=0xC546FF
            )
            embed.add_field(name="❤️ `,love`", value="Sends a heartful message of love.", inline=False)
            embed.add_field(name="🧹 `,purge <number>`", value="Deletes a specified number of messages.", inline=False)
            embed.add_field(name="⏱ `,uptime`", value="Shows the bot’s uptime in minutes and seconds.", inline=False)
            embed.add_field(name="📊 `,serverinfo`", value="Displays information about the server.", inline=False)
            embed.add_field(name="🏓 `,ping`", value="Check the bot’s ping (latency).", inline=False)
            embed.add_field(name="👤 `,userinfo [@user]`", value="Displays information about the user (default is the author).", inline=False)
            embed.add_field(name="🎂 `,birthday [YYYY-MM-DD]`", value="Set and store your birthday (for future notifications).", inline=False)
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
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772170643013704/image.gif?ex=67795dba&is=67780c3a&hm=fd4db37e349fa7a247004321c99daec0fdeffbf520794a94ea9a00a0f4cb400f&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772186233245776/image.gif?ex=67795dbe&is=67780c3e&hm=1247fdc9caacb550d6a3510a64c3bf839d13f4091558a98b1ac0a3ccf5787c69&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772198585471057/image.gif?ex=67795dc1&is=67780c41&hm=1cd9857e79027166684629d64bba27fc4452acb1d2551770aea7d0d4b81c560e&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772209167827057/image.gif?ex=67795dc3&is=67780c43&hm=1325b127811e0384052855039ec5448f4ff2c2daed42612ffa06c11c5b9de97a&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772228977524776/image.gif?ex=67795dc8&is=67780c48&hm=23c34003c798f06369dfbb528314fa0c98ca3ced24ab3b03c7645f6009fb267c&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772239719006342/image.gif?ex=67795dcb&is=67780c4b&hm=e3863684668fc30b83841d352d19fa5168917a5899b14811387b7ecde1f86cdd&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772247654629467/image.gif?ex=67795dcc&is=67780c4c&hm=42da043b259401324a79134a90605f54e20bc9df210bbd18214694554807082e&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772258970861578/image.gif?ex=67795dcf&is=67780c4f&hm=ed792a940df9f23d399bd940914d4923933090de72f052718507a3a8aa9627e7&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772267410067517/image.gif?ex=67795dd1&is=67780c51&hm=20943cc26ffc8cf5fa278c025b24640d7b886ca1badf83ef78f2d9209fbdd81f&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772275479642132/image.gif?ex=67795dd3&is=67780c53&hm=64586fb94fa2331656e878bd06e537bac366690fbf882ae9a198cf37a18f9fa7&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772283012612157/image.gif?ex=67795dd5&is=67780c55&hm=dc98318f2a79175fea75918b42ee5d8cf967ccd5ce2a43d91722095b4001e58b&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772293393649784/image.gif?ex=67795dd7&is=67780c57&hm=21dad58e68e4fc09f6a18611870098bd177b3f7f25537da548f23be5fe1f502f&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772300972625940/image.gif?ex=67795dd9&is=67780c59&hm=4eadd2a48e8923bdb41dd56e1957eb98b6d21c96d42b4d989298e9c12ee1a866&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772310774972487/image.gif?ex=67795ddb&is=67780c5b&hm=de71e4cd3344d92007de476039fa14b814296b2330191ac285a40ebe0b8f1b13&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772318471389184/image.gif?ex=67795ddd&is=67780c5d&hm=07798268d444442b5acaff096e3ced8200804c0a830e18ac071c557665655b82&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772328789508176/image.gif?ex=67795de0&is=67780c60&hm=82452bf5541191733c5810be79aca07083205694f885ef083a0836668b696a58&",
                                "https://cdn.discordapp.com/attachments/1324770554187616347/1324772335517175880/image.gif?ex=67795de1&is=67780c61&hm=cde10f0b635eb1b50715c5b787449552875ffe8b119087917e37ec227d9a0ad1&"
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
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771891373801593/image.gif?ex=67795d77&is=67780bf7&hm=cb96e3d17e43c842ce951fa399e859b5ea528623e6ab2eb157e4b41df87a03cb&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771903755386911/image.gif?ex=67795d7a&is=67780bfa&hm=45de810d196a29536808b637fcd7472f14a66befc605be7696f5524f271caa4c&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771909597921351/image.gif?ex=67795d7c&is=67780bfc&hm=792ed0ce0c7f6bd3410c74ce9c7171a1ac34488fdcafc034abaa2dcba9465a33&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771915834982441/image.gif?ex=67795d7d&is=67780bfd&hm=f5ce04510198de99000c244f278f95c5e00cd9f9d3a6fd688de3dddbc02cd84a&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771929441308704/image.gif?ex=67795d81&is=67780c01&hm=a5bf530bfa56a1675e1ace2c92a5a377cdd2eda214bcd161c280f514c67f45ac&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771938689745078/image.gif?ex=67795d83&is=67780c03&hm=a9851f98a6225c0e6baa60a38390760e538500fd6e01236852273d0dd52b5f60&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771945052508160/image.gif?ex=67795d84&is=67780c04&hm=27b8e04ffe0ea1f92278302d4e72820ed3bff590b5d39fa6f143527320b17d18&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771953520672850/image.gif?ex=67795d86&is=67780c06&hm=a989e48839edd8888ae8cb5ffbff9c0bea9e733ce85e090372fe96103d46a336&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771963419230288/image.gif?ex=67795d89&is=67780c09&hm=bb4344e6386c22aa894b273440d0086742452cc1a0c4e52371f8adc83e4e93b2&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771971237675089/image.gif?ex=67795d8b&is=67780c0b&hm=b389b8b9f0d7f427f223b2111aadb1f44b41c3301a6ddab9f7e6baafa91a1dc4&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771976539017319/image.gif?ex=67795d8c&is=67780c0c&hm=4414080922f59a91b5967d57dbe647f6ccbe1f3f21b33e2a6dcb7d02cc6253ee&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771984839544864/image.gif?ex=67795d8e&is=67780c0e&hm=89c5bbc11292f3722598d1f2facaa8ebc7cdaece1ff714e273e2329ddfc6386a&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772000450871459/image.gif?ex=67795d91&is=67780c11&hm=48e903b9d6367a637579b9d0e66e1ec19481ce188b8ba778242175474da61da0&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772019925155944/image.gif?ex=67795d96&is=67780c16&hm=b4d2475b72f451621bb69488013732ee7efe76d7129b33f563ce005505fa89c9&"
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
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772507819180122/image.gif?ex=67795e0a&is=67780c8a&hm=fa170f3f50de030ea4bbdaf5264be8316a07654541a98ed4dea072ade3158bbe&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772513422512129/image.gif?ex=67795e0c&is=67780c8c&hm=dcb4df2828df0e3941fb6b0f797923b58cafe052cf85024571e5273a7c043dcc&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772530078220298/image.gif?ex=67795e10&is=67780c90&hm=019c4634030bf50e9090d24baa808c349b218a6aec7cbb89bef6e29b942d3d9f&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772541985980516/image.gif?ex=67795e13&is=67780c93&hm=cfba8199baf58c5e4b80622c6384685ec3847b96f2be7aefb81d6e1fcf310ea0&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772556972228628/image.gif?ex=67795e16&is=67780c96&hm=bac792f39170759e06d9511aea82e12bf7a93d0bfcaf5f01b94afb69a8ddfd60&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772562965626881/image.gif?ex=67795e18&is=67780c98&hm=8973cb089055e1ceb23ab7035593e62af35f7bbd415be074a9603be0a176adff&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772568061837382/image.gif?ex=67795e19&is=67780c99&hm=0a90ec4a1dc01daf95c73ad1d55e72a2df4d3be9f11c8c6dac5c0d4230bc2cbc&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772574348968028/image.gif?ex=67795e1a&is=67780c9a&hm=7e65b42b8603745019ce056bffce8b8b7d93529cb713b16131caeab58f94d769&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772583438028820/image.gif?ex=67795e1c&is=67780c9c&hm=940ebe3fd4b58114bea1c7109764b720ab7f1b90338b3ad574d9e2306484a5ce&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772599372320768/image.gif?ex=67795e20&is=67780ca0&hm=149ce92a1b00c56a44e5c571da0e798cd3080e6992521c40a9f29c1392559c76&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772619270225970/image.gif?ex=67795e25&is=67780ca5&hm=559866cc439f073a4d0bbaf2ab27b1ebdf7c7aeee0b157231e9091677af7db95&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772626169725071/image.gif?ex=67795e27&is=67780ca7&hm=d381c9220abb9f2e4d3d132aaeed88b06dafaae947afa9d15d66eb650590727d&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772644737777735/image.gif?ex=67795e2b&is=67780cab&hm=fcc8e6f273d5e8a5e125ff0c14a59f48b97459cabdaa5c10454bb03862e3d55f&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772660475068539/image.gif?ex=67795e2f&is=67780caf&hm=2f927ab44c5e580e83d81920bad55d3b50f648f39997814f1368cf3fc0a9b960&"
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324772670776020992/image.gif?ex=67795e31&is=67780cb1&hm=90a66e965ff5dad06d4a8d72a080d588637835ad2e4ac8f636e780c7edf59d25&"
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
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771426766688388/image.gif?ex=67795d09&is=67780b89&hm=3d328d60eef10d1533067ad858b816902398f053ac95d66e886ea35f461f92d4&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771433834086422/image.gif?ex=67795d0a&is=67780b8a&hm=b855a242df3fa6c8aa2eef26d29283b85199ae8b2d3e64de365c26c4aea4dcca&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771442688131133/image.gif?ex=67795d0d&is=67780b8d&hm=4211fa279bd6c68158b50022a3a0a93d3d2f7d61cdf1b6a8b2343e8b354faee8&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771450519031948/image.gif?ex=67795d0e&is=67780b8e&hm=17013a12e963441352302a6f526188a05b56ee9bb8e6ef1c6f873b46c567711e&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771459851223083/image.gif?ex=67795d11&is=67780b91&hm=b797097f1ee28989c6fc38c3719adb5eb4b8567de3c133617eaf168bffef85e0&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771477941387324/image.gif?ex=67795d15&is=67780b95&hm=6905ea14ea2b5ddb20ded1b000602c4faf48ec2eebc5027c8714cb22d31760e9&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771487093100554/image.gif?ex=67795d17&is=67780b97&hm=c45bf15f8bfcadc38f45aa523ab3f9beab50ea2cb851a644e6c4f301083310bc&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771497432055808/image.gif?ex=67795d1a&is=67780b9a&hm=81ef14368ca83e5ea503fa4e40b2f80e23c7a68c91a46e809fce883d57470466&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771522795147420/image.gif?ex=67795d20&is=67780ba0&hm=d3c08b4ff26ba19c582b2da8f86ec75538daa5e8eb88830d7334f7076db85d47&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771537324081222/image.gif?ex=67795d23&is=67780ba3&hm=7f1b1dc0829d518b46cd314a83ebfb87704bec793715b4bfb7a2574415442fb4&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771545314365490/image.gif?ex=67795d25&is=67780ba5&hm=1b4b97402f29c36c7f6641c758fe2cd16a9b162e4f1471cf3b59ae9b7ffa029e&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771559130534013/image.gif?ex=67795d28&is=67780ba8&hm=f8d9c49d917e70d3106975429b892dda7cf4d5366fdb7b58a9a476c6e1952cd4&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771567342850048/image.gif?ex=67795d2a&is=67780baa&hm=84cd9cebb5455cda3b5d2c719bf05bf10cb73c526014ebe592609ad0d0ef6a04&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771574137487490/image.gif?ex=67795d2c&is=67780bac&hm=3811377a5677ff6b6e08440ddb9ea44ddebd8a24a0d59d324400e90b019ec7ef&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771581624582244/image.gif?ex=67795d2e&is=67780bae&hm=6b4beb06ccb7cff35fad1b8a79618b872b599848fac22a924e169d40d75c99a0&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771587798601738/image.gif?ex=67795d2f&is=67780baf&hm=aea83491710e75791a7df2c4528f49e7ae570a9f7bc76727608b5f9ad4f435db&",
            "https://cdn.discordapp.com/attachments/1324770554187616347/1324771595943677963/image.gif?ex=67795d31&is=67780bb1&hm=abe6f3ba95f91af73af08eed8bcc5463cef9fdc98f4b6c56bc370ac2f7b8e107&"
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
        
# Run the bot
bot.run(DISCORD_TOKEN)
