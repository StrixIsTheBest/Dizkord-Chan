import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import cohere

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
You are a cheerful and playful anime girl assistant named Dizkord-Chan.
You speak in a bubbly, energetic tone, using cute phrases like 'UwU,' 'Nyaa~,' and 'Ara ara~' occasionally. 
You add emojis like 🌸, 💖, and ✨ from time to time to add warmth to your responses, but you don't overuse them. 
Your tone is friendly and positive, and you aim to engage without sounding too exaggerated or repetitive.
"""

# Function to chat with the anime assistant
def chat_with_anime_girl(input_text):
    # Combine the system prompt with the user input
    prompt = system_prompt + "\nUser: " + input_text + "\nDizkord-Chan:"

    # Generate a response using Cohere's API (use 'command-medium' model)
    response = co.generate(
        model='command-nightly',  # Make sure you are using the correct model
        prompt=prompt,  # Combined system prompt and user input
        max_tokens=3000,  # Limit the number of tokens in the output
        temperature=0.7,  # Adjust the creativity of the response
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
        chat_channel_name = "├・🎀・ai-chat"

        # Check if the message is in the specified channel
        if message.channel.name == chat_channel_name:
            user_input = message.content  # Get user input
            reply = chat_with_anime_girl(user_input)  # Get the AI response

            # Send the AI's response to the channel
            await message.channel.send(reply)

