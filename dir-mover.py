#!/usr/bin/env python
import ConfigParser
import os
import re
import shutil

COMPLETE_DIR = os.path.expanduser('~/deluge/complete')
MOVE_TO = os.path.expanduser('~/deluge/ready')
FILENAME_PATTERN = re.compile(r'^(?P<name>.+)S(?P<season>\d+)E(?P<episode>\d+)')

def main():
    for f in os.listdir(COMPLETE_DIR):
        name, season, episode = FILENAME_PATTERN.search(f).groups()
        name = name.replace('.', ' ').strip()
        path = os.path.join(MOVE_TO, name, 'Season %02d' % int(season))
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(os.path.join(path, f)):
            shutil.copy(os.path.join(COMPLETE_DIR, f), path)

if __name__ == "__main__":
    main()
