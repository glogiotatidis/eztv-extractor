import ConfigParser
import re
import requests
from pyquery import PyQuery as pq
import transmissionrpc

CONFIG_FILE = 'eztv-extractor.cfg'
REGEX = re.compile('.+ ((S(\d{2})E(\d{2}))|((\d{1,2})x(\d{1,2}))) (.+)')


def eztv_scrapper(url, current_season, current_episode, match, notmatch, tc=None):
    response = requests.get(url)
    dd = pq(response.content)

    for link in reversed(dd('a.epinfo')):
        title = link.attrib['title']
        try:
            matches = REGEX.match(title).groups()
        except:
            # # probably something special, let's just downloadit
            # magnet = link.getparent().getnext().getchildren()[0].attrib['href']
            # if tc:
            #     tc.add_torrent(magnet)
            continue

        if matches[2]:
            season, episode = matches[2:4]
        else:
            season, episode = matches[5:7]

        season = int(season)
        episode = int(episode)
        extra = matches[7]

        if ((season < current_season) or
            (season == current_season and episode <= current_episode) or
            (match and match not in extra) or
            (notmatch and notmatch in data)):
            continue

        magnet = link.getparent().getnext().getchildren()[0].attrib['href']
        if tc:
            tc.add_torrent(magnet)

        current_episode = episode
        current_season = season

    return current_season, current_episode


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
        current_season = config.getint(section, 'season')
        current_episode = config.getint(section, 'episode')
        match = config.get(section, 'match')
        notmatch = config.get(section, 'notmatch')
        season, episode = eztv_scrapper(eztv_uri, current_season,
                                        current_episode, match, notmatch, tc)
        update_config(section, season, episode)


if __name__ == '__main__':
    config = ConfigParser.SafeConfigParser()
    config.read(CONFIG_FILE)
    host = config.get('Configuration', 'transmission_host')
    port = config.getint('Configuration', 'transmission_port')
    tc = None
    if host and port:
        tc = transmissionrpc.Client(host, port=port)
    main()
