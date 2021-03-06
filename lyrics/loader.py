import json
import logging
import os
import random
import lyrics.converter

json_file = None
json_file_is_up_to_date = False


def get_lyrics_json_path():
    """Returns the path of lyrics.json."""
    cur_dir = os.path.dirname(__file__)
    lyrics_json = os.path.join(cur_dir, "lyrics.json")
    return lyrics_json


def make_lyrics_file():
    global json_file_is_up_to_date
    lyrics.converter.make_lyrics_file(get_lyrics_json_path())
    json_file_is_up_to_date = False


def ensure_the_lyrics_file_exists():
    path = get_lyrics_json_path()
    if os.path.exists(path) and os.path.isfile(path):
        return
    else:
        logging.info("Lyrics file does not exist. Triggering remake.")
        make_lyrics_file()


def ensure_the_lyrics_file_is_up_to_date():
    json_modification_time = os.stat(get_lyrics_json_path()).st_mtime
    sources_modification_time = os.stat(lyrics.converter.get_sources_path()).st_mtime
    if sources_modification_time > json_modification_time:
        logging.info("Lyrics file is outdated. Triggering remake.")
        make_lyrics_file()


def ensure_the_lyrics_file_exists_and_is_up_to_date():
    ensure_the_lyrics_file_exists()
    ensure_the_lyrics_file_is_up_to_date()


def get_all_songs():
    """Retrieves all songs as dictionaries containing artist, title, and lyrics."""
    global json_file, json_file_is_up_to_date
    ensure_the_lyrics_file_exists_and_is_up_to_date()
    if not json_file_is_up_to_date:
        json_file = json.load(open(get_lyrics_json_path()))
        json_file_is_up_to_date = True
    return json_file["songs"]


def get_random_song():
    """Retrieves any song as a dictionary containing artist, title, and lyrics."""
    song_list = get_all_songs()
    song_data = random.choice(song_list)
    return song_data
