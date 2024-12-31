import discord
from discord.ext import commands
import json
import os

# Set the channel name where the locklist will be stored
LOCKLIST_CHANNEL_NAME = "╰・🎀・lock-list"

# Initialize locklist as an empty dictionary
locklist = {}

async def get_locklist_channel(ctx):
    """Get the locklist channel by name."""
    return discord.utils.get(ctx.guild.text_channels, name=LOCKLIST_CHANNEL_NAME)

async def update_locklist_channel(ctx):
    """Update the locklist channel with the latest list of locked characters."""
    locklist_channel = await get_locklist_channel(ctx)
    if locklist_channel:
        embed = discord.Embed(
            title="🌸 **Locked Characters List** 🌸",
            description="Here are the characters that have been locked by members! ✨",
            color=0xC546FF
        )
        
        for user_id, characters in locklist.items():
            user = ctx.guild.get_member(user_id)
            embed.add_field(name=f"**{user.display_name}:**", value=", ".join(characters), inline=False)
        
        await locklist_channel.send(embed=embed)

async def save_locklist_to_channel(ctx):
    """Save the current locklist data to the locklist channel."""
    locklist_channel = await get_locklist_channel(ctx)
    if locklist_channel:
        # Serialize locklist to a JSON string
        locklist_data = json.dumps(locklist, indent=4)
        
        # Send or edit a message with the locklist data
        # Check if a locklist message already exists; otherwise, create one
        async for message in locklist_channel.history(limit=1):
            if message.author == ctx.guild.me and message.content.startswith("```json"):
                # If message already exists, edit it
                await message.edit(content=f"```json\n{locklist_data}\n```")
                return
        
        # If no existing locklist message, send a new one
        await locklist_channel.send(f"```json\n{locklist_data}\n```")

async def load_locklist_from_channel(ctx):
    """Load the locklist from the locklist channel after bot restart."""
    locklist_channel = await get_locklist_channel(ctx)
    if locklist_channel:
        async for message in locklist_channel.history(limit=5):
            if message.author == ctx.guild.me and message.content.startswith("```json"):
                try:
                    # Attempt to parse the JSON content of the message
                    return json.loads(message.content.strip("```json\n").strip())
                except json.JSONDecodeError:
                    pass
    return {}

def setup_locklist(bot: commands.Bot):
    @bot.command(name="lock")
    async def lock(ctx, *characters: str):
        """Command to lock characters."""
        # Check if the user already locked in 5 characters
        if ctx.author.id in locklist and len(locklist[ctx.author.id]) >= 5:
            await ctx.send("💖 Oops! You can only lock in **5 characters**! Please unlock some before locking new ones. ✨")
            return

        # Check if any of the characters are already locked by someone else
        already_locked = [char for char in characters if any(char in chars for user_id, chars in locklist.items() if user_id != ctx.author.id)]
        
        if already_locked:
            await ctx.send(f"🚫 These characters are already locked by someone else: {', '.join(already_locked)}. Please choose different ones! 💕")
            return

        # Add the new characters to the user's locklist
        if ctx.author.id not in locklist:
            locklist[ctx.author.id] = []

        locklist[ctx.author.id].extend(characters)
        locklist[ctx.author.id] = locklist[ctx.author.id][:5]  # Limit to 5 characters

        # Save the updated locklist to the locklist channel
        await save_locklist_to_channel(ctx)

        await ctx.send(f"🎉 Success! You've locked in these characters: {', '.join(characters)}! 🥳")

    @bot.command(name="unlock")
    async def unlock(ctx, *characters: str):
        """Command to unlock characters (only available to users with admin/mod permissions)."""
        if not any(permission in [p.name.lower() for p in ctx.author.permissions_in(ctx.channel)] for permission in ["administrator", "manage_roles", "manage_messages"]):
            await ctx.send("🚫 You do not have permission to unlock characters! Only admins or mods can unlock characters. 💕")
            return
        
        if ctx.author.id not in locklist or not locklist[ctx.author.id]:
            await ctx.send("😢 You haven't locked any characters yet! Please lock in some characters first. 💖")
            return

        for char in characters:
            if char in locklist[ctx.author.id]:
                locklist[ctx.author.id].remove(char)

        # Save the updated locklist to the locklist channel
        await save_locklist_to_channel(ctx)

        await ctx.send(f"🎊 Successfully unlocked characters: {', '.join(characters)}! ✨")

    @bot.command(name="view_locklist")
    async def view_locklist(ctx):
        """View the current locklist of characters."""
        embed = discord.Embed(
            title="🌸 **Current Locklist** 🌸",
            description="Here are all the characters locked by our members! ✨",
            color=0xC546FF
        )
        if not locklist:
            embed.add_field(name="No locked characters", value="It seems no one has locked any characters yet! 💖", inline=False)
        else:
            for user_id, characters in locklist.items():
                user = ctx.guild.get_member(user_id)
                embed.add_field(name=f"**{user.display_name}:**", value=", ".join(characters), inline=False)

        await ctx.send(embed=embed)

    # Load locklist from channel when the bot starts
    @bot.event
    async def on_ready():
        print(f"{bot.user} has connected to Discord!")
        # Assuming the context is passed here
        ctx = await bot.get_context(bot.user)
        loaded_locklist = await load_locklist_from_channel(ctx)
        if loaded_locklist:
            global locklist
            locklist = loaded_locklist
            print("Locklist loaded from the channel.")
