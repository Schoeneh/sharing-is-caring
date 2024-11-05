#!/usr/bin/python3
# coding: utf-8
'''
    author: Henrik Schoenemann
    created on: 2022-12-29
    last update: 2024-11-05

    GPLv3 2024 Henrik Schoenemann

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
    https://mastodonpy.readthedocs.io/en/stable/
    API: https://docs.stormglass.io/#/
'''

import requests
import json
import pytz
from os.path import exists
from io import BytesIO
from datetime import datetime, timezone, timedelta, time
from time import sleep
from pymeeus.Sun import Sun
from mastodon import Mastodon

test = False

### App registration and authentication ###
if exists("./mastodonpy_clientcred.secret") == False:
    Mastodon.create_app(
    'mastodonpy',
    api_base_url = 'https://mastodon-server.example',
    to_file = './mastodonpy_clientcred.secret'
    )

if exists("./mastodonpy_usercred.secret") == False:
    mastodon = Mastodon(client_id = './mastodonpy_clientcred.secret',)
    mastodon.log_in(
        'my_login_email@example.com',
        'incrediblygoodpassword',
        to_file = './mastodonpy_usercred.secret'
    )

mastodon = Mastodon(access_token = './mastodonpy_usercred.secret')

### Variables, modify as needed ###
loc_name = "Berlin"
loc_tz = "EST"
loc_lat = 52.520008
loc_lng = 13.404954

#print(datetime.now())
today = datetime.now()
today = datetime.fromisoformat('2024-12-24')
yesterday = today - timedelta(days = 1)

### Fetching data from API ###
# Get your API key from https://stormglass.io and put it in a file called 'API_key.secret'
with open("./key_API.secret") as f:
    key = f.readlines()

file_data_today = "./data/data_" + datetime.now().strftime(r'%Y-%m-%d') + ".json"

if exists(file_data_today) == False:
    response = requests.get(
    'https://api.stormglass.io/v2/astronomy/point',
    params={'lat': loc_lat,'lng': loc_lng,'start': yesterday,'end': today,},
    headers={'Authorization': key[0]}
    )
    json_data = response.json()

    try:
        if 'data' in json_data:
            with open(file_data_today, 'w') as f:
                json.dump(json_data, f)
    except:
        print("Error fetching data from API.")
else:
    json_data = json.load(open(file_data_today))

### Getting data from JSON
day_0 = datetime.fromisoformat(json_data['data'][0]['time'])
sunrise_0 = datetime.fromisoformat(json_data['data'][0]['sunrise']).astimezone()
sunset_0 = datetime.fromisoformat(json_data['data'][0]['sunset']).astimezone()

print(day_0)
print(sunrise_0)
print(sunset_0)

day_1 = datetime.fromisoformat(json_data['data'][1]['time'])
sunrise_1 = datetime.fromisoformat(json_data['data'][1]['sunrise']).astimezone()
sunset_1 = datetime.fromisoformat(json_data['data'][1]['sunset']).astimezone()

print(day_1)
print(sunrise_1)
print(sunset_1)

delta_0 = sunset_0 - sunrise_0
delta_1 = sunset_1 - sunrise_1

### Dealing with winter/summer solstice ###
diff_neg = False
diff = delta_1 - delta_0

epoch = Sun.get_equinox_solstice(datetime.now().year, target="winter")
y, m, d, h, mi, s = epoch.get_full_date()
day_solstice_winter = "{}/{}/{}".format(y, m, d)
day_solstice_winter = datetime.strptime(day_solstice_winter,r'%Y/%m/%d')
day_solstice_winter = pytz.timezone(loc_tz).localize(day_solstice_winter)
#print(day_solstice_winter)

epoch = Sun.get_equinox_solstice(datetime.now().year, target="summer")
y, m, d, h, mi, s = epoch.get_full_date()
day_solstice_summer = "{}/{}/{}".format(y, m, d)
day_solstice_summer = datetime.strptime(day_solstice_summer,r'%Y/%m/%d')
day_solstice_summer = pytz.timezone(loc_tz).localize(day_solstice_summer)
#print(day_solstice_summer)

if diff < timedelta(0):
    diff = delta_0 - delta_1
    delta_day_solstice_winter = day_solstice_winter - day_1
    diff_neg = True

