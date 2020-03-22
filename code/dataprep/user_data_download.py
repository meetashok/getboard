import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime
import random

def build_zipcode(number):
    '''The zip column in the uszips file is read as a number
    This function converts the number to a string and prefixes
    additional zeroes to make the length == 5
    '''
    num_string = str(number)
    if len(num_string) == 5:
        return num_string
    else:
        return (5 - len(num_string))*"0" + num_string
    
def get_zipcodes(filename):
    '''Reads the zipcode file and returns an array of zipcode
    '''
    data = pd.read_csv(filename)
    data["zip"] = data.zip.apply(build_zipcode)
    
    zipcodes = data.zip.values
    
    print(f"Number of zipcodes in US: {len(zipcodes):,.0f}")
    
    return zipcodes

def sleep(MIN_TIME, MAX_TIME):
    time.sleep(random.randint(MIN_TIME*10, MAX_TIME*10)/10)
    
def build_url(zipcode, maxdist):
    base_url = "https://boardgamegeek.com/findgamers.php?action=findclosest&country=US&"
    url = f"{base_url}srczip={zipcode}&maxdist={maxdist}&B1=Submit"
    return url

def get_userinfo(div):
    username = div.get("data-username")
    urlusername = div.get("data-urlusername")
    userid = div.get("data-userid")
    name = div.div.text
    
    return urlusername, username, userid, name


if __name__ == "__main__":
    filename = "../../data/uszips.csv"

    MIN_TIME = 1
    MAX_TIME = 3

    MAXDIST = 25

    zipcodes = get_zipcodes(filename)

    n_requests = 0
    n_users = 0

for i, zipcode in enumerate(zipcodes[30:33]):
    url = build_url(zipcode, MAXDIST)
    response = requests.get(url)
    
    timenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if response.ok:
        html_soup = BeautifulSoup(response.text, 'html.parser')
        user_divs = html_soup.find_all("div", class_="avatarblock")
        with open("../../data/usernames_download.csv", "a+") as f:
            record = f"{timenow},{zipcode},{MAXDIST},{len(user_divs)}\n"
            f.write(record)
        if len(user_divs) > 0:
            for div in user_divs:
                urlusername, username, userid, name = get_userinfo(div)
                with open("../../data/usernames.csv", "a+") as f:
                    record = f"{zipcode},{MAXDIST},{urlusername},{username},{userid},{name}\n"
                    f.write(record)
    
    n_requests += 1
    n_users += len(user_divs)
    
    print(f"{timenow}, Requests: {n_requests}, Users: {n_users}")
    
    sleep(MIN_TIME, MAX_TIME)