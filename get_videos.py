# -*- coding: utf-8 -*-

import json
import numpy as np
import os
import webbrowser
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta
from Google import Create_Service
from isodate import parse_duration
from os import listdir, remove
from os.path import isfile, join, getctime
from pprint import pformat
from time import sleep

""" - CREDITS - """

"""
Channel database with categories created with https://yousub.info/, PocketTube - YouTube Subs. Manager. application.

Video retrieving function ('api_get_channel_videos') by "Indian Pythonista".

Original code: https://github.com/nikhilkumarsingh/YouTubeAPI-Examples/blob/master/4.Channel-Vids.ipynb
GitHub: https://github.com/nikhilkumarsingh
YouTube: https://www.youtube.com/channel/UCkUq-s6z57uJFUFBvZIVTyg
"""

""" - SCRIPT INFORMATION - """

"""
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

""" - PREPARATORY ELEMENTS - """

CLIENT_SECRET_FILE = 'code_secret_client.json'
API_NAME = 'youtube'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/youtube']

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

# Possible inactive channels to ignore.
channels_url_exeception = {"UC4YCVy0ggUoFd2NVU2z04WA", 'UCh8awPsk105z9y9-BwEduGw'}

""" - LOCAL FUNCTIONS - """


def api_get_channel_videos(a_channel_id):
    """
    A function to get all videos published / uploaded by a YouTube channel. Public, unlisted and premiere type videos
    will be retrieved by this function.

    :param a_channel_id: A channel ID (https://www.youtube.com/channel/[THIS PART]).
    :return: All video uploaded to this channel.
    """

    lst_of_videos = list()
    next_page_token = None

    request = service.channels().list(id=a_channel_id, part='contentDetails').execute()
    playlist_id = request['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    while 1:

        request = service.playlistItems().list(playlistId=playlist_id, part='snippet', maxResults=50,
                                               pageToken=next_page_token).execute()
        lst_of_videos += request['items']
        next_page_token = request.get('nextPageToken')

        if next_page_token is None:
            break

    return lst_of_videos


def api_get_videos_duration(list_videos_ids):
    """
    A function to get the duration of 50 videos at once.

    :param list_videos_ids: A list of video IDs, maximum size 50.
    :return: a dictionary associating video id and duration of said video.
    """
    durations = list()
    chunks50 = [list(sub_list) for sub_list in
                np.array_split(np.array(list_videos_ids), len(list_videos_ids) // 50 + 1)]

    for chunk in chunks50:
        request = service.videos().list(id=",".join(chunk), part='contentDetails', maxResults=50).execute()
        durations += [parse_duration(element["contentDetails"]["duration"]) for element in request["items"]]

    id_and_duration = {video_id: duration for video_id, duration in zip(list_videos_ids, durations)}

    return id_and_duration


def api_add_to_playlist(playlist_id, ids_list):
    """
    A function to add selected video to a playlist.

    :param playlist_id: A specified playlist ID.
    :param ids_list: List of videos's ID
    :return: small text for logs.
    """

    if ids_list:
        to_print = f"Estimated cost: {len(ids_list) * 50}\n"
        print(to_print)
        sleep(1)
        for video_id in ids_list:
            the_body = {
                "snippet": {"playlistId": playlist_id, "resourceId": {"videoId": video_id, "kind": "youtube#video"}}}

            service.playlistItems().insert(part="snippet", body=the_body).execute()
        return to_print
    else:
        to_print = "No video in this list.\n"
    return to_print


def get_channel_list(json_path, category):
    """
    A function to get the list of channel to explore.

    :param json_path: the file path to the .json file with channels' IDs, classified by categories (such as "MUSIQUE").
    :param category: a channel category to explore.
    :return: the list of channel's id in the said category.
    """

    with open(json_path) as json_file:
        data = json.load(json_file)

    channel_ids_list = data[category]

    return channel_ids_list


def read_json(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)

    return data


def video_in_period(latest_date, oldest_date, video_date):
    """
    A function returning a Boolean indicating if a said video was uploaded in a specified period.

    :param latest_date: Upper bound of time interval.
    :param oldest_date: Lower bound of time interval.
    :param video_date: video's upload date, in ISO 8601 format, corresponding to UTC+00 (GMT) timezone.
    :return: True / False depending if the video's upload date is defined period or not.
    """

    # Date transposed to UTC timezone.
    latest_date_utc = latest_date.astimezone(tz=timezone.utc).replace(tzinfo=None)
    oldest_date_utc = oldest_date.astimezone(tz=timezone.utc).replace(tzinfo=None)

    if oldest_date_utc <= video_date <= latest_date_utc:
        return True
    else:
        return False


def video_selection(api_videos_list, latest_date, oldest_date):
    """
    A function giving videos uploaded by a channel in a specified period and the number of videos upload in a year.

    :param api_videos_list: list of videos got from 'api_get_channel_videos' function.
    :param latest_date: Upper bound of time interval. (Corresponding with 'video_in_period' function)
    :param oldest_date: Lower bound of time interval. (Corresponding with 'video_in_period' function)
    :return: a dictionary containing selected videos and number of video uploaded in a year.
    """

    # Get the channel name to write into logs.
    channel_name = api_videos_list[0]["snippet"]["channelTitle"]

    selection_list = list()
    a_year_ago_count = int()
    a_year_ago = datetime.today() - relativedelta(years=1)

    for video in api_videos_list:

        # Convert date string in ISO 8601 format into a datetime object.
        upload_date = datetime.strptime(video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")

        if video_in_period(latest_date, oldest_date, upload_date):
            selection_list.append(video["snippet"]["resourceId"]["videoId"])

        if upload_date >= a_year_ago:
            a_year_ago_count += 1

    return {"selection_list": selection_list, "a_year_ago_count": a_year_ago_count, "channel_name": channel_name}


def get_all_videos(channel_ids_list, latest_date, oldest_date):
    """
    A function to get all videos from all channels in selected category. The function will also open in a web browser
    inactive YouTube channel link (one year without a video).

    :param channel_ids_list: list of channel from 'get_channel_list'.
    :param latest_date: Upper bound of time interval. (Corresponding with 'video_in_period' function)
    :param oldest_date: Lower bound of time interval. (Corresponding with 'video_in_period' function)
    :return: a dictionary containing list of video's id and information to write into log.
    """

    log_str = str()
    all_video_ids = list()
    count = int()

    nb_channels = len(channel_ids_list)

    for channel_id in channel_ids_list:
        count += 1

        channel_selection = video_selection(api_get_channel_videos(channel_id), latest_date, oldest_date)
        all_video_ids += channel_selection["selection_list"]

        to_print = f"Channel {count} out of {nb_channels} ({count * 100 / nb_channels:.2f} %).\n\n" \
                   f"Channel ID: {channel_id}\n" \
                   f"Channel Name: {channel_selection['channel_name']}\n\n" \
                   f"Number of selected videos: {len(channel_selection['selection_list'])}\n"

        if channel_selection["a_year_ago_count"] != 0:
            to_print += f"Number of videos uploaded in a year: {channel_selection['a_year_ago_count']}\n" \
                        f"STATUS: ACTIVE\n"
        else:
            to_print += f"Number of videos uploaded in a year: 0\n" \
                        f"STATUS: INACTIVE\n"
            if channel_id not in channels_url_exeception:
                # Ignore exceptions.
                webbrowser.open(f"https://www.youtube.com/channel/{channel_id}")

        to_print += f"\nTotal number of videos selected so far: {len(all_video_ids)}\n{'/' * 50}\n"

        log_str += f"{to_print}"
        print(to_print)

    if len(all_video_ids) * 50 > 8000:
        print("Warning! API cost could be higher than 8000.")
        log_str += "\nWarning! API cost could be higher than 8000."

    return {"all_video_ids": all_video_ids, "log_str": log_str}


def duration_filter(dict_ids_and_durations, minute_threshold):
    """
    A function to sort short and long videos in two list.

    :param dict_ids_and_durations: dictionary of video's id and associated duration (from 'api_get_videos_duration').
    :param minute_threshold: minimum number of minutes to consider a video as a long video (10 minutes by default).
    :return: dictionary separating short and long videos.
    """

    # Threshold passed in second to fit 'timedelta'.
    delta_sec = minute_threshold * 60

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
    """
    A function clean oldest log files.

    :param directory: Logs folder path.
    :return: short string saying if some logs were removed or not.
    """
    to_log = str()
    files = [{"file_name": f"{directory}/{file}", "date_crea": getctime(f"{directory}/{file}")} for file in
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


def execution(path_channel_data_base_json, path_playlist_ids_json, latest_date, oldest_date,
              selected_category="MUSIQUE", short_vid_index="music", long_vid_index="mix", min_dur_long_vids=10):
    """
    Full execution of the process.

    :param path_channel_data_base_json: file path to channel data_base. (Corresponding with 'get_channel_list' function)
    :param path_playlist_ids_json: file path to playlists URL. (Corresponding with 'read_json' function)
    :param latest_date: Upper bound of time interval. (Corresponding with 'get_all_videos' function)
    :param oldest_date: Lower bound of time interval. (Corresponding with 'get_all_videos' function)
    :param selected_category: channel's category to explore ("MUSIQUE" by default, feel free to change it).
                              (Corresponding with 'get_channel_list' function)
    :param short_vid_index: key value corresponding to short videos playlist in 'playlist_ids_json' file ("music by
                            default, feel free to change it).
    :param long_vid_index: key value corresponding to long videos playlist in 'playlist_ids_json' file ("mix" by
                           default, feel free to change it).
    :param min_dur_long_vids: minimum duration to consider that a video is long (10 minutes by default, feel free to
                              change it). (Corresponding with 'minute_threshold' argument in 'duration_filter' function)
    """

    today_date = datetime.today()

    log = f"Date of execution: {today_date:%Y-%m-%d %H:%M:%S}\n" \
          f"Latest Date: {latest_date:%Y-%m-%d %H:%M:%S}\n" \
          f"Oldest Date: {oldest_date:%Y-%m-%d %H:%M:%S}\n\n"

    print(log)

    music_channels = get_channel_list(path_channel_data_base_json, category=selected_category)
    playlist_ids = read_json(path_playlist_ids_json)

    all_vids = get_all_videos(music_channels, latest_date=latest_date, oldest_date=oldest_date)
    log += f'{all_vids["log_str"]}\n'

    duration_dict = api_get_videos_duration(all_vids["all_video_ids"])

    duration_filter_dict = duration_filter(duration_dict, minute_threshold=min_dur_long_vids)
    log += f'{duration_filter_dict["logs"]}\n'

    print("Adding videos into playlists...\n")
    log += "Adding videos into playlists...\n\n"

    log_short_vid_text = api_add_to_playlist(playlist_ids[short_vid_index], duration_filter_dict["short_videos"])
    log += f'{log_short_vid_text}\n'

    log_long_vid_text = api_add_to_playlist(playlist_ids[long_vid_index], duration_filter_dict["long_videos"])
    log += f'{log_long_vid_text}\n'

    print("- ALL DONE! -\n")
    log += "- ALL DONE! -\n"

    log += f"\n{clean_logs('Logs')}"

    with open(f'Logs/Log_{today_date:%Y-%m-%d_%H.%M.%S}.txt', 'w', encoding="utf-8") as file:
        file.write(log)

    sleep(5)

    webbrowser.open(f"https://www.youtube.com/playlist?list={playlist_ids[short_vid_index]}")
    webbrowser.open(f"https://www.youtube.com/playlist?list={playlist_ids[long_vid_index]}")


" - MAIN PROGRAM -"

if __name__ == "__main__":
    music_channels_test = "PocketTube_DB.json"
    playlist_ids_json = "temp_playlist.json"

    today = datetime.today()
    a_date = today - timedelta(days=7)
    prev_date = datetime.strptime(a_date, '%Y-%m-%d %H:%M:%S')

    execution(path_channel_data_base_json=music_channels_test,
              path_playlist_ids_json=playlist_ids_json,
              latest_date=today,
              oldest_date=prev_date,
              selected_category="MUSIQUE",
              short_vid_index="music",
              long_vid_index="mix",
              min_dur_long_vids=10)
