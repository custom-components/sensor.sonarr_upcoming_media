"""
Home Assistant component to feed the Upcoming Media Lovelace card with
Sonarr's upcoming releases.

https://github.com/custom-components/sensor.radarr_upcoming_media

https://github.com/custom-cards/upcoming-media-card

"""
import logging, requests, time, re, json
from datetime import date, datetime
import voluptuous as vol, homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_HOST, CONF_PORT, CONF_SSL
from homeassistant.helpers.entity import Entity

__version__ = '0.1.4'

_LOGGER = logging.getLogger(__name__)

CONF_DAYS = 'days'
CONF_URLBASE = 'urlbase'
CONF_MAX = 'max'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_DAYS, default='7'): cv.string,
    vol.Optional(CONF_HOST, default='localhost'): cv.string,
    vol.Optional(CONF_PORT, default=8989): cv.port,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_URLBASE, default=''): cv.string,
    vol.Optional(CONF_MAX, default=5): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    add_devices([SonarrUpcomingMediaSensor(hass, config)], True)

class SonarrUpcomingMediaSensor(Entity):

    def __init__(self, hass, conf):
        from pytz import timezone
        self.host = conf.get(CONF_HOST)
        self.port = conf.get(CONF_PORT)
        self.urlbase = conf.get(CONF_URLBASE)
        if self.urlbase: self.urlbase = "{}/".format(self.urlbase.strip('/'))
        self.apikey = conf.get(CONF_API_KEY)
        self.days = int(conf.get(CONF_DAYS))
        self.ssl = 's' if conf.get(CONF_SSL) else ''
        self._state = None
        self.data = []
        self._tz = timezone(str(hass.config.time_zone))
        self.attribNum = 0
        self.now = str(get_date(self._tz))
        self.max_items = int(conf.get(CONF_MAX))

    @property
    def name(self):
        return 'Sonarr_Upcoming_Media'

    @property
    def state(self):
        return self._state

    @property
    def device_state_attributes(self):
        """Build JSON for the sensor."""
        self.attribNum = 0
        attributes = {}
        default = {}
        data = []
        default['title_default'] = '$title'
        default['line1_default'] = '$episode'
        default['line2_default'] = '$release'
        default['line3_default'] = '$rating - $runtime'
        default['line4_default'] = '$number - $studio'
        default['icon'] = 'mdi:arrow-down-bold'
        data.append(default)
        for show in self.data:
            pre = {}
            try: pre['airdate'] = show['airDateUtc']
            except: continue
            try:
                """Get number of days between now and air date."""
                n=list(map(int, self.now.split("-")))
                r=list(map(int, show['airDateUtc'][:-10].split("-")))
                today = date(n[0],n[1],n[2])
                airday = date(r[0],r[1],r[2])
                daysBetween = (airday-today).days
            except: continue
            if daysBetween <= 7: pre['release'] = '$day, $time'
            else: pre['release'] = '$day, $date $time'
            pre['flag'] = show.get('hasFile', False)
            try: pre['title'] = show['series']['title']
            except: continue
            pre['episode'] = show.get('title','')
            try: pre['number'] = 'S{:02d}E{:02d}'.format(show['seasonNumber'], show['episodeNumber'])
            except: pre['number'] = 0
            try: pre['runtime'] = show['series']['runtime']
            except: pre['runtime'] = 0
            try: pre['studio'] = show['series']['network']
            except: pre['studio'] = 0
            try:
                if show['series']['ratings']['value'] > 0:
                    pre['rating'] = '\N{BLACK STAR} '+str(show['series']['ratings']['value'])
                else: pre['rating'] = ''
            except: pre['rating'] = ''
            try: pre['genres'] = ', '.join(show['series']['genres'])
            except: pre['genres'] = ''
            try: pre['poster'] = re.sub('banners/', 'banners/_cache/', show['series']['images'][2]['url'])
            except: continue
            try:
                if '.jpg' in show['series']['images'][0]['url']:
                    pre['fanart'] = re.sub('banners/', 'banners/_cache/', show['series']['images'][0]['url'])
                else: pre['fanart'] = ''
            except: pre['fanart'] = ''
            self.attribNum += 1
            data.append(pre)
        self._state = self.attribNum
        attributes['data'] = json.dumps(data)
        return attributes

    def update(self):
        start = get_date(self._tz)
        end = get_date(self._tz, self.days)
        try:
            res = requests.get('http{0}://{1}:{2}/{3}api/calendar?start={4}&end={5}'.format(
                    self.ssl, self.host, self.port, self.urlbase, start, end),
                headers={'X-Api-Key': self.apikey}, timeout=10)
        except OSError:
            _LOGGER.warning("Host %s is not available", self.host)
            self._state = None
            return

        if res.status_code == 200:
            if self.days == 1:
                self.data = list(filter(lambda
                    x: x['airDate'][:-10] == str(start), res.json()))[:self.max_items]
            else: self.data = res.json()[:self.max_items]

def get_date(zone, offset=0):
    """Get date based on timezone and offset of days."""
    return datetime.date(datetime.fromtimestamp(time.time() + 86400 * offset, tz=zone))
