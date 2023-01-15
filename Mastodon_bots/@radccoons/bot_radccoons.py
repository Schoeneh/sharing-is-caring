#!/usr/bin/python3
# coding: utf-8
'''
author: Henrik Schoenemann
created on: 2023-01-15

Copyright (C) 2023 Henrik Schoenemann

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Using:
https://github.com/halcy/Mastodon.py
'''
import csv
import pickle
import random
from mastodon import Mastodon

with open('id_list.pkl', 'rb') as file:
    id_list = pickle.load(file)

###Create new list based on metadata file
if len(id_list) == 0:
    id_list = []
    with open('racoons_metadata.csv', mode ='r')as file:
        raccoon_csv = csv.DictReader(file)
    
        for lines in raccoon_csv:
            id_list.append(int(lines["id"]))

    with open('id_list.pkl', 'wb') as file:
        pickle.dump(id_list, file)

###Read list of ids, pick a random one, remove it from the list and save the new list
with open('id_list.pkl', 'rb') as file:
    id_list = pickle.load(file)

id_rand = random.choice(id_list)

id_list.remove(id_rand)
with open('id_list.pkl', 'wb') as file:
    pickle.dump(id_list, file)


###Start posting
mastodon = Mastodon(access_token = 'pytooter_usercred.secret')

with open('racoons_metadata.csv', mode ='r')as file:
    raccoon_csv = csv.DictReader(file)
    for lines in raccoon_csv:
        if lines['id'] == str(id_rand):
            file = lines['file_name']
            url = lines['url']
            title = "\""+lines['title']+"\""
            desc = "\""+lines['description']+"\""
            date = lines['date']
            licen = lines['license']
            creator = lines['creator']


file_full = "images/"+file+"_(Large).jpg"

media = mastodon.media_post(file_full, mime_type='image/jpeg', description=desc)

status = (
    title+" by "+creator
    +"\n via "+url+"\n\n"+date+", "+licen
    +"\n#Raccoon #Radccoon #Bot"
    )

mastodon.status_post(
                status,
                media_ids=media,
                sensitive=False)