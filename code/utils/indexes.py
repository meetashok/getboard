import pandas as pd

username_location = "../data/unique_usernames.csv"
gameid_location = "../data/unique_games.csv"

usernames = pd.read_csv(username_location)
games = pd.read_csv(gameid_location)

index_to_username = {}
username_to_index = {}
index_to_gameid = {}
gameid_to_index = {}

for i, row in usernames.iterrows():
    index = row.get("index")
    username = row.get("username")
    index_to_username[index] = username
    username_to_index[username] = index

for i, row in games.iterrows():
    index = row.get("index")
    gameid = row.get("gameid")
    index_to_gameid[index] = gameid
    gameid_to_index[gameid] = index