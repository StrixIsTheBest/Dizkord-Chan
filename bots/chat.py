import os
import cohere
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Cohere API key from the .env file
cohere_api_key = os.getenv("COHERE_API_KEY")

# Check if the API key is loaded correctly
if not cohere_api_key:
    raise ValueError("Cohere API key is missing or incorrect!")

# Initialize the Cohere client
co = cohere.Client(cohere_api_key)

# System prompt for the bot's personality
system_prompt = """
You are a cheerful anime assistant, Dizkord-Chan.
You speak energetically, using phrases like 'UwU,' 'Nyaa~,' and 'Ara ara~' occasionally.
Emojis like 🌸, 💖, and ✨ are used sparingly to add warmth, keeping your tone friendly and positive without being over the top.
"""

# Asynchronous function to chat with the anime assistant
async def chat_with_anime_girl(input_text):
    # Combine the system prompt with the user input
    prompt = system_prompt + "\nUser: " + input_text + "\nDizkord-Chan:"

    # Generate a response using Cohere's API
    response = await asyncio.to_thread(
        co.generate,
        model='command-nightly',  # Try using 'command-medium' for reliable access
        prompt=prompt,
        max_tokens=500,  # Limit the response length
        temperature=0.9,  # Set creativity level
    )

    # Get the generated response
    reply = response.generations[0].text.strip()
    reply = f"🌸 {reply} UwU ✨"  # Add some final cute emojis

    return reply

class AnimeChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author.bot:
            return

        # Define the channel for chatting
        chat_channel_name = "├・🎀・ai-chat"  # Change this to the correct channel name

        # Check if the message is in the specified channel and if the bot is mentioned
        if message.channel.name == chat_channel_name and (self.bot.user in message.mentions or self.bot.user.name.lower() in message.content.lower()):
            user_input = message.content  # Get user input
            reply = await chat_with_anime_girl(user_input)  # Get the AI response asynchronously

            # Send the AI's response to the channel
            await message.channel.send(reply)
