#!/usr/bin/env python
import ConfigParser
import os
import re
import shutil

CONFIG_FILE = 'eztv-extractor.cfg'
FILENAME_PATTERN = re.compile(r'^(?P<name>.+)[Ss](?P<season>\d+)[Ee](?P<episode>\d+)')
FILENAME_PATTERN2 = re.compile(r'^(?P<name>.+).(?P<season>\d+)x(?P<episode>\d+)')


def move_files(src_dir, dst_dir):
    """Moves files from a source directory to a destination directory."""
    for f in os.listdir(src_dir):
        try:
            name, season, episode = FILENAME_PATTERN.search(f).groups()
        except AttributeError:
            try:
                name, season, episode = FILENAME_PATTERN2.search(f).groups()
            except AttributeError:
                print "Cannot parse", f
                pass

        name = name.replace('.', ' ').replace('_', ' ').strip().title()

        dir_path = os.path.join(dst_dir, name, 'Season %02d' % int(season))
        full_path = os.path.join(dir_path, f)
        source_path = os.path.join(src_dir, f)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path, 0777)

        if not os.path.exists(full_path):
            shutil.move(source_path, full_path)
            os.symlink(full_path, source_path)


def main():
    """Main"""
    for section in config.sections():
        if not section.lower() == 'configuration':
            continue

        complete = config.get(section, 'complete_dir')
        ready = config.get(section, 'ready_dir')
        complete_dir = os.path.expanduser(complete)
        move_to = os.path.expanduser(ready)

        move_files(complete_dir, move_to)


if __name__ == "__main__":
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)
    main()
