from flask import Flask, render_template, redirect, url_for, request

import turicreate as tc
import sys
import datetime

from helper import Database, BGGAPI, RecommendationEngine

item_model = tc.load_model("../models/itemsimilarity_2020-03-15")
factorization_model = tc.load_model("../models/factorization_2020-04-11")

db, dbuser, dbhost = "ashok", "ashok", "localhost"
database = Database(db, dbuser, dbhost)
engine_item = RecommendationEngine(item_model)
engine_factorization = RecommendationEngine(factorization_model)
bggapi = BGGAPI()

app = Flask(__name__)
app.secret_key = 'development key'

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route('/user/<string:username>', methods=["GET"])
def username(username):
    usergames = database.get_usergames(username)
    
    if len(usergames) > 0:
        user_found = True #user found in our internal database
    else:
        user_found = False #user not found in our internal database 
        usergames = api.get_usergames(username) #games for user downloaded from API

    if user_found:
        gameids, ranks = engine_factorization.recommendations(username, 10)
        gameinfo = database.games_info(gameids)

        recos = []
        
        for game in gameinfo:
            game["rank"] = ranks[gameids.index(game["gameid"])]
            recos.append(game)

    print(recos)

    return render_template("username.html", 
            username=username, 
            topgames=usergames,
            recos=recos)

@app.route("/user/<string:username>/recommendations")

@app.route('/boardgame/<int:gameid>', methods=["GET"])
def boardgame(gameid):
    print(gameid)
    return render_template("boardgame.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)