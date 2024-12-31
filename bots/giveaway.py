import asyncio
import random
import discord
from discord.ext import commands
from datetime import datetime, timedelta

def setup_giveaway(bot: commands.Bot):
    @bot.command(name="giveaway")
    @commands.has_permissions(manage_messages=True)
    async def giveaway(ctx):
        """
        Creates a giveaway event with Dizkord-Chan's aesthetic.
        """
        embed = discord.Embed(
            title="🌸 Dizkord-Chan Giveaway Setup 🌸",
            description="Let's create a dreamy giveaway together! Answer the following questions 💖",
            color=0xC546FF
        )
        embed.set_footer(text="Giveaway Wizard ~ Powered by Dizkord-Chan ✨")
        await ctx.send(embed=embed)

        questions = [
            "🎁 What is the **prize** for the giveaway? (e.g., Cute Plushie, Nitro Boost)",
            "📢 In which **channel** should the giveaway take place? (e.g., #general-chat)",
            "⏳ How long should the giveaway last? (e.g., `10s`, `5m`, `1h`)"
        ]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for question in questions:
            embed = discord.Embed(
                title="✨ Dizkord-Chan Giveaway Question ✨",
                description=question,
                color=0xC546FF
            )
            embed.set_footer(text="Please reply within 60 seconds 💌")
            await ctx.send(embed=embed)
            
            try:
                msg = await bot.wait_for("message", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                cancel_embed = discord.Embed(
                    title="⏳ Giveaway Canceled",
                    description="You took too long to respond! Please try again later 💔",
                    color=0xC546FF
                )
                await ctx.send(embed=cancel_embed)
                return
            answers.append(msg.content)

        prize = answers[0]
        try:
            channel = await commands.TextChannelConverter().convert(ctx, answers[1])
        except commands.BadArgument:
            error_embed = discord.Embed(
                title="❌ Invalid Channel",
                description="The channel you mentioned doesn't exist! Giveaway creation canceled.",
                color=0xC546FF
            )
            await ctx.send(embed=error_embed)
            return

        time = answers[2]
        try:
            time_seconds = parse_duration(time)
        except ValueError:
            error_embed = discord.Embed(
                title="❌ Invalid Duration",
                description="The duration format is incorrect! Use `10s`, `5m`, or `1h`. Giveaway canceled.",
                color=0xC546FF
            )
            await ctx.send(embed=error_embed)
            return

        # Calculate end time
        end_time = datetime.utcnow() + timedelta(seconds=time_seconds)
        unix_timestamp = int(end_time.timestamp())

        # Send the giveaway announcement
        giveaway_embed = discord.Embed(
            title="🎉 Giveaway Time! 🎉",
            description=(f"🌟 **Prize:** {prize}\n"
                         f"💬 React with 🎉 to enter!\n"
                         f"⏳ **Ends in:** <t:{unix_timestamp}:R>\n\n"
                         f"✨ Hosted by: {ctx.author.mention}"),
            color=0xC546FF
        )
        giveaway_embed.set_footer(text="Good luck, everyone! 🍀 Powered by Dizkord-Chan")
        giveaway_message = await channel.send(embed=giveaway_embed)
        await giveaway_message.add_reaction("🎉")

        # Wait for the giveaway to end
        await asyncio.sleep(time_seconds)

        # Fetch the message again to get reactions
        giveaway_message = await channel.fetch_message(giveaway_message.id)
        reaction = discord.utils.get(giveaway_message.reactions, emoji="🎉")

        if reaction and reaction.count > 1:
            users = [user async for user in reaction.users() if not user.bot]
            winner = random.choice(users)
            winner_embed = discord.Embed(
                title="🎊 Giveaway Winner! 🎊",
                description=f"🌸 Congratulations {winner.mention}! You won **{prize}**! 🌸",
                color=0xC546FF
            )
            winner_embed.set_footer(text="Thank you for participating! 💖")
            await channel.send(embed=winner_embed)
        else:
            no_winner_embed = discord.Embed(
                title="❌ No Participants",
                description="It seems no one joined the giveaway 😢. Better luck next time!",
                color=0xC546FF
            )
            await channel.send(embed=no_winner_embed)

    @giveaway.error
    async def giveaway_error(ctx, error):
        """
        Handle errors for the giveaway command.
        """
        if isinstance(error, commands.MissingPermissions):
            error_embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You need the **Manage Messages** permission to use this command.",
                color=0xC546FF
            )
            await ctx.send(embed=error_embed)

    def parse_duration(duration: str) -> int:
        """
        Parse a duration string (e.g., '10s', '5m', '1h') into seconds.
        """
        units = {"s": 1, "m": 60, "h": 3600}
        try:
            return int(duration[:-1]) * units[duration[-1]]
        except (ValueError, KeyError):
            raise ValueError("Invalid duration format. Use '10s', '5m', or '1h'.")
