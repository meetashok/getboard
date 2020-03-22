import pandas as pd
import numpy as np
from collections import defaultdict

datalocation = "../../data/userinfo.csv"

names = [
    "username", "gameid", "userrating", "own", "prevowned", 
    "fortrade", "want", "wanttoplay", "wanttobuy", "wishlist", 
    "wishlistpriority", "preordered", "numplays", "lastmodified"
]

print("Reading userinfo.csv...")
userinfo = pd.read_csv(datalocation, names=names)

# Saving usernames to csv
# Users are sorted in the descending order of number of games
print("Saving unique usernames")
usernames = userinfo\
    .groupby("username", as_index=False)["gameid"]\
    .count()\
    .rename({"gameid": "game_count"}, axis=1)\
    .sort_values("game_count", ascending=False)\
    .reset_index(drop=True)

usernames.index.name = "index"
usernames.to_csv("../../data/unique_usernames.csv")

# Saving games to csv
# Games are sorted in descending order of the number of users
print("Saving unique gameids")
games = userinfo\
    .groupby("gameid", as_index=False)["username"]\
    .count()\
    .rename({"username": "user_count"}, axis=1)\
    .sort_values("user_count", ascending=False)\
    .reset_index(drop=True)\

games.index.name = "index"
games.to_csv("../../data/unique_games.csv")