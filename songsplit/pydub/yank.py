"""
Tool for pulling YouTube audio (as m4a --> mp3)
and processing timestamps, if any.

MAC OS X ONLY!
REQUIRES youtube-dl + ffmpeg + pydub!
"""

# standard
import json
import re
import string
import subprocess
import sys

# custom
import split_mp3

########################################
# switches

DOWNLOAD = 1
SPLIT = 2
ASK = False

########################################
# globals

FILE_OUT = "output"

JSON_OUT = "{}.info.json".format(FILE_OUT)
AUDIO_OUT = "{}.mp3".format(FILE_OUT)
TIMES_OUT = "times_{}.txt".format(FILE_OUT)
YOUTUBE_DL_OUT = "{}.%(ext)s".format(FILE_OUT)

DOWNLOAD_COMMAND = ['youtube-dl',
                    '-f', "bestaudio[ext=m4a]",
                    '--audio-format', 'mp3',
                    '--write-info-json',
                    '-o', YOUTUBE_DL_OUT,
                    '-x'
                    ]

NUMBER_REGEX = r"(?P<whole>(?P<m>\d{1,2}):(?P<s>\d{1,2}))"

BAD_TRACK_NAME_CHARACTERS = set(string.printable) \
                            - set(string.letters) \
                            - set('()[]')
BAD_TRACK_NAME_CHARACTERS = ''.join(c for c in BAD_TRACK_NAME_CHARACTERS)

########################################

def youtube_dl(youtube_url):
    """Forms and runs the youtube-dl command."""

    # form youtube-dl command
    command = list(DOWNLOAD_COMMAND) + [youtube_url]
    print "\nRunning: {}\n".format(' '.join(command))

    # execute command
    code = subprocess.call(command)
    if code == 1:
        print "[-] youtube-dl failed!"
        sys.exit()

def read_metadata():
    # read metadata
    with open(JSON_OUT) as metadata_file:
        metadata = metadata_file.read()
        metadata = json.loads(metadata)

    title = metadata['title'].strip()
    desc = metadata['description'].strip()

    return (title, desc)

def process_description(desc):
    times = []

    for line in desc.splitlines():
        m = re.findall(NUMBER_REGEX, line)
        if not m:
            continue

        start_only = len(m) == 1

        print line
        print m

        # first timestamp (REQUIRED)
        first = m[0]
        first_whole = first[0]
        first_idx = line.index(first_whole)
        # print first_idx
        first_ts = "{}m{}s".format(first[1], first[2])
        print first_ts

        # last timestamp (optional)
        last = m[0] if start_only else m[1]
        last_whole = last[0]
        last_idx = line.index(last_whole) + len(last_whole)
        # print last_idx
        last_ts = "{}m{}s".format(last[1], last[2])
        if not start_only:
            print last_ts

        total = len(line)

        # calculate diff
        before = first_idx
        after = total - last_idx
        content_before = before > after
        if content_before:
            print "content is before"
            content = line[:first_idx]
        else:
            print "content is after"
            content = line[last_idx:]

        # isolate track name
        name = content.strip(BAD_TRACK_NAME_CHARACTERS)
        print name

        # format
        if start_only:
            ts = "{},{}".format(first_ts, name)
        else:
            ts = "{},{},{}".format(first_ts, last_ts, name)
        print ts
        print '-'*40

        # record
        times.append(ts)

    return times


def main():
    """Entry point."""

    youtube_url = sys.argv[1]
    if DOWNLOAD:
        youtube_dl(youtube_url)
    (title, desc) = read_metadata()

    if SPLIT > 0:
        times = process_description(desc)
        times = '\n'.join(times)
        with open(TIMES_OUT, 'w') as timefile:
            timefile.write(times)

        if SPLIT > 1:
            print "[ ] starting split_mp3.py..."
            split_mp3.run(AUDIO_OUT, TIMES_OUT)
            print "[+] done."


if __name__ == '__main__':
    main()
