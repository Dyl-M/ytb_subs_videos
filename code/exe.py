# -*- coding: utf-8 -*-

import get_videos as gv
import glob
import os
import re
from datetime import datetime
from Google import create_service

"""- SCRIPT INFORMATION -

@file_name: exe.py
@author: Dylan "dyl-m" Monfret

For more information, see 'get_videos.py' file.
"""

" - Google Service Creation - "

CLIENT_SECRET_FILE = '../files/code_secret_client_2.json'
API_NAME = 'YouTube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

service = create_service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

" - Local Functions - "


def get_last_exe_date(logs_directory):
    """Get the last script execution date from logs' directory (so from most recent log file).

    :param logs_directory: Logs' directory.
    :return: last execution date as datetime.datetime object.
    """
    list_of_files = glob.glob(f'{logs_directory}/*')
    latest_file = max(list_of_files, key=os.path.getctime)

    with open(f'{latest_file}', 'r', encoding="utf8") as f:
        first_line = f.readline()

    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', first_line)
    date = datetime.strptime(match.group(), '%Y-%m-%d %H:%M:%S')

    return date


" - Main - "

music_channels = "../files/PocketTube_DB.json"
playlist_ids_json = "../files/temp_playlist.json"

today = datetime.today()

# a_date = "2020-01-01 00:00:00"
# previous_date = datetime.strptime(a_date, '%Y-%m-%d %H:%M:%S')

previous_date = get_last_exe_date("../Logs")

gv.execution(path_channel_data_base_json=music_channels,
             path_playlist_ids_json=playlist_ids_json,
             latest_date=today,
             oldest_date=previous_date,
             api_service=service,
             selected_category="MUSIQUE",
             short_vid_index="music",
             long_vid_index="mix")
