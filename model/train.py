# from utils.indexes import index_to_username, username_to_index
# from utils.indexes import index_to_gameid, gameid_to_index

import pandas as pd
import numpy as np

import turicreate as tc
from turicreate import recommender, item_similarity_recommender, factorization_recommender

def build_userinfo(datalocation, username_th=5, gameid_th=5):
    '''Userinfo dataset is read. Records where no rating is present
    are removed. The username and gameid fields are converted
    to indexes based on username_to_index and gameid_to_index maps.
    The dataset is then filtered for users where users have rated less
    than `username_th` games. It is also filtered for games where a game
    has been rated by less than `gameid_th` users

    Parameters
    ----------
    datalocation: location of the userinfo.csv file 
    username_th: threshold for minimum number of games to be rated by a user
    gameid_th: threshold for minimum number of users to have rated a game

    Returns
    -------
    Filtered dataset for use with creating recommendation model with turicreate

    '''
    print("Loding userinfo dataset...")
    names = [
            "username", "gameid", "userrating", "own", "prevowned", 
            "fortrade", "want", "wanttoplay", "wanttobuy", "wishlist", 
            "wishlistpriority", "preordered", "numplays", "lastmodified"
        ]

    data = pd.read_csv(datalocation, names=names)\
        .filter(["username", "gameid", "userrating"])\
        .query("userrating == userrating")\
        .query("userrating > 0")\
        # .assign(username_index=lambda row: row.username.map(username_to_index))\
        # .assign(gameid_index=lambda row: row.gameid.map(gameid_to_index))\

    filtered_data = data.merge(data\
            .groupby("username", as_index=False)["gameid"]\
            .count()\
            .rename({"gameid": "username_count"}, axis=1)\
            .query("username_count >= @username_th"),
        how="inner",
        on="username")\
        .merge(data\
            .groupby("gameid", as_index=False)["username"]\
            .count()\
            .rename({"username": "gameid_count"}, axis=1)\
            .query("gameid_count >= @gameid_th"),
        how="inner",
        on="gameid")\
        .filter(["username", "gameid", "userrating"])\
        
    for i, df in enumerate((data, filtered_data)):
        if i == 0:
            print("For full dataset----")
        else:
            print("For filtered dataset----")
        
        print(f"Total records = {len(df.index):,.0f}")
        print(f"Unique users = {len(df.username.unique()):,.0f}")
        print(f"Unique games = {len(df.gameid.unique()):,.0f}\n")

    return filtered_data

def recommender_model(model, data):
    """Build a recommender model, and return the model

    Parameters
    ----------
    model: A turicreate recommender model
    data: Dataframe containing the following columns: user_id, item_id, rating

    Returns
    -------
    Trained model
    """
    sf = tc.SFrame(data)
    trained_model = model.create(sf, target="userrating", user_id="username", item_id="gameid")

    return trained_model

if __name__ == "__main__":
    datalocation = "../data/userinfo.csv"
    data = build_userinfo(datalocation)

    print("Building factorization model...")
    model = recommender_model(factorization_recommender, data)
    
    print("Saving factorization model...")
    model.save("../models/factorization_2020-04-11")

    print("Building item-similarity model...")
    model = recommender_model(item_similarity_recommender, data)
    
    print("Saving item-similarity model...")
    model.save("../models/itemsimilarity_2020-03-15")

