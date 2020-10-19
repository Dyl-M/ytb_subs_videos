# -*- coding: utf-8 -*-


import json
import numpy as np
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import build
from isodate import parse_duration
from os import listdir, remove
from os.path import isfile, join, getctime

# import browserhistory as bh

""" - CREDITS - """

"""
Base de données de catégorie de chaîne par https://yousub.info/, application PocketTube - YouTube Subs. Manager.

Fonction de récupération des vidéos par "Indian Pythonista"

Code Original : https://github.com/nikhilkumarsingh/YouTubeAPI-Examples/blob/master/4.Channel-Vids.ipynb
GitHub : https://github.com/nikhilkumarsingh
YouTube : https://www.youtube.com/channel/UCkUq-s6z57uJFUFBvZIVTyg
"""

""" - INFORMATION DE SCRIPT """

"""
Nom : YTB_Music_Playlist_Generator_Proj.py
Objectif : créer un script capable de capter les vidéos des chaines YouTube musicales entre 2 dates pour en faire une
playlist d'écoute personelle.

Sommaire des phases

1. Importer une liste d'URL de chaine YouTube musicale (cf. dossier JSON).
<<2. Récupération des vidéos entre 2 dates souhaitées.
3. Ouverture des playlists temporaires non-modifiables.
4. Création & ouverture des playlists temporaires modifiables.

# La phase 4 est a éxécuté après un traitement préalable dans un naviguateur web pouvant gérer facilement des favoris.
"""

""" - ELEMENTS PREPARATOIRE - """

with open("API_KEY.txt", "r") as reader:
    api_key = reader.read()
    reader.close()

youtube = build('youtube', version='v3', developerKey=api_key)

id_excep = {"UCd-9JELFGru-WnXiCAZudbw", "UC4YCVy0ggUoFd2NVU2z04WA"}

""" - FONCTION LOCALES - """


def music_channel_in_json(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)
    return_lst = data["MUSIQUE"]
    return return_lst


def get_channel_videos(channel_id):
    res = youtube.channels().list(id=channel_id, part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    lst_of_videos = list()
    next_page_token = None

    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id, part='snippet', maxResults=50,
                                           pageToken=next_page_token).execute()
        lst_of_videos += res['items']
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break

    return lst_of_videos


def get_vid_duration(list_video_ids):
    res = youtube.videos().list(id=",".join(list_video_ids), part='contentDetails', maxResults=50).execute()
    durations = [parse_duration(element["contentDetails"]["duration"]) for element in res["items"]]
    return durations


def video_selection(original_list, up_date, down_date):
    return_list = list()
    a_year_list = list()
    a_year_ago = datetime.today() - relativedelta(years=1)
    print(f"Number of video to manage : {len(original_list)}")
    for video in original_list:
        date_org_format = video["snippet"]["publishedAt"].replace("T", " ").replace("Z", "").replace(".000", "")
        date_new_format = datetime.strptime(date_org_format, "%Y-%m-%d %H:%M:%S") + timedelta(hours=1)
        if down_date <= date_new_format <= up_date:
            return_list.append(
                {"id": video["snippet"]["resourceId"]["videoId"], "date": date_new_format,
                 "title": video["snippet"]["title"]})
        if a_year_ago <= date_new_format:
            a_year_list.append(
                {"id": video["snippet"]["resourceId"]["videoId"], "date": date_new_format,
                 "title": video["snippet"]["title"]})
    return [return_list, len(a_year_list)]


def get_all_videos(channel_list, up_date, down_date):
    print(f"Number of channels to explore : {len(channel_list)}\n")
    all_channels_content = list()
    for channelid in channel_list:
        print(f"[CHANNEL] Progress : {channel_list.index(channelid) + 1} out of {len(channel_list)}")
        content_raw = get_channel_videos(channelid)
        selection_lists = video_selection(content_raw, up_date, down_date)
        content_reformat = selection_lists[0]
        a_year_len = selection_lists[1]
        all_channels_content += content_reformat
        if a_year_len == 0:
            status = f"CHANNEL n°{channel_list.index(channelid) + 1} (ID: {channelid}) DONE.\nStatus: INACTIVE\n"
            if channelid not in id_excep:
                webbrowser.open(f"https://www.youtube.com/channel/{channelid}")
        else:
            status = f"CHANNEL n°{channel_list.index(channelid) + 1} (ID: {channelid}) DONE.\n" \
                     f"Status: ACTIVE ({a_year_len} video(s) in a year)\n" \
                     f"Number of videos selected: {len(content_reformat)}.\n"
        print(status)
    return all_channels_content


def open_lot_url(list_of_url):
    for url in list_of_url:
        webbrowser.open(url)


