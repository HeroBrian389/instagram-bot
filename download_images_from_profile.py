from functionality import setup, download, beauty_score, interact, request
import traceback
import time
from tqdm import tqdm
import random

def label_func(o):
    return float(Path(o).parent.name)


s = setup()

d = download(s)

pred = beauty_score()


inter = interact(s)
req = request(s)

num = 40
offset = 0
users = d.get_users(num)

LENGTH = len(users)

pbar = tqdm(total=LENGTH) # Init pbar

try:
    for row in users:
        try:
            if (random.random() < .3):
                inter.like_photos(random.randint(1, 2))
            else:
                inter.process_stories(random.randint(4, 8))
                
            username = row['username']

            d.get_page(f"https://instagram.com/{username}")
            time.sleep(3)

            d.download_images(username)

            # This is used to predict the score of faces it extracts
            #pred.images(username)

            d.update_user(username)
        except:
            traceback.print_exc()
        finally:
            pbar.update(n=1)
except:
    traceback.print_exc()
finally:
    s.close_connection()