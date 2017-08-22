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

import unittest
import asyncio
import uvloop
import async_connect as connect


class TestGetAllCatalog(unittest.TestCase):
    def setUp(self):
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = asyncio.get_event_loop()
        self.connect = connect.Client(loop=self.loop)

    def test_release(self):
        async def test():
            release = await self.connect.get_release('MC011')
            print('\n[connect.Client.get_release]\n{0.title} by {0.artists} had been release on {0.release_date} and has the following track(s):'.format(release))
            tracks = await release.tracks()
            print('\n'.join(['{0.title} by {0.artists}'.format(track) for track in tracks]))
        self.loop.run_until_complete(test())

    def test_playlist(self):
        async def test():
            playlist = await self.connect.get_playlist('577ec5395891d31a15b80c39')
            print('\n[connect.Client.get_playlist]\nThe playlist with the name {0} has the following tracks:'.format(playlist.name))
            tracks = await playlist.tracks()
            for track in tracks:
                print('[{0.release.catalog_id}] {0.title} by {0.artists} from {0.release.title}'.format(track))
        self.loop.run_until_complete(test())

    def test_track(self):
        async def test():
            track = await self.connect.get_track('512bdb6db9a8860a11000029')
            print('\n[connect.Client.get_track]\n{0.title} by {0.artists} has been featured on the following releases:'.format(track))
            self.assertEqual(track.artists, str(await self.connect.get_artist(track.get_artists()[0].id)))
            release = await self.connect.get_release('MC011')
            self.assertEqual([album.id for album in track.albums if album.id == release.id][0], release.id)
            for album in track.albums:
                print('[{0.catalog_id}] {0.title}'.format(await self.connect.get_release(album.id)))
        self.loop.run_until_complete(test())

    def test_artist(self):
        async def test():
            artist = await self.connect.get_artist('gq')
            print('\n[connect.connect.get_artist]\n{}, is featured on the year(s) {} and has released the following:'.format(
                artist, ', '.join(str(year) for year in artist.years)))
            releases = await artist.releases()
            for release in releases:
                if not release.artists.lower() == 'various artists':
                    print('[{0.catalog_id}] {0.title} with {1} track(s)'.format(release, len(await release.tracks())))
            print("And appears on:")
            releases = await artist.releases()
            for release in releases:
                if release.artists.lower() == 'various artists':
                    print('[{0.catalog_id}] {0.title}'.format(release))
        self.loop.run_until_complete(test())

    def tearDown(self):
        self.loop.run_until_complete(self.connect.close())
