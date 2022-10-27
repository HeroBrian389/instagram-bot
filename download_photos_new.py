import json

import requests

import time

from datetime import datetime
import pymysql.cursors
import os

import re


def request_profile(username):

    url = f"https://i.instagram.com/api/v1/feed/user/{username}/username/?count=12"

    payload={}
    headers = {
        'authority': 'i.instagram.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'mid=YkX0-wAEAAEGbZt_635pxhDbtW-d; ig_did=9C4EFEB4-0BA5-46E2-B2FF-B07821D3352E; csrftoken=NSNE6WHcjos4XhWRoi64uhdwVMSXCyXI; ds_user_id=5331193944; datr=lTGzYgyT1zBCJ7k7gggK0NDx; shbid="18152\\0545331193944\\0541698176260:01f7798139271798566e64bd394f57bab8c6b645a5f5d5a9aa14b001c9c44a79ed2b10a8"; shbts="1666640260\\0545331193944\\0541698176260:01f7bdd39759224c55a5cb155376742bd519579b04f26867955358662e5cf8229027ce9d"; dpr=2; sessionid=5331193944%3AC45ksrDvL9fqEA%3A27%3AAYcSmry2yj-m9C2ECsRLkSu8fWEwlaH_0IpZyVWKAoE; rur="RVA\\0545331193944\\0541698428029:01f713dc2a2e245b7d80e6023319673c32b8398354ed954b262c84150fd30c5a43f67159"; csrftoken=NSNE6WHcjos4XhWRoi64uhdwVMSXCyXI; ds_user_id=5331193944; rur="RVA\\0545331193944\\0541698428068:01f7e8a2f65b8e6d8cde0a767af81629d1a7a39c6ac803b6baddbc983e2c395c89c88b2a"',
        'origin': 'https://www.instagram.com',
        'referer': 'https://www.instagram.com/',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'x-asbd-id': '198387',
        'x-csrftoken': 'NSNE6WHcjos4XhWRoi64uhdwVMSXCyXI',
        'x-ig-app-id': '936619743392459',
        'x-ig-www-claim': 'hmac.AR3N4m33I2DWImdnM9d4lYLY1hV3DAAAQfaOk0-s-subTwbw',
        'x-instagram-ajax': '1006477071'
    }

    """
    Differences:
    cookie:
        shbts: different
    x-csrftoken: different
    x-instagram-ajax: different
    """

    response = requests.request("GET", url, headers=headers, data=payload)

    results = json.loads(response.text)['items']


    urls = []

    status = 'not_processed'


    date_entered, time_entered = get_dt()
    photo_inc = 0
   
    folder_checks(username)

    if (len(results) > 0):
        

        for result in results:

            taken_at = result['taken_at']
            device_timestamp = result['device_timestamp']

            # test for carousel_media
            # if it exists then go image_versions, candidates, 0, url

            list_of_keys = result.keys()

            if ('carousel_media' in list_of_keys):
                pictures = result['carousel_media']

                for item in pictures:
                    photo_inc += 1
                    alt_caption = item['accessibility_caption']

                    photo_id = item['id']

                    target_url = item['image_versions2']['candidates'][0]['url']
                    print(target_url)
                    root = 'instagram_webserver/static/'
                    filename = f'images/{username}/raw/{photo_id}.jpg'

                    download_url(target_url, f'{root}{filename}')

                    """
                    Get the following info from the request
                    """

                    insert_photo_table(username, taken_at, photo_id, device_timestamp, filename, status, alt_caption, target_url, time_entered, date_entered)
                    print(f'Inserted photo #{photo_inc} for {username}')

            else:
                photo_inc += 1
                alt_caption = result['accessibility_caption']

                photo_id = result['id']

                target_url = result['image_versions2']['candidates'][0]['url']
                print(target_url)

                root = 'instagram_webserver/static/'
                filename = f'images/{username}/raw/{photo_id}.jpg'

                download_url(target_url, f'{root}{filename}')

                """
                Get the following info from the request
                """

                insert_photo_table(username, taken_at, photo_id, device_timestamp, filename, status, alt_caption, target_url, time_entered, date_entered)
                print(f'Inserted photo #{photo_inc} for {username}')



def get_dt():

    today = datetime.now()
    d1 = today.strftime("%d-%m-%Y")
    t1 = today.strftime("%H:%M:%S")

    return [d1, t1]




def download_url(url, filename):

    response = requests.get(url)

    image = open(filename, "wb")
    image.write(response.content)
    image.close()

    return True


def insert_photo_table(username, taken_at, photo_id, device_timestamp, filename, status, alt_caption, url, time_entered, date_entered):
    global mycursor, mydb

    sql = f'''INSERT INTO images_new (username, taken_at, photo_id, device_timestamp, filename, status, alt_caption, url, time_entered, date_entered) VALUES ("{username}", "{taken_at}", "{photo_id}", "{device_timestamp}", "{filename}", "{status}", "{alt_caption}", "{url}", "{time_entered}", "{date_entered}")'''
    mycursor.execute(sql)
    mydb.commit()



def folder_checks(username):

    if (os.path.exists(f'instagram_webserver/static/images/') == False):
            os.system(f'mkdir images')

    if (os.path.exists(f'instagram_webserver/static/images/{username}') == False):
            os.system(f'mkdir instagram_webserver/static/images/{username}')

    if (os.path.exists(f'instagram_webserver/static/images/{username}/face') == False):
        os.system(f'mkdir instagram_webserver/static/images/{username}/face')


    if (os.path.exists(f'instagram_webserver/static/images/{username}/process') == False):
        os.system(f'mkdir instagram_webserver/static/images/{username}/process')


    if (os.path.exists(f'instagram_webserver/static/images/{username}/finish') == False):
        os.system(f'mkdir instagram_webserver/static/images/{username}/finish')

    
    if (os.path.exists(f'instagram_webserver/static/images/{username}/raw') == False):
        os.system(f'mkdir instagram_webserver/static/images/{username}/raw')



def user_downloaded(username):

    if (os.path.exists(f'instagram_webserver/static/images/{username}/') == False):
        return False


# connect to db
mydb = pymysql.connect(
    host="34.89.55.66",
    user="root",
    password="Mintylucky9",
    database="instagram",
    cursorclass=pymysql.cursors.DictCursor
)

mycursor = mydb.cursor()

opened_file = open('following.json', 'r').read()

json_array = json.loads(opened_file)['users']

list_of_names = open('list_of_names.txt', 'r').read().splitlines() 

inc = 0
limit = inc + 10

for user in json_array:

    username = user['username']

    if (user_downloaded(username) == False):

        name_found = False

        for name in list_of_names:

            if (name.lower() in user['full_name'].lower() or name.lower() in user['username']):
                name_found = True
                break
        
        print(f'Name found: {name_found}')
        if (name_found == True):
            request_profile(username)
            inc += 1


        else:
            folder_checks(username)

        print('Quitting...')
        
    
    if (inc > 6):
        break