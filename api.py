from flask import Flask
from flask_restful import Resource, Api
from flask_restful_swagger import swagger
from helper import Database, BGGAPI, RecommendationEngine
import turicreate as tc




app = Flask(__name__)
api = Api(app)

item_model = tc.load_model("models/itemsimilarity_2020-03-15")
factorization_model = tc.load_model("models/factorization_2020-04-11")

db, dbuser, dbhost = "ashok", "ashok", "localhost"
database = Database(db, dbuser, dbhost)
engine_item = RecommendationEngine(item_model)
engine_factorization = RecommendationEngine(factorization_model)

bggapi = BGGAPI()

class HelloWorld(Resource):
    def get(self):
        return {"hello": "world"}

class UserGames(Resource):
    def get(self, username):
        usergames = database.get_usergames(username)
        
        if len(usergames) > 0:
            user_found = True #user found in our internal database
        else:
            usergames = bggapi.get_usergames(username) #games for user downloaded from API

        return {
            "totalgames": len(usergames),
            "data": usergames,
        }

class GameInfo(Resource):
    def get(self, gameid):
        return 

class UserRecommendations(Resource):
    def get(self, username):
        gameids, ranks = engine_factorization.recommendations(username, 10)
        gameinfo = database.games_info(gameids)

        recos = []
        
        for game in gameinfo:
            game["rank"] = ranks[gameids.index(game["gameid"])]
            recos.append(game)

        return {
            "data": recos
        }

class SimilarGames(Resource):
    def get(self, gameid):
        return 

class SearchGame(Resource):
    def get(self, search):
        return

class PopularGames(Resource):
    def get(self):
        return

class GameCategories(Resource):
    def get(self, category, sorting):
        if category not in ("mechanic", "category"):
            return {
                "error": "type must be in [mechanic, category]"
            }
        
        if sorting not in ("alphabetical", "popular"):
            return {
                "error": "sorting should be in [alphabetical, popular]"
            }

        categories = database.get_categories(category, sorting)
        
        return {
            "totalmechanics": len(categories),
            "data": categories
            }
        
api.add_resource(HelloWorld, "/")
api.add_resource(GameCategories, "/api/categories/type=<string:category>&sort=<string:sorting>")
api.add_resource(UserGames, "/api/user/<string:username>")
api.add_resource(GameInfo, "/api/game/<string:gameid>")
api.add_resource(SimilarGames, "/api/game/similar/<string:gameid>")
api.add_resource(UserRecommendations, "/api/user/<string:username>/recos")

if __name__ == "__main__":
    app.run(debug=True, port=5004)