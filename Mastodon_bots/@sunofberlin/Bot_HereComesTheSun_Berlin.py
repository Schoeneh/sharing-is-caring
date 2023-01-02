#!/usr/bin/python3
# coding: utf-8
'''
author: Henrik Schoenemann
created on: 2022-12-29

Copyright (C) 2022 Henrik Schoenemann

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


Modified 2022-12-29 by using code by Joerg Jaspert <joerg@ganneff.de>
https://codeberg.org/Fulda.Social/herecomesthesun/src/branch/main/Bot_HereComesTheSun_Fulda.py

https://github.com/halcy/Mastodon.py
API: https://docs.stormglass.io/#/
'''

import requests
from datetime import datetime, timedelta, time
from mastodon import Mastodon

# Modify as needed
loc_name = "Berlin"
loc_lat = 52.520008
loc_lng = 13.404954


# Need an API key, get it from stormglass.io and place it into API_key.txt
with open('API_key.txt') as f:
    key = f.readlines()

mastodon = Mastodon(access_token = 'pytooter_usercred.secret')
today = datetime.now()
yesterday = today - timedelta(days = 1)
data_check = False
req_count = 0

#Asking API
while data_check == False and req_count < 2:
    response = requests.get(
      'https://api.stormglass.io/v2/astronomy/point',
      params={
        'lat': loc_lat,
        'lng': loc_lng,
        'start': yesterday,
        'end': today,
      },
      headers={
        'Authorization': key[0]
      }
    )
    json_data = response.json()
    req_count = req_count + 1

    if 'data' in json_data:
        data_check = True 
    
day_0 = datetime.fromisoformat(json_data['data'][0]['time'])
sunrise_0 = datetime.fromisoformat(json_data['data'][0]['sunrise']).astimezone()
sunset_0 = datetime.fromisoformat(json_data['data'][0]['sunset']).astimezone()

day_1 = datetime.fromisoformat(json_data['data'][1]['time'])
sunrise_1 = datetime.fromisoformat(json_data['data'][1]['sunrise']).astimezone()
sunset_1 = datetime.fromisoformat(json_data['data'][1]['sunset']).astimezone()

delta_0 = sunset_0 - sunrise_0
delta_1 = sunset_1 - sunrise_1
diff = delta_1 - delta_0
diff_total = time.fromisoformat("0" + str(diff))
diff_sec = int(diff_total.strftime('%S'))
diff_min = int(diff_total.strftime('%M'))
diff_hour = int(diff_total.strftime('%H'))


and_sec = False
and_min = False
and_hour = False

if diff_sec == 0:
    diff_sec_str = ""
elif diff_sec == 1:
    diff_sec_str = "one second"
    and_sec = True
else:
    diff_sec_str = str(diff_sec) + " seconds"
    and_sec = True

if diff_min == 0:
    diff_min_str = ""
elif diff_min == 1:
    diff_min_str = "one minute"
    and_min = True
else:
    diff_min_str = str(diff_min) + " minutes"
    and_min = True

if diff_hour == 0:
    diff_hour_str = ""
elif diff_hour == 1:
    diff_hour_str = "one hour"
    and_hour = True
else:
    diff_hour_str = str(diff_hour) + " hours"
    and_hour = True


toot = (
    "#HereComesTheSun 🌞 for #" + loc_name +" on "
    + day_1.strftime("%a, %b %d")
    + ":\nThe sun rises at "
    + sunrise_1.strftime("%H:%M")
    + " and sets at "
    + sunset_1.strftime("%H:%M")
    + ".\nWe will see " + str(delta_1) + " of daylight.\n\n"
)

if and_min == False and and_hour == False:
    toot = toot + "That's " + diff_sec_str + " more than yesterday!"
elif and_sec == False and and_min == True and and_hour == False:
    toot = toot + "That's " + diff_min_str + " more than yesterday!"
elif and_sec == True and and_min == True and and_hour == False:
    toot = toot + "That's " + diff_min_str + " and " + diff_sec_str +" more than yesterday!"
elif and_sec == False and and_min == False and and_hour == True:
    toot = toot + "That's " + diff_hour_str + " more than yesterday!"
elif and_sec == True and and_min == False and and_hour == True:
    toot = toot + "That's " + diff_hour_str + " and " + diff_sec_str +" more than yesterday!"
elif and_sec == False and and_min == True and and_hour == True:
    toot = toot + "That's " + diff_hour_str + " and " + diff_min_str +" more than yesterday!"
elif and_sec == True and and_min == True and and_hour == True:
    toot = toot + "That's " + diff_hour_str + ", " + diff_min_str + " and " + diff_sec_str +" more than yesterday!"

mastodon.toot(toot)