#!/usr/bin/env python3
import json
import random
import time
import logging
import os

# Set up logging for testing
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only console output for testing
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
        with open('posted_lines_test.json', 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()
    except Exception as e:
        logging.error(f"Error loading posted lines: {e}")
        return set()

def save_posted_lines(posted_lines):
    """Save posted lines to file"""
    try:
        with open('posted_lines_test.json', 'w', encoding='utf-8') as f:
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
                lines = [line.strip() for line in song['lyrics'] if line.strip()]
            else:
                lines = [line.strip() for line in song['lyrics'].split('\n') if line.strip()]

            # Get a random line
            line = random.choice(lines)
            
            # Check if we've posted this line before
            normalized = normalize_line(line)
            if normalized not in posted_lines:
                return line, normalized, song['title']
            
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
        return line, normalized, song['title']
    except Exception as e:
        logging.error(f"Error getting fallback line: {e}")
        return None, None, None

def post_to_bluesky(text, client=None):
    """Simulate posting to Bluesky (no actual post)"""
    if client is None:
        # Test mode - just print
        print(text)
        logging.info(f"Would post: {text[:50]}...")
    else:
        # Real mode - actual post (same as main script)
        try:
            client.send_post(text)
            logging.info(f"Successfully posted: {text[:50]}...")
        except Exception as e:
            logging.error(f"Error posting to Bluesky: {e}")

def test_bot_multiple_posts(num_posts=5):
    """Test the bot with multiple simulated posts"""
    print(f"🧪 Testing bot with {num_posts} simulated posts")
    print("=" * 80)
    
    try:
        # Load songs and posted lines
        songs = load_lyrics()
        if not songs:
            raise Exception("Failed to load songs")
        
        posted_lines = load_posted_lines()
        
        print(f"🎵 Loaded {len(songs)} songs")
        print(f"📊 Previously posted lines: {len(posted_lines)}")
        
        # Calculate total available lines
        total_lines = 0
        for song in songs:
            if isinstance(song['lyrics'], list):
                total_lines += len([line for line in song['lyrics'] if line.strip()])
            else:
                total_lines += len([line for line in song['lyrics'].split('\n') if line.strip()])
        
        remaining_lines = total_lines - len(posted_lines)
        print(f"📈 Remaining unique lines: {remaining_lines}/{total_lines}")
        print()

        # Test multiple posts
        for i in range(num_posts):
            # Get unique random line
            result = get_random_line(songs, posted_lines)
            if result and result[0]:
                line, normalized, song_title = result
                post_to_bluesky(line)  # No client = test mode
                
                # Mark this line as posted
                posted_lines.add(normalized)
                save_posted_lines(posted_lines)
            else:
                print("❌ Could not find a unique line to post")
            
            # Small delay between tests
            time.sleep(0.5)
    
    except Exception as e:
        logging.error(f"Test error: {e}")

def show_statistics():
    """Show detailed statistics about the lyrics database"""
    songs = load_lyrics()
    posted_lines = load_posted_lines()
    
    if not songs:
        print("❌ Could not load songs")
        return
    
    print("📊 LYRICS DATABASE STATISTICS")
    print("=" * 40)
    
    total_songs = len(songs)
    total_lines = 0
    song_line_counts = []
    
    for song in songs:
        if isinstance(song['lyrics'], list):
            lines = [line for line in song['lyrics'] if line.strip()]
        else:
            lines = [line for line in song['lyrics'].split('\n') if line.strip()]
        
        line_count = len(lines)
        total_lines += line_count
        song_line_counts.append((song['title'], line_count))
    
    # Sort by line count
    song_line_counts.sort(key=lambda x: x[1], reverse=True)
    
    print(f"🎵 Total songs: {total_songs}")
    print(f"📝 Total lines: {total_lines}")
    print(f"📊 Posted lines: {len(posted_lines)}")
    print(f"🆕 Remaining unique lines: {total_lines - len(posted_lines)}")
    print(f"📈 Average lines per song: {total_lines / total_songs:.1f}")
    
    print(f"\n🔝 TOP 10 SONGS BY LINE COUNT:")
    for i, (title, count) in enumerate(song_line_counts[:10], 1):
        print(f"{i:2d}. {title}: {count} lines")
    
    print(f"\n🔽 BOTTOM 5 SONGS BY LINE COUNT:")
    for i, (title, count) in enumerate(song_line_counts[-5:], len(song_line_counts)-4):
        print(f"{i:2d}. {title}: {count} lines")

def main():
    print("🤖 El Mato Bot - Local Test Mode")
    print("=" * 50)
    print("1. Test single post")
    print("2. Test multiple posts (5)")
    print("3. Test many posts (20)")
    print("4. Show statistics")
    print("5. Clear test post history")
    print("6. Exit")
    
    while True:
        choice = input("\nChoose an option (1-6): ").strip()
        
        if choice == '1':
            test_bot_multiple_posts(1)
        elif choice == '2':
            test_bot_multiple_posts(5)
        elif choice == '3':
            test_bot_multiple_posts(20)
        elif choice == '4':
            show_statistics()
        elif choice == '5':
            try:
                os.remove('posted_lines_test.json')
                print("✅ Cleared test post history")
            except FileNotFoundError:
                print("ℹ️  No test history to clear")
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please choose 1-6.")

if __name__ == "__main__":
    main()