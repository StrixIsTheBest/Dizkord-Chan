from flask import Flask
from threading import Thread
import requests
import asyncio
import time

# Set up Flask Web server
app = Flask('')

@app.route('/')  # This is the health check endpoint
def home():
    return "Dizkord-chan is online! UwU"

def run():
    app.run(host="0.0.0.0", port=8080)

async def keep_alive():
    t = Thread(target=run)  # Start the web server in a separate thread
    t.start()

# This task will ping your bot's web server periodically to keep it alive
async def ping_bot():
    while True:
        try:
            response = requests.get('https://dizkord-chan.onrender.com')  # Replace with your actual Render URL
            if response.status_code == 200:
                print("Ping successful. Bot is alive!")
            else:
                print(f"Error with status code: {response.status_code}")
        except Exception as e:
            print(f"Error during ping: {e}")
        await asyncio.sleep(300)  # Wait for 5 minutes before the next ping

# Run the Flask web server and periodic ping tasks together
async def start_ping_task():
    keep_alive()  # Start the Flask web server
    await ping_bot()  # Start the ping task

# Run the bot and web server in the same event loop
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_ping_task())  # Start pinging in the background
    loop.run_forever()  # Keep the bot and server running