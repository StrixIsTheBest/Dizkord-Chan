import discord
import requests
from discord.ext import tasks
import pytz
from datetime import datetime
import asyncio

# Function to fetch a random quote from the Anime-chan API
def get_random_quote():
    response = requests.get("https://animechan.io/api/v1/quotes/random")

    try:
        # Parse the JSON response
        data = response.json()
        
        # Check if the response contains the necessary data
        if data.get("status") == "success" and "data" in data:
            quote_data = data["data"]
            
            quote = quote_data.get("content", "No quote available")
            author = quote_data["character"].get("name", "Unknown character")
            anime = quote_data["anime"].get("name", "Unknown anime")

            return {
                "quote": quote,
                "author": author,
                "anime": anime
            }
        else:
            # Log the response if it's not as expected for debugging purposes
            print(f"Unexpected API response: {data}")
            return {
                "quote": "No quote available",
                "author": "Unknown character",
                "anime": "Unknown anime"
            }
    except Exception as e:
        # Log any error that occurs during the API call
        print(f"Error fetching quote: {e}")
        return {
            "quote": "No quote available",
            "author": "Unknown character",
            "anime": "Unknown anime"
        }

# Function to send the quote to a Discord channel
async def send_quote_of_the_day(bot, channel_id):
    quote_data = get_random_quote()
    quote = quote_data["quote"]
    author = quote_data["author"]
    anime = quote_data["anime"]

    embed = discord.Embed(
        title="✨ Quote of the Day ✨",
        description=f"\"{quote}\"\n- {author} from *{anime}*",
        color=0xC546FF
    )

    embed.set_footer(text="Stay inspired! 💖 - Dizkord-Chan")

    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(embed=embed)
        await channel.send(f"||@everyone||")  # Send a spoiler-ping to everyone
    else:
        print(f"Channel with ID {channel_id} not found.")

# Task to send the quote at 12:00 AM Dubai time
@tasks.loop(seconds=60)  # Run every minute to check for the time
async def quote_of_the_day(bot, channel_id):
    dubai_tz = pytz.timezone('Asia/Dubai')
    now = datetime.now(dubai_tz)

    # Check if it's 12:00 AM Dubai time
    if now.hour == 0 and now.minute == 0:
        await send_quote_of_the_day(bot, channel_id)

# Function to start the task
def start_quote_task(bot, channel_id):
    if not quote_of_the_day.is_running():
        quote_of_the_day.start(bot, channel_id)
    else:
        print("Quote of the day task is already running.")
