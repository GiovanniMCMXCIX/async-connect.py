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

import asyncio

from .http import HTTPClient
from .errors import NotFound
from .release import Release
from .track import Track, BrowseEntry
from .artist import Artist
from .playlist import Playlist
from .utils import find
from typing import List, Tuple
from urllib.parse import quote


class Client:
    def __init__(self, *, loop=None):
        self.loop = asyncio.get_event_loop() if not loop else loop
        self.http = HTTPClient(loop=self.loop)
        self.browse_filters = self.loop.run_until_complete(self.http.request('GET', self.http.BROWSE_FILTERS))
        self._is_closed = False

    async def sign_in(self, email: str, password: str, token: int = None):
        """Logs in the client with the specified credentials.

        Parameters
        ----------
        email: str
            Email that the client should use to sign in.
        password: str
            Password that the client should use to sign in.
        token: int
            Token that the client should use to sign in. (2FA Only)

        Raises
        ------
        HTTPSException
            Invalid email, password or token.
        """
        if not token:
            await self.http.email_sign_in(email, password)
        else:
            await self.http.two_feature_sign_in(email, password, token)

    @property
    async def is_signed_in(self):
        """bool: Indicates if the client has logged in successfully."""
        return await self.http.is_signed_in()

    async def sign_out(self):
        """Logs out of Monstercat Connect and closes all connections."""
        await self.http.sign_out()
        await self.close()

    async def close(self):
        """Closes all connections."""
        if self._is_closed:
            return
        else:
            await self.http.close()
            self._is_closed = True

    async def create_playlist(self, name: str, *, public: bool = False, entries: List[Tuple[Track, Release]] = None) -> Playlist:
        """Creates a playlist.

        Parameters
        ----------
        name: str
           Name of the playlist that is going to be created.
        public: bool
           If the playlist that is going to be created should be public or not.
        entries: List[Tuple[connect.Track, connect.Release]]
           The tracks that would be added to the playlist that is created.

        Raises
        ------
        ValueError
           Some of the given entries are not valid.
        Forbidden
           The client isn't signed in.
        """
        if entries:
            json_entries = []
            for entry in entries:
                if find(lambda a: a.id == entry[1].id, entry[0].albums):
                    json_entries.append({'trackId': entry[0].id, 'releaseId': entry[1].id})
                else:
                    raise ValueError(f'The track "{entry[0]}" is not in the release\'s "{entry[1]}" track list.')

            return Playlist(**await self.http.create_playlist(name=name, public=public, entries=json_entries))
        else:
            return Playlist(**await self.http.create_playlist(name=name, public=public))

    async def edit_playlist(self, playlist: Playlist, *, name: str = None, public: bool = False) -> Playlist:
        """Edits a playlist.

        Parameters
        ----------
        playlist: connect.Playlist
            Playlist that is gonna be edited.
        name: str
            New name of the playlist that is edited
        public: bool
            If the playlist should be public or not after it's edited

        Raises
        ------
        Forbidden
            The client isn't signed in/ You don't own the playlist.
        """
        return Playlist(**await self.http.edit_playlist(playlist_id=playlist.id, name=name, public=public))

    async def edit_profile(self, *, name: str = None, real_name: str = None, location: str = None, password: str = None):
        """Edits the current profile of the client.

        Parameters
        ----------
        name: str
            New name of the account's profile.
        real_name: str
            New real name of the account's profile.
        location: str
            New location of the account's profile. (buggy)
        password: str
            New password of the account.

        Raises
        ------
        Forbidden
            The client isn't signed in.
        """
        self.http.edit_profile(name=name, real_name=real_name, location=location, password=password)

    async def add_playlist_track(self, playlist: Playlist, track: Track, release: Release) -> Playlist:
        """Adds a track to a playlist's tracklist

        Parameters
        ----------
        playlist: connect.Playlist
            Playlist that the track are going added to.
        track: connect.Track
            Track that is added to the given playlist.
        release: connect.Release
            Release where the track is originated from.
        Raises
        ------
        ValueError
           Some of the given track, release combination is not valid.
        Forbidden
           The client isn't signed in/ You don't own the given playlist.
        """
        if find(lambda a: a.id == release.id, track.albums):
            return Playlist(**await self.http.add_playlist_track(playlist_id=playlist.id, track_id=track.id, release_id=release.id))
        else:
            raise ValueError(f'The track "{track}" is not in the release\'s "{release}" track list.')

    async def add_playlist_tracks(self, playlist: Playlist, entries: List[Tuple[Track, Release]]) -> Playlist:
        """Adds a track to a playlist's tracklist

        Parameters
        ----------
        playlist: connect.Playlist
            Playlist that the tracks are going added to.
        entries: List[Tuple[connect.Track, connect.Release]]
            Tracks that would be added to the given playlist.

        Raises
        ------
        ValueError
           Some of the given track, release combination is not valid.
        Forbidden
           The client isn't signed in/ You don't own the given playlist.
        """
        json_entries = []
        for entry in entries:
            if find(lambda a: a.id == entry[1].id, entry[0].albums):
                json_entries.append({'trackId': entry[0].id, 'releaseId': entry[1].id})
            else:
                raise ValueError(f'The track "{entry[0]}" is not in the release\'s "{entry[1]}" track list.')
        return Playlist(**await self.http.add_playlist_tracks(playlist_id=playlist.id, entries=json_entries))

    async def add_reddit_username(self, username: str):
        """Adds the reddit username to the current profile of the client.

        Parameters
        ----------
        username: str
            Reddit username that is added to the monstercat account.

        Raises
        ------
        NotFound
            "I need to buy monstercat gold again in order to finish this library" ~ Library Author
        """
        await self.http.add_reddit_username(username)

    async def delete_playlist(self, playlist: Playlist):
        """Deletes a playlist.

        Parameters
        ----------
        playlist: connect.Playlist
           The playlist that is deleted.

        Raises
        ------
        Forbidden
            The client isn't signed in/ You don't own the given playlist.
        """
        await self.http.delete_playlist(playlist.id)

    async def delete_playlist_track(self, playlist: Playlist, track: Track) -> Playlist:
        """Deletes a track from a playlist's tracklist.

        Parameters
        ----------
        playlist: connect.Playlist
           Playlist from where the client should remove the given track.
        track: connect.Track
           Track that is deleted from the tracklist of the given playlist.

        Raises
        ------
        Forbidden
            The client isn't signed in/ You don't own the given playlist.
        """
        return Playlist(**await self.http.delete_playlist_track(playlist_id=playlist.id, track_id=track.id))

    async def get_discord_invite(self) -> str:
        """Gets an invite for the gold discord channel on the monstercat discord guild.
        The client needs gold subscription in order to get the invite for that channel.

        Raises
        ------
        NotFound
            "I need to buy monstercat gold again in order to finish this library" ~ Library Author
        """
        return await self.http.get_discord_invite()

    async def get_release(self, catalog_id: str) -> Release:
        """Returns a release with the given ID.

        Parameters
        ----------
        catalog_id: str
           The id of the release that the client should get.

        Raises
        ------
        NotFound
            The client couldn't get the release.
        """
        return Release(**await self.http.get_release(catalog_id))

    async def get_track(self, track_id: str) -> Track:
        """Returns a track with the given ID.

        Parameters
        ----------
        track_id: str
            The id of the track that the client should get.

        Raises
        ------
        NotFound
            The client couldn't get the track.
        """
        return Track(**await self.http.get_track(track_id))

    async def get_artist(self, artist_id: str) -> Artist:
        """Returns a artist with the given ID.

        Parameters
        ----------
        artist_id: str
           The id/vanity_uri of the artist that the client should get.

        Raises
        ------
        NotFound
            The client couldn't get the artist.
        """
        return Artist(**await self.http.get_artist(artist_id))

    async def get_playlist(self, playlist_id: str) -> Playlist:
        """Returns a playlist with the given ID.

        Parameters
        ----------
        playlist_id: str
            The id of the playlist that the client should get.

        Raises
        ------
        Forbidden
            The client can't access a private playlist.
        NotFound
            The client couldn't get the playlist.
        """
        return Playlist(**await self.http.get_playlist(playlist_id))

    async def get_all_releases(self, *, singles: bool = True, eps: bool = True, albums: bool = True, podcasts: bool = False, limit: int = None, skip: int = None) -> List[Release]:
        """Retrieves every release the client can access.

        Parameters
        ----------
        singles: bool
           If the client should get singles.
        eps: bool
           If the client should get EPs.
        albums: bool
           If the client should get albums.
        podcasts: bool
           If the client should get podcasts.
        limit: int
           The limit for how many tracks are supposed to be shown.
        skip: int
           Number of tracks that are skipped to be shown.
        """
        releases = []
        data = await self.http.get_all_releases(singles=singles, eps=eps, albums=albums, podcasts=podcasts, limit=limit, skip=skip)
        for release in data['results']:
            releases.append(Release(**release))
        return releases

    async def get_all_tracks(self, *, limit: int = None, skip: int = None) -> List[Track]:
        """Retrieves every track the client can access.

        Parameters
        ----------
        limit: int
           Limit for how many tracks are supposed to be shown.
        skip: int
           Number of tracks that are skipped to be shown.
        """
        tracks = []
        data = await self.http.get_all_tracks(limit=limit, skip=skip)
        for track in data['results']:
            tracks.append(Track(**track))
        return tracks

    async def get_all_artists(self, *, year: int = None, limit: int = None, skip: int = None) -> List[Artist]:
        """Retrieves every artist the client can access.

        Parameters
        ----------
        year: int
           Artists from the year specified that are to be shown.
        limit: int
           Limit for how many artists are supposed to be shown.
        skip: int
           Number of artists that are skipped to be shown.
        """
        artists = []
        data = await self.http.get_all_artists(year=year, limit=limit, skip=skip)
        for artist in data['results']:
            artists.append(Artist(**artist))
        return artists

    async def get_all_playlists(self, *, limit: int = None, skip: int = None) -> List[Playlist]:
        """Retrieves every playlist the client can access.

        Raises
        ------
        Unauthorized
            The client isn't signed in.
        """
        playlists = []
        data = await self.http.get_all_playlists(limit=limit, skip=skip)
        for playlist in data['results']:
            playlists.append(Playlist(**playlist))
        return playlists

    async def get_browse_entries(self, *, types: List[str] = None, genres: List[str] = None, tags: List[str] = None, limit: int = None, skip: int = None) -> List[BrowseEntry]:
        # I can't think of a better way to name this function...
        """
        Check `connect.Client.browse_filters` for filters that are needed to be used on the function's parameters.

        Parameters
        ----------
        types: List[str]
            Browse entries types that the API should get.
        genres: List[str]
            Browse entries genres that the API should look for.
        tags: List[str]
            Browse entries tags that the API should look for.
        limit: int
            The limit for how many releases are supposed to be shown.
        skip: int
            Number of releases that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any releases.
        """
        entries = []
        data = await self.http.get_browse_entries(types=types, genres=genres, tags=tags, limit=limit, skip=skip)
        for entry in data['results']:
            entries.append(BrowseEntry(**entry))
        if not entries:
            raise NotFound('No browse entry was found.')
        else:
            return entries

    async def search_release(self, term: str, *, limit: int = None, skip: int = None) -> List[Release]:
        """Searches for a release.

        Parameters
        ----------
        term: str
           The release name that is searched.
        limit: int
           Limit for how many releases are supposed to be shown.
        skip: int
           Number of releases that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any releases.
        """
        releases = []
        data = await self.http.request('GET', f'{self.http.RELEASE}?fuzzyOr=title,{quote(term)},renderedArtists,{quote(term)}&limit={limit}&skip={skip}')
        for release in data['results']:
            releases.append(Release(**release))
        if not releases:
            raise NotFound('No release was found.')
        else:
            return releases

    async def search_release_advanced(self, title: str, artists: str, *, limit: int = None, skip: int = None) -> List[Release]:
        """Searches for a release in a more advanced way.

        Parameters
        ----------
        title: str
           The release title that is searched.
        artists: str
           The release artists that are searched.
        limit: int
           Limit for how many releases are supposed to be shown.
        skip: int
           Number of releases that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any releases.
        """
        releases = []
        data = await self.http.request('GET', f'{self.http.RELEASE}?fuzzy=title,{quote(title)},renderedArtists,{quote(artists)}&limit={limit}&skip={skip}')
        for release in data['results']:
            releases.append(Release(**release))
        if not releases:
            raise NotFound('No release was found.')
        else:
            return releases

    async def search_track(self, term: str, *, limit: int = None, skip: int = None) -> List[Track]:
        """Searches for a track.

        Parameters
        ----------
        term: str
           The track name that is searched.
        limit: int
           Limit for how many tracks are supposed to be shown.
        skip: int
           Number of tracks that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any tracks.
        """
        tracks = []
        data = await self.http.request('GET', f'{self.http.TRACK}?fuzzyOr=title,{quote(term)},artistsTitle,{quote(term)}&limit={limit}&skip={skip}')
        for track in data['results']:
            tracks.append(Track(**track))
        if not tracks:
            raise NotFound('No track was found.')
        else:
            return tracks

    async def search_track_advanced(self, title: str, artists: str, *, limit: int = None, skip: int = None) -> List[Track]:
        """Searches for a track in a more advanced way.

        Parameters
        ----------
        title: str
           The track title that is searched.
        artists: str
           The track artists that are searched.
        limit: int
           Limit for how many tracks are supposed to be shown.
        skip: int
           Number of tracks that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any tracks.
        """
        tracks = []
        data = await self.http.request('GET', f'{self.http.TRACK}?fuzzy=title,{quote(title)},artistsTitle,{quote(artists)}&limit={limit}&skip={skip}')
        for track in data['results']:
            tracks.append(Track(**track))
        if not tracks:
            raise NotFound('No track was found.')
        else:
            return tracks

    async def search_artist(self, term: str, *, year: int = None, limit: int = None, skip: int = None) -> List[Artist]:
        """Searches for a artist.

        Parameters
        ----------
        term: str
           The artist name that is searched.
        year: int
           The artists from the year specified that are to be shown.
        limit: int
           Limit for how many artists are supposed to be shown.
        skip: int
           Number of artists that are skipped to be shown.

        Raises
        ------
        NotFound
            The client couldn't find any artists.
        """
        artists = []
        base = f'{self.http.ARTIST}?limit={limit}&skip={skip}&fuzzyOr=name,{quote(term)}'
        if year:
            base = f'{base},year,{year}'
        data = await self.http.request('GET', base)
        for artist in data['results']:
            artists.append(Artist(**artist))
        if not artists:
            raise NotFound('No artist was found.')
        else:
            return artists

    async def search_playlist(self, term: str, *, limit: int = None, skip: int = None) -> List[Playlist]:
        """Searches for a playlist.

        Parameters
        ----------
        term: str
           The playlist name that is searched.
        limit: int
           Limit for how many playlists are supposed to be shown.
        skip: int
           Number of playlists that are skipped to be shown.

        Raises
        ------
        Unauthorized
            The client isn't signed in.
        NotFound
            The client couldn't find any playlists.
        """
        playlists = []
        data = await self.http.request('GET', f'{self.http.PLAYLIST}?fuzzyOr=name,{quote(term)}&limit={limit}&skip={skip}')
        for playlist in data['results']:
            playlists.append(Playlist(**playlist))
        if not playlists:
            raise NotFound('No playlist was found.')
        else:
            return playlists
