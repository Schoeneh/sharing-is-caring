import os
import requests
from PIL import Image
from tqdm import tqdm
from yaspin import yaspin

url = "https://www.berliner-stadtplansammlung.de/images/maps/Abbildungen/Berlin%201690%20Stridbeck/Blatt%204%20Schloss%20und%20Schlossplatz"

zoom = 5 #zoom level
cols = 31 #max y-value of leaflet-tiles
rows = 27 #max x-value of leaflet-tiles

print("Step 1/2: Downloading the Tiles")

if not os.path.exists(f"images/{str(zoom)}"):
    os.makedirs(f"images/{str(zoom)}")

for y in tqdm(range(cols+1), desc="Downloading columns"):
    for x in tqdm(range(rows+1), desc="Downloading row", leave=False):
        if not os.path.exists(f"images/{str(zoom)}/{str(y)}"):
            os.makedirs(f"images/{str(zoom)}/{str(y)}")

        if not os.path.exists(f"images/{str(zoom)}/{str(y)}/{str(x)}.png"):
            data = requests.get(url + f"/{str(zoom)}/{str(y)}/{str(x)}.png").content
            f = open(f"images/{str(zoom)}/{str(y)}/{str(x)}.png",'wb')
            f.write(data)
            f.close()

print("---")
print("Step 2/2: Stitching the image")
c_cols = len(next(os.walk(f'images/{zoom}'))[1])
c_rows = len(next(os.walk(f'images/{zoom}/0'))[2])

(img_width, img_height) = Image.open(f'images/{str(zoom)}/0/0.png').size

result_rows = Image.new('RGB', (img_width, img_height * c_rows))
for col in tqdm(range(c_cols), desc="Stitching each Column"):
    if not os.path.exists(f'images/{str(zoom)}/row{str(col)}.png'):
        for img in range(c_rows):
            result_rows.paste(im=Image.open(f'images/{str(zoom)}/{str(col)}/{str(img)}.png'), box=(0, img_height * img))
        result_rows.save(f'images/{str(zoom)}/row{str(col)}.png')

result = Image.new('RGB', (img_width * c_cols, img_height * c_rows))
if not os.path.exists(f'images/image_zoom{str(zoom)}.png'):
    for img in tqdm(range(c_cols), desc="Stitching whole Image"):
        result.paste(im=Image.open(f'images/{str(zoom)}/row{str(img)}.png'), box=(img_width * img, 0))
    
    with yaspin(text="Saving image... (This may take a while)") as spinner:
        result.save(f'images/image_zoom{str(zoom)}.png')

print("---")
print("Finished!")
