import json
import random
from atproto import Client
import time
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

def load_lyrics():
    """Load lyrics from JSON file"""
    try:
        with open('el_mato_lyrics.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading lyrics file: {e}")
        return None

def get_random_line(songs):
    """Select a random song and then a random line from its lyrics"""
    try:
        # Get a random song
        song = random.choice(songs)

        # Split lyrics into lines and filter out empty lines
        lines = [line.strip() for line in song['lyrics'].split('\n') if line.strip()]

        # Get a random line
        return random.choice(lines)
    except Exception as e:
        logging.error(f"Error getting random line: {e}")
        return None

def post_to_bluesky(text, client):
    """Post to Bluesky"""
    try:
        client.send_post(text)
        logging.info(f"Successfully posted: {text[:50]}...")
    except Exception as e:
        logging.error(f"Error posting to Bluesky: {e}")

def main():
    # Get credentials from environment variables
    bluesky_handle = os.getenv('BLUESKY_HANDLE')
    bluesky_password = os.getenv('BLUESKY_PASSWORD')

    if not bluesky_handle or not bluesky_password:
        logging.error("Missing Bluesky credentials in .env file")
        return

    try:
        # Initialize the Bluesky client
        client = Client()
        client.login(bluesky_handle, bluesky_password)
        logging.info("Successfully logged into Bluesky")

        # Load songs
        songs = load_lyrics()
        if not songs:
            raise Exception("Failed to load songs")

        # Get and post random line
        line = get_random_line(songs)
        if line:
            post_to_bluesky(line, client)

    except Exception as e:
        logging.error(f"Main function error: {e}")

if __name__ == "__main__":
    while True:
        try:
            main()
            # Wait for 3 hours before next post
            logging.info("Waiting 3 hours until next post...")
            time.sleep(10800)  # 3 hours in seconds
        except Exception as e:
            logging.error(f"Critical error: {e}")
            logging.info("Waiting 5 minutes before retry...")
            time.sleep(300)  # 5 minutes retry delay
