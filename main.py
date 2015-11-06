import logging
import sqlite3

import guesser.guesses
import guesser.loader
import guesser.songs


def print_song_artist_and_title(song):
    print("That was", song.title, "by", song.artist + ".")


def get_affirmative_answers():
    return "1", "y", "yes", "yeah", "yup", "sure", "obviously"


def get_negative_answers():
    return "0", "n", "no", "nope", "nah"


def get_all_answers():
    return get_affirmative_answers() + get_negative_answers()


def parse_user_affirmative_or_negative(string):
    """
    Parses a string attempting to determine whether it is an affirmative or negative answer. Raises a ValueError if it
    cannot be parsed.
    :param string: the answer
    :return: whether or not the string is an affirmative answer
    """
    if string.lower() in get_affirmative_answers():
        return True
    elif string.lower() in get_negative_answers():
        return False
    else:
        raise ValueError("string '{}' does not match any registered answer.".format(string))


def check_if_user_wants_to_play():
    while True:
        answer = input("Do you want to play again? ")
        try:
            return parse_user_affirmative_or_negative(answer)
        except ValueError:
            print("I don't understand that. But I understand all of these:")
            print(" ", "Affirmatives:", " ".join(get_affirmative_answers()))
            print(" ", "Negatives:", " ".join(get_negative_answers()))


def ask_for_guesses():
    artist = input("Guess the song's artist: ")
    title = input("Guess the song's title: ")
    print()
    return guesser.guesses.Guess(artist, title)


def print_score(score):
    print("Your score so far:", score)


def initialize_logger():
    logging.basicConfig(filename="log.log", format="%(asctime)-15s %(levelname)s %(message)s", level=logging.DEBUG)


def acquisition_loop(random_song):
    """
    The loop that allows the player to buy more lines.
    :return: how many lines the player bought
    """
    revealed = 2  # Keep track of how many lines the user has revealed.
    shifted_lyrics = guesser.songs.ShiftedLyrics(random_song.lyrics)
    while True:
        print_lyrics(shifted_lyrics, revealed)
        acquisition = input("Acquire this many lines: ")
        try:
            acquisition = int(acquisition)
        except ValueError:
            print("Enter a number.")
            continue
        if acquisition <= 0:
            break
        else:
            not_yet_acquired = shifted_lyrics.get_line_count() - revealed
            if acquisition > not_yet_acquired:
                print("{0} is enough to buy the rest of the song. You only spent {0} points.".format(not_yet_acquired))
            revealed += min(acquisition, not_yet_acquired)
            if revealed == shifted_lyrics.get_line_count():
                break
    return revealed - 2


def print_lyrics(shifted_lyrics, unlocked):
    """
    Print the first unlocked lines from a ShiftedLyrics object.
    """
    print()
    for line in shifted_lyrics.get(unlocked):
        print("   ", line)
    print()


def update_database(connection, song, bought, got_artist_right, got_title_right, score_delta):
    columns = "(artist, title, bought, got_artist_right, got_title_right, score_delta)"
    insert = "insert into playing_data {} values (?, ?, ?, ?, ?, ?)".format(columns)
    cursor = connection.cursor()
    cursor.execute(insert, (song.artist, song.title, bought, got_artist_right, got_title_right, score_delta))


def mainloop():
    connection = sqlite3.connect('data.sqlite3')
    cursor = connection.cursor()
    # artist | title | bought | got_artist_right | got_title_right | score_diff
    cursor.execute("""create table if not exists playing_data (id integer primary key,
                                                               artist text not null,
                                                               title text not null,
                                                               bought integer not null,
                                                               got_artist_right integer not null,
                                                               got_title_right integer not null,
                                                               score_delta integer not null)""")
    score = cursor.execute("select sum(score_delta) from playing_data").fetchone()[0]
    if score is None:
        score = 0
    while True:
        random_song = guesser.songs.Song(**guesser.loader.get_random_song())
        bought = acquisition_loop(random_song)
        user_guesses = ask_for_guesses()
        got_artist_right = user_guesses.check_artist(random_song)
        got_title_right = user_guesses.check_title(random_song)
        score_delta = -bought
        if got_title_right and got_artist_right:
            print("You got everything right.")
            score_delta += 5
        elif got_artist_right:
            print("You only got the artist right.")
            score_delta += 2
        elif got_title_right:
            print("You only got the title right.")
            score_delta += 2
        else:
            print("You are wrong.")
            score_delta -= 1
        update_database(connection, random_song, bought, got_artist_right, got_title_right, score_delta)
        print_song_artist_and_title(random_song)
        score += score_delta
        print_score(score)
        if not check_if_user_wants_to_play():
            connection.commit()
            break


if __name__ == '__main__':
    initialize_logger()
    mainloop()
