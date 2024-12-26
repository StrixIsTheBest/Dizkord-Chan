from flask import Flask
from threading import Thread
import requests
import time

# Set up Flask Web server
app = Flask('')

@app.route('/')  # This is the health check endpoint
def home():
    return "Webserver OK, Discord Bot OK"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)  # Start the web server in a separate thread
    t.start()

# This task will ping your bot's web server periodically to keep it alive
def ping_bot():
    try:
        response = requests.get('https://dizkord-chan.onrender.com')  # Replace with your actual Render URL
        if response.status_code == 200:
            print("Ping successful. Bot is alive!")
        else:
            print(f"Error with status code: {response.status_code}")
    except Exception as e:
        print(f"Error during ping: {e}")

# You can use a task scheduler like a cron job or a Python loop
if __name__ == "__main__":
    keep_alive()  # Start the Flask web server
    while True:
        ping_bot()  # Ping every 5 minutes
        time.sleep(300)  # Wait for 5 minutes before next ping
