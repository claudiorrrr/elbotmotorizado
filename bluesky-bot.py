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

def load_posted_lines():
    """Load previously posted lines from file"""
    try:
        with open('posted_lines.json', 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()
    except Exception as e:
        logging.error(f"Error loading posted lines: {e}")
        return set()

def save_posted_lines(posted_lines):
    """Save posted lines to file"""
    try:
        with open('posted_lines.json', 'w', encoding='utf-8') as f:
            json.dump(list(posted_lines), f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving posted lines: {e}")

def normalize_line(line):
    """Normalize line for comparison"""
    return ' '.join(line.strip().split()).lower()

def get_random_line(songs, posted_lines, max_attempts=100):
    """Select a random song and then a random line that hasn't been posted"""
    attempts = 0
    
    while attempts < max_attempts:
        try:
            # Get a random song
            song = random.choice(songs)

            # Handle both string and list format for lyrics
            if isinstance(song['lyrics'], list):
                # If lyrics is already a list
                lines = [line.strip() for line in song['lyrics'] if line.strip()]
            else:
                # If lyrics is a string (our format)
                lines = [line.strip() for line in song['lyrics'].split('\n') if line.strip()]

            # Get a random line
            line = random.choice(lines)
            
            # Check if we've posted this line before
            normalized = normalize_line(line)
            if normalized not in posted_lines:
                return line, normalized
            
            attempts += 1
            
        except Exception as e:
            logging.error(f"Error getting random line: {e}")
            attempts += 1
    
    # If no unique line found, clear history and try again
    logging.warning("No unique lines found, clearing post history")
    posted_lines.clear()
    save_posted_lines(posted_lines)
    
    try:
        song = random.choice(songs)
        if isinstance(song['lyrics'], list):
            lines = [line.strip() for line in song['lyrics'] if line.strip()]
        else:
            lines = [line.strip() for line in song['lyrics'].split('\n') if line.strip()]
        line = random.choice(lines)
        normalized = normalize_line(line)
        return line, normalized
    except Exception as e:
        logging.error(f"Error getting fallback line: {e}")
        return None, None

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

        # Load songs and posted lines
        songs = load_lyrics()
        if not songs:
            raise Exception("Failed to load songs")
        
        posted_lines = load_posted_lines()

        # Get unique random line
        result = get_random_line(songs, posted_lines)
        if result and result[0]:
            line, normalized = result
            post_to_bluesky(line, client)
            
            # Mark this line as posted
            posted_lines.add(normalized)
            save_posted_lines(posted_lines)
            
            logging.info(f"Added line to posted history. Total posted: {len(posted_lines)}")
        else:
            logging.error("Could not find a line to post")

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