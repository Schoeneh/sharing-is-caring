#!/usr/bin/python3
# coding: utf-8
'''
author: Henrik Schoenemann
created on: 2023-12-23

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

https://github.com/halcy/Mastodon.py
'''

import requests
from io import BytesIO
from time import sleep
from PIL import Image
from mastodon import Mastodon


Mastodon.create_app(
    'pytooterapp',
    api_base_url = 'https://botsin.space',
    to_file = 'pytooter_clientcred.secret'
)


mastodon = Mastodon(client_id = 'pytooter_clientcred.secret',)
mastodon.log_in(
    'sun_q6h@schoeneh.eu',
    'fsFWCR9vn4pf$4D',
    to_file = 'pytooter_usercred.secret'
)

#Fetching images from https://sdo.gsfc.nasa.gov
url_171 = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0171.jpg"
url_193 = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0193.jpg"
url_304 = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0304.jpg"

img_171 = Image.open(BytesIO(requests.get(url_171).content))
img_193 = Image.open(BytesIO(requests.get(url_193).content))
img_304 = Image.open(BytesIO(requests.get(url_304).content))

img_comp = Image.blend(img_171, img_193, 0.5)
img_comp = Image.blend(img_comp, img_304, 0.33)
img_comp.save('img_comp.jpg')

desc = "Image of the sun created in two steps:\n" + "1. Compositing (50-50) channels highlighting the corona - \'AIA 0171\' and \'AIA 0193\'\n" + "2. Compositing (66-33) the image from 1. with a channel highlighting cooler dense plumes of plasma - \'AIA 0304\'\n"

img_dict = mastodon.media_post('img_comp.jpg', description=desc)
toot_img_courtesy = "\n\n\n\n\nImage courtesy of NASA/SDO and the AIA, EVE, and HMI science teams.\nhttps://sdo.gsfc.nasa.gov"


toot = "#HelloWorld" + "\n" + "#SunQ6H"

toot = toot + toot_img_courtesy


#toot = "automated test via supervisord"
#print(toot)
mastodon.status_post(toot, media_ids=img_dict)
#print("Tooted!")
sleep(120)