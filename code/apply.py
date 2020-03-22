from train import build_userinfo
import turicreate as tc 
import pandas as pd
import numpy as np

import requests
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

import argparse

def build_gamesinfo(location):
    names = [
        "gameid",
        "primaryname",
        "yearpublished",
        "gamerank",
        "usersrated",
        "average",
        "bayesaverage",
        "minplayers",
        "maxplayers",
        "playingtime",
        "minplaytime",
        "maxplaytime",
        "thumbnail",
    ]
    gamesinfo = pd.read_csv(location, names=names)\
        .assign(primaryname=lambda row: row.primaryname.str[1:-1])

    return gamesinfo

class BoardGameRecommender(object):
    def __init__(self, username, input_games, model, userinfo, gamesinfo, k=5):
        self.username = username
        self.model = model
        self.userinfo = userinfo
        self.gamesinfo = gamesinfo
        self.k = k
        self.input_games = input_games

    def recommendations(self):
        if self.input_games:
            recs = self.model.recommend_from_interactions(self.input_games, k=self.k)
        else:
            if self.username not in self.userinfo.username.unique():
                print(f"Username {self.username} not found\n")
            recs = self.model.recommend(users=[self.username], k=self.k)\

        recs_df = recs.to_dataframe()\
            .merge(self.gamesinfo, how="inner", 
                on="gameid")\
            .filter(["gameid", "score", "rank", "primaryname"])

        return recs_df

    def get_rated_games(self):
        filtered = self.userinfo\
            .query("username == @self.username")\
            .merge(self.gamesinfo, how="inner", on="gameid")\
            .filter(["primaryname", "userrating"])\

        return filtered

    def recs_summary(self):
        rated_games = self.get_rated_games()

        recs = self.recommendations().primaryname.values
        
        print("-"*30)
        print(f"Username: {self.username}")
        
        if self.input_games is None:
            print(f"User has rated {len(rated_games.index)} games")

        if len(rated_games.index) > 0:
            print("-"*30)
            sampled_games = rated_games.sample(n=10).sort_values("userrating", ascending=False)
            for i, (primaryname, userrating) in enumerate(sampled_games.values):
                print(f"{i+1:2.0f}. {primaryname:30}: {userrating:4.1f}")

        if self.input_games:
            print("-"*30)
            print(f"User has liked {len(self.input_games)} games")
            for i, gameid in enumerate(self.input_games):
                gamename = self.gamesinfo.query("gameid == @gameid")["primaryname"].iloc[0]
                print(f"{i+1:2.0f}. {gamename:30}")

        print("-"*30)
        print("Recommended games:")
        for i, rec in enumerate(recs):
            print(f"{i+1:2.0f}. {rec}")
        print("-"*30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sample command:  python apply.py -u <username>')
    parser.add_argument("-u", "--username", dest="username",
                        help="Provide a username for generating recommendations")
    parser.add_argument("-k", "--n_recommendations", dest="k", 
                        help="Number of recommendations", type=int)
    parser.add_argument("-g", "--games", dest="input_games", required=False,
                        help="Provide the games that the user has liked")
    
    args = parser.parse_args()

    username = args.username
    k = args.k
    if args.input_games is not None:
        input_games = [int(gameid) for gameid in args.input_games.split(",")]
    else:
        input_games = None

    userinfo = build_userinfo("../data/userinfo.csv")
    gamesinfo = build_gamesinfo("../data/gamesinfo.csv")
    model = tc.load_model("../models/itemsimilarity_2020-03-15")

    recommender = BoardGameRecommender(username, input_games, model, userinfo, gamesinfo, k=k)
    recommender.recs_summary()