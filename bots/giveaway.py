import asyncio
import random
import discord
from discord.ext import commands

async def setup(bot):
    @bot.command(name="giveaway")
    async def giveaway(ctx):
        """
        Creates a giveaway event.
        """
        await ctx.send("🎉 Let's start a giveaway! 🎉\n\nReply with the details:")

        questions = [
            "What is the **prize** for the giveaway?",
            "Which **channel** should the giveaway take place in? (Mention the channel like #channel-name)",
            "How long should the giveaway last? (Format: e.g., `10s` for 10 seconds, `5m` for 5 minutes, `1h` for 1 hour)"
        ]

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        for question in questions:
            await ctx.send(question)
            try:
                msg = await bot.wait_for("message", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("⏳ You took too long to respond. Giveaway creation canceled.")
                return
            answers.append(msg.content)

        prize = answers[0]
        try:
            channel = await commands.TextChannelConverter().convert(ctx, answers[1])
        except commands.BadArgument:
            await ctx.send("❌ Invalid channel. Giveaway creation canceled.")
            return

        time = answers[2]
        try:
            time_seconds = parse_duration(time)
        except ValueError:
            await ctx.send("❌ Invalid time format. Giveaway creation canceled.")
            return

        # Send giveaway announcement
        giveaway_message = await channel.send(
            f"🎉 **GIVEAWAY TIME!** 🎉\n\n**Prize:** {prize}\nReact with 🎉 to enter!\n"
            f"**Ends in:** {time}.\n\nHosted by: {ctx.author.mention}"
        )
        await giveaway_message.add_reaction("🎉")

        await asyncio.sleep(time_seconds)

        # Fetch message again to get reactions
        giveaway_message = await channel.fetch_message(giveaway_message.id)
        reaction = discord.utils.get(giveaway_message.reactions, emoji="🎉")

        if reaction and reaction.count > 1:  # Reaction count includes the bot's reaction
            users = [user async for user in reaction.users() if not user.bot]
            winner = random.choice(users)
            await channel.send(f"🎊 Congratulations {winner.mention}! You won the **{prize}**! 🎊")
        else:
            await channel.send("❌ No participants in the giveaway. Better luck next time!")

    def parse_duration(duration: str) -> int:
        """
        Parse a duration string (e.g., '10s', '5m', '1h') into seconds.
        """
        units = {"s": 1, "m": 60, "h": 3600}
        try:
            return int(duration[:-1]) * units[duration[-1]]
        except (ValueError, KeyError):
            raise ValueError("Invalid duration format. Use '10s', '5m', or '1h'.")
