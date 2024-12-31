import asyncio
import discord
from discord.ext import commands
from datetime import datetime, timedelta

def setup_poll(bot: commands.Bot):
    @bot.command(name="polladd")
    async def polladd(ctx, question: str, duration: str, *options):
        """
        Creates a kawaii poll with a time limit and permissions check.
        """
        # Permission Check
        if not ctx.author.guild_permissions.manage_messages:
            error_embed = discord.Embed(
                title="❌ Insufficient Permissions",
                description="You need the **Manage Messages** permission to create a poll! 🌸",
                color=0xC546FF
            )
            await ctx.send(embed=error_embed)
            return

        # Validate options
        if len(options) < 2:
            error_embed = discord.Embed(
                title="❌ Not Enough Options",
                description="Please provide at least **two options** for the poll 💡.",
                color=0xC546FF
            )
            await ctx.send(embed=error_embed)
            return

        if len(options) > 10:
            error_embed = discord.Embed(
                title="❌ Too Many Options",
                description="You can provide a maximum of **10 options** for the poll.",
                color=0xC546FF
            )
            await ctx.send(embed=error_embed)
            return

        # Parse duration
        try:
            time_seconds = parse_duration(duration)
        except ValueError:
            error_embed = discord.Embed(
                title="❌ Invalid Duration",
                description="The duration format is incorrect! Use `10s`, `5m`, or `1h`. Poll creation canceled.",
                color=0xC546FF
            )
            await ctx.send(embed=error_embed)
            return

        # Calculate the poll's end time as Unix timestamp
        end_time = datetime.utcnow() + timedelta(seconds=time_seconds)
        unix_timestamp = int(end_time.timestamp())

        # Create poll
        embed = discord.Embed(
            title="🌸 Dizkord-Chan Poll Time! 🌸",
            description=f"**{question}**\n\nReact below to vote! 💖\n\n" +
                        "\n".join([f"{i+1}️⃣ {option}" for i, option in enumerate(options)]),
            color=0xC546FF
        )
        
        embed.add_field(name="⏳ **Poll Info:**", value=f"Poll ends in <t:{unix_timestamp}:R>! Powered by Dizkord-Chan ✨", inline=False)
        poll_message = await ctx.send(embed=embed)

        # Add reactions for options
        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for i in range(len(options)):
            await poll_message.add_reaction(reactions[i])

        # Wait for the poll to end
        await asyncio.sleep(time_seconds)

        # Fetch the message again to get updated reactions
        poll_message = await ctx.channel.fetch_message(poll_message.id)
        reaction_counts = [(reactions[i], poll_message.reactions[i].count - 1) for i in range(len(options))]

        # Determine the winner(s)
        max_votes = max(reaction_counts, key=lambda x: x[1])[1]
        winners = [options[i] for i, count in enumerate(reaction_counts) if count[1] == max_votes]

        if max_votes > 0:
            winner_embed = discord.Embed(
                title="🎉 Poll Results! 🎉",
                description=(f"The results are in for **{question}**:\n\n" +
                             "\n".join([f"{reactions[i]} **{options[i]}** - {reaction_counts[i][1]} votes"
                                        for i in range(len(options))]) +
                             f"\n\n🌸 Winner(s): {', '.join(winners)} 🌸"),
                color=0xC546FF
            )
            winner_embed.set_footer(text="Thank you for voting! 💖 Powered by Dizkord-Chan ✨")
            await ctx.send(embed=winner_embed)
        else:
            no_votes_embed = discord.Embed(
                title="❌ No Votes Cast",
                description="It seems no one voted in the poll 😢. Better luck next time!",
                color=0xC546FF
            )
            await ctx.send(embed=no_votes_embed)

    def parse_duration(duration: str) -> int:
        """
        Parse a duration string (e.g., '10s', '5m', '1h') into seconds.
        """
        units = {"s": 1, "m": 60, "h": 3600}
        try:
            return int(duration[:-1]) * units[duration[-1]]
        except (ValueError, KeyError):
            raise ValueError("Invalid duration format. Use '10s', '5m', or '1h'.")
