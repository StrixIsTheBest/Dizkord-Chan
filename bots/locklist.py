import discord
from discord.ext import commands
from datetime import datetime
import json

locklist = {}

async def update_locklist_channel(ctx):
    """Update the locklist channel with the latest list of locked characters."""
    locklist_channel = discord.utils.get(ctx.guild.text_channels, name="locklist")
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

def setup_locklist(bot: commands.Bot):
    @bot.command(name="lock")
    async def lock(ctx, *characters: str):
        """Command to lock characters."""
        if ctx.author.id in locklist and len(locklist[ctx.author.id]) >= 5:
            await ctx.send("💖 Oops! You can only lock in **5 characters**! Please unlock some before locking new ones. ✨")
            return

        already_locked = [char for char in characters if any(char in chars for chars in locklist.values())]
        if already_locked:
            await ctx.send(f"🚫 These characters are already locked by someone else: {', '.join(already_locked)}. Please choose different ones! 💕")
            return

        if ctx.author.id not in locklist:
            locklist[ctx.author.id] = []

        locklist[ctx.author.id].extend(characters)
        locklist[ctx.author.id] = locklist[ctx.author.id][:5]

        await update_locklist_channel(ctx)

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

        await update_locklist_channel(ctx)

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
