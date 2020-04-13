import turicreate as tc
import time

sf1 = tc.SFrame({
    'user_id': ["0", "0", "2", "2", "2", "1", "1", "1", "3", "3", "3"],
    'item_id': ["b", "c", "a", "b", "d", "a", "b", "c", "a", "b", "d"],
    'rating':  [5,   5,   5,   1,   5,   1,   5,   5,   5,   1,   5]
    })

sf2 = tc.SFrame({
    'user_id': ["0", "0", "0", "1", "1", "2", "2", "2"],
    'item_id': ["a", "b", "c", "a", "b", "b", "c", "d"],
    'rating': [  1,   3,   2,   5,   4,   1,   4,   3]
    })

# Creating the default model with sf1
for i, sf in enumerate((sf1, sf2)):
    for modeltype in (tc.recommender, tc.item_similarity_recommender):
        print("-"*40)
        print(f"Model = {modeltype.__name__}")
        print(f"Data = sf{i+1}")
        print("-"*40)
        
        model = modeltype.create(sf, 
            target="rating", 
            verbose=False)
        time.sleep(10)

        print("Recommendations for a new user without any observation")
        time.sleep(2)
        print(model.recommend(users=["Charlie"], 
            verbose=False))

        print("Recommendations for a new user who has 'a=1' and 'c=5' in their observations")
        time.sleep(2)
        likes = tc.SFrame({
            "user_id": ["Charlie", "Charlie"],
            "item_id": ["a", "c"],
            "rating": [1, 5]
        })
        
        print(model.recommend(users=["Charlie"], 
            new_observation_data=likes,
            verbose=False))

        print("Recommendations for a new user who has 'a=5' and 'c=1' in their observations")
        time.sleep(2)
        likes = tc.SFrame({
            "user_id": ["Charlie", "Charlie"],
            "item_id": ["a", "c"],
            "rating": [5, 1]
        })

        print(model.recommend(users=["Charlie"], 
            new_observation_data=likes,
            verbose=False))

        print("-"*40)

## Item similarity model 
item_sim_model = tc.item_similarity_recommender.create(sf, target="rating")

print("Recommendations for a new user without any observation")
item_sim_model.recommend(users=["Charlie"])

print("Recommendations for a new user who has 'a' and 'c' in their observations")
likes = tc.SFrame({
    "user_id": ["Charlie", "Charlie"],
    "item_id": ["a", "c"],
})

item_sim_model.recommend(users=["Charlie"], new_observation_data=likes)

print("Recommendations for a new user who has 'a' and 'd' in their observations")
likes = tc.SFrame({
    "user_id": ["Charlie", "Charlie"],
    "item_id": ["a", "d"],
})
item_sim_model.recommend(users=["Charlie"], new_observation_data=likes)

print("Recommendations for a new user who has 'a' and 'c' in their observations")
likes = tc.SFrame({
    "user_id": ["Charlie", "Charlie"],
    "item_id": ["a", "c"],
})
item_sim_model.recommend(users=["Charlie"], new_observation_data=likes)


recs = model.recommend()

model.recommend(users=["3"])

model.recommend(users=["4"])

likes_b = turicreate.SFrame({
    "user_id": ["5", "5"],
    "item_id": ["a", "b"],
    "rating": [1, 5]
})



model.recommend_from_interactions(likes)
model.recommend(users=["Charlie"])

model.recommend_from_interactions(["a", "c"])

