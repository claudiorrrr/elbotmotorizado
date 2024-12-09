import requests
from bs4 import BeautifulSoup
import time
import json

def get_song_urls(base_url):
    """
    Get list of song URLs from the main artist page
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all song rows with the correct class
        song_rows = soup.find_all('li', class_='songList-table-row --song isVisible')
        songs_data = []

        for row in song_rows:
            # Extract data from the row
            data_id = row.get('data-id')
            data_name = row.get('data-name')

            # Get the link from within the row
            link = row.find('a', class_='songList-table-songName')
            if link and link.get('href'):
                full_url = f"https://www.letras.com{link['href']}"

                song_info = {
                    'title': data_name,
                    'id': data_id,
                    'url': full_url
                }
                songs_data.append(song_info)

        return songs_data
    except Exception as e:
        print(f"Error fetching song list: {e}")
        return []

def get_lyrics(url, headers):
    """
    Get lyrics from a song page
    """
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the lyrics div
        lyrics_div = soup.find('div', class_='lyric')
        if lyrics_div:
            # Get all paragraphs and join them with newlines
            # Remove script tags first if they exist
            for script in lyrics_div.find_all('script'):
                script.decompose()

            lyrics = lyrics_div.get_text(separator='\n').strip()
            return lyrics
        return None
    except Exception as e:
        print(f"Error fetching lyrics: {e}")
        return None

def process_songs(songs_data):
    """
    Process each song and get its lyrics
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    processed_data = []

    for song in songs_data:
        try:
            print(f"Processing: {song['title']}")
            time.sleep(2)  # Respectful delay between requests

            lyrics = get_lyrics(song['url'], headers)

            if lyrics:
                song_info = {
                    'title': song['title'],
                    'id': song['id'],
                    'url': song['url'],
                    'lyrics': lyrics
                }
                processed_data.append(song_info)
                print(f"Successfully got lyrics for: {song['title']}")
            else:
                print(f"No lyrics found for: {song['title']}")

        except Exception as e:
            print(f"Error processing {song['title']}: {e}")

    return processed_data

def save_to_json(data, filename='el_mato_lyrics.json'):
    """
    Save the collected data to a JSON file
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, ensure_ascii=False, indent=2, fp=f)

def main():
    base_url = "https://www.letras.com/el-mato-un-policia-motorizado/"
    print("Fetching song list...")
    songs_data = get_song_urls(base_url)
    print(f"Found {len(songs_data)} songs")

    print("Processing songs and fetching lyrics...")
    processed_data = process_songs(songs_data)

    print("Saving to JSON file...")
    save_to_json(processed_data)
    print(f"Successfully processed {len(processed_data)} songs")

if __name__ == "__main__":
    main()

