# -*- coding: utf-8 -*-

import get_videos as gv
from datetime import datetime

""" - SCRIPT INFORMATION - """

"""
@file_name: get_videos.py
@author: Dylan "dyl-m" Monfret

For more information, see get_videos.py file.
"""

music_channels_test = "PocketTube_DB.json"
playlist_ids_json = "temp_playlist.json"

today = datetime.today()
a_date = "2020-11-12 10:48:19"
prev_date = datetime.strptime(a_date, '%Y-%m-%d %H:%M:%S')

gv.execution(path_channel_data_base_json=music_channels_test,
             path_playlist_ids_json=playlist_ids_json,
             latest_date=today,
             oldest_date=prev_date,
             short_vid_index="music",
             long_vid_index="mix")
