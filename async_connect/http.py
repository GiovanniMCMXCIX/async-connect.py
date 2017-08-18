import aiohttp
import json
import sys
import re

from .errors import HTTPSException, Unauthorized, Forbidden, NotFound
from . import utils, __version__


class HTTPClient:
    BASE = 'https://connect.monstercat.com'
    SIGN_IN = BASE + '/signin'
    SIGN_OUT = BASE + '/signout'
    API_BASE = BASE + '/api'
    SELF = API_BASE + '/self'
    CATALOG = API_BASE + '/catalog'
    PLAYLIST = API_BASE + '/playlist'
    TRACK = CATALOG + '/track'
    RELEASE = CATALOG + '/release'
    ARTIST = CATALOG + '/artist'
    BROWSE = CATALOG + '/browse'
    BROWSE_FILTERS = BROWSE + '/filters'

    def __init__(self, loop):
        self.session = aiohttp.ClientSession(loop=loop)
        self.download_link_gen = utils.DownloadLinkGenerator()
        user_agent = 'AsyncConnectBot (https://github.com/GiovanniMCMXCIX/async-connect.py {0}) ' \
                     'Python/{1[0]}.{1[1]} aiohttp/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, aiohttp.__version__)

    async def request(self, method, url, **kwargs):
        headers = {
            'User-Agent': self.user_agent
        }

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = utils.to_json(kwargs.pop('json'))

        kwargs['headers'] = headers
        response = await self.session.request(method, url, **kwargs)
        try:
            text = await response.text()
            try:
                data = json.loads(text)
            except json.decoder.JSONDecodeError:
                data = {'message': text} if text else None

            if 300 > response.status >= 200:
                return data
            elif response.status == 401:
                raise Unauthorized(data.pop('message', 'Unknown error'))
            elif response.status == 403:
                raise Forbidden(data.pop('message', 'Unknown error'))
            elif response.status == 404:
                raise NotFound(data.pop('message', 'Unknown error'))
            else:
                raise HTTPSException(data.pop('message', 'Unknown error'), response)
        except Exception as e:
            raise e
