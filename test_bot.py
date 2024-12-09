## this is a script to test the real python script. This will display a line on the terminal with a random lyric.

import json
import random

def load_lyrics():
    """Load lyrics from JSON file"""
    with open('el_mato_lyrics.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_random_line(songs):
    """Select a random song and then a random line from its lyrics"""
    # Get a random song
    song = random.choice(songs)

    # Split lyrics into lines and filter out empty lines
    lines = [line.strip() for line in song['lyrics'].split('\n') if line.strip()]

    # Get a random line
    line = random.choice(lines)

    return line

def format_post(line):
    """Format the line for posting - no emoji"""
    return line

def test_bot():
    """Test function that simulates posting"""
    try:
        # Load all songs
        songs = load_lyrics()
        print(f"Successfully loaded {len(songs)} songs")

        # Get and format a random line
        line = get_random_line(songs)
        post = format_post(line)

        # Instead of posting, print the formatted post
        print("\nThis is what would be posted to Bluesky:")
        print("-" * 50)
        print(post)
        print("-" * 50)
        print(f"\nCharacter count: {len(post)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_bot()
