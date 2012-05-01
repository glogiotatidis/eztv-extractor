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

        dir_path = os.path.join(MOVE_TO, name, 'Season %02d' % int(season))
        full_path = os.path.join(dir_path, f)
        source_path = os.path.join(COMPLETE_DIR, f)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path, 0777)

        if not os.path.exists(full_path):
            shutil.move(source_path, full_path)
            os.symlink(full_path, source_path)

if __name__ == "__main__":
    main()
