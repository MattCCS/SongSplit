"""
Utility for splitting up MP3 files by timestamp.

MAC OS X ONLY!
REQUIRES ffmpeg + pydub!
"""


import argparse
import pathlib
import re

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


def split_times(timestamps):
    times = [parse_row(row) for row in timestamps.strip().splitlines()]

    # correct single timestamps
    for i in range(len(times)):

        if times[i][1] is None:
            try:
                # get end time from next track's start time
                times[i][1] = times[i + 1][0]
            except IndexError:
                # we're the last track
                times[i][1] = -1

    return times


def split(filename, timeranges, folder=None):
    """Split given filename by given times."""
    print(f"[ ] Loading {repr(filename)}...")
    fmt = pathlib.Path(filename).suffix.lstrip('.')
    song = AudioSegment.from_file(filename, fmt)

    for (s, e, title) in timeranges:
        title = title.replace('/', ':')  # NOTE: this escapes forward-slashes in macOS
        outfile_temp = pathlib.Path(title + '.mp4')
        outfile = pathlib.Path(str(outfile_temp).rsplit('.', 1)[0] + '.m4a')

        print(f"[+] Writing {str(outfile)}...")
        sub = song[s:e]
        sub.export(outfile_temp, format='mp4')
        if folder:
            outfile_temp.rename(folder / outfile)
        else:
            outfile_temp.rename(outfile)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("timestamps", nargs="+", type=str)
    parser.add_argument("-f", "--folder", nargs="?", type=str)
    return parser.parse_args()


def main():
    args = parse_args()

    folder = pathlib.Path(args.folder.replace('/', ':'))
    if folder:
        folder.mkdir(exist_ok=True)

    timeranges = split_times('\n'.join(args.timestamps))
    split(args.filename, timeranges, folder=folder)


if __name__ == '__main__':
    main()
