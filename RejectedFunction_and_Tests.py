""" - TESTS - """

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
