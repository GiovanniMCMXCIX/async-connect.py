# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2017 GiovanniMCMXCIX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import async_connect as connect
import unittest
import asyncio
import uvloop


class TestGetAllCatalog(unittest.TestCase):
    def setUp(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.get_event_loop()
        self.connect = connect.Client(loop=self.loop)

    def test_release(self):
        async def test():
            print('\n[connect.Client.get_all_releases]')
            releases = []
            data = await self.connect.get_all_releases()
            for release in data:
                releases.append((str(release), len(await release.tracks())))
            print(f'There are {len(releases)} total releases.')
        self.loop.run_until_complete(test())

    def test_track(self):
        async def test():
            print('\n[connect.Client.get_all_tracks]')
            tracks = []
            data = await self.connect.get_all_tracks()
            for track in data:
                tracks.append((str(track), len(track.albums)))
            print(f'There are {len(tracks)} total tracks.')
        self.loop.run_until_complete(test())

    def test_artist(self):
        async def test():
            print('\n[connect.Client.get_all_artists]')
            artists = []
            data = await self.connect.get_all_artists()
            for artist in data:
                artists.append((str(artist), len(await artist.releases())))
            print(f'There are {len(artists)} total artists.')
        self.loop.run_until_complete(test())

    def tearDown(self):
        self.loop.run_until_complete(self.connect.close())
