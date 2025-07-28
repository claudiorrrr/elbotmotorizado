import json
import random
import logging
from time import sleep

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_test.log'),
        logging.StreamHandler()
    ]
)

def load_lyrics():
    """Load lyrics from JSON file"""
    try:
        with open('el_mato_lyrics_formatted.json', 'r', encoding='utf-8') as f:
            songs = json.load(f)
            # Process songs to ensure lyrics are in the correct format
            processed_songs = []
            for song in songs:
                lyrics = song['lyrics']
                # Convert lyrics to list if it's a string
                if isinstance(lyrics, str):
                    lyrics = [lyrics]
                # Clean up lyrics
                clean_lyrics = []
                for line in lyrics:
                    # Split multi-line strings
                    if isinstance(line, str):
                        parts = [l.strip() for l in line.split('\n') if l.strip()]
                        clean_lyrics.extend(parts)
                song['lyrics'] = clean_lyrics
                if clean_lyrics:  # Only add songs with valid lyrics
                    processed_songs.append(song)
            return processed_songs
    except Exception as e:
        logging.error(f"Error loading lyrics file: {e}")
        return None

def get_random_line(songs):
    """Select a random song and then a random line from its lyrics"""
    try:
        # Get a random song
        song = random.choice(songs)

        # Get a random line
        if song['lyrics']:
            line = random.choice(song['lyrics'])
            return f"{line} [de '{song['title']}']"
        return None

    except Exception as e:
        logging.error(f"Error getting random line: {e}")
        return None

def simulate_post(text):
    """Simulate posting by printing to terminal"""
    try:
        print("\n=== SIMULATED POST ===")
        print(f"Content: {text}")
        print("===================\n")
        logging.info(f"Successfully simulated post: {text[:50]}...")
    except Exception as e:
        logging.error(f"Error simulating post: {e}")

def main():
    try:
        # Load songs
        songs = load_lyrics()
        if not songs:
            raise Exception("Failed to load songs")

        # Get and simulate posting random line
        line = get_random_line(songs)
        if line:
            simulate_post(line)
        else:
            logging.error("Failed to get random line")

    except Exception as e:
        logging.error(f"Main function error: {e}")

if __name__ == "__main__":
    print("Starting test bot - Press Ctrl+C to stop")
    while True:
        try:
            main()
            # Wait for 5 seconds before next post
            logging.info("Waiting 5 seconds until next post...")
            sleep(5)
        except KeyboardInterrupt:
            print("\nBot stopped by user")
            break
        except Exception as e:
            logging.error(f"Critical error: {e}")
            logging.info("Waiting 5 seconds before retry...")
            sleep(5)
