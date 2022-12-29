#!/usr/bin/python3
# coding: utf-8
'''
author: Henrik Schönemann
created on: 2022-12-29
coding: utf-8

https://github.com/halcy/Mastodon.py
https://docs.stormglass.io/#/
'''


import requests
from datetime import datetime, timedelta, time
from mastodon import Mastodon

today = datetime.now()
yesterday = today - timedelta(days = 1)


with open('/home/schoeneh/mastodon_bot/herecomesthesun_berlin/API_key.txt') as f:
    key = f.readlines()

response = requests.get(
  'https://api.stormglass.io/v2/astronomy/point',
  params={
    'lat': 52.520008,
    'lng': 13.404954,
    'start': yesterday,
    'end': today,
  },
  headers={
    'Authorization': key[0]
  }
)

json_data = response.json()


day_0 = datetime.fromisoformat(json_data['data'][0]['time'])
sunrise_0 = datetime.fromisoformat(json_data['data'][0]['sunrise'])
sunrise_0 = sunrise_0 + timedelta(hours = 1)
sunset_0 = datetime.fromisoformat(json_data['data'][0]['sunset'])
sunset_0 = sunset_0 + timedelta(hours = 1)

day_1 = datetime.fromisoformat(json_data['data'][1]['time'])
sunrise_1 = datetime.fromisoformat(json_data['data'][1]['sunrise'])
sunrise_1 = sunrise_1 + timedelta(hours = 1)
sunset_1 = datetime.fromisoformat(json_data['data'][1]['sunset'])
sunset_1 = sunset_1 + timedelta(hours = 1)

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


toot = "#HereComesTheSun 🌞 for #Berlin on " + day_1.strftime('%a, %b %d') + ":\nThe sun rises at " + sunrise_1.strftime('%H:%M') + " and sets at " + sunset_1.strftime('%H:%M') + ".\nOur (theoretical) maximum amount of daylight will be " + str(delta_1) + ".\n\n"

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


mastodon = Mastodon(access_token = '/home/schoeneh/mastodon_bot/herecomesthesun_berlin/pytooter_usercred.secret')
mastodon.toot(toot)

