# -*- coding: utf-8 -*-

import json
import webbrowser

from datetime import datetime, timedelta  # , timezone
from dateutil import tz
from dateutil.relativedelta import relativedelta
from Google import Create_Service
from googleapiclient.errors import HttpError
from isodate import parse_duration
from os import listdir, remove
from os.path import isfile, join, getctime
from pprint import pformat  # , pprint
from time import sleep

# import os
# import numpy as np

""" - CREDITS -

Channel database with categories created with https://yousub.info/, PocketTube - YouTube Subs. Manager. application.

Video retrieving function ('api_get_channel_videos') by "Indian Pythonista".

Original code: https://github.com/nikhilkumarsingh/YouTubeAPI-Examples/blob/master/4.Channel-vid.ipynb
GitHub: https://github.com/nikhilkumarsingh
YouTube: https://www.youtube.com/channel/UCkUq-s6z57uJFUFBvZIVTyg
"""

""" - SCRIPT INFORMATION -

@file_name: get_videos.py
@author: Dylan "dyl-m" Monfret

Objective: create a script able to capture videos from YouTube music channels between 2 dates to make two
personal playlists. The first one containing short videos, and the second one containing longer videos (by default,
music / mixes).

Summary

1. Import a list of music YouTube channel URLs and URLS of temporary playlists (see JSON files).
2. Retrieve videos between 2 desired dates.
3. Sorting videos according to their length.
4. Adding videos to the associated temporary playlists.
"""

" - PREPARATORY ELEMENTS - "

channels_url_exception = {"UC4YCVy0ggUoFd2NVU2z04WA",
                          'UCh8awPsk105z9y9-BwEduGw',
                          'UC3hV4vnwzTUPSb7CAx4mXvg',
                          'UCbAEthmNnJk8JVZP8FWXqZg',
                          'UC2ZsqkwvxEpw-aYAIJHTRDg',
                          'UCU3ba7mBFprROpg1hJK7e_g'}  # Possible inactive channels to ignore.

# channels_ignored = {'UC0n9yiP-AD2DpuuYCDwlNxQ'}
channels_ignored = {''}

" - LOCAL FUNCTIONS - "


