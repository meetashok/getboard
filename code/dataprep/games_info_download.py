from utils.indexes import index_to_gameid, gameid_to_index
import requests
import pandas as pd
import numpy as np
import time
import datetime
import random
import xml.etree.ElementTree as ET 
import csv

timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_gamesids(index_to_gameid, n=100):
    max_id = max(index_to_gameid.keys())
    all_gameids = np.array([index_to_gameid[i] for i in range(max_id)])

    iterations = max_id // n + 1
    
    for iteration in range(iterations):
        ids = all_gameids[n*iteration: n*(iteration+1)]
        yield ",".join([str(id) for id in ids])

MIN_TIME = 1
MAX_TIME = 3

def sleep(MIN_TIME, MAX_TIME):
    time.sleep(random.randint(MIN_TIME*10, MAX_TIME*10)/10)

def build_url(ids_string):
    base_url = "https://www.boardgamegeek.com"
    thing_url = "/xmlapi2/things?id="
    url = f"{base_url}{thing_url}{ids_string}&stats=1"
    return url

def get_xml_data(ids):
    url = build_url(ids)
    response = requests.get(url)
    tries = 0
    while not response.status_code == 200:
        tries += 1
        sleep(MIN_TIME, MAX_TIME)
        if tries >= 3:
            with open("../../data/gamesskipped.csv", "a+") as f:
                f.write(f"{ids}\n")
            break
        response = requests.get(url)

    data = ET.fromstring(response.text)
    return data

def extract_information(item):
    objectid = item.get("id")

    if item.find("thumbnail") is not None:
        thumbnail = item.find("thumbnail").text
    else:
        thumbnail = None
    yearpublished = item.find("yearpublished").get("value")
    
    names = item.findall("name")
    for name in names:
        if name.get("type").lower() == "primary":
            primaryname = f'"{name.get("value")}"'
            break
    
    minplayers = item.find("minplayers").get("value")
    maxplayers = item.find("maxplayers").get("value")

    playingtime = item.find("playingtime").get("value")
    minplaytime = item.find("minplaytime").get("value")
    maxplaytime = item.find("maxplaytime").get("value")

    minage = item.find("minage").get("value")

    categories, mechanics = [], []
    
    links = item.findall("link")
    for link in links:
        if link.get("type") == "boardgamecategory":
            categories.append(f'"{link.get("value")}"')
        if link.get("type") == "boardgamemechanic":
            mechanics.append(f'"{link.get("value")}"')

    ratings = item.find("statistics").find("ratings")
    usersrated = ratings.find("usersrated").get("value")
    average = ratings.find("average").get("value")
    bayesaverage = ratings.find("bayesaverage").get("value")

    ranks = ratings.find("ranks").findall("rank")
    gamerank = None
    for rank in ranks:
        if rank.get("name") == "boardgame":
            gamerank = rank.get("value")

    return_tuple = [
        objectid,
        primaryname,
        yearpublished,
        gamerank,
        usersrated,
        average,
        bayesaverage,
        minplayers,
        maxplayers,
        playingtime,
        minplaytime,
        maxplaytime,
        thumbnail,
        categories,
        mechanics,
    ]

    return return_tuple

if __name__ == "__main__":
    for ids in get_gamesids(index_to_gameid, n=100):
        timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = get_xml_data(ids)
        items = data.findall("item")

        for item in items:
            result_tuple = extract_information(item)
            objectid = result_tuple[0]
            print(f"{timenow}: {objectid}")
            gamesdata = result_tuple[:-2]

            with open("../../data/gamesinfo.csv", "a+") as f:
                gamesinfo_out = csv.writer(f)
                gamesinfo_out.writerow(gamesdata)

            categories, mechanics = result_tuple[-2:]

            with open("../../data/gamescategories.csv", "a+") as f:
                gamescategories_out = csv.writer(f)
                for category in categories:
                    category_row = [objectid, "category", category]
                    gamescategories_out.writerow(category_row)
                
                for mechanic in mechanics:
                    mechanic_row = [objectid, "mechanic", mechanic]
                    gamescategories_out.writerow(mechanic_row)
            
        sleep(MIN_TIME, MAX_TIME)