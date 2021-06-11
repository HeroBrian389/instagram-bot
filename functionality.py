import sys
import pymysql.cursors
import os
import time
import sys
from selenium import webdriver
import matplotlib.pyplot as plt
from collections import Counter
import statistics

from selenium.webdriver.firefox.options import Options

#from selenium.webdriver.chrome.options import Options

import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import traceback
import re
from datetime import datetime
import json
import csv
import string
import time
import requests
import numpy as np
import glob
import os.path
from os import path
from fastai.vision.all import *
from tqdm import tqdm





# This class is all about tracking who I follow and who follows me
#
# LIST OF FUNCTIONS in "profile"
#
##########################
#
# 1. following_list(status)
# 2. in_database(username, table)
# 3. insert_info(table, username, info)
# 4. extract_info(username)
# 5. clean_text(text)
#
# Run following_list with status = 'following'/'followers' first
# This gets a list of users that follow/are followed by me
# Checks if they exist using in_database
# If they don't, extract profile information using extract_info

class profile(object):
    def __init__(self, setup):
        self.driver = setup.driver
        self.mycursor = setup.mycursor
        self.mydb = setup.mydb


    # Get the list of users that I follow
    def following_list(self, status):
        self.get_page('https://instagram.com/_briankelleher/')
        # Click the "followers" button
        #followers = -2
        #following = -1

        dictionary = {
            "followers": -2,
            "following": -1,
        }

        table_dict = {
            "followers" : "followed_users",
            "following" : "following_users"
        }

        # click on the button of the following or following tab using the dictionary
        button = self.driver.find_elements_by_class_name("g47SY")[dictionary[status]]

        # get number of followers for comparison later
        number_of_target = button.text.replace(',', '')

        button.click()

        time.sleep(5)

        start = time.time()

        print('---------- Starting the scroll ----------')

        # scroll to the bottom of the following/follower window
        self.scroll_window(int(number_of_target))

        end = time.time()
        print(f'FINISHED: {end - start}s')
        
        # Once all users have loaded, record them
        list_of_users = self.driver.find_elements_by_class_name('FPmhX')

        print(f'RETRIEVED: {len(list_of_users)}')
        print(f'TARGET: {number_of_target}')

        user_list = []
        u = ''

        # Cycle through list of users recorded and append them to list "user_list"
        for user in list_of_users:
            username = user.text
            
            # add username to a list for analysis later
            user_list.append(username)
            u += f"{user.text},"


        url = "cool2.txt"
        ff = open(url,"a") 
        ff.write(u)
        ff.write('\n')
        print('FILE HAS BEEN WRITTEN TO')
        
        # get a list of the current state of db
        # this looks like [andrew=>"following", dylan=>"not"]
        db_list = self.get_db_list(table_dict[status])

        # get all values of "not"
        status_table = 'followed'
        followed_list = self.get_table_list(table_dict[status], status_table)

        # user_list = ['Andrew', 'Harry', 'John']

        # db_list = [
        # 'Andrew'>'followed',
        # 'Harry'>'not',
        # 'Brandon'>'followed',
        # 'hilary'>'not'
        # ]

        # given this data, 
        # not_list: ['Harry', 'Hilary']
        # follow_list: ['Brandon', 'Andrew']

        # desired result:
        # gained: ['John', 'Harry]
        # lost: ['brandon']

        # how to get first result?
        # looking for elements in user_list and not in follow_list

        # how to get second result?
        # looking for elements in follow_list and not in user_list
        


        # use set theory to find the followers gained/lost of a given metric
        # it's good to lose followers from "following", bad for "followers"

        # if there is [dylan, andrew, harry] in user_list but [harry, andrew, luke] already exist in not_list
        # only want [dylan] returned
        # LOST USERS = absence of users

        # gained = [user_list - followed_list]
        # gained = [['Andrew', 'Harry', 'John'] - ['Brandon', 'Andrew']]
        # gained = ['Harry', 'John']

        # lost = [followed_list - user_list]
        # lost = [['Brandon', 'Andrew'] - ['Andrew', 'Harry', 'John']]
        # lost = ['Brandon']
        gained = self.diff_l1_l2(user_list, followed_list)

        lost = self.diff_l1_l2(followed_list, user_list)


        #print(f"Abolute number of {status} gained: {len(gained_temp)}")
        print(f"Net number of {status} gained: {len(gained)}")
        #print(f"Abolute number of {status} lost: {len(net_not_list)}")
        print(f"Net number of {status} lost: {len(lost)}")

        print("Lost:")
        print(lost)

        # user already exists

        for user in lost:
            self.update_status(table_dict[status], user, 'not')


        print("Gained:")
        print(gained)

        for user in gained:
            if (self.in_database(table_dict[status], user) != True):
                information = self.extract_info(user)
                self.insert_info(table_dict[status], information)

            self.update_status(table_dict[status], user, 'followed')
            self.update_date(user)


    def update_date(self, user):
        dt = self.get_dt()
        date_dt = dt[0]
        time_dt = dt[1]
        sql = f'''UPDATE followed SET outcome_date="{date_dt}" WHERE user="{user}"'''

    
    def dump_current_nums(self):
        # class name for the elements with following 
        # and followers is g47SY
        element_list = self.retrieve_name('g47SY')

        # followers then following
        followers = self.clean_num(element_list[1].text)
        following = self.clean_num(element_list[2].text)

        # get current time and date
        dt = self.get_dt()
        date_dt = dt[0]
        time_dt = dt[1]

        self.insert_current(followers, following, date_dt, time_dt)

        print('---- Current profile status retrieved ----')



    # get current time and date
    def get_dt(self):
        today = datetime.now()
        d1 = today.strftime("%d-%m-%Y")
        t1 = today.strftime("%H:%M:%S")

        return [d1, t1]


    def clean_num(self, text):
        text = text.replace(',', '')
        return text


    def insert_current(self, followers, following, date_dt, time_dt):
        sql = f'''INSERT INTO track_profile (followers, following, date, time) VALUES ("{followers}", "{following}", "{date_dt}", "{time_dt}")'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print('Record inserted about current status')



    def compare_status(self, status):
        btn_dict = {
            "followers": 1,
            "following": 2
        }
        # which button I should click
        btn_value = btn_dict[status]

        table_dict = {
            "followers": "followed_users",
            "following": "following_users"
        }

        # class to get info is g47SY 
        btn_class = "g47SY"
        count = self.retrieve_name(btn_class)[btn_value].text

        current_state = self.get_current_state(table_dict[status])

        if (current_state != count):
            return True
        else:
            return False


    # get number of following users in a given table
    def get_current_state(self, table):
        sql = f'''SELECT COUNT(*) FROM {table} WHERE status="followed"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        print(results[0]['COUNT(*)'])
        return results[0]['COUNT(*)']


    def get_table_list(self, table, field):
        sql = f'''SELECT username FROM {table} WHERE status="{field}"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        n_list = []

        for row in results:
            n_list.append(row['username'])

        return n_list


    # get list of users from a given table
    def get_db_list(self, table):
        sql = f'''SELECT username FROM {table}'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        n_list = []

        for row in results:
            n_list.append(row['username'])

        return n_list


    def lost_users(self, current, old):
        # it returns all the users that have unfollowed me
        # if I had:
        # current = [Dylan, Andrew] and old = [Dylan, Andrew, John], old list has more people
        # and therefore John must have unfollowed me
        net = set(old) - set(current)
        return list(net)
    

    # this is the first list element minus second
    def gained_users(self, current, old):
        # it returns all the users that have followed me and need the status updated
        # if I had:
        # current = [John, Dylan, Daniel] and old = [John, Dylan] it would return Daniel
        # it means Daniel has followed me and needs his status updated
        net = set(current) - set(old)
        return list(net)



    def diff_l1_l2(self, list1, list2):
        # get elements of list1 - list2
        net = set(list1) - set(list2)
        return list(net)

    
    def scroll_window(self, target):
        #As long as I don't have all the users, program will continue looping

        # This gets each user's element
        scroll_window = self.retrieve_name('FPmhX')

        # Loop through elements until all users are recorded

        attempts = 0

        pbar = tqdm(total=target) # Init pbar

        while (len(scroll_window) <= target):
            old = scroll_window
            self.driver.execute_script("arguments[0].scrollIntoView();", scroll_window[-1])
            time.sleep(1)
            scroll_window = self.retrieve_name('FPmhX')

            pbar.update(n = (len(scroll_window) - len(old)))
            
            if (old == scroll_window):
                attempts += 1

            if (len(scroll_window) > len(old)):
                attempts = 0

            if (attempts > 15):
                break
            
        print('complete')
        


    def print_progress(self, current, total):
        percent = (int(current) / int(total)) * 100
        return round(percent, 2)


    def in_database(self, table, username):
        # get all usernames without followers or following info
        sql = f"SELECT username, following FROM {table} WHERE username='{username}'"
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())

        # some checks for the results
        if (len(results) > 0):
            if (results[0]['username'] != '' and results[0]['following'] != ''):
                return True
    

    # insert the info into the mysql database
    def insert_info(self, table, info):
        sql = f'''INSERT INTO {table} (username, name, followers, following, pictures, date, follow_time, status) VALUES ("{info[0]}", "{info[1]}", "{info[2]}", "{info[3]}", "{info[4]}", "{info[5]}", "{info[6]}", "{info[7]}")'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print('Record inserted')


    def update_status(self, table, username, status):
        sql = f'''UPDATE {table} SET status="{status}" WHERE username="{username}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print(f'{username} {status} update')


    # extract information from my profile
    def extract_info(self, username):
        self.get_page("https://instagram.com/%s/" % username)

        time.sleep(2)
        
        try:
            name = self.retrieve_name('rhpdm')[0].text
            name = ''.join([i if ord(i) < 128 else ' ' for i in name])
        except:
            print('name not found')
            name = ''

        # get the list of photos, followers and following
        key_info = self.retrieve_name('g47SY')

        # clean data
        followers = self.clean_info(key_info[1].text)
        following = self.clean_info(key_info[2].text)
        photos = key_info[0].text.replace(',', '')

        # get current date
        today = datetime.now()
        d1 = today.strftime("%d-%m-%Y")
        t1 = today.strftime("%H:%M:%S")

        status = 'following'

        return [username, name, followers, following, photos, d1, t1, status]


    def get_page(self, url):
        self.driver.get(url)
        time.sleep(12)

    
    # clean followers/following
    def clean_info(self, text):
        text = text.replace(',','')
        if ('k' in text):
            text = text.replace('k', '')
            text = int(float(text) * 1000)
        return text


    # get element by class name
    def retrieve_name(self, class_name):
        return self.driver.find_elements_by_class_name(class_name)



