# Copyright (c) 2009 StudioNow, Inc <patrick@studionow.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Test the Playlist object
"""

import unittest
import uuid
import mock

from pybrightcove import enums
from pybrightcove import exceptions
from pybrightcove import playlist
from pybrightcove import video


TEST_VIDEO_ID = 11449913001
TEST_VIDEO_IDS = [TEST_VIDEO_ID, 24780403001, 24780402001]
TEST_PLAYLIST_ID = 24781161001
TEST_PLAYLIST_IDS = [TEST_PLAYLIST_ID, 10518202001]
TEST_PLAYLIST_REF_ID = 'unittest-playlist'
TEST_PLAYLIST_REF_IDS = [TEST_PLAYLIST_REF_ID, 'test']


class PlaylistTest(unittest.TestCase):

    def setUp(self):
        self.test_uuid = str(uuid.uuid4())

    def _get_list_mock(self, ConnectionMock):
        m = ConnectionMock()
        c = mock.Mock()
        c.items = [mock.Mock(), mock.Mock()]
        c.total_count = 2
        c.page_size = 0
        m.get_list.return_value = c
        return m

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_instantiate_new(self, ConnectionMock):
        pl = playlist.Playlist(name='My Playlist', type=enums.PlaylistTypeEnum.EXPLICIT)
        pl.video_ids = TEST_VIDEO_IDS
        self.assertEquals(pl.id, None)
        self.assertEquals(pl.name, 'My Playlist')
        self.assertEquals(pl.type, enums.PlaylistTypeEnum.EXPLICIT)
        self.assertEquals(pl.video_ids, TEST_VIDEO_IDS)
        self.assertEquals(pl.short_description, None)

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_instantiate_with_playlist_id(self, ConnectionMock):
        m = ConnectionMock()
        m.get_item.return_value = {'id': TEST_PLAYLIST_ID, 'name': '', 'shortDescription': '', 'referenceId': TEST_PLAYLIST_REF_ID, 'thumbnailURL': '', 'videoIds': [], 'playlistType': ''}
        pl = playlist.Playlist(id=TEST_PLAYLIST_ID)
        self.assertEquals(pl.reference_id, TEST_PLAYLIST_REF_ID)

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_instantiate_with_reference_id(self, ConnectionMock):
        m = ConnectionMock()
        m.get_item.return_value = {'id': TEST_PLAYLIST_ID, 'name': '', 'shortDescription': '', 'referenceId': TEST_PLAYLIST_REF_ID, 'thumbnailURL': '', 'videoIds': [], 'playlistType': ''}
        pl = playlist.Playlist(reference_id=TEST_PLAYLIST_REF_ID)
        self.assertEquals(pl.id, TEST_PLAYLIST_ID)

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_instantiate_with_invalid_parameters(self, ConnectionMock):
        try:
            playlist.Playlist(name="No type specified")
            self.fail('Should have raised an error.')
        except exceptions.PyBrightcoveError, e:
            self.assertEquals(str(e), 'Invalid parameters for Playlist.')

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_save_new(self, ConnectionMock):
        m = self._get_list_mock(ConnectionMock)
        m.post.return_value = 10
        pl = playlist.Playlist(name="Unit Test Videos",
            type=enums.PlaylistTypeEnum.EXPLICIT)
        for v in video.Video.find_by_tags(and_tags=['unittest', ]):
            pl.videos.append(v)
        pl.save()
        self.assertEquals(pl.id, 10)
        self.assertEquals(pl.name, 'Unit Test Videos')
        self.assertEquals(m.method_calls[0][0], 'get_list')
        self.assertEquals(m.method_calls[0][1][0], 'find_videos_by_tags')
        self.assertEquals(m.method_calls[1][0], 'post')
        self.assertEquals(m.method_calls[1][1][0], 'create_playlist')

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_save_update(self, ConnectionMock):
        m = ConnectionMock()
        data = {}
        data['id'] = TEST_PLAYLIST_ID
        data['referenceId'] = TEST_PLAYLIST_REF_ID
        data['name'] = "test-%s" % self.test_uuid
        data['shortDescription'] = "My description"
        data['thumbnailURL'] = "http://google.com"
        data['videoIds'] = TEST_VIDEO_IDS
        data['playlistType'] = enums.PlaylistTypeEnum.EXPLICIT
        m.get_item.return_value = data
        m.post.return_value = data
        pl = playlist.Playlist(id=TEST_PLAYLIST_ID)
        pl.name = 'test-%s' % self.test_uuid
        pl.save()
        self.assertEquals(pl.id, TEST_PLAYLIST_ID)
        self.assertEquals(pl.name, 'test-%s' % self.test_uuid)
        self.assertEquals(m.method_calls[0][0], 'get_item')
        self.assertEquals(m.method_calls[0][1][0], 'find_playlist_by_id')
        self.assertEquals(m.method_calls[1][0], 'post')
        self.assertEquals(m.method_calls[1][1][0], 'update_playlist')

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_delete(self, ConnectionMock):
        m = self._get_list_mock(ConnectionMock)
        m.post.return_value = 10

        pl = playlist.Playlist(name="DELETE - Unit Test Videos",
            type=enums.PlaylistTypeEnum.EXPLICIT)
        for v in video.Video.find_by_tags(and_tags=['unittest', ]):
            pl.videos.append(v)
        self.assertEquals(pl.id, None)
        pl.save()
        self.assertEquals(pl.id, 10)
        pl.delete()
        self.assertEquals(pl.id, None)
        self.assertEquals(m.method_calls[0][0], 'get_list')
        self.assertEquals(m.method_calls[0][1][0], 'find_videos_by_tags')
        self.assertEquals(m.method_calls[1][0], 'post')
        self.assertEquals(m.method_calls[1][1][0], 'create_playlist')
        self.assertEquals(m.method_calls[2][0], 'post')
        self.assertEquals(m.method_calls[2][1][0], 'delete_playlist')

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_find_by_ids(self, ConnectionMock):
        m = self._get_list_mock(ConnectionMock)
        playlists = playlist.Playlist.find_by_ids(TEST_PLAYLIST_IDS)
        for pl in playlists:
            print pl
        print m.method_calls
        self.assertEquals(m.method_calls[0][0], 'get_list')
        self.assertEquals(m.method_calls[0][1][0], 'find_playlists_by_ids')
        self.assertEquals(m.method_calls[0][2]['playlist_ids'], ','.join([str(x) for x in TEST_PLAYLIST_IDS]))

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_find_by_reference_ids(self, ConnectionMock):
        m = self._get_list_mock(ConnectionMock)
        playlists = playlist.Playlist.find_by_reference_ids(TEST_PLAYLIST_REF_IDS)
        for pl in playlists:
            print pl
        print m.method_calls
        self.assertEquals(m.method_calls[0][0], 'get_list')
        self.assertEquals(m.method_calls[0][1][0], 'find_playlists_by_reference_ids')
        self.assertEquals(m.method_calls[0][2]['reference_ids'], ','.join([str(x) for x in TEST_PLAYLIST_REF_IDS]))

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_find_for_player_id(self, ConnectionMock):
        m = self._get_list_mock(ConnectionMock)
        playlists = playlist.Playlist.find_for_player_id(23424255)
        for pl in playlists:
            print pl
        print m.method_calls
        self.assertEquals(m.method_calls[0][0], 'get_list')
        self.assertEquals(m.method_calls[0][1][0], 'find_playlists_for_player_id')
        self.assertEquals(m.method_calls[0][2]['player_id'], 23424255)

    @mock.patch('pybrightcove.connection.APIConnection')
    def test_find_all(self, ConnectionMock):
        m = self._get_list_mock(ConnectionMock)
        playlists = playlist.Playlist.find_all()
        for pl in playlists:
            print pl
        self.assertEquals(m.method_calls[0][0], 'get_list')
        self.assertEquals(m.method_calls[0][1][0], 'find_all_playlists')

    def test_ensure_essential_fields(self):

        essentials = ['id', 'referenceId', 'name', 'shortDescription',
                      'thumbnailURL', 'videoIds', 'playlistType']

        kwargs = playlist.Playlist.ensure_essential_fields(**{})
        self.assertEqual(kwargs, {})
        kwargs = {'playlist_fields': ['itemState', ]}
        kwargs = playlist.Playlist.ensure_essential_fields(**kwargs)
        for key in essentials:
            self.assertTrue(key in kwargs['playlist_fields'])
        self.assertTrue('itemState' in kwargs['playlist_fields'])
