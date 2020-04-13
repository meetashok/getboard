import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime
import random
import xml.etree.ElementTree as ET 
import csv

MIN_TIME = 1
MAX_TIME = 3

def sleep(MIN_TIME, MAX_TIME):
    time.sleep(random.randint(MIN_TIME*10, MAX_TIME*10)/10)

def build_url(username):
    base_url = "https://www.boardgamegeek.com"
    collections_url = "/xmlapi2/collection?username="
    url = f"{base_url}{collections_url}{username}&excludesubtype=boardgameexpansion&stats=1"
    return url

def userslist():
    usernames_file = "../../data/cleaned_usernames.csv"
    usernames = pd.read_csv(usernames_file, names=["username"])\
            .username\
            .values

    try:
        completed_usernames = pd.read_csv("../../data/userinfo.csv", names=["username"], usecols=[0])\
            .username\
            .unique()
    except pd.errors.EmptyDataError:
        completed_usernames = []
    
    try:
        skipped_usernames = pd.read_csv("../../data/usersskipped.csv", names=["username"])\
            .username\
            .unique()
    except pd.errors.EmptyDataError:
        skipped_usernames = []

    try:
        nogames_usernames = pd.read_csv("../../data/usernogames.csv", names=["username"])\
            .username\
            .unique()
    except pd.errors.EmptyDataError:
        nogames_usernames = []

    final_users = list(set(usernames).union(set(skipped_usernames)).difference(set(completed_usernames)).difference(set(nogames_usernames)))

    print(f"Total users     = {len(usernames):,.0f}")
    print(f"Completed users = {len(completed_usernames):,.0f}")
    print(f"Skipped users   = {len(skipped_usernames):,.0f}")
    print(f"No game users   = {len(nogames_usernames):,.0f}")
    print(f"In this run     = {len(final_users):,.0f}")
        
    return final_users

def information(item):
    gameid = item.get("objectid")
    userrating = item.find("stats").find("rating").get("value")
    
    status = item.find("status")
    
    own = status.get("own")
    prevowned = status.get("prevowned")
    fortrade = status.get("fortrade")
    want = status.get("want")
    wanttoplay = status.get("wanttoplay")
    wanttobuy = status.get("wanttobuy")
    wishlist = status.get("wishlist")
    wishlistpriority = status.get("wishlistpriority")
    preordered = status.get("preordered")
    lastmodified = status.get("lastmodified")

    numplays = item.find("numplays").text
    
    comment_tag = item.find("comment")

    if not comment_tag is None:
        commentdata = (username, gameid, userrating, comment_tag.text.encode("utf-8", "ignore"))
    else:
        commentdata = None
    
    userdata = (username, gameid, userrating, own, prevowned, 
            fortrade, want, wanttoplay, wanttobuy, 
            wishlist, wishlistpriority, preordered, 
            numplays, lastmodified)

    return userdata, commentdata

if __name__ == "__main__":
    usernames = userslist()
    
    for i, username in enumerate(usernames[:20]):
        timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timenow}: {i+1:6}: {username}")

        url = build_url(username)
        response = requests.get(url)
        tries = 0
        while not response.status_code == 200:
            tries += 1
            sleep(MIN_TIME, MAX_TIME)
            if tries >= 3:
                with open("../../data/usersskipped.csv", "a+") as f:
                    f.write(f"{username}\n")
                break
            response = requests.get(url)
                
        data = ET.fromstring(response.text)
        
        if "errors" in data.keys():
            message = data.find("message")
            print(message)
        else:
            if data.get("totalitems") != "0":
                items = data.findall("item")
        
                for item in items:
                    userdata, commentdata = information(item)
                    with open("../../data/userinfo.csv", "a+") as f:
                        userinfo_out = csv.writer(f)
                        userinfo_out.writerow(userdata)
                        
                    if commentdata:
                        with open("../../data/usercomments.csv", "a+") as f:
                            usercomments_out = csv.writer(f)
                            usercomments_out.writerow(commentdata)
            else:
                with open("../../data/usernogames.csv", "a+") as f:
                        record = f"{username}\n"
                        f.write(record)
            
        sleep(MIN_TIME, MAX_TIME)