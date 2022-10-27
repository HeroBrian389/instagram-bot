from functionality import setup, interact, request, profile
import traceback
import time
from tqdm import tqdm
import random

def label_func(o):
    return float(Path(o).parent.name)


s = setup()

pro = profile(s)

inter = interact(s)
req = request(s)


LENGTH = len(users)

pbar = tqdm(total=LENGTH) # Init pbar

try:
    pro.following_list("followers")
except:
    traceback.print_exc()
finally:
    s.close_connection()