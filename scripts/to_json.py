# The file that converts all plain text lyrics into JSON.
# The first line of the text file identifies the artist, the second one identifies the title of the opus, and the
# remaining text represents the lyrics.

import os
import json


def read_lines_from_file(filename):
    return open(filename).readlines()


def get_clean_lines_from_file(filename):
    lines = read_lines_from_file(filename)
    # Remove leading and tailing whitespace.
    lines = [line.strip() for line in lines]
    # Remove empty lines.
    lines = [line for line in lines if line != '']
    return lines


def json_from_file(filename):
    prepared_lines = get_clean_lines_from_file(filename)
    if len(prepared_lines) < 3:
        raise Exception("Only got {} prepared lines from {}. Expected at least 3.".format(len(prepared_lines), filename))
    return {"artist": prepared_lines[0], "title": prepared_lines[1], "lyrics": prepared_lines[2:]}


if __name__ == '__main__':
    json_list = []
    sources_folder = os.path.join(os.path.dirname(__file__), "sources")
    for file in os.listdir(sources_folder):
        json_list.append(json_from_file(os.path.join(sources_folder, file)))
    with open('lyrics.json', 'w') as output:
        json.dump({"songs": json_list}, output)
