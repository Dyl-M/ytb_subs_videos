# -*- coding: utf-8 -*-

from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json
import webbrowser

""" - CREDITS - """

# Base de données de catégorie de chaîne par https://yousub.info/, application PocketTube - YouTube Subs. Manager.

# Fonction de récupération des vidéos par "Indian Pythonista"

# Code Original : https://github.com/nikhilkumarsingh/YouTubeAPI-Examples/blob/master/4.Channel-Vids.ipynb
# GitHub : https://github.com/nikhilkumarsingh
# YouTube : https://www.youtube.com/channel/UCkUq-s6z57uJFUFBvZIVTyg

""" - INFORMATION DE SCRIPT """

# Nom : YTB_Music_Playlist_Generator_Proj.py
# Objectif : créer un script capable de capter les vidéos des chaines YouTube musicales entre 2 dates pour en faire une
# playlist d'écoute personelle.

# Sommaire des phases

# 1. Importer une liste d'URL de chaine YouTube musicale (cf. dossier JSON).
# 2. Récupération des vidéos entre 2 dates souhaitées.
# 3. Ouverture des playlists temporaires non-modifiables.
# 4. Création & ouverture des playlists temporaires modifiables.

# La phase 4 est a éxécuté après un traitement préalable dans un naviguateur web pouvant gérer facilement des favoris.

""" - ELEMENTS PREPARATOIRE - """

