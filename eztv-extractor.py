#!/usr/bin/env python
# http://www.stabellini.net/rtorrent-howto.txt
import ConfigParser
import re
import os
import md5

import requests
from pyquery import PyQuery as pq

CONFIG_FILE = 'eztv-extractor.cfg'
EZTV_PATTERN = re.compile(R'S(?P<season>\d+)E(?P<episode>\d+) (?P<data>.+)-(?P<group>[\d\w]+) \((?P<size>\d+.\d+) (?P<sunit>\w+)\)$')
EZTV_PATTERN1 = re.compile(r'(?P<season>\d+)x(?P<episode>\d+) \((?P<data>.+)-(?P<group>[\d\w]+)\) .+ \((?P<size>\d+.\d+) (?P<sunit>\w+)\)$')
MAGNET_PATTERN = re.compile(r'magnet:\?xt=urn:btih:(?P<hash>[A-Z0-9]+)&')
TORRENT_DOWNLOAD_DIR = None

class DownloadError(Exception):
    pass

def create_magnet_file(magnet_url):
    magnet_file = 'meta-%s.torrent' % MAGNET_PATTERN.search(magnet_url).group('hash')
    with open(os.path.join(TORRENT_WATCH_DIR, magnet_file), 'w') as f:
        bencoded_magnet = 'd10:magnet-uri%(length)s:%(uri)se' % {'length': len(magnet_url),
                                                                 'uri': magnet_url}
        f.write(bencoded_magnet)

def fetch_torrent(torrent_url):
    _, torrent_file = torrent_url.rsplit('/', 1)
    r = requests.get(torrent_url)

    if r.status_code != 200:
        raise DownloadError

    if r.content[0:3] != 'd8:':
        raise DownloadError

    filename = os.path.join(TORRENT_WATCH_DIR, '%s.torrent' % md5(torrent_file).hexdigest())
    try:
        with open(filename, 'wb') as f:
            f.write(r.content)
    except IOError:
        raise DownloadError

def eztv_scrapper(url, last_season, last_episode, magnet=False,
                  match=None, notmatch=None):
    max_season = last_season
    max_episode = last_episode

    r = requests.get(url)
    d = pq(r.content)

    items = d(".forum_thread_post")

    i = -4
    while True:
        i += 4
        if i == len(items):
            break

        try:
            season, episode, data, group, size, sunit =\
                    EZTV_PATTERN.search(items[i+1].find('a').values()[1]).groups()
        except AttributeError:
            try:
                season, episode, data, group, size, sunit =\
                        EZTV_PATTERN1.search(items[i+1].find('a').values()[1]).groups()
            except:
                continue

        season = int(season)
        episode = int(episode)
        size = float(size)

        if max_season == season:
            max_episode = max(episode, max_episode)
        elif max_season <= season:
            max_season = season
            max_episode = episode

        if ((season < last_season) or
            (season == last_season and episode <= last_episode) or
            (match and match not in data) or
            (notmatch and notmatch in data)):
            continue

        if magnet:
            magnet_url = items[i+2].find_class('magnet')[0].values()[0]
            create_magnet_file(magnet_url)
        else:
            k = 1
            while True:
                torrent_url = items[i+2].find_class('download_%d' % k)
                if len(torrent_url) == 0:
                    # We didn't manage to find a link :(
                    break
                torrent_url = torrent_url[0].values()[0]
                try:
                    fetch_torrent(torrent_url)
                    break
                except DownloadError:
                    k += 1

    return max_season, max_episode

def update_config(section, season, episode):
    config.set(section, 'season', str(season))
    config.set(section, 'episode', str(episode))
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)


def main():
    for section in config.sections():
        if section.lower() == 'configuration':
            continue

        eztv_uri = config.get(section, 'eztv_uri')
        last_season = int(config.get(section, 'season'))
        last_episode = int(config.get(section, 'episode'))
        match = config.get(section, 'match')
        notmatch = config.get(section, 'notmatch')
        magnet = config.get(section, 'magnet') == True
        season, episode = eztv_scrapper(eztv_uri, last_season, last_episode,
                                        magnet, match, notmatch)
        update_config(section, season, episode)

if __name__ == '__main__':
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)
    try:
        TORRENT_WATCH_DIR = config.get('Configuration', 'download_dir')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        TORRENT_WATCH_DIR = '.'
    main()
