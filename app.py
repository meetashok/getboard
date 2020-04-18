from flask import Flask, render_template, redirect, url_for, request

import turicreate as tc
import sys
import datetime
import ast
from pprint import pprint

from helper import Database, BGGAPI, RecommendationEngine

item_model = tc.load_model("models/itemsimilarity_2020-03-15")
factorization_model = tc.load_model("models/factorization_2020-04-11")

db, dbuser, dbhost = "ashok", "ashok", "localhost"
database = Database(db, dbuser, dbhost)
engine_item = RecommendationEngine(item_model)
engine_factorization = RecommendationEngine(factorization_model)
bggapi = BGGAPI()

app = Flask(__name__)
app.secret_key = 'development key'

@app.route("/", methods=["GET", "POST"])
def index():
    search_game_title_request = ""
    search_game_title_results = []
    populargames = [] 
    user_game_list = []
    recommended_games = [] 
     
    if request.method == "GET":
      print("GET REQUEST!")
      # pull list of popular games
      populargames = database.popular_games(k=12, top=100, percentile=0.90)
      # print("populargames:",populargames)
     
    elif request.method == "POST":
      print("POST REQUEST!")
      request_form = request.form.to_dict()
      # print("request_form", request_form, "\n")
       
      # search game (return fields: gameid,primaryname,yearpublished,gamerank,usersrated,bayesaverage,minplayers,maxplayers,playingtime,minplaytime,maxplaytime,thumbnail)
      if "search_game_title_results" in request_form:
        search_game_title_results = ast.literal_eval(request_form['search_game_title_results'])
      if "search_game_title_request" in request_form:
        search_game_title_request = request_form['search_game_title_request']
        search_game_title_results = database.search_games(search_game_title_request, k=None)
        print("search_game_title_results:",search_game_title_results, "\n")
      if "user_game_list" in request_form:
        user_game_list = ast.literal_eval(request_form['user_game_list'])
       
      # game search inputs 
      game_search_inputs = [ast.literal_eval(val) for key, val in request_form.items() if "game_search_inputs" in key]
      if len(game_search_inputs) > 0:
        print("game_search_inputs:",game_search_inputs,"\n")
        user_game_list = user_game_list + game_search_inputs
       
      # popular games inputs 
      popular_games_inputs = [ast.literal_eval(val) for key, val in request_form.items() if "popular_game_inputs" in key]
      if len(popular_games_inputs) > 0:
        print("popular_games_inputs:",popular_games_inputs,"\n")
        user_game_list = user_game_list + popular_games_inputs
       
      # display previous populargames list
      if "populargames" in request_form:
        populargames = ast.literal_eval(request_form['populargames'])
       
      # provide recommendations given a list of game ids
      recommendation_inputs = [val for key, val in request_form.items() if "recommendation_inputs" in key]
      if len(recommendation_inputs) > 0:
        recommendation_inputs = [int(gameid) for gameid in recommendation_inputs]
        recommended_gameids = engine_item.recommendations_newuser(recommendation_inputs, k=12, filters={})[0]
        recommended_games = database.games_info(recommended_gameids)
        # recommended_games = engine_factorization.recommendations_newuser(recommendation_inputs, k=12, filters={})
        print("recommended_games:",recommended_games,"\n")
       
      # ensure no duplicates in game list
      if len(user_game_list) > 0:
        user_game_list = list({item["gameid"]: item for item in user_game_list}.values())
        print("user_game_list:")
        pprint(user_game_list)
     
    return render_template("index.html",
      populargames=populargames,
      search_game_title_request=search_game_title_request,
      search_game_title_results=search_game_title_results,
      user_game_list=user_game_list,
      recommended_games=recommended_games
    )

@app.route('/user/', methods=["POST"])
def username():
    request_form = request.form.to_dict()
    #if "username" in request_form:
    username = request_form['username']
    usergames = database.get_usergames(username)
    print("usergames", usergames)
    
    if len(usergames) > 0:
        user_found = True #user found in our internal database
    else:
        user_found = False #user not found in our internal database 
        usergames = bggapi.get_usergames(username) #games for user downloaded from API
        if len(usergames) < 1:
            return render_template("user_not_found.html")

    categories = database.get_categories('category', 'popular')
    mechanics = database.get_categories('mechanic', 'popular')


    recos = []
    if user_found:
        gameids, ranks = engine_item.recommendations(username, 10)
        gameinfo = database.games_info(gameids)

        
        for game in gameinfo:
            game["rank"] = ranks[gameids.index(game["gameid"])]
            recos.append(game)
    print("recos:",recos)

    return render_template("username.html", 
            username=username, 
            topgames=usergames,
            recos=recos,
            categories = categories,
            mechanics = mechanics)

@app.route('/filter/<username>', methods=["GET","POST"])
def filter(username):
    usergames = database.get_usergames(username)

    select = ""
    if request.form.get("cat_select") != "0":
        select = request.form.get("cat_select")
    else:
        select = request.form.get("mech_select")

    playtime_max = int(request.form.get("slider_duration"))
    min_players = int(request.form.get("slider_players"))
    if len(usergames) > 0:
        user_found = True  # user found in our internal database
    else:
        user_found = False  # user not found in our internal database
        usergames = bggapi.get_usergames(username)  # games for user downloaded from API

    #print("usergames",usergames)
    usergameids = [sub['gameid'] for sub in usergames]
    print("usergameIDs",usergameids)
    print("select",select)
    usergames = database.get_gamesbyfilter(gameids=usergameids, category=select)
    usergames_storage = usergames
    print(usergames_storage)
    usergames = []
    for game in usergames_storage:
        if(game["playingtime"]<=playtime_max and game["minplayers"] <= min_players):
            usergames.append(game)

    recos = []

    categories = database.get_categories('category', 'popular')
    mechanics = database.get_categories('mechanic', 'popular')
    if user_found:
        gameids, ranks = engine_factorization.recommendations(username, 10)
        gameinfo = database.get_gamesbyfilter(gameids=gameids,category=select)


        for game in gameinfo:
            if(game["playingtime"] <= playtime_max):
                game["rank"] = ranks[gameids.index(game["gameid"])]
                recos.append(game)
    print(request.form.get("cat_select"))

    return render_template("username.html",
            username=username,
            topgames=usergames,
            recos=recos,
            categories = categories,
            mechanics = mechanics,
            cat_select=request.form.get("cat_select"),
            mech_select=request.form.get("mech_select"),
            duration=request.form.get("slider_duration"),
            players=request.form.get("slider_players"))

@app.route("/user/<string:username>/recommendations")

@app.route('/boardgame/<int:gameid>', methods=["GET"])
def boardgame(gameid):
    print(gameid)
    return render_template("boardgame.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
