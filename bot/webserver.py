from flask import Flask # Make sure to install the flask package
from threading import Thread

app = Flask('')

@app.route('/') # The "main" page of the website. The root.
def home():
  return "Webserver OK, Discord Bot OK"

def run():
  app.run(host="0.0.0.0", port=8080)

def keep_alive():
  t = Thread(target=run) # We use threading so the function doesn't block the discord client from running.
  t.start()

# It's pretty simple, create a simple webserver using Flask so replit gives you a URL to use, when starting the webserver use threading so it doesn't block the rest of the code from running.