# this class is used to get new users to follow from other people's profiles
# run following_list() with a username and a status and then it will collect all followers from that persons profile
class extract_users(object):
    def __init__(self, setup):
        self.driver = setup.driver
        self.mydb = setup.mydb
        self.mycursor = setup.mycursor


    # Get the list of users that I follow
    def following_list(self, username, status):
        self.get_page('https://instagram.com/%s' % username)
        # Click the "followers" button
        #followers = -2
        #following = -1

        dictionary = {
            "followers": -2,
            "following": -1,
        }

        # click on the button of the following or following tab using the dictionary
        button = self.driver.find_elements_by_class_name("g47SY")[dictionary[status]]

        # get number of followers for comparison later
        number_of_target = button.text.replace(',', '')

        print(number_of_target)

        button.click()

        time.sleep(5)

        start = time.time()

        print('Starting the scroll')

        # scroll to the bottom of the following/follower window
        self.scroll_window(int(number_of_target))

        end = time.time()
        print(end - start)
        
        # Once all users have loaded, record them
        list_of_users = self.driver.find_elements_by_class_name('FPmhX')

        user_list = []
        user_str = ''

        # Cycle through list of users recorded and append them to list "user_list"
        for user in list_of_users:
            item = user.text
            
            # add username to a list for analysis later
            user_list.append(item)

        current_users = self.get_db_list('followed')

        net_users = list(set(user_list) - set(current_users))

        for x in net_users:
            x = "%s," % x
            self.write_text(x, "asha")

        print(net_users)
        print(len(net_users))

        # run and verify each of the users
        self.process_users(net_users, username)


    def process_users(self, net_users, username):
        for user in net_users:
            if (self.in_database('followed', user) != True):
                try:
                    print('Processing %s' % user)
                    information = self.extract_info(user, username)
                    self.insert_info('followed', information)
                except Exception as e:
                    print(e, user)



    def from_textfile(self, profile):
        print('reading file')
        filename = 'asha.txt'
        filename_open = open(filename, "r")
        filename_read = filename_open.readlines()

        # The users are separated by ',' so they will be split and placed in 'list_of_users'
        list_of_users = filename_read[-1].split(",")
        print(len(list_of_users))

        self.process_users(list_of_users, profile)



    # Write infromation to a text file
    def write_text(self, text, destination):
        url = "%s.txt" % destination
        ff = open(url,"a") 

        ff.write(text)


    # get list of users from a given table
    def get_db_list(self, table):
        # Reinitialise the database to have new rows
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
            )

        self.mycursor = self.mydb.cursor()

        sql = f'''SELECT username FROM {table}'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        n_list = []

        for row in results:
            n_list.append(row['username'])

        return n_list


    # insert the info into the mysql database
    def update_table_info(self, table, username):
        sql = f'''INSERT INTO {table} (username, name, followers, following, pictures, date, time) VALUES ("{info[0]}", "{info[1]}", "{info[2]}", "{info[3]}", "{info[4]}", "{info[5]}", "{info[6]}")'''
        self.mycursor.execute(sql)
        self.mydb.commit()

    
    def scroll_window(self, target):
        #As long as I don't have all the users, program will continue looping
        user_list_full = 'incomplete'

        # This gets each user's element
        scroll_window = self.retrieve_name('FPmhX')

        # Loop through elements until all users are recorded

        attempts = 0

        while (len(scroll_window) <= target):
            old = scroll_window
            self.driver.execute_script("arguments[0].scrollIntoView();", scroll_window[-1])
            time.sleep(1)
            scroll_window = self.retrieve_name('FPmhX')

            if (len(scroll_window) > 1600):
                print(len(scroll_window))

            if (old == scroll_window):
                attempts += 1

            if (len(scroll_window) > len(old)):
                attempts = 0

            if (attempts > 10):
                break
            
        print('complete')



    def in_database(self, table, username):
        # get all usernames without followers or following info
        sql = f"SELECT username, following FROM {table} WHERE username='{username}'"
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())

        # some checks for the results
        if (len(results) > 0):
            if (results[0][0] != '' and results[0][1] != ''):
                return True
    

    # insert the info into the mysql database
    def insert_info(self, table, info):
        sql = f'''INSERT INTO {table} (username, name, followers, following, pictures, date, follow_time, status, outcome, profile_from) VALUES ("{info[0]}", "{info[1]}", "{info[2]}", "{info[3]}", "{info[4]}", "{info[5]}", "{info[6]}", "{info[7]}", "{info[8]}", "{info[9]}")'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print('Record inserted for %s' % info[0])


    def update_status(self, table, username, status):
        # Reinitialise the database to have new rows
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
            )

        self.mycursor = self.mydb.cursor()

        sql = f'''UPDATE {table} SET status="{status}" WHERE username="{username}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print(f'{username} {status} update')


    # extract information from my profile
    def extract_info(self, username, profile):
        self.get_page("https://instagram.com/%s/" % username)

        time.sleep(2)
        
        try:
            name = self.retrieve_name('rhpdm')[0].text
            name = ''.join([i if ord(i) < 128 else ' ' for i in name])
        except:
            print('name not found')
            name = ''

        # get the list of photos, followers and following
        key_info = self.retrieve_name('g47SY')

        # clean data
        followers = self.clean_info(key_info[1].text)
        following = self.clean_info(key_info[2].text)
        photos = key_info[0].text.replace(',', '')

        # get current date
        today = datetime.now()
        d1 = today.strftime("%d-%m-%Y")
        t1 = today.strftime("%H:%M:%S")

        status = 'not'
        outcome = 'not'

        return [username, name, followers, following, photos, d1, t1, status, outcome, profile]


    def get_page(self, url):
        self.driver.get(url)
        time.sleep(3)

    
    # clean followers/following
    def clean_info(self, text):
        text = text.replace(',','')
        if ('k' in text):
            text = text.replace('k', '')
            text = int(text) * 1000
        return text


    # get element by class name
    def retrieve_name(self, class_name):
        return self.driver.find_elements_by_class_name(class_name)




# requests is used to manage requests I send out
class request(object):
    def __init__(self, setup):
        self.driver = setup.driver
        self.mycursor = setup.mycursor
        self.mydb = setup.mydb

        self.white_list = [
            'layla.noone',
            'alexxgiblin',
            'ameliaflyn',
            'lucydaly21',
            'aisling_spillane',
            'molmuir',
            'mia.plower',
            'michellexmelvin',
            'jennyxrussell',
            'mollylongstaff',
            'leahhcarolann',
            'orlaryanx',
            'charlottefortunee',
            'sadbh_2626',
            'isabelle199xx',
            'athenaw_04',
            'ashagracierait',
            'charlie_garland_oconnor',
            'mollygosullivan',
            'olivia.walshx',
            'charlottemccarth.y',
            'poppystafford',
            'aoifebyrne02',
            'caoimheegilsenan',
            'qinyue_wang'
        ]


    def retrieve_name(self, class_name):
        return self.driver.find_elements_by_class_name(class_name)


    # insert the info into the mysql database
    def insert_info(self, table, info):
        sql = f'''INSERT INTO {table} (username, name, followers, following, pictures, date, follow_time, status) VALUES ("{info[0]}", "{info[1]}", "{info[2]}", "{info[3]}", "{info[4]}", "{info[5]}", "{info[6]}", "{info[7]}")'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print('Record inserted')

        
    # clean followers/following
    def clean_info(self, text):
        text = text.replace(',','')
        if ('k' in text):
            text = text.replace('k', '')
            text = int(text) * 1000
        return text

    
    # follow the next user with the lowest ratio of following to followers in the db
    def get_next_user(self, limit):
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()

        #sql = "SELECT username FROM followed WHERE profile_from='trindertcd' and status='not' and outcome='not' and gender='girl' ORDER BY CAST(ratio_following_to_follower AS SIGNED) ASC LIMIT 1"
        sql = f"SELECT username FROM followed WHERE status='not' and outcome='not' and profile_from is not null ORDER BY CAST(following AS SIGNED) DESC LIMIT {limit}"
        self.mycursor.execute(sql)

        results = list(self.mycursor.fetchall())

        return results

    
    # func in charge of following the next user
    def follow_next_user(self, limit):
        
        # get a list of users returned (usually 1/2)
        users = self.get_next_user(limit)

        # iterate through users and follow + insert each one
        for user in users:
            self.follow_user(user['username'])
            
            # brief wait
            time.sleep(random.randint(1, 3))


    # follow a user given a url
    def follow_user(self, username):

        # navigate to url
        self.get_page("https://instagram.com/%s" % username)

        time.sleep(random.randint(3, 5))

        dt = self.get_dt()

        # test to see if we are already friends
        if (self.follow_status() == 'not'):
            
            self.follow_button()
            print('"%s" has been followed!' % username)

        if (self.in_database('followed', username) == True):
            self.update_status('followed', username, 'followed', dt[0])
        else:
            info = self.extract_info(username)
            print('info has been extracted')
            self.insert_info('followed', info)



    def update_status(self, table, username, status, follow_date):
        sql = f'''UPDATE {table} SET status="{status}", follow_date="{follow_date}" WHERE username="{username}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print(f'{username}:{status} update')   


    def extract_info(self, username):
        try:
            name = self.retrieve_name('rhpdm')[0].text
            name = ''.join([i if ord(i) < 128 else ' ' for i in name])
        except:
            print('name not found')
            name = ''

        # get the list of photos, followers and following
        key_info = self.retrieve_name('g47SY')

        # clean data
        followers = self.clean_info(key_info[1].text)
        following = self.clean_info(key_info[2].text)
        photos = key_info[0].text.replace(',', '')

        # get current date
        today = datetime.now()
        d1 = today.strftime("%d-%m-%Y")
        t1 = today.strftime("%H:%M:%S")

        status = 'following'

        return [username, name, followers, following, photos, d1, t1, status]


    def get_page(self, url):
        self.driver.get(url)
        time.sleep(random.randint(4,6))


    def unfollow(self, username):
        if (username not in self.white_list):
            self.get_page('https://instagram.com/%s' % username)

            try:
                unfollow_button = self.retrieve_name('yZn4P')[0]
            except:
                unfollow_button = self.retrieve_name('sqdOP')[1]
            
            unfollow_button.click()

            time.sleep(random.randint(2,5))

            self.accept_prompt()

            self.update_status('followed', username, 'not', self.get_dt()[0])

            time.sleep(random.randint(3,7))
        else:
            print(username)


    def accept_prompt(self):
        try:
            self.driver.find_elements_by_xpath("//*[contains(text(), 'Unfollow')]")[-1].click()
        except:
            print('not found')
            

    # get current time and date
    def get_dt(self):
        today = datetime.now()
        d1 = today.strftime("%d-%m-%Y")
        t1 = today.strftime("%H:%M:%S")

        return [d1, t1]


    # func to click follow button
    def follow_button(self):
        # find the follow button
        follow_button = self.driver.find_elements_by_class_name('y3zKF')[0]

        # click follow button
        follow_button.click()


    # see whether I'm following the user whose page I'm on
    def follow_status(self):
        try:
            follow = self.driver.find_elements_by_xpath("//button[contains(text(), 'Follow')]")
            status = 'not'
            print(status)
            if (len(follow) == 0):
                status = 'following'
        except:
            status = 'following'

        print('%s is status' % status)

        return status


    def in_database(self, table, username):
    
        # get all usernames without followers or following info
        sql = f'''SELECT username, following FROM {table} WHERE username="{username}"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())

        # some checks for the results
        if (len(results) > 0):
            if (results[0]['username'] != '' and results[0]['following'] != ''):
                return True
    


# this class is used for analytics
class track(object):
    def __init__(self):
        # connect to db
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()

        

    def process_followed(self, username):
        sql = f'''UPDATE followed SET outcome="followed" WHERE username="{username}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print(f'Outcome updated for {username}')


    def process_following(self, username):
        sql = f'''UPDATE followed SET accepted="followed" WHERE username="{username}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print(f'Accepted updated for {username}')


    def get_requests_list(self):
        sql = '''SELECT * FROM followed where status="followed"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def get_track_profile(self):
        sql = '''SELECT * FROM track_profile'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def get_followed(self):
        sql = '''SELECT * FROM followed WHERE status="followed" AND follow_date is not NULL'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def extract_data_profile(self, lst, target):
        list_datetime = []
        list_count = []

        for row in lst:
            dt = datetime.combine(datetime.strptime(row['date'], '%d-%m-%Y').date(), datetime.strptime(row['time'], "%H:%M:%S").time())
            list_datetime.append(dt)
            list_count.append(int(row[target]))

        return list_datetime, list_count


    def extract_data_followed(self, lst):
        followed_temp_list = []

        for row in lst:
            followed_temp_list.append(row['follow_date'])
        
        # counts all the instances of a date to find how many people I followed that day
        follow_count = Counter(followed_temp_list)
        print(follow_count)

        new_dict = {}

        for row in follow_count:
            print(row)

            if ('-' in row):
                date_format = "%d-%m-%Y"
            elif ('/' in row):
                date_format = "%d/%m/%Y"

            try:
                dt = datetime.strptime(row, date_format)
                new_dict[dt] = follow_count[row]
            except:
                print('Error converting date')


        dictionary_items = new_dict.items()

        sorted_items = sorted(dictionary_items)
        print(sorted_items)


        dates_followed = []
        count_followed = []
        for x in sorted_items:
            dates_followed.append(x[0])
            count_followed.append(x[1])

        print(dates_followed, count_followed)
        
        return dates_followed, count_followed
    

    def convert_date(self, dt):
        try:
            if ('-' in dt):
                date_format = "%d-%m-%Y"
            elif ('/' in dt):
                date_format = "%d/%m/%Y"

            return datetime.strptime(dt, date_format)
        except:
            return 0

    def get_average_followed(self, lst):
        # mean() function
        followers_list = []
        following_list = []

        previous = lst[0]['follow_date']
        print(previous)

        new_dict = {}

        temp_list = []
        for row in lst:
            try:
                if (row['follow_date'] == previous):
                    temp_list.append(int(row['followers']))
                else:
                    new_dict[self.convert_date(row['follow_date'])] = statistics.mean(temp_list)
                    previous = row['follow_date']
                    temp_list = []
                    temp_list.append(int(row['followers']))
            except Exception as e:
                print(e)

        print(new_dict)
        return new_dict


    def get_ratio_score_data(self):
        sql = '''SELECT * FROM following_users WHERE average_score is not null and average_score!=0 and ratio_following_to_follower is not null'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def graph_ratio_vs_score(self):
        results = self.get_ratio_score_data()

        max_score = []
        min_score = []
        ratio = []
        avg = []
        followers = []

        for row in results:
            if (float(row['ratio_following_to_follower']) < 5):
                max_score.append(float(row['max_score']))
                ratio.append(float(row['ratio_following_to_follower']))
                avg.append(float(row['average_score']))
                min_score.append(float(row['min_score']))
                followers.append(float(row['followers']))
                


        plt.scatter(max_score, ratio)
        #plt.scatter(avg, ratio)

        plt.savefig("test.png")

        plt.show(block=True)

        plt.scatter(min_score, ratio)
        plt.savefig("test.png")
        plt.show(block=True)

        plt.scatter(avg, ratio)
        plt.savefig("test.png")
        plt.show(block=True)

        plt.scatter(avg, followers)
        plt.savefig("test.png")
        plt.show(block=True)


    def graph_all_faces(self):
        sql = '''SELECT * FROM faces WHERE score is not null'''
        self.mycursor.execute(sql)
        faces_results = list(self.mycursor.fetchall())

        sql = '''SELECT username, followers, following FROM following_users'''
        self.mycursor.execute(sql)
        users_results = self.mycursor.fetchall()

        faces = []
        user_followers = []

        for row in faces_results:

            for item in users_results:
                if (item['username'] == row['username']):
                    user_followers.append(float(item['following']))
                    faces.append(float(row['score']))

        plt.scatter(faces, user_followers)
        plt.savefig("test.png")
        plt.show(block=True)        

    def graph_users(self):
        
        followers_data = self.extract_data_profile(self.get_track_profile(), 'followers')
        datetime_followers = followers_data[0]
        count_followers = followers_data[1]
        plt.plot(datetime_followers, count_followers)

        following_data = self.extract_data_profile(self.get_track_profile(), 'following')
        datetime_following = following_data[0]
        count_following = following_data[1]
        plt.plot(datetime_following, count_following)

        followed_data = self.extract_data_followed(self.get_followed())
        datetime_followed = followed_data[0]
        count_followed = followed_data[1]
        plt.plot(datetime_followed, count_followed)

        plt.savefig("test.png")

        plt.show(block=True)


    def graph_change(self):
        
        followers_data = self.extract_data_profile(self.get_track_profile(), 'followers')
        datetime_followers = followers_data[0]
        count_followers = self.process_growth_list(followers_data[1])
        plt.plot(datetime_followers, count_followers)

        following_data = self.extract_data_profile(self.get_track_profile(), 'following')
        datetime_following = following_data[0]
        count_following = self.process_growth_list(following_data[1])
        plt.plot(datetime_following, count_following)

        plt.savefig("test.png")

        plt.show(block=True)


    def process_growth_list(self, lst):
        new_list = []
        old_value = lst[0]

        for item in lst:
            net_value = int(item) - int(old_value)
            new_list.append(net_value)
            old_value = item

        return new_list

        

