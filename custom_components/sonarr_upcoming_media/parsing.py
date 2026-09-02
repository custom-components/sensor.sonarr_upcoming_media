import logging
import re
import time
from datetime import datetime

import requests

from .const import DEFAULT_PARSE_DICT

_LOGGER = logging.getLogger(__name__)

TMDB_DETAILS_URL = 'https://api.themoviedb.org/3/tv/{}?api_key=1f7708bb9a218ab891a5d438b1b63992&append_to_response=videos'

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


def image_url(series, cover_type):
    """Series artwork from Sonarr, chosen by coverType.

    remoteUrl points at TheTVDB's CDN, where appending _t before the extension
    returns a thumbnail -- hence the substitution, which is anchored to the end
    of the URL so it cannot mangle a path that happens to contain '.jpg'
    earlier.
    """
    for image in series.get('images') or []:
        if image.get('coverType') == cover_type:
            url = image.get('remoteUrl') or image.get('url') or ''
            return re.sub(r'\.jpg$', '_t.jpg', url)
    return ''


def fetch_trailer(session, tmdb_id, cache):
    """YouTube trailer for a series, looked up once per series.

    Sonarr has no trailer field, so this is the one thing TMDB still supplies.
    Keyed by the tmdbId Sonarr already provides -- a title search cannot
    distinguish two shows with the same name, and the calendar returns one row
    per EPISODE, so searching per row asked TMDB the same question repeatedly.

    Failures are cached as empty. TMDB being unreachable should cost one
    attempt per series per update, not one per episode, and must never take the
    whole sensor down with it.
    """
    if not tmdb_id:
        return ''
    if tmdb_id in cache:
        return cache[tmdb_id]
    trailer = ''
    try:
        details = session.get(TMDB_DETAILS_URL.format(tmdb_id), timeout=10).json()
        for video in (details.get('videos') or {}).get('results') or []:
            if video.get('type') == 'Trailer' and video.get('key'):
                trailer = f'https://www.youtube.com/watch?v={video["key"]}'
                break
    except Exception as err:  # noqa: BLE001 - a trailer is never worth failing over
        _LOGGER.debug("TMDB trailer lookup failed for %s: %s", tmdb_id, err)
    cache[tmdb_id] = trailer
    return trailer


def parse_data(data, tz, host, port, ssl, url_base=None):
    """Return JSON for the sensor."""
    attributes = {}
    card_json = []
    card_json.append(DEFAULT_PARSE_DICT)

    session = requests.Session()
    session.headers.update({"Accept-Encoding": "identity"})
    trailer_cache = {}

    for show in data:
        card_item = {}
        series = show.get('series') or {}
        if not series.get('title'):
            continue

        card_item['airdate'] = show['airDateUtc']
        if days_until(show['airDateUtc'], tz) <= 7:
            card_item['release'] = '$day, $time'
        else:
            card_item['release'] = '$day, $date $time'
        card_item['flag'] = show.get('hasFile', False)
        card_item['title'] = series['title']
        card_item['episode'] = show.get('title', '')
        if 'seasonNumber' in show and 'episodeNumber' in show:
            card_item['number'] = 'S{:02d}E{:02d}'.format(show['seasonNumber'],
                                                          show['episodeNumber'])
        else:
            card_item['number'] = ''
        card_item['runtime'] = series.get('runtime', '')
        card_item['studio'] = series.get('network', '')
        rating = (series.get('ratings') or {}).get('value') or 0
        card_item['rating'] = ('\N{BLACK STAR} ' + str(rating)) if rating > 0 else ''
        card_item['genres'] = ', '.join(series.get('genres') or [])
        card_item['summary'] = show.get('overview', '')

        # Sonarr already knows the TMDB id, so no search is needed to find it.
        card_item['tmdb_id'] = series.get('tmdbId', '')
        card_item['trailer'] = fetch_trailer(session, series.get('tmdbId'),
                                             trailer_cache)

        # Artwork comes from Sonarr. It always did in practice -- the previous
        # code fetched posters from TMDB and then overwrote them from this same
        # payload a few lines later.
        card_item['poster'] = image_url(series, 'poster')
        card_item['fanart'] = image_url(series, 'fanart')

        series_title_slug = series.get('titleSlug', '')
        protocol = 'https' if ssl else 'http'
        card_item['deep_link'] = f'{protocol}://{host}:{port}/{url_base.strip("/") + "/" if url_base else ""}series/{series_title_slug}'
        card_json.append(card_item)
    attributes['data'] = card_json
    return attributes
