import time
from datetime import date, datetime
from pytz import timezone
import requests
import json

from homeassistant.core import HomeAssistant

def get_date(zone, offset=0):
    """Get date based on timezone and offset of days."""
    return datetime.date(datetime.fromtimestamp(
        time.time() + 86400 * offset, tz=zone))

def days_until(date, tz):
    from pytz import utc
    date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    date = str(date.replace(tzinfo=utc).astimezone(tz))[:10]
    date = time.strptime(date, '%Y-%m-%d')
    date = time.mktime(date)
    now = datetime.now().strftime('%Y-%m-%d')
    now = time.strptime(now, '%Y-%m-%d')
    now = time.mktime(now)
    return int((date - now) / 86400)

def parse_data(data, tz, host, port, ssl):
    import re
    """Return JSON for the sensor."""
    attributes = {}
    default = {}
    card_json = []
    default['title_default'] = '$title'
    default['line1_default'] = '$episode'
    default['line2_default'] = '$release'
    default['line3_default'] = '$rating - $runtime'
    default['line4_default'] = '$number - $studio'
    default['icon'] = 'mdi:arrow-down-bold'
    card_json.append(default)
    for show in data:
        card_item = {}
        if 'series' not in show:
            continue
        card_item['airdate'] = show['airDateUtc']
        if days_until(show['airDateUtc'], tz) <= 7:
            card_item['release'] = '$day, $time'
        else:
            card_item['release'] = '$day, $date $time'
        card_item['flag'] = show.get('hasFile', False)
        if 'title' in show['series']:
            card_item['title'] = show['series']['title']
        else:
            continue
        card_item['episode'] = show.get('title', '')
        if 'seasonNumber' and 'episodeNumber' in show:
            card_item['number'] = 'S{:02d}E{:02d}'.format(show['seasonNumber'],
                                                    show['episodeNumber'])
        else:
            card_item['number'] = ''
        if 'runtime' in show['series']:
            card_item['runtime'] = show['series']['runtime']
        else:
            card_item['runtime'] = ''
        if 'network' in show['series']:
            card_item['studio'] = show['series']['network']
        else:
            card_item['studio'] = ''
        if ('ratings' in show['series'] and
        show['series']['ratings']['value'] > 0):
                card_item['rating'] = ('\N{BLACK STAR} ' +
                                str(show['series']['ratings']['value']))
        else:
            card_item['rating'] = ''
        if 'genres' in show['series']:
            card_item['genres'] = ', '.join(show['series']['genres'])
        else:
            card_item['genres'] = ''
        card_item['summary'] = show.get('overview', '')
        try:
            for img in show['series']['images']:
                if img['coverType'] == 'poster':
                    card_item['poster'] = re.sub('.jpg', '_t.jpg', img['remoteUrl'])
        except:
            continue
        try:
            card_item['fanart'] = ''
            for img in show['series']['images']:
                if img['coverType'] == 'fanart':
                    card_item['fanart'] = re.sub('.jpg', '_t.jpg', img['remoteUrl'])
        except:
            pass
        series_title_slug = show['series']['titleSlug']
        protocol = 'https' if ssl else 'http'
        card_item['deep_link'] = f'{protocol}://{host}:{port}/series/{series_title_slug}'
        card_json.append(card_item)
    attributes['data'] = card_json
    return attributes


class SonarrApi():
    def __init__(
        self,
        hass: HomeAssistant,
        api: str, 
        days: int, 
        host: str, 
        port: int, 
        ssl: bool, 
        urlbase: str, 
        max: int
    ):
        self._api = api
        self._max = max
        self._days = days
        self._hass = hass
        self._host = host
        self._port = port
        self._ssl = ssl

        self._address = 'http{0}://{1}:{2}/{3}api/v3/calendar?start={4}&end={5}&includeEpisodeImages=true&includeSeries=true'.format(
                            's' if ssl else '', 
                            host,
                            port,
                            "{}/".format(urlbase.strip('/')) if urlbase else urlbase,
                            get_date(timezone(str(self._hass.config.time_zone))),
                            get_date(timezone(str(self._hass.config.time_zone)), self._days)
                            )

    def update(self):
        tz = timezone(str(self._hass.config.time_zone))
        start = get_date(tz)
        try:
            api = requests.get(self._address, headers={'X-Api-Key': self._api}, timeout=10)
        except OSError:
            raise SonarrCannotBeReached

        if api.status_code == 200:
            if self._days == 1:
                return {
                    'online': True,
                    'data': parse_data(list(
                                        filter(
                                            lambda x: x['airDate'][:-10] == str(start),
                                            api.json()))[:self._max], self._host, self._port, self._ssl)
                }
                            
            return {
                'online': True,
                'data': parse_data(api.json()[:self._max], tz, self._host, self._port, self._ssl)
            }
        
        raise SonarrCannotBeReached

class FailedToLogin(Exception):
    "Raised when the Sonarr user fail to Log-in"
    pass

class SonarrCannotBeReached(Exception):
    "Raised when the Sonarr cannot be reached"
    pass