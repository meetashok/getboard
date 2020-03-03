import requests
import re
from bs4 import BeautifulSoup

import time
import datetime
import random

starting_page = None
ending_page = None

base_url = "https://boardgamegeek.com/browse/boardgame/page/"

MIN_TIME = 1
MAX_TIME = 5

def sleep(MIN_TIME, MAX_TIME):
    time.sleep(random.randint(MIN_TIME*10, MAX_TIME*10)/10)

def boardgameinfo(info):
    links = info.find_all("a")
    
    rank = links[0].get("name")
    gameid = links[1].get("href").split("/")[2]
    gamename = links[2].text
    
    span = info.select("span")
    if len(span) > 0:
        releaseyear = span[0].text
    else:
        releaseyear = ""
    
    if len(releaseyear) > 0:
        if (releaseyear[0] == "(") & (releaseyear[-1] == ")"):
            releaseyear = releaseyear[1:-1]
    
    ratingdata = info.find_all("td", {"class": "collection_bggrating"})
    
    geekrating = ratingdata[0].text.strip()
    userrating = ratingdata[1].text.strip()
    numvotes = ratingdata[2].text.strip()
    
    return (rank, gameid, releaseyear, geekrating, userrating, numvotes, gamename)

def geturl(base_url, pagenumber):
    return f"{base_url}{pagenumber}"

if __name__ == "__main__":
    timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    games_collected = 0

    for pagenumber in range(starting_page, ending_page+1):
        url = geturl(base_url, pagenumber)
        response = requests.get(url)
        while response.status_code != 200:
            print(response.status_code)
            sleep(MIN_TIME, MAX_TIME)
            response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.find_all("tr", {"id": "row_"})

        if len(rows) > 0:
            for row in rows:
                rank, gameid, releaseyear, geekrating, userrating, numvotes, gamename = boardgameinfo(row)
                with open("../data/boardgames.csv", "a+") as f:
                    record = f"{rank},{gameid},{releaseyear},{geekrating},{userrating},{numvotes},'{gamename}'\n"
                    f.write(record)

        games_collected += len(rows)

        print(f"{timenow}, Page: {pagenumber}, Games: {games_collected}")

        sleep(MIN_TIME, MAX_TIME)













