import time
from datetime import datetime
from pytz import timezone
import requests
import json

from homeassistant.core import HomeAssistant

from .parsing import parse_data

def get_date(zone, offset=0):
    """Get date based on timezone and offset of days."""
    return datetime.date(datetime.fromtimestamp(
        time.time() + 86400 * offset, tz=zone))

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
        self._url_base = urlbase

    def update(self):
        tz = timezone(str(self._hass.config.time_zone))
        start = get_date(tz)
        end = get_date(tz, self._days)
        url_prefix = "{}/".format(self._url_base.strip('/')) if self._url_base else self._url_base
        protocol = 's' if self._ssl else ''
        address_calendar = f'http{protocol}://{self._host}:{self._port}/{url_prefix}api/v3/calendar?start={start}&end={end}&includeEpisodeImages=true&includeSeries=true'
        address_wanted = f'http{protocol}://{self._host}:{self._port}/{url_prefix}api/v3/wanted/missing?page=1&pageSize={self._max}&sortKey=airDateUtc&sortDir=descending&includeSeries=true&includeImages=true'

        try:
            api_calendar = requests.get(address_calendar, headers={'X-Api-Key': self._api}, timeout=10)
            api_wanted = requests.get(address_wanted, headers={'X-Api-Key': self._api}, timeout=10)
        except OSError:
            raise SonarrCannotBeReached

        if api_calendar.status_code == 200 and api_wanted.status_code == 200:
            upcoming_raw = api_calendar.json()
            if self._days == 1:
                upcoming_raw = list(filter(lambda x: x.get('airDate', '')[:-10] == str(start), upcoming_raw))
            upcoming_data = parse_data(upcoming_raw[:self._max], tz, self._host, self._port, self._ssl, self._url_base)

            wanted_json = api_wanted.json()
            wanted_records = wanted_json.get('records', wanted_json) if isinstance(wanted_json, dict) else wanted_json
            wanted_data = parse_data(wanted_records[:self._max], tz, self._host, self._port, self._ssl, self._url_base)

            return {
                'online': True,
                'upcoming': upcoming_data,
                'wanted': wanted_data,
                'data': upcoming_data,
            }

        raise SonarrCannotBeReached

class FailedToLogin(Exception):
    "Raised when the Sonarr user fail to Log-in"
    pass

class SonarrCannotBeReached(Exception):
    "Raised when the Sonarr cannot be reached"
    pass