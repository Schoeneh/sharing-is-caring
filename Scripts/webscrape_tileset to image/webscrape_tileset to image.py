import sys
import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image, UnidentifiedImageError 
from tqdm import tqdm
from yaspin import yaspin

#Sets working directory to directory of this file
os.chdir(sys.path[0])

url_check = True
while url_check:
    url_in = input(f"Type/Paste URL of website to scrape: ")
    if url_in.startswith("http"):
        url_check = False
    else:
        print("Error: Not a valid URL, please try again.")

with yaspin(text="Accessing URL... (This may take a few seconds)", side="right", timer=True) as spinner:
    try:
        opts = webdriver.FirefoxOptions()
        opts.add_argument("-headless")
        driver = webdriver.Firefox(options=opts)
        driver.get(url_in)
        leaflet_tile = driver.find_element(By.CLASS_NAME, 'leaflet-tile')
        url = leaflet_tile.get_attribute("src")
        url = url.rstrip("1/0.png") #leaflet-tiles should be png (https://leafletjs.com/reference.html#tilelayer)
    except Exception as e:
        sys.exit(f"Error: Script can't find leaflet-tiles, check URL {url_orig}")


#Checking available zoom-levels
with yaspin(text="Checking available zoom-levels", side="right", timer=True) as spinner:
    check_zoom = True
    zoom_max = 0
    while check_zoom:
        test = requests.get(f"{url}/{zoom_max}/0/0.png")
        if test.status_code == 200:
            zoom_max = zoom_max+1
        else:
            zoom_max = zoom_max-1
            check_zoom = False


print("Step 1/2: Downloading all non-empty tiles")
confirmation = True
step_download = True
while confirmation:
    zoom = input(f"Found zoom-levels 0 to {zoom_max}. Download tiles at what zoom-level? (Type number or 'skip'): ")
    if int(zoom) in range(0,zoom_max):
        zoom = int(zoom)
        confirmation = False
    elif zoom == "skip":
        step_download = False
        confirmation = False
    else:
        print(f"Error: \'{zoom}\' is not a valid input.")


while step_download:
    #Creating directory for chosen zoom-level
    if zoom == 0:
        data = requests.get(url + f"/{str(zoom)}/0/0.png").content
        f = open(f'images/image_zoom{str(zoom)}.png','wb')
        f.write(data)
        f.close()
        step_download = False
    else:
        if not os.path.exists(f"images/{str(zoom)}"):
            os.makedirs(f"images/{str(zoom)}")

        cols = True
        y = 0
        with tqdm(desc="Downloading tiles in column", unit="", total=pow(2,zoom)) as counter_cols:
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
                        if not os.path.exists(f"images/{str(zoom)}/{str(y)}/{str(x)}.png"):
                            try:
                                data = requests.get(url + f"/{str(zoom)}/{str(y)}/{str(x)}.png").content
                                f = open(f"images/{str(zoom)}/{str(y)}/{str(x)}.png",'wb')
                                f.write(data)
                                f.close()

                                uniquePixels = set(Image.open(f"images/{str(zoom)}/{str(y)}/{str(x)}.png").getdata())
                                #if len(uniquePixels) == 1:
                                    #os.remove(f"images/{str(zoom)}/{str(y)}/{str(x)}.png")
                            except UnidentifiedImageError:
                                os.remove(f"images/{str(zoom)}/{str(y)}/{str(x)}.png")
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
#Assumption: tiles will all have the same width and height (usually 256px*256px)

if not zoom == 0:
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
        if element.endswith(".png"):
            list_rows_imgs.append(element.split(".")[0])

    list_rows = list(map(int, list_rows_imgs))
    list_rows.sort()
    c_rows = len(list_rows)


    (img_width, img_height) = Image.open(f'images/{str(zoom)}/{list_cols[0]}/{list_rows[0]}.png').size

    result_rows = Image.new('RGBA', (img_width, img_height * c_rows))
    for col in tqdm(range(c_cols), desc="Combining images in each column"):
        if not os.path.exists(f'images/{str(zoom)}/col{str(list_cols[col])}.png'):
            pbar = tqdm(total=c_rows+1, desc="", leave=False)
            pbar.set_postfix_str("Stitching images...")
            for img in range(c_rows):
                try: 
                    result_rows.paste(im=Image.open(f'images/{str(zoom)}/{str(list_cols[col])}/{str(list_rows[img])}.png'), box=(0, img_height * img))
                    pbar.update(1)
                except Exception as e:
                    pbar.close()
                    sys.exit(f"{type(e).__name__} at: {f'images/{str(zoom)}/{str(list_cols[col])}/{str(list_rows[img])}.png'}")
                    
            pbar.set_postfix_str("Saving image...")
            result_rows.save(f'images/{str(zoom)}/col{str(list_cols[col])}.png')
            pbar.update(1)
            pbar.close()

    result = Image.new('RGBA', (img_width * c_cols, img_height * c_rows))
    if not os.path.exists(f'images/image_zoom{str(zoom)}.png'):
        for img in tqdm(range(c_cols), desc="Combining all columns"):
            try:
                result.paste(im=Image.open(f'images/{str(zoom)}/col{str(list_cols[img])}.png'), box=(img_width * img, 0))
            except:
                tqdm.close()
                sys.exit(f"Failure at: {f'images/{str(zoom)}/col{str(list_cols[img])}.png'}")
        
        with yaspin(text="Saving image... (This may take a while)", side="right", timer=True) as spinner:
            result.save(f'images/image_zoom{str(zoom)}.png')

        print("---")
        with yaspin(text="Opening final image...", side="right") as spinner:
            result.show()
        print("Finished!")
    else:
        print("---")
        print("Image already exists.")
else:
    print("---")
    print("Opening final image...")
    final = Image.open(f'images/image_zoom{str(zoom)}.png')
    final.show()
    print("Finished!")