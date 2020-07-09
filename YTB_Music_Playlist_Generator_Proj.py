# -*- coding: utf-8 -*-

import json
import sys
import webbrowser
from apiclient.discovery import build
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
2. Récupération des vidéos entre 2 dates souhaitées.
3. Ouverture des playlists temporaires non-modifiables.
4. Création & ouverture des playlists temporaires modifiables.

# La phase 4 est a éxécuté après un traitement préalable dans un naviguateur web pouvant gérer facilement des favoris.
"""

""" - ELEMENTS PREPARATOIRE - """

reader = open("API_KEY.txt", "r")
api_key = reader.read()
youtube = build('youtube', version='v3', developerKey=api_key)

""" - FONCTION LOCALES - """


def music_channel_in_json(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)
    return_lst = data["MUSIQUE"]
    return return_lst


def get_channel_videos(channel_id):
    res = youtube.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    lst_of_videos = []
    next_page_token = None

    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        lst_of_videos += res['items']
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break

    return lst_of_videos


def video_selection(original_list, up_date, down_date):
    return_list = []
    a_year_list = []
    a_year_ago = datetime.today() - relativedelta(years=1)
    print("Number of video to manage : {}".format(len(original_list)))
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
    print("Number of channel to explore : {}\n".format(len(channel_list)))
    all_channels_content = []
    for channelid in channel_list:
        print("[CHANNEL] Progress : {} out of {}".format(channel_list.index(channelid) + 1, len(channel_list)))
        content_raw = get_channel_videos(channelid)
        selection_lists = video_selection(content_raw, up_date, down_date)
        content_reformat = selection_lists[0]
        a_year_len = selection_lists[1]
        all_channels_content += content_reformat
        if a_year_len == 0:
            status = "CHANNEL n°{} (ID: {}) DONE.\nStatus: INACTIVE\n".format(channel_list.index(channelid) + 1,
                                                                              channelid)
            webbrowser.open("https://www.youtube.com/channel/{}".format(channelid))
        else:
            status = "CHANNEL n°{} (ID: {}) DONE.\nStatus: ACTIVE ({} video(s) in a year)\nNumber of video(s)" \
                     " selected: {}.\n".format(channel_list.index(channelid) + 1, channelid, a_year_len,
                                               len(content_reformat))
        print(status)
    return all_channels_content


def open_lot_url(list_of_url):
    for url in list_of_url:
        webbrowser.open(url)


def temp_playlist_builder(list_videos):
    str_ids = ""
    list_of_playlist = []
    for element in list_videos:
        modulo = (list_videos.index(element) + 1) % 50
        if list_videos.index(element) + 1 != len(list_videos) and modulo != 0:
            str_ids += "{},".format(element["id"])
        else:
            str_ids += "{}|".format(element["id"])
    ids_lists = str_ids.split("|")
    ids_lists.remove("")
    for id_chain in ids_lists:
        playlist_txt_format = "http://www.youtube.com/watch_videos?video_ids={}".format(id_chain)
        list_of_playlist.append(playlist_txt_format)
    to_print = "Temporal playlists created.\nNumber of temp. playlist : {}\nNumber of videos : {}".format(
        len(list_of_playlist), len(list_videos))
    print(to_print)
    open_lot_url(list_of_playlist)
    return list_of_playlist


def open_edited_url(url_file_path):
    list_of_edited_pl = []
    f = open("{}.txt".format(url_file_path), "r")
    text = f.read()
    lst_pl_url = text.split("\n")
    for link in lst_pl_url:
        list_of_edited_pl.append("https://www.youtube.com/playlist?list={}&disable_polymer=true".format(link[-26:]))
    open_lot_url(list_of_edited_pl)


def managing_db(channel_data_base, date_sup, date_inf):
    return_list = []
    born_inf = 0
    born_sup = 10
    while born_inf <= len(channel_data_base):
        if born_sup + 1 > len(channel_data_base):
            print("Channel {} to {}\n".format(born_inf + 1, len(channel_data_base)))
            return_list += get_all_videos(channel_data_base[born_inf:], date_sup, date_inf)
            born_inf += 10
        else:
            print("Channel {} to {}\n".format(born_inf + 1, born_sup))
            return_list += get_all_videos(channel_data_base[born_inf:born_sup], date_sup, date_inf)
            born_inf += 10
            born_sup += 10
    return return_list


""" - PROGRAMME PRINCIPAL - """

""" - 1. Récupération de la liste des chaine YouTube -  """

channel_db = music_channel_in_json("PocketTube_DB.json")

""" - 2. Récupération des vidéos entre 2 dates souhaitées -  """

today = datetime.today()

""" Exemple de format : """
# prev_date = today - timedelta(days=2)
prev_date = datetime.strptime("2020-06-27 12:48:13", '%Y-%m-%d %H:%M:%S')
# Dernière date : 2020-07-03 15:48:41

""" - 3. Ouverture des playlists temporaires non-modifiables -  """

# orig_stdout = sys.stdout
# with open('Logs/Log_{:%Y-%m-%d_%H.%M.%S}.txt'.format(today), 'w', encoding="utf-8") as file:
#     sys.stdout = file
#     final_list = managing_db(channel_db, today, prev_date)
#     print(temp_playlist_builder(final_list))
#     print("")
#     print("Execution date: {:%Y-%m-%d %H:%M:%S}".format(today))
#     sys.stdout = orig_stdout
#     file.close()

""" - 4. Création & ouverture des playlists temporaires modifiables -  """

# open_edited_url("url_playlist")