def api_get_channel_videos(a_channel_id, api_service):
    """Get all videos published / uploaded by a YouTube channel. Public, unlisted and premiere type videos will be
    retrieved by this function.

    :param a_channel_id: A channel ID (https://www.youtube.com/channel/[THIS PART]).
    :param api_service: API Google Token generated with Google.py call.
    :return: All video uploaded to this channel.
    """
    lst_of_videos = []
    next_page_token = None

    request = api_service.channels().list(id=a_channel_id, part='contentDetails').execute()
    playlist_id = request['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    try:
        while 1:

            request = api_service.playlistItems().list(playlistId=playlist_id, part=['snippet', 'contentDetails'],
                                                       maxResults=50,
                                                       pageToken=next_page_token).execute()
            lst_of_videos += request['items']
            next_page_token = request.get('nextPageToken')

            if next_page_token is None:
                break

    except HttpError:
        pass

    return lst_of_videos


def api_get_videos_duration(list_videos_ids, api_service):
    """Get the duration of 50 videos at once.

    :param list_videos_ids: A list of video IDs, maximum size 50.
    :param api_service: API Google Token generated with Google.py call.
    :return: a dictionary associating video id and duration of said video.
    """
    durations = []

    chunks50 = divide_chunks(list_videos_ids, 50)

    for chunk in chunks50:
        request = api_service.videos().list(id=",".join(chunk), part='contentDetails', maxResults=50).execute()
        durations += [parse_duration(element["contentDetails"]["duration"]) for element in request["items"]]

    id_and_duration = dict(zip(list_videos_ids, durations))

    return id_and_duration


def api_add_to_playlist(playlist_id, ids_list, api_service):
    """Add selected video to a playlist.

    :param playlist_id: A specified playlist ID.
    :param ids_list: List of videos' ID
    :param api_service: API Google Token generated with Google.py call.
    :return: small text for logs.
    """
    if ids_list:

        to_print = f"Estimated cost: {len(ids_list) * 50}\n"
        print(to_print)

        cpt = 1

        for video_id in ids_list:

            print(f"{cpt:02d}. Adding https://www.youtube.com/watch?v={video_id}...")

            sleep(1 + (cpt - 1) / 10)
            cpt += 1

            the_body = {"snippet": {"playlistId": playlist_id,
                                    "resourceId": {"videoId": video_id, "kind": "youtube#video"}}}

            success = False

            while not success:
                try:
                    api_service.playlistItems().insert(part="snippet", body=the_body).execute()
                    success = True

                except ConnectionResetError:
                    print("ConnectionResetError: let me sleep for 5 seconds, just enough time to recover...")
                    sleep(5)

                except HttpError:

                    error_message = f"Problem encountered with this video: https://www.youtube.com/watch?v={video_id}"
                    print(error_message)
                    to_print += error_message + '\n'
                    success = True

    else:
        to_print = "No video in this list.\n"

    return to_print


def divide_chunks(a_list, n):
    """Divide a list into chunks of size n.

    :param a_list: an entry list.
    :param n: size of each chunk.
    :return: chunks in a list object.
    """
    return [a_list[i:i + n] for i in range(0, len(a_list), n)]


def get_channel_list(json_path, category):
    """Get the list of channel to explore.

    :param json_path: the file path to the .json file with channels' IDs, classified by categories (such as "MUSIQUE").
    :param category: a channel category to explore.
    :return: the list of channel's id in the said category.
    """
    with open(json_path) as json_file:
        data = json.load(json_file)

    channel_ids_list = data[category]

    return channel_ids_list


def read_json(json_path):
    """Read JSON files.

    :param json_path: file path to JSON file.
    :return: file data as list / dict.
    """
    with open(json_path) as json_file:
        data = json.load(json_file)

    return data


def video_in_period(latest_date, oldest_date, video_date):
    """Return a Boolean indicating if a said video was uploaded in a specified period.

    :param latest_date: Upper bound of time interval.
    :param oldest_date: Lower bound of time interval.
    :param video_date: video's upload date, in ISO 8601 format, corresponding to UTC+00 (GMT) timezone.
    :return: True / False depending if the video's upload date is defined period or not.
    """
    tz_local = tz.tzlocal()

    latest_date_utc = latest_date.astimezone(tz_local)
    oldest_date_utc = oldest_date.astimezone(tz_local)

    if oldest_date_utc <= video_date <= latest_date_utc:
        return True
    return False


def video_selection(api_videos_list, latest_date, oldest_date):
    """Give videos uploaded by a channel in a specified period and the number of videos upload in a year.

    :param api_videos_list: list of videos got from 'api_get_channel_videos' function.
    :param latest_date: Upper bound of time interval. (Corresponding with 'video_in_period' function)
    :param oldest_date: Lower bound of time interval. (Corresponding with 'video_in_period' function)
    :return: a dictionary containing selected videos and number of video uploaded in a year.
    """
    if api_videos_list:
        channel_name = api_videos_list[0]["snippet"]["channelTitle"]  # Get the channel name to write into logs.

        selection_list = []
        a_year_ago_count = int()
        a_year_ago = datetime.today() - relativedelta(years=1)

        # cpt_test = 1

        for video in api_videos_list:

            try:
                # Convert date string in ISO 8601 format into a datetime object.
                upload_date = datetime.strptime(video["contentDetails"]["videoPublishedAt"], "%Y-%m-%dT%H:%M:%S%z")

                if video_in_period(latest_date, oldest_date, upload_date):
                    selection_list.append(video["snippet"]["resourceId"]["videoId"])

                if video_in_period(latest_date, a_year_ago, upload_date):
                    a_year_ago_count += 1

            except KeyError:
                webbrowser.open(f'https://www.youtube.com/watch?v={video}')

            # cpt_test += 1

        return {"selection_list": selection_list, "a_year_ago_count": a_year_ago_count, "channel_name": channel_name}

    else:

        return {"selection_list": [], "a_year_ago_count": 0, "channel_name": 'No Video so No Name lol'}


def get_all_videos(channel_ids_list, latest_date, oldest_date, api_service):
    """Get all videos from all channels in selected category. The function will also open in a web browser inactive
    YouTube channel link (one year without a video).

    :param channel_ids_list: list of channel from 'get_channel_list'.
    :param latest_date: Upper bound of time interval. (Corresponding with 'video_in_period' function)
    :param oldest_date: Lower bound of time interval. (Corresponding with 'video_in_period' function)
    :param api_service: API Google Token generated with Google.py call.
    :return: a dictionary containing list of video's id and information to write into log.
    """
    log_str = str()
    all_video_ids = []
    count = int()
    ignored_report = []

    nb_channels = len(channel_ids_list)

    for channel_id in channel_ids_list:
        count += 1

        channel_selection = video_selection(api_get_channel_videos(channel_id, api_service), latest_date, oldest_date)

        to_print = f"Channel {count} out of {nb_channels} ({count * 100 / nb_channels:.2f} %).\n\n" \
                   f"Channel ID: {channel_id}\n" \
                   f"Channel Name: {channel_selection['channel_name']}\n\n" \
                   f"Number of selected videos: {len(channel_selection['selection_list'])}\n"

        if channel_id in channels_ignored or len(channel_selection['selection_list']) * 50 > 800:
            to_print += f"Number of videos uploaded in a year: {channel_selection['a_year_ago_count']}\n" \
                        f"STATUS: IGNORED\n"
            if channel_id in channels_ignored:
                ignored_report.append({'channel_id': channel_id,
                                       'channel_name': channel_selection['channel_name'],
                                       'cause': 'In ignored set.',
                                       'n': len(channel_selection['selection_list'])})
            else:
                ignored_report.append({'channel_id': channel_id,
                                       'cause': 'To many videos selected',
                                       'n': len(channel_selection['selection_list'])})

        elif channel_selection["a_year_ago_count"] != 0:
            to_print += f"Number of videos uploaded in a year: {channel_selection['a_year_ago_count']}\n" \
                        f"STATUS: ACTIVE\n"
            all_video_ids += channel_selection["selection_list"]

        else:
            to_print += "Number of videos uploaded in a year: 0\n" \
                        "STATUS: INACTIVE\n"

            if channel_id not in channels_url_exception:
                # Ignore exceptions.
                webbrowser.open(f"https://www.youtube.com/channel/{channel_id}")

        to_print += f"\nTotal number of videos selected so far: {len(all_video_ids)}\n{'/' * 50}\n"

        log_str += f"{to_print}\n"

        for ignored_elem in ignored_report:
            log_str += f'Channel "{ignored_elem["channel_name"]}"' \
                       f' ({ignored_elem["channel_id"]}) ignored - ' \
                       f'Cause: {ignored_elem["cause"]} - N_Videos: {ignored_elem["n"]}\n'

        print(to_print)

    if len(all_video_ids) * 50 > 8000:
        print("Warning! API cost could be higher than 8000.")
        log_str += "\nWarning! API cost could be higher than 8000."

    return {"all_video_ids": all_video_ids, "log_str": log_str}


def duration_filter(dict_ids_and_durations, minute_threshold):
    """Sort short and long videos in two list.

    :param dict_ids_and_durations: dictionary of video's id and associated duration (from 'api_get_videos_duration').
    :param minute_threshold: minimum number of minutes to consider a video as a long video (10 minutes by default).
    :return: dictionary separating short and long videos.
    """
    delta_sec = minute_threshold * 60  # Threshold passed in second to fit 'timedelta'.

    short_videos = [key for key, value in dict_ids_and_durations.items() if value <= timedelta(seconds=delta_sec)]
    long_videos = [key for key, value in dict_ids_and_durations.items() if value > timedelta(seconds=delta_sec)]

    to_print = f"- END OF THE RETRIEVING PROCESS -\n\n" \
               f"Number of short videos: {len(short_videos)}\n" \
               f'{pformat([f"https://www.youtube.com/watch?v={element}" for element in short_videos])}\n\n' \
               f"Number of long videos: {len(long_videos)}\n" \
               f'{pformat([f"https://www.youtube.com/watch?v={element}" for element in long_videos])}\n'

    print(to_print)

    return {"short_videos": short_videos, "long_videos": long_videos, "logs": to_print}


def clean_logs(directory):
    """Clean oldest log files.

    :param directory: Logs folder path.
    :return: short string saying if some logs were removed or not.
    """
    to_log = str()
    files = [{"file_name": f"{directory}/{file}", "creation_date": getctime(f"{directory}/{file}")} for file in
             listdir(f"{directory}") if isfile(join(f"{directory}", file))][:-9]

    if not files:

        print("No log removed.")
        to_log += "No log removed."

    else:

        for file in files:
            remove(file["file_name"])
            print(f"{file['file_name']} removed!")
            to_log += f"{file['file_name']} removed!\n"

    return to_log


def execution(path_channel_data_base_json, path_playlist_ids_json, latest_date, oldest_date, api_service,
              selected_category="MUSIQUE", short_vid_index="music", long_vid_index="mix", min_dur_long_vid=10):
    """Execute the whole process.

    :param path_channel_data_base_json: file path to channel data_base. (Corresponding with 'get_channel_list' function)
    :param path_playlist_ids_json: file path to playlists URL. (Corresponding with 'read_json' function)
    :param latest_date: Upper bound of time interval. (Corresponding with 'get_all_videos' function)
    :param oldest_date: Lower bound of time interval. (Corresponding with 'get_all_videos' function)
    :param api_service: API Google Token generated with Google.py call.
    :param selected_category: channel's category to explore ("MUSIQUE" by default, feel free to change it).
                              (Corresponding with 'get_channel_list' function)
    :param short_vid_index: key value corresponding to short videos playlist in 'playlist_ids_json' file ("music by
                            default, feel free to change it).
    :param long_vid_index: key value corresponding to long videos playlist in 'playlist_ids_json' file ("mix" by
                           default, feel free to change it).
    :param min_dur_long_vid: minimum duration to consider that a video is long (10 minutes by default, feel free to
                              change it). (Corresponding with 'minute_threshold' argument in 'duration_filter' function)
    """
    today_date = datetime.today()

    log = f"Date of execution: {today_date:%Y-%m-%d %H:%M:%S}\n" \
          f"Latest Date: {latest_date:%Y-%m-%d %H:%M:%S}\n" \
          f"Oldest Date: {oldest_date:%Y-%m-%d %H:%M:%S}\n\n"

    print(log)

    music_channels = get_channel_list(path_channel_data_base_json, category=selected_category)
    playlist_ids = read_json(path_playlist_ids_json)

    all_vid = get_all_videos(music_channels, latest_date=latest_date, oldest_date=oldest_date, api_service=api_service)
    log += f'{all_vid["log_str"]}\n'

    duration_dict = api_get_videos_duration(all_vid["all_video_ids"], api_service)

    duration_filter_dict = duration_filter(duration_dict, minute_threshold=min_dur_long_vid)
    log += f'{duration_filter_dict["logs"]}\n'

    print("Adding videos into playlists...\n")
    log += "Adding videos into playlists...\n\n"

    log_short_vid_text = api_add_to_playlist(playlist_ids[short_vid_index], duration_filter_dict["short_videos"],
                                             api_service)
    log += f'{log_short_vid_text}\n'

    log_long_vid_text = api_add_to_playlist(playlist_ids[long_vid_index], duration_filter_dict["long_videos"],
                                            api_service)
    log += f'{log_long_vid_text}\n'

    print("- ALL DONE! -\n")
    log += "- ALL DONE! -\n"

    log += f"\n{clean_logs('../Logs')}"

    with open(f'../Logs/Log_{today_date:%Y-%m-%d_%H.%M.%S}.txt', 'w', encoding="utf-8") as file:
        file.write(log)

    sleep(5)

    webbrowser.open(f"https://www.youtube.com/playlist?list={playlist_ids[short_vid_index]}")
    webbrowser.open(f"https://www.youtube.com/playlist?list={playlist_ids[long_vid_index]}")


" - MAIN PROGRAM -"

if __name__ == "__main__":
    CLIENT_SECRET_FILE = '../files/code_secret_client.json'
    API_NAME = 'YouTube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube']

    my_service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

    music_channels_test = "../files/PocketTube_DB.json"
    playlist_ids_json = "../files/temp_playlist.json"

    today = datetime.today()
    a_date = today - timedelta(days=7)
    prev_date = datetime.strftime(a_date, '%Y-%m-%d %H:%M:%S')

    execution(path_channel_data_base_json=music_channels_test,
              path_playlist_ids_json=playlist_ids_json,
              latest_date=today,
              oldest_date=prev_date,
              api_service=my_service,
              selected_category="MUSIQUE",
              short_vid_index="music",
              long_vid_index="mix",
              min_dur_long_vid=10)