if exists("./data/data_winter_solstice_" + datetime.now().strftime('%Y') + ".json") == False:
    data_check = False
    req_count = 0

    while data_check == False and req_count < 2:
        response = requests.get(
        'https://api.stormglass.io/v2/astronomy/point',
        params={'lat': loc_lat,'lng': loc_lng,'start': day_solstice_winter,},
        headers={'Authorization': key[0]}
        )
        json_data_winter_solstice = response.json()
        req_count = req_count + 1

        if 'data' in json_data_winter_solstice:
            data_check = True 

    file_winter_solstice = "./data/data_winter_solstice_" + datetime.now().strftime('%Y') + ".json"

    with open(file_winter_solstice, 'w') as f:
        json.dump(json_data_winter_solstice, f)


diff = delta_1 - delta_0

### Generating text of toot ###
toot_lines = [
    "#HereComesTheSun 🌞 for #" + loc_name +" on " + day_1.strftime("%a, %b %d") + ":",
    "The sun rises at "+ sunrise_1.strftime("%H:%M %p") + " and sets at "+ sunset_1.strftime("%H:%M %p") + ".",
    "We will see 0" + str(delta_1) + " of daylight.\n\n"
]
toot = "\n".join(toot_lines)


if diff_neg:
    diff_calc = timedelta(days=1) + diff
    diff_calc = timedelta(days=1).total_seconds() - diff_calc.total_seconds()
    diff_total = time.fromisoformat("0" + str(timedelta(seconds=diff_calc)))
else:
    diff_total = time.fromisoformat("0" + str(diff))


# Parsing str(delta_1) as whole sentence
diff_sec = int(diff_total.strftime('%S'))
diff_min = int(diff_total.strftime('%M'))
diff_hour = int(diff_total.strftime('%H'))

and_sec = and_min = and_hour = False

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
    
if diff_neg == True:
    if and_min == False and and_hour == False:
        toot = toot + "That's " + diff_sec_str + " less than yesterday."
    elif and_sec == False and and_min == True and and_hour == False:
        toot = toot + "That's " + diff_min_str + " less than yesterday."
    elif and_sec == True and and_min == True and and_hour == False:
        toot = toot + "That's " + diff_min_str + " and " + diff_sec_str +" less than yesterday."
    elif and_sec == False and and_min == False and and_hour == True:
        toot = toot + "That's " + diff_hour_str + " less than yesterday."
    elif and_sec == True and and_min == False and and_hour == True:
        toot = toot + "That's " + diff_hour_str + " and " + diff_sec_str +" less than yesterday."
    elif and_sec == False and and_min == True and and_hour == True:
        toot = toot + "That's " + diff_hour_str + " and " + diff_min_str +" less than yesterday."
    elif and_sec == True and and_min == True and and_hour == True:
        toot = toot + "That's " + diff_hour_str + ", " + diff_min_str + " and " + diff_sec_str +" less than yesterday."
    toot = toot + "\nBut don't you fret, the winter solstice is only "+ str(delta_day_solstice_winter.days) + " days away!"
else:
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
    
    json_data_winter_solstice = json.load(open('/home/schoeneh/bots_mastodon/sunofberlin/data/data_winter_solstice_2023.json'))
    sunrise_winter_solstice = datetime.fromisoformat(json_data_winter_solstice['data'][0]['sunrise']).astimezone()
    sunset_winter_solstice  = datetime.fromisoformat(json_data_winter_solstice['data'][0]['sunset']).astimezone()
    amount_winter_solstice = sunset_winter_solstice - sunrise_winter_solstice
    delta_winter_solstice = delta_1 - amount_winter_solstice

    toot = toot + "\n\nAnd an additional 0"+str(delta_winter_solstice)+" of daylight compared to the winter solstice."


### Fetching image from Solar Dynamics Observatory ###
url = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"
desc_lines = [
    "Most recent picture of the sun; taken by the Solar Dynamics Observatory - Channel: \'AIA 0193\'\n",
    "\"This channel highlights the outer atmosphere of the Sun - called the corona - as well as hot flare plasma.",
    "Hot active regions, solar flares, and coronal mass ejections will appear bright here.",
    "The dark areas - called coronal holes - are places where very little radiation is emitted, yet are the main source of solar wind particles.\"",
    "\nImage courtesy of NASA/SDO (Solar Dynamics Observatory) and the AIA, EVE, and HMI science teams.",
    "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"
]
desc = "\n".join(desc_lines)


response = requests.get(url)
img_dict = mastodon.media_post(BytesIO(response.content), mime_type="image/jpeg", description=desc)

### Checking if test
if test == False:
    mastodon.status_post(toot, media_ids=img_dict)
    sleep(120)
elif test == True:
    #toot = "Testing"
    mastodon.status_post(toot, media_ids=img_dict, spoiler_text="Testing, via hosting on astroids")
    print("Tooted!")
else:
    print(toot)