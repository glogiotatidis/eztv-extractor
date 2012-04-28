#!/usr/bin/env python
# http://www.stabellini.net/rtorrent-howto.txt
import ConfigParser
import re
import os
from urllib import quote
from hashlib import md5

import requests
from pyquery import PyQuery as pq

CONFIG_FILE = 'sss.cfg'
EZTV_URL = ('https://ezrss.it/search/index.php?'
            'show_name=%(name)s&show_name_exact=true'
            '&date=&quality=&release_group=&mode=rss')
EZTV_PATTERN = re.compile(r'S(?P<season>\d+)E(?P<episode>\d+) (?P<data>.+)-(?P<group>[\d\w]+) \((?P<size>\d+.\d+) (?P<sunit>\w+)\)$')
MAGNET_PATTERN = re.compile(r'magnet:\?xt=urn:btih:(?P<hash>[A-Z0-9]+)&')
TORRENT_WATCH_DIR = './deluge/watch/'

def create_magnet_file(magnet_url):
    magnet_file = 'meta-%s.torrent' % MAGNET_PATTERN.search(magnet_url).group('hash')
    with open(os.path.join(TORRENT_WATCH_DIR, magnet_file), 'w') as f:
        bencoded_magnet = 'd10:magnet-uri%(length)s:%(uri)se' % {'length': len(magnet_url),
                                                                 'uri': magnet_url}
        f.write(bencoded_magnet)

def fetch_torrent(torrent_url):
    _, torrent_file = torrent_url.rsplit('/', 1)
    with open(os.path.join(TORRENT_WATCH_DIR, torrent_file), 'w') as f:
        r = requests.get(torrent_url)
        f.write(r.content)

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
            continue

        season = int(season)
        episode = int(episode)
        size = float(size)

        if max_season <= season:
            max_season = season
            max_episode = max(max_episode, episode)

        if ((season < last_season) or
            (season == last_season and episode <= last_episode) or
            (match and match not in data) or
            (notmatch and notmatch in data)):
            continue

        print "foo", magnet

        if magnet:
            magnet_url = items[i+2].find_class('magnet')[0].values()[0]
            create_magnet_file(magnet_url)
        else:
            torrent_url = items[i+2].find_class('download_1')[0].values()[0]
            fetch_torrent(torrent_url)

    return max_season, max_episode

def update_config(section, season, episode):
    config.set(section, 'season', str(season))
    config.set(section, 'episode', str(episode))
    with open(CONFIG_FILE, 'w') as f:
        config.write(f)


def main():
    for section in config.sections():
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
    main()
