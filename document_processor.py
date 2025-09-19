#!/usr/bin/env python3


import db_setup as db
import embedding

import glob
import itertools
import os
import psycopg
import re
import sys

SUPPORTED_EXTENSIONS = ['.org']
MAX_LENGTH_IN_WORDS = 250


def enchunk(file_handle):
    chunk = []
    min_paragraph_length = 50
    for line in file_handle.readlines():
        for word in line.split():
            if len(chunk) == MAX_LENGTH_IN_WORDS:
                yield " ".join(chunk)
                chunk = [word]
            elif re.search('^\\s*\n', line) and len(chunk) > min_paragraph_length:
                yield " ".join(chunk)
                chunk = []
            elif any(word.endswith(punct) for punct in ('.', '?', '!')) and len(chunk) >= min_paragraph_length:
                yield " ".join(chunk + [word])
                chunk = []
            elif any(word.endswith(punct) for punct in (',', ':', '---', '—', ';')) and len(chunk) >= (MAX_LENGTH_IN_WORDS - min_paragraph_length):
                yield " ".join(chunk + [word])
                chunk = []
            else:
                chunk.append(word)
    if len(chunk):
        yield " ".join(chunk)

def persist_chunk(chunk, filename, cursor):
    cursor.execute(
        """
        INSERT INTO document_chunks
        (document_id, document_title, text, embedding)
        VALUES
        (%s, %s, %s, %s)
        """,
        (filename,
         re.sub('\\d+-', '', os.path.splitext(os.path.basename(filename))[0]),
         chunk,
         embedding.get_embedding(chunk))
    )

def process_file(filename, cursor):
    with open(filename) as f:
        for chunk in enchunk(f):
            print(f"Persisting {filename}")
            persist_chunk(chunk, filename, cursor)

# Returns list of (dilename, doc) tuples
# doc has metadata.word_count, pages
def process_all_input_files(dir_name):
    globbed_files = [glob.glob(os.path.join(dir_name, '*' + ext)) for ext in SUPPORTED_EXTENSIONS]
    file_count = sum(map(len, globbed_files))
    files = itertools.chain(*globbed_files)
    i = 1
    db_config = db.config()
    for f in files:
        with psycopg.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                print(f"Processing {i}/{file_count}")
                process_file(f, cursor)
                i += 1

def print_help():
    print(f"""USAGE:

        python #{sys.argv[0]} [<input file directory> | --help]

    Stores all of the input files in the database.

    Supported formats: {SUPPORTED_EXTENSIONS}
    """)


if __name__ == "__main__":
    cmd_or_dir = sys.argv[1]
    if cmd_or_dir.lower() == "--help":
        print_help()
    elif not os.path.isdir(cmd_or_dir):
        print("Invalid directory")
        print_help()
    else:
        process_all_input_files(cmd_or_dir)