class export(object):
    def __init__(self, input_filename):
        # connect to db
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()

        self.filename = input_filename


    def write_to_csv(self, input_list):
                
        with open(self.filename, 'a', newline='') as file:
            writer = csv.writer(file)
            for row in input_list:
                temp_list = []
                for item in row:
                    temp_list.append(item)

                writer.writerow(temp_list)

        print('Successfully written to csv')



    # dump all information to a csv
    def dump_all(self, table):
        rows = self.retrieve_all_info(table)
        self.write_to_csv(rows)


    # put specific info to a csv
    def dump_some(self, table, field, value):
        rows = self.retrieve_some_info(table, field, value)
        temp_list = []
        for row in rows:
            temp_list.append(list(row.values()))
        self.write_to_csv(temp_list)


    # get a specfic row from a db
    def retrieve_some_info(self, table, field, value):
        sql = f'''SELECT * FROM {table} WHERE {field}="{value}"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results

    
    # get all rows from a table
    def retrieve_all_info(self, table):
        sql = f"SELECT * FROM {table}"
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())

        temp_list = []
        for row in results:
            temp_list.append(row.values())

        return temp_list



    def user_difference(self):
        sql = '''SELECT username FROM following_users WHERE status="followed"'''
        self.mycursor.execute(sql)

        results = list(self.mycursor.fetchall())
        following = []
        for row in results:
            following.append(row['username'])

        sql = '''SELECT username FROM followed_users WHERE status="followed"'''
        self.mycursor.execute(sql)

        results = list(self.mycursor.fetchall())

        followers = []
        for row in results:
            followers.append(row['username'])

        net = set(following) - set(followers)
        return list(net)



    def dump_diff(self, filename):
        net = self.user_difference()
        print(len(net))

        for row in net:
            temp_list = []
            results = self.retrieve_row(row)

            self.write_row(filename, list(results[0].values()))



    def write_row(self, filename, row):
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)



    def retrieve_row(self, username):
        sql = f'''SELECT * FROM following_users WHERE username="{username}"'''
        self.mycursor.execute(sql)

        results = list(self.mycursor.fetchall())
        return results




# do analysis on the data
class analysis(object):
    def __init__(self):
        # connect to db
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()


    def get_table(self, table):
        sql = f'''SELECT * FROM {table} WHERE images_collected is not null and score is null'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def insert_avg_max(self):
        sql = '''SELECT * FROM following_users WHERE average_score is null or min_score is null or max_score is null and images_collected="collected"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())

        length = len(results)
        pbar = tqdm(total=length) # Init pbar

        for row in results:
            try:
                user = row['username']

                user_rows = db().get_specific_row('faces', 'username', user)

                if (len(user_rows) != 0):
                    user_score = []
                
                    for score in user_rows:
                        user_score.append(score['score'])

                    max_score = max(user_score)

                    average_score = round((sum(user_score) / len(user_score)), 4)

                    min_score = min(user_score)

                    db().update_column('following_users', 'average_score', average_score, 'username', user)

                    db().update_column('following_users', 'max_score', max_score, 'username', user)

                    db().update_column('following_users', 'min_score', min_score, 'username', user)

            except:
                pass
            finally:
                pbar.update(n=1)


    def insert_average_score(self):
        following_results = self.get_table('following_users')

        self.process_results('following_users', following_results)
        #self.process_results('followed_users', followed_results)



    def process_results(self, table, results):
        for row in results:
            try:
                user = row['username']
                user_rows = db().get_specific_row('faces', 'username', user)

                user_score = []

                for score in user_rows:
                    user_score.append(score['score'])

                average_score = max(user_score)
                print(average_score, user)
                column1 = 'score'
                value = average_score
                target = user
                column2 = 'username'
                db().update_column(table, column1, value, column2, target)

                print('Changes committed')
            except Exception as e:
                print(e)
            


    def open_beautiful_images(self):
        sql = '''SELECT url FROM faces WHERE score>4.7'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        
        for row in results:
            url = row['url']
            os.system(f'open {url}')

        self.mydb.close()

    def get_faces(self):
        sql = '''SELECT score, score FROM faces WHERE score is not null and score is not null and score!="None"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def clean_numbers(self):
        sql = '''SELECT following, followers, username FROM followed'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())

        for user in results:
            self.update(self.clean(user['following']), self.clean(user['followers']), user['username'])


    def update(self, following, followers, username):
        sql = f'''UPDATE followed SET following="{following}", followers="{followers}" WHERE username="{username}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print('updated')


    def clean(self, num):
        num = num.replace(',', '')

        if ('k' in num):
            num = num.replace('k', '')
            num = float(num) * 1000

        if ('m' in num):
            num = num.replace('m', '')
            num = float(num) * 1000000

        return int(num)



    def get_collected(self):
        sql = '''SELECT username FROM following_users WHERE images_collected="collected"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results



    def update_followed(self, username):
        sql = f'''UPDATE followed SET status="followed" WHERE username="{username}"'''
        self.mycursor.execute(sql)
        

    def u_followed(self):
        sql = '''SELECT username FROM following_users'''
        self.mycursor.execute(sql)

        results = list(self.mycursor.fetchall())

        for row in results:
            self.update_followed(row['username'])
            print(f'{row["username"]} entered')

        self.mydb.commit()
        self.mydb.close()


    def get_average_beauty(self):
        list_of_users = self.get_collected()

        for user in list_of_users:
            try:
                username = user['username']
                scores = self.get_scores(username)
                avg = max(scores)
                
                print(avg)

                self.update_user_score(username, avg)
            except Exception as e:
                print(e)



    def update_user_score(self, username, avg):
        sql = f'''UPDATE following_users SET average_score={avg} WHERE username="{username}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()
        print('Record updated')


    def get_scores(self, username):
        sql = f'''SELECT score FROM faces WHERE username="{username}"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        my_temp = []
        for x in results:
            my_temp.append(float(x[0]))

        return my_temp



    def get_names(self, gender):
        # name can either be Boys or Girls
        names = []

        with open(f'Top {gender}s Names 2003. Source CSO Ireland.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                names.append(row[0])

        return names


    def get_blank_rows(self, table, field, target):

        sql = f"SELECT {field}, id from {table} where {target} is NULL"
        
        self.mycursor.execute(sql)

        results = list(self.mycursor.fetchall())

        return results



    def correct_deciamls(self):
        sql = f"SELECT * from {table} WHERE pictures LIKE '%,%'"
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        
        for row in results:
            num = self.clean_num(row['pictures'])


    def get_names(self):
        sql = '''select * from following_users where status='following' order by id desc limit 150,20;'''


    def do_analysis(self):
        self.assign_genders('followed_users', 'name')
        self.assign_genders('following_users', 'username')

        self.assign_genders('following_users', 'name')
        self.assign_genders('following_users', 'username')

        self.assign_ratio('following_users')
        self.assign_ratio('followed_users')
        self.assign_ratio('followed')


    def assign_genders(self, table, field):
        boy_names = self.get_names('Boy')
        girl_names = self.get_names('Girl')

        blank_rows = self.get_blank_rows(table, field, 'gender')

        for row in blank_rows:
            name = list(row.values())[0]
            user_id = row['id']

            if (self.compare_names(name, girl_names, 'girl')):
                self.update_values(table, 'gender', 'girl', user_id)
            else:
                if (self.compare_names(name, boy_names, 'boy')):
                    self.update_values(table, 'gender', 'boy', user_id)


    def compare_names(self, name, gender_list, gender):
        for csv_name in gender_list:
            try:
                name = name.lower()
                csv_name = csv_name.lower() 

                if (csv_name in name):
                    print(csv_name, name)
                    return True
            except Exception as e:
                print(e)
                return False


    def get_all_rows(self, table):
        sql = f'''SELECT following, followers, id FROM {table}'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def assign_ratio(self, table):
        blank_rows = self.get_blank_rows(table, 'following, followers', 'ratio_following_to_follower')
        #blank_rows = self.get_all_rows(table)

        for row in blank_rows:
            try:
                following = self.clean_num(row['following'])
                followers = self.clean_num(row['followers'])
                user_id = row['id']

                ratio = following / followers
                ratio = round(ratio, 3)

                self.update_values(table, 'ratio_following_to_follower', ratio, user_id)
            except Exception as e:
                print(e)


    def clean_num(self, num):
        num = num.replace(',', '')

        if ('k' in num):
            num = num.replace('k', '')
            num = float(num) * 1000

        if ('m' in num):
            num = num.replace('m', '')
            num = float(num) * 1000000

        return int(num)


    def update_values(self, table, field, value, user_id):
        sql = f"UPDATE {table} set {field}='{value}' where id={user_id}"
        print(sql)
        self.mycursor.execute(sql)
        self.mydb.commit()


    
# main ways to interact is by liking my feed and viewing stories
# viewing stories are significantly less risky as you don't accidentally like something you don't mean to
# like feed func: like_feed() - runs forever
# prcoess stories: process_stories(stories_num) - stories_num = how many stories I should view
class interact(object):
    def __init__(self, setup):
        self.driver = setup.driver
        self.mycursor = setup.mycursor
 

    def process_stories(self, stories_num):
        self.get_page('https://instagram.com')
        time.sleep(6)

        stories = self.retrieve_name('eebAO')

        stories[random.randint(0, 3)].click()

        time.sleep(7)

        for inc in range(stories_num):
            right_arrow = self.retrieve_name('coreSpriteRightChevron')[0].click()
            time.sleep(random.random()*7)

        print(f'{stories_num} Stories processed')


    def retrieve_name(self, class_name):
        return self.driver.find_elements_by_class_name(class_name)


    def get_page(self, url):
        self.driver.get(url)
        time.sleep(3)

    
    def like_feed(self):
        self.get_page('https://instagram.com')
        # get list of photos on feed
        like_list = self.retrieve_name('_8-yf5')

        next_user = False

        print(len(like_list))
        inc = 0
        while (inc < 3):
            old_like_list = self.retrieve_name('_8-yf5')

            for item in like_list:
                if (item.get_attribute('aria-label') == 'Like' and item.get_attribute('height') == '24'):
                    self.scroll_to(item)

                    item.click()

                    time.sleep(random.random()*12)

            print('reached the end of the page')
            time.sleep(5)

            new_like_list = self.retrieve_name('_8-yf5')
            print(len(old_like_list), len(new_like_list))

            ra = len(old_like_list) -1

            like_list = new_like_list

            del like_list[0:ra]
            print(len(like_list))
            inc += 1


    
    def like_photos(self, max_likes):
        self.get_page('https://instagram.com')

        # get list of photos on feed
        net_list = self.retrieve_name('_8-yf5')

        print('----- Liking photos -----')
        photo_count = 0
        inc = 0
        while (inc < max_likes):
            current_state = self.retrieve_name('_8-yf5')

            for item in net_list:
                self.scroll_to(item)

                if (item.get_attribute('aria-label') == 'Like' and item.get_attribute('height') == '24'):
                    time.sleep(5)
                    item.click()
                    photo_count += 1
                    time.sleep(random.random()*7)


                if (random.random() < .5):
                    time.sleep(random.random()*5)

            time.sleep(5)

            new_state = self.retrieve_name('_8-yf5')
            
            net_list = []
            for item in new_state:
                if (item not in current_state):
                    net_list.append(item)

            inc += 1




    def scroll_to(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(false);", element)



class download(object):
    def __init__(self, setup):
        print("requests file:", requests.__file__)
        self.mycursor = setup.mycursor
        self.mydb = setup.mydb
        self.driver = setup.driver



    # download images given a username
    # main function in class
    def download_images(self, username):

        images = self.scroll_window(username)

    # download profile picture given username
    def profile_picture(self, username):
        folder_checks(username)
        
        picture = self.retrieve_name('_6q-tv')[0]

        url = picture.get_attribute('src')
        alt = picture.get_attribute('alt')
        alt = alt.replace("'", '').replace('"', '')

        date_time = self.get_dt()
        date_dt = date_time[0]
        time_dt = date_time[1]

        filename = f"images/{username}/process/profile_{date_dt}_{time_dt}.jpg"

        self.download_url(url, filename)

        self.insert_image(username, date_dt, time_dt, '0', url, alt, filename)

        picture.click()
        time.sleep(2)


    # download story images from the profile picture
    def stories(self, username):
        self.retrieve_name('_8-yf5')[0].click()
        time.sleep(1)

        image = self.retrieve_name('i1HvM')[0]

        url = image.get_attribute('src')
        alt = image.get_attribute('alt')

        date_time = self.get_dt()
        date_dt = date_time[0]
        time_dt = date_time[1]

        filename = f"images/{username}/process/story_{date_dt}_{time_dt}.jpg"

        self.download_url(url, filename)

        self.insert_image(username, date_dt, time_dt, '0', url, alt, filename)


    # scroll down the profile picture to load all images
    def scroll_window(self, username):
        #As long as I don't have all the users, program will continue looping
        user_list_full = 'incomplete'

        # This gets each user's element
        scroll_window = self.driver.find_elements_by_class_name('FFVAD')
        scroll_window_old = []

        # keep track of attempts to ensure bottom of the scroll window is reached
        attempts = 1

        inc = 0

        images = []

        folder_checks(username)

        if (len(scroll_window) > 0):

            # Loop through elements until all users are recorded
            while (user_list_full == 'incomplete'):
                # Scroll down to load new users
                self.driver.execute_script("arguments[0].scrollIntoView();", scroll_window[-1])

                #time.sleep(random.randint(2,2))
                time.sleep(6)

                # get the net images and add them to the list
                net_images = self.add_images(scroll_window, scroll_window_old)

                # Assign old list of users for comparison with new ones
                scroll_window_old = scroll_window

                scroll_window = self.driver.find_elements_by_class_name('FFVAD')

                for image in net_images:
                    url = image.get_attribute('src')
                    alt = image.get_attribute('alt').replace('"', '').replace("'",'')
                    alt = ''.join([i if ord(i) < 128 else ' ' for i in alt])

                    alt = alt[:999]

                    dt = self.get_dt()
                    date_dt = dt[0]
                    time_dt = dt[1]
                    inc += 1
                    
                    filename = f"images/{username}/process/{inc}_{date_dt}_{time_dt}.jpg"
                
                    # download image
                    self.download_url(url, filename)

                    self.insert_image(username, date_dt, time_dt, inc, url, alt, filename)

                time.sleep(2)

                # If old list of users is equal to new list
                if (len(scroll_window) == len(scroll_window_old)): 
                    if (attempts == 0):
                        user_list_full = 'complete'
                    attempts -= 1

        else:
            images = []
            
        return images


    # insert image to table
    def insert_image(self, username, date, time, photo_id, url, alt, filename):
        sql = f'''INSERT INTO images (username, date, time, photo_id, url, alt, filename) VALUES ("{username}", "{date}", "{time}", "{photo_id}", "{url}", "{alt}", "{filename}")'''
        self.mycursor.execute(sql)
        self.mydb.commit()


    # get page given url
    def get_page(self, url):
        self.driver.get(url)
        time.sleep(3)


    # get the net images that need to be added to the list
    def add_images(self, current, old):
        net = set(current) - set(old)
        return list(net)


    # get element by class
    def retrieve_name(self, class_name):
        return self.driver.find_elements_by_class_name(class_name)


    # get current time and date
    def get_dt(self):
        today = datetime.now()
        d1 = today.strftime("%d-%m-%Y")
        t1 = today.strftime("%H:%M:%S")

        return [d1, t1]


    # download image given url
    def download_url(self, url, filename):
        response = requests.get(url)

        image = open(filename, "wb")
        image.write(response.content)
        image.close()


    # get list of users that need to have images collected
    def get_users(self, limit, offset=0):
        sql = f'''SELECT username FROM following_users WHERE images_collected is null and status="followed" and pictures NOT LIKE "%,%" and pictures<50 and pictures>0 ORDER BY id DESC LIMIT {offset}, {limit}'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        print(len(results))
        return results


    # update image collection status
    def update_user(self, username):
        sql = f'''UPDATE following_users SET images_collected="collected" WHERE username="{username}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()




class training(object):
    def __init__(self):
        # connect to db
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="training",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()


    def get_rows(self):
        sql = 'SELECT * FROM images WHERE score is not null'
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def copy_images(self):
        images = self.get_rows()

        for row in images:
            url = row['url'].split('/')[-1]
            os.system(f"cp {row['url']} training/{row['score']}/{url}")


class beauty_score(object):

    import cv2

    def __init__(self):
                
        # connect to db
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()

        # load model
        self.ML_model = load_learner('export.pkl')

        # Needed for image preprocessing later.
        self.CASCADE = "Face_cascade.xml"
        self.FACE_CASCADE = self.cv2.CascadeClassifier(self.CASCADE)


    # this is the main function for the class
    def images(self, username):
        image_count = 0

        # verify folder structure exists
        folder_checks(username)

        # list images that need to be processed
        images = os.listdir(f'images/{username}/process')

        # process each image
        for image in images:
            # extract faces from image
            processed_images = self.process_image(f'images/{username}/process/{image}')
            
            # move image from processed folder to finished folder
            os.system(f'mv images/{username}/process/{image} images/{username}/finish/{image}')

            # get ratings for the faces
            ratings = self.process_faces(processed_images, username, image_count)
            image_count += 1


    # Define function to extract and preprocess face images from photos. Results in 350x350 pixel images.
    def extract_faces(self, image):
        
        processed_images = []

        # convert image to grayscale
        image_grey = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2GRAY)

        # Minimum size of detected faces is set to 75x75 pixels.
        faces = self.FACE_CASCADE.detectMultiScale(image_grey,scaleFactor=1.16,minNeighbors=5,minSize=(75,75),flags=0)

        for x,y,w,h in faces:
            # attempt to extract faces from each image
            try:
                sub_img = image[y-15:y+h+15,x-15:x+w+15]
                side = np.max(np.array([sub_img.shape[0],sub_img.shape[1]]))
                sub_image_padded = self.cv2.copyMakeBorder(sub_img,int(np.floor((side-sub_img.shape[1])/2)),int(np.ceil((side-sub_img.shape[1])/2)),int(np.floor((side-sub_img.shape[0])/2)),int(np.ceil((side-sub_img.shape[0])/2)),self.cv2.BORDER_CONSTANT)
                sub_image_resized = self.cv2.resize(src = sub_image_padded,dsize=(400,400))
                processed_images.append(sub_image_resized)
            except Exception as e:
                print(e)

        return processed_images


    # process each image
    def process_image(self, image_filename):

        # read the filename
        image = self.cv2.imread(image_filename)

        # get faces from image
        processed_images = self.extract_faces(image)

        return processed_images


    # get beauty score for each face
    def process_faces(self, processed_images, username, photo_num):

        face_count = 0
        ratings = [0]

        # iterate through processed_images
        # load the image and run it through the ML model
        if (len(processed_images) > 0):
            for face in processed_images:
                # get current time and date
                dt = self.get_dt()
                date_dt = dt[0]
                time_dt = dt[1]
                
                # write the face to a file
                filename = f"images/{username}/face/{photo_num}_{date_dt}_{time_dt}_{face_count}.jpg"

                self.cv2.imwrite(filename, face)

                # Apply the neural network to predict face beauty.
                pred = self.ML_model.predict(filename)

                # insert the face and rating into DB
                self.insert_face(username, pred[0][0], date_dt, time_dt, photo_num, filename)

                face_count += 1

        return ratings


    def update_ml_score(self, prediction, url):
        sql = f'''UPDATE faces SET score="{prediction}" WHERE url="{url}"'''
        self.mycursor.execute(sql)
        

    def commit_changes(self):
        self.mydb.commit()


    def get_faces(self):
        sql = '''SELECT url FROM faces WHERE score IS NULL'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def predict_face(self, url):

        # Apply the neural network to predict face beauty.
        pred = self.ML_model.predict(url)
        return (pred[0][0])


    # get current time and date
    def get_dt(self):
        today = datetime.now()
        d1 = today.strftime("%d-%m-%Y")
        t1 = today.strftime("%H:%M:%S")

        return [d1, t1]

    
    # insert face into table
    def insert_face(self, username, score, date, time, photo_id, url):
        sql = f'''INSERT INTO faces (username, score, date, time, photo_id, url) VALUES ("{username}", "{score}", "{date}", "{time}", "{photo_id}", "{url}")'''
        self.mycursor.execute(sql)
        self.mydb.commit()



class setup(object):
    def __init__(self):
        
        # Use the following code for Chrome

        # Default profile:
        #options = webdriver.ChromeOptions() 

        # Custom profile
        '''
        options = Options()
        options.add_argument('--profile-directory=Profile 1')

        options.add_argument("user-data-dir=/Users/briankelleher/Library/Application Support/Google/Chrome/")
        options.add_argument('--profile-directory=Default')



        self.driver = webdriver.Chrome(chrome_options=options, executable_path="/Users/briankelleher/ig/chromedriver")
                                    
        '''

        # Put your firefox profile here
        profile = webdriver.FirefoxProfile('/Users/briankelleher/Library/Application Support/Firefox/Profiles/gi3j6ich.default')

        #options = Options()
        #options.headless = True

        self.driver = webdriver.Firefox(firefox_profile=profile)
        #self.driver = webdriver.Firefox(firefox_profile=profile, options=options)

        # connect to db
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()

        print(self.mycursor)

        time.sleep(3)
        print('setup complete')



    def close_connection(self):
        self.mydb.close()
        self.driver.quit()



class stats(object):
    def __init__(self):
        pass


class db(object):
    def __init__(self):
        # connect to db
        self.mydb = pymysql.connect(
            host="34.89.55.66",
            user="root",
            password="Mintylucky9",
            database="instagram",
            cursorclass=pymysql.cursors.DictCursor
        )

        self.mycursor = self.mydb.cursor()



    def get_table(self, table):
        sql = f'''SELECT * FROM {table}'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def get_specific_row(self, table, column, value):
        sql = f'''SELECT * FROM {table} WHERE {column}="{value}"'''
        self.mycursor.execute(sql)
        results = list(self.mycursor.fetchall())
        return results


    def update_column(self, table, column1, value, column2, target):
        sql = f'''UPDATE {table} SET {column1}="{value}" WHERE {column2}="{target}"'''
        self.mycursor.execute(sql)
        self.mydb.commit()
    

    def commit_changes(self):
        self.mydb.commit()


def folder_checks(username):
    if (path.exists(f'images/{username}') == False):
            os.system(f'mkdir images/{username}')

    if (path.exists(f'images/{username}/face') == False):
        os.system(f'mkdir images/{username}/face')


    if (path.exists(f'images/{username}/process') == False):
        os.system(f'mkdir images/{username}/process')


    if (path.exists(f'images/{username}/finish') == False):
        os.system(f'mkdir images/{username}/finish')