def temp_playlist_builder(videos_dict):
    music_playlists = list()
    mix_playlists = list()
    chunk_durations = list()
    all_ids = [video["id"] for video in videos_dict]
    chunck50 = [list(subl) for subl in np.array_split(np.array(all_ids), len(all_ids) // 50 + 1)]

    for a_chunk in chunck50:
        chunk_durations += get_vid_duration(a_chunk)

    duration_list = [{"id": an_id, "duration": dur} for an_id, dur in zip(all_ids, chunk_durations)]
    music_ids = [elem["id"] for elem in duration_list if elem["duration"] <= timedelta(seconds=1200)]
    mix_ids = [elem["id"] for elem in duration_list if elem["duration"] > timedelta(seconds=1200)]

    if music_ids:
        music_chunck50 = [list(subl2) for subl2 in np.array_split(np.array(music_ids), len(music_ids) // 50 + 1)]
        for a_chuck in music_chunck50:
            playlist_txt_format = f"http://www.youtube.com/watch_videos?video_ids={','.join(a_chuck)}"
            music_playlists.append(playlist_txt_format)
    else:
        music_ids = list()

    if mix_ids:
        mix_chunck50 = [list(subl3) for subl3 in np.array_split(np.array(mix_ids), len(mix_ids) // 50 + 1)]
        for a_chuck in mix_chunck50:
            playlist_txt_format = f"http://www.youtube.com/watch_videos?video_ids={','.join(a_chuck)}"
            mix_playlists.append(playlist_txt_format)
    else:
        mix_ids = list()

    to_print = f"Temporary playlists created.\n" \
               f"Number of temp. playlists : {len(music_playlists) + len(mix_playlists)}\n" \
               f"Number of potential music videos : {len(music_ids)}\n" \
               f"Number of potential mix videos : {len(mix_ids)}"

    print(to_print)
    if music_playlists:
        open_lot_url(music_playlists)
    if mix_playlists:
        open_lot_url(mix_playlists)
    return [music_playlists, mix_playlists]


def open_edited_url(url_file_path):
    list_of_edited_pl = list()
    f = open(f"{url_file_path}.txt", "r")
    text = f.read()
    lst_pl_url = text.split("\n")
    for link in lst_pl_url:
        list_of_edited_pl.append(f"https://www.youtube.com/playlist?list={link[49:77]}&disable_polymer=true")
    open_lot_url(list_of_edited_pl)


def managing_db(channel_data_base, date_sup, date_inf):
    return_list = list()
    born_inf = 0
    born_sup = 10
    while born_inf <= len(channel_data_base):
        if born_sup + 1 > len(channel_data_base):
            print(f"Channel {born_inf + 1} to {len(channel_data_base)}\n")
            return_list += get_all_videos(channel_data_base[born_inf:], date_sup, date_inf)
            born_inf += 10
        else:
            print(f"Channel {born_inf + 1} to {born_sup}\n")
            return_list += get_all_videos(channel_data_base[born_inf:born_sup], date_sup, date_inf)
            born_inf += 10
            born_sup += 10
    return return_list


def clean_logs(directory):
    files = [{"file_name": f"{directory}/{file}", "date_crea": getctime(f"{directory}/{file}")} for file in
             listdir(f"{directory}") if isfile(join(f"{directory}", file))][:-10]
    if not files:
        print("No log removed.")
    else:
        for file in files:
            remove(file["file_name"])
            print(f"{file['file_name']} removed!")


def execution(channel_database, date_sup, date_inf):
    orig_stdout = sys.stdout
    with open(f'Logs/Log_{today:%Y-%m-%d_%H.%M.%S}.txt', 'w', encoding="utf-8") as file:
        sys.stdout = file
        final_list = managing_db(channel_database, date_sup, date_inf)
        print(temp_playlist_builder(final_list))
        print("")
        print(f"Date of execution: {today:%Y-%m-%d %H:%M:%S}")
        sys.stdout = orig_stdout
        file.close()
    clean_logs("Logs")


""" - PROGRAMME PRINCIPAL - """

""" - 1. Récupération de la liste des chaine YouTube -  """

channel_db = music_channel_in_json("PocketTube_DB.json")

""" - 2. Récupération des vidéos entre 2 dates souhaitées -  """

today = datetime.today()

""" Exemple de format : """
# prev_date = today - timedelta(days=2)
a_date = "2020-10-15 19:33:28"
prev_date = datetime.strptime(a_date, '%Y-%m-%d %H:%M:%S')

""" - 3. Ouverture des playlists temporaires non-modifiables -  """

# execution(channel_db, today, prev_date)

""" - 4. Création & ouverture des playlists temporaires modifiables -  """

# open_edited_url("url_playlist")

# print(dict_obj)
# print(dict_obj['chrome'][0:10])