reader = open("API_KEY.txt", "r")
api_key = reader.read()
youtube = build('youtube', 'v3', developerKey=api_key)

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
    print("Number of video to manage : {}".format(len(original_list)))
    for video in original_list:
        date_org_format = video["snippet"]["publishedAt"].replace("T", " ").replace("Z", "")
        date_new_format = datetime.strptime(date_org_format, "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=1)
        if down_date <= date_new_format <= up_date:
            return_list.append(
                {"id": video["snippet"]["resourceId"]["videoId"], "date": date_new_format,
                 "title": video["snippet"]["title"]})
        print("[VIDEO] Progress : {} of {} DONE".format(original_list.index(video) + 1, len(original_list)))
    print("{} videos selected.".format(len(return_list)))
    return return_list


def get_all_videos(channel_list, up_date, down_date):
    print("Number of channel to explore : {}\n".format(len(channel_list)))
    all_channels_content = []
    for channelid in channel_list:
        print("[CHANNEL] Progress : {} of {}".format(channel_list.index(channelid) + 1, len(channel_list)))
        content_raw = get_channel_videos(channelid)
        content_reformat = video_selection(content_raw, up_date, down_date)
        all_channels_content += content_reformat
        print("Channel n°{} DONE.\n".format(channel_list.index(channelid) + 1))
    return all_channels_content


def open_lot_url(list_of_url):
    for url in list_of_url:
        webbrowser.open(url)


def temp_playlist_builder(list_videos):
    str_ids = ""
    list_of_playlist = []
    print("{} videos to manage.".format(len(list_videos)))
    for element in list_videos:
        modulo = (list_videos.index(element) + 1) % 50
        print("Progresse : {} of {}".format(list_videos.index(element) + 1, len(list_videos)))
        if list_videos.index(element) + 1 != len(list_videos) and modulo != 0:
            str_ids += "{},".format(element["id"])
        else:
            str_ids += "{}|".format(element["id"])
    ids_lists = str_ids.split("|")
    ids_lists.remove("")
    for id_chain in ids_lists:
        playlist_txt_format = "http://www.youtube.com/watch_videos?video_ids={}".format(id_chain)
        list_of_playlist.append(playlist_txt_format)
    print("Task done. Number of temp. playlist : {}.".format(len(list_of_playlist)))
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
            print("Channel {} to {}".format(born_inf, len(channel_data_base)))
            return_list += get_all_videos(channel_data_base[born_inf:], date_sup, date_inf)
            born_inf += 10
        else:
            print("Channel {} to {}".format(born_inf, born_sup - 1))
            return_list += get_all_videos(channel_data_base[born_inf:born_sup], date_sup, date_inf)
            born_inf += 10
            born_sup += 10
    return return_list


""" - PROGRAMME PRINCIPAL - """

""" - 1. Récupération de la liste des chaine YouTube -  """

channel_db = music_channel_in_json("PocketTube_DB.json")

""" - 2. Récupération des vidéos entre 2 dates souhaitées -  """

today = datetime.today()
prev_date = today - timedelta(days=3)
# Exemple de format : prev_date = datetime.strptime("2019/07/19", '%Y/%m/%d')


final_list = managing_db(channel_db, today, prev_date)

# print("Channel 1 to 9")
# all_the_music_i_want1 = get_all_videos(channel_db[0:10], today, prev_date)
#
# print("Channel 10 to 19")
# all_the_music_i_want2 = get_all_videos(channel_db[10:20], today, prev_date)
#
# print("Channel 20 to 29")
# all_the_music_i_want3 = get_all_videos(channel_db[20:30], today, prev_date)
#
# print("Channel 30 to 39")
# all_the_music_i_want4 = get_all_videos(channel_db[30:40], today, prev_date)
#
# print("Channel 40 to 49")
# all_the_music_i_want5 = get_all_videos(channel_db[40:50], today, prev_date)
#
# print("Channel 50 to 59")
# all_the_music_i_want6 = get_all_videos(channel_db[50:60], today, prev_date)
#
# print("Channel 60 to 69")
# all_the_music_i_want7 = get_all_videos(channel_db[60:70], today, prev_date)
#
# print("Channel 70 to 79")
# all_the_music_i_want8 = get_all_videos(channel_db[70:80], today, prev_date)
#
# print("Channel 80 to 89")
# all_the_music_i_want9 = get_all_videos(channel_db[80:90], today, prev_date)
#
# print("Channel 90 to 99")
# all_the_music_i_want10 = get_all_videos(channel_db[90:100], today, prev_date)
#
# print("Channel 100 to END")
# all_the_music_i_want11 = get_all_videos(channel_db[100:], today, prev_date)
#
# print("LOADING - FUSION")
# final_list = all_the_music_i_want1 + all_the_music_i_want2 + all_the_music_i_want3 + all_the_music_i_want4 + \
#              all_the_music_i_want5 + all_the_music_i_want6 + all_the_music_i_want7 + all_the_music_i_want8 + \
#              all_the_music_i_want9 + all_the_music_i_want10 + all_the_music_i_want11

""" - 3. Ouverture des playlists temporaires non-modifiables -  """

print(temp_playlist_builder(final_list))

""" - 4. Création & ouverture des playlists temporaires modifiables -  """

# open_edited_url("url_playlist")

""" - TESTS - """
# print(len(all_the_music_i_want))
# print(all_the_music_i_want)

# videos_from_Monstercat_Ins = get_channel_videos('UCp8OOssjSjGZRVYK6zWbNLg')

# print(type(videos_from_Monstercat_Ins[0]))
# print(len(videos_from_Monstercat_Ins))
#
# for video in videos_from_Monstercat_Ins:
#     print(video['snippet']["resourceId"]["videoId"])

#  Dans "snippet" puis "resourceId" : videoId - Récupération des URL
#  Dans "snippet" : publishedAt - Récupération des dates d'upload

# last_upload_date = videos_from_Monstercat_Ins[0]["snippet"]["publishedAt"].replace("T", " ").replace("Z", "")
# date_reformat = datetime.strptime(last_upload_date, "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=1)

# print(datetime.today())
# print(last_upload_date)
# print(date_reformat)
#
# print(datetime.today() - date_reformat > timedelta(days=3))

# date_sup = datetime.today()
# date_inf = date_sup + timedelta(days=-6 * 30)
# print(date_sup)
# print(date_inf)
# print(date_sup - date_inf)


# write_url("test.txt", Mons_Ins_dict)

# write_url("video_to_add_", final_list)

# test_text = writre_playlist_url("video_to_add__", 1, 29)

# print(test_text[0])
# print(len(test_text))
# print(test_text)

# open_lot_url(test_text)

""" - FONCTION REJETEES- """

# def writre_playlist_url(file_path_schem, start, end):
#     text = ""
#     list_of_50 = []
#     list_of_temp_playlist = []
#     for idx in range(start, end + 1):
#         f = open("{}{}.txt".format(file_path_schem, idx), "r")
#         text += f.read()
#         text += "\n"
#     text = text.replace(",", "")
#     lst_text = text.split("\n")
#     lst_text.remove("")
#     lenght = len(lst_text)
#     inf = 0
#     sup = 50
#     while inf < lenght:
#         if sup < lenght:
#             list_of_50.append(list(lst_text[inf:sup]))
#             inf += 50
#             sup += 50
#         else:
#             list_of_50.append(list(lst_text[inf:]))
#             inf += 50
#     for internal_list in list_of_50:
#         playlist_txt_format = "http://www.youtube.com/watch_videos?video_ids="
#         for id in internal_list:
#             if internal_list.index(id) + 1 != len(internal_list):
#                 playlist_txt_format += "{},".format(id)
#             else:
#                 playlist_txt_format += "{}".format(id)
#         list_of_temp_playlist.append(playlist_txt_format)
#     return list_of_temp_playlist

# def write_url(file_name_format, lst_videos):
#     str_to_write = ''
#     print("Writting phase\nNumber of row to right: {}".format(len(lst_videos)))
#     for element in lst_videos:
#         modulo = (lst_videos.index(element) + 1) % 200
#         print("Progresse : {} of {}".format(lst_videos.index(element) + 1, len(lst_videos)))
#         if lst_videos.index(element) + 1 != len(lst_videos) and modulo != 0:
#             str_to_write += "{},\n".format(element["id"])
#         else:
#             str_to_write += "{}|".format(element["id"])
#     lst_str = str_to_write.split("|")
#     lst_str.remove("")
#     for rows in lst_str:
#         writter = open("{}_{}.txt".format(file_name_format, lst_str.index(rows) + 1), "a", encoding="utf-8")
#         writter.write(rows)
#         writter.close()
#         print("Document N°{} rendu en .txt".format(lst_str.index(rows) + 1))
#     print("SCHEM \"{}\" DONE\n".format(file_name_format))
#     return str_to_write
