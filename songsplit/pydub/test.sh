#!/bin/bash

youtube-dl "$1" \
    -f 'bestaudio[ext=m4a]' \
    --audio-format mp3 \
    --write-description \
    -x \
    -o '%(title)s.%(ext)s'

python split_mp3.py
