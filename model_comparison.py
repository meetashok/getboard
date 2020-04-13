import pandas as pd
import numpy as np
import turicreate as tc
import psycopg2
from sqlalchemy import create_engine

random_seed = 1337

engine = create_engine('postgresql://ashok@localhost:5432/ashok')
gamesinfo = pd.read_sql_query("select * from getboard.gamesinfo;", engine) 
userinfo = pd.read_sql_query("select * from getboard.userinfo;", engine) 
gamecategories = pd.read_sql_query("select * from getboard.gamecategories;", engine) 

data = userinfo\
    .filter(["username", "gameid", "userrating"])\
    .query("userrating == userrating")

sf = tc.SFrame(data)

train, test = tc.recommender.util.random_split_by_user(sf, 
                    user_id="username",
                    item_id="gameid",
                    random_seed=random_seed,
                    item_test_proportion=0.3)

m1 = tc.item_similarity_recommender.create(train, 
                    user_id="username",
                    item_id="gameid")

m2 = tc.item_similarity_recommender.create(train, 
                    user_id="username",
                    item_id="gameid",
                    target="userrating")

m3 = tc.ranking_factorization_recommender.create(train, 
                    user_id="username",
                    item_id="gameid",
                    target="userrating")

m4 = tc.factorization_recommender.create(train, 
                    user_id="username",
                    item_id="gameid",
                    target="userrating")

comparison = tc.recommender.util.compare_models(test, 
            [m1, m2, m3, m4], 
            model_names=["m1", "m2", "m3", "m4"])

for i, model in enumerate((m1, m2, m3, m4)):
    for df in (train, test):
        result = model.evaluate_rmse(df, target="userrating")
        print(f"Model = {i+1}: {result.get('rmse_overall'):0.2f}")
        

m2.evaluate_rmse(train, target="userrating")

m3.evaluate_rmse(train, target="userrating")
m4.evaluate_rmse(train, target="userrating")

m4.recommend(["NewUser2121"], k=5)
m4.recommend(["NewUser2122"], k=8)

m4.recommend_from_interactions(tc.SFrame({
    "username": ["newuser", "newuser", "newuser"],
    "gameid": [13, 246900, 291951],
    "userrating": [10, 3, 1] 
}), k=5)

user1 = tc.SFrame({
    "username": ["user1", "user1", "user1", "user1", "user1", "user1"],
    "gameid": [13, 12, 11, 5, 289843, 196045],
    "userrating": [10, 10, 10, 10, 1, 1]
})

m4.recommend(["user1"], new_observation_data=user1, diversity=1.5)
m4.recommend(["user1"])

import turicreate
train_data = turicreate.SFrame({'user_id': ["0", "0", "0", "1", "1", "2", "2", "2"],
    'item_id': ["a", "c", "e", "b", "f", "b", "c", "d"]})
test_data = turicreate.SFrame({'user_id': ["0", "0", "1", "1", "1", "2", "2"],
    'item_id': ["b", "d", "a", "c", "e", "a", "e"]})
m1 = turicreate.item_similarity_recommender.create(train_data)
m2 = turicreate.item_similarity_recommender.create(train_data, only_top_k=1)
turicreate.recommender.util.compare_models(test_data, [m1, m2], model_names=["m1", "m2"])