import sys
import os
import requests
from PIL import Image, UnidentifiedImageError 
from tqdm import tqdm
from yaspin import yaspin

url = "https://www.berliner-stadtplansammlung.de/images/maps/Abbildungen/Berlin%201690%20Stridbeck/Blatt%204%20Schloss%20und%20Schlossplatz"
img_type = ".png"
zoom = 6 #zoom level
#Assumption: tiles will all have the same width and height (usually 256px*256px)

#Sets working directory to directory of this file
os.chdir(sys.path[0])

print("Step 1/2: Downloading all non-empty tiles")
step_download = True

skip = input("Skip download? (type 'skip'): ")
if skip == "skip":
    step_download = False

while step_download:
    #Creating directory for zoom-level
    if not os.path.exists(f"images/{str(zoom)}"):
        os.makedirs(f"images/{str(zoom)}")

    cols = True
    y = 0
    with tqdm(desc="Downloading tiles in column", unit="") as counter_cols:
        while cols:
            #Creating a directory for each column
            if not os.path.exists(f"images/{str(zoom)}/{str(y)}"):
                    os.makedirs(f"images/{str(zoom)}/{str(y)}")

            rows = True
            x = 0
            list_uniquePixels = []
            with tqdm(desc="Downloading tile", unit="", leave=False) as counter_tiles:
                while rows:
                    #Downloading each image of column
                    if not os.path.exists(f"images/{str(zoom)}/{str(y)}/{str(x)}{img_type}"):
                        try:
                            data = requests.get(url + f"/{str(zoom)}/{str(y)}/{str(x)}{img_type}").content
                            f = open(f"images/{str(zoom)}/{str(y)}/{str(x)}{img_type}",'wb')
                            f.write(data)
                            f.close()

                            uniquePixels = set(Image.open(f"images/{str(zoom)}/{str(y)}/{str(x)}{img_type}").getdata())
                            if len(uniquePixels) == 1:
                                os.remove(f"images/{str(zoom)}/{str(y)}/{str(x)}{img_type}")
                        except UnidentifiedImageError:
                            os.remove(f"images/{str(zoom)}/{str(y)}/{str(x)}{img_type}")
                            rows = False
                    x = x + 1
                    counter_tiles.update(1)

            list_files = os.listdir(f"images/{str(zoom)}/{str(y)}")
            if not list_files:
                os.rmdir(f"images/{str(zoom)}/{str(y)}")
                cols = False
            y = y + 1
            counter_cols.update(1)
    step_download = False

print("---")
print("Step 2/2: Stitching the image")
#Getting names of all directories of current zoom-level
list_cols = next(os.walk(f'images/{zoom}'))[1]
#Converting names of directories into integers and sorting
list_cols = list(map(int, list_cols))
list_cols.sort()
c_cols = len(list_cols)

#Getting names of all files in  of current zoom-level
list_rows = next(os.walk(f'images/{zoom}/{list_cols[0]}'))[2]
list_rows_imgs = []
for element in list_rows:
    if element.endswith(img_type):
        list_rows_imgs.append(element.split(".")[0])

list_rows = list(map(int, list_rows_imgs))
list_rows.sort()
c_rows = len(list_rows)


(img_width, img_height) = Image.open(f'images/{str(zoom)}/{list_cols[0]}/{list_rows[0]}{img_type}').size

result_rows = Image.new('RGB', (img_width, img_height * c_rows))
for col in tqdm(range(c_cols), desc="Combining images in each column"):
    if not os.path.exists(f'images/{str(zoom)}/col{str(list_cols[col])}{img_type}'):
        pbar = tqdm(total=c_rows+1, desc="", leave=False)
        pbar.set_postfix_str("Stitching images...")
        for img in range(c_rows):
            try: 
                result_rows.paste(im=Image.open(f'images/{str(zoom)}/{str(list_cols[col])}/{str(list_rows[img])}{img_type}'), box=(0, img_height * img))
                pbar.update(1)
            except Exception as e:
                pbar.close()
                sys.exit(f"{type(e).__name__} at: {f'images/{str(zoom)}/{str(list_cols[col])}/{str(list_rows[img])}{img_type}'}")
                
        pbar.set_postfix_str("Saving image...")
        result_rows.save(f'images/{str(zoom)}/col{str(list_cols[col])}{img_type}')
        pbar.update(1)
        pbar.close()

result = Image.new('RGB', (img_width * c_cols, img_height * c_rows))
if not os.path.exists(f'images/image_zoom{str(zoom)}{img_type}'):
    for img in tqdm(range(c_cols), desc="Combining all columns"):
        try:
            result.paste(im=Image.open(f'images/{str(zoom)}/col{str(list_cols[img])}{img_type}'), box=(img_width * img, 0))
        except:
            tqdm.close()
            sys.exit(f"Failure at: {f'images/{str(zoom)}/col{str(list_cols[img])}{img_type}'}")
    
    with yaspin(text="Saving image... (This may take a while)", side="right", timer=True) as spinner:
        result.save(f'images/image_zoom{str(zoom)}{img_type}')

    print("---")
    print("Finished!")
    result.show()
else:
    print("---")
    print("Image already exists.")
