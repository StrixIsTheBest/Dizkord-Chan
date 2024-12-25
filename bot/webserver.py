from flask import Flask  # Make sure to install the Flask package
from threading import Thread

app = Flask('')

@app.route('/')  # The "main" page of the website. The root.
def home():
    return "Webserver OK, Discord Bot OK"  # Message shown when the web server is accessed

def run():
    # Run the Flask app with threading enabled for efficient request handling
    app.run(host="0.0.0.0", port=8080, threaded=True)

def keep_alive():
    # Start the web server in a separate thread to avoid blocking
    t = Thread(target=run)
    t.daemon = True  # Ensures the thread is killed when the main program exits
    t.start()
