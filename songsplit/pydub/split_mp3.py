#!/usr/bin/python
# encoding: utf-8

"""
Utility for splitting up MP3 files by timestamp.

MAC OS X ONLY!
REQUIRES ffmpeg + pydub!
"""


import re
import sys

from pydub import AudioSegment


MSMS_REGEX = r"((\d+)m)?((\d+)s)?((\d+)ms)?"


def int_or_0(s):
    return int(s) if s else 0


def parse_time(time_string):
    try:
        return int(time_string)
    except ValueError:
        try:
            msms = re.match(MSMS_REGEX, time_string).groups()[1::2]
            (m, s, ms) = map(int_or_0, msms)
            return m * 60 * 1000 + s * 1000 + ms
        except AttributeError:
            raise


def parse_row(row):
    try:
        (s, e, n) = row.split(',', 2)
        return [parse_time(s), parse_time(e), n]
    except ValueError:
        (s, n) = row.split(',', 1)
        return [parse_time(s), None, n]


def split_times(times_string):
    times = [parse_row(row) for row in times_string.strip().splitlines()]

    # correct single timestamps
    for i in xrange(len(times)):

        if times[i][1] is None:
            try:
                # get end time from next track's start time
                times[i][1] = times[i + 1][0]
            except IndexError:
                # we're the last track
                times[i][1] = -1

    return times


def split(name, times):
    """Split given filename by given times."""
    print "[ ] loading {}...".format(name)
    song = AudioSegment.from_mp3(name)

    for (s, e, old) in times:
        old = old + '.mp3'
        new = old.replace('/', ':')  # <--- this is for forward-slashes to work on Macs
        print "[ ] writing '{}' --> '{}'...".format(old, new)
        sub = song[s:e]
        sub.export("{}".format(new), format='mp3')


def run(mp3name, timesname):
    with open(timesname) as timesfile:
        times_string = timesfile.read().strip()
        times = split_times(times_string)

    split(mp3name, times)


def main():
    """Entry point."""
    mp3name = sys.argv[1]
    timesname = sys.argv[2]

    run(mp3name, timesname)


if __name__ == '__main__':
    main()
