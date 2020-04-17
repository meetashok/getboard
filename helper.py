import psycopg2
import requests
import xml.etree.ElementTree as ET
import turicreate as tc
import numpy as np

def makedict(rows, names):
    return [dict(zip(names, row)) for row in rows]

class RecommendationEngine(object):
    def __init__(self, model):
        self.model = model
    
    def recommendations(self, username, k=12, filters={}):
        games = self.model.recommend(users=[username], k=k)
        return list(games["gameid"]), list(games["rank"])

    def recommendations_newuser(self, gameids, k=12, filters={}):
        """Method to generating recommendations for new users based on a list of input games

        Parameters:
        -----------
        gameids: List of ints
            Each integer in the list is a gameid that a new user has selected on the user interface 
        
        k: Int, Optinal 
            Number of recommendations to be returns 

        filters: Dict, Optional
            This will be a dictionary of filter keys and value for filtering games. Not currently 
            operational 

        Returns:
        --------
        List of gameids 
        Rank of gameids sorted by most recommended to least recommended 
        """
        games = self.model.recommend_from_interactions(observed_items=gameids, k=k)
        return list(games["gameid"]), list(games["rank"])

class BGGAPI(object):
    base_url = "https://www.boardgamegeek.com"
    collections_url = "/xmlapi2/collection?username="

    def __init__(self):
        pass

    def _item_info(self, item):
        gameid = item.get("objectid")
        userrating = item.find("stats").find("rating").get("value")
        userrating = 0.0 if userrating == "N/A" else float(userrating)
        primaryname = item.find("name").text
        yearpublished = item.find("yearpublished").text
        thumbnail = item.find("thumbnail").text
        return (gameid, userrating, primaryname, yearpublished, thumbnail)

    def _parse_userdata(self, data):
        userinfo = []
        if data.get("totalitems") == "0":
            return None #No data found
        else:
            items = data.findall("item")
            for item in items:
                userinfo.append(self._item_info(item))
        
        s = sorted(userinfo, key=lambda x: -x[1])

        names = ["gameid", "userrating", "primaryname", "yearpublished", "gamerank", 
            "usersrated", "bayesaverage", "minplayers", "maxplayers", "playingtime",
            "minplaytime", "maxplaytime", "thumbnail"]
        return makedict(s, names)

    def get_usergames(self, username):
        url = f"{self.base_url}{self.collections_url}{username}"
        url += "&excludesubtype=boardgameexpansion&stats=1"
        response = requests.get(url)

        while not response.status_code == 200:
            response = requests.get(url)
        
        data = ET.fromstring(response.text)

        if data is None: #No data is returned if the user does not exist
            return []
        else:
            return self._parse_userdata(data)

class Database(object):
    def __init__(self, dbname, user, host):
        self.dbname = dbname
        self.user = user
        self.host = host
        self.conn = self.create_conn()

    def create_conn(self):
        connect_string = f"dbname='{self.dbname}' user='{self.user}' host='{self.host}'"
        return psycopg2.connect(connect_string).cursor()

    def get_userinfo(self, username):
        query = f"SELECT * FROM GETBOARD.USERINFO WHERE USERNAME = '{username}';"
        self.conn.execute(query)
        rows = self.conn.fetchall()
        return rows

    def get_gameinfo(self, gameid):
        query = f"SELECT * FROM GETBOARD.GAMESINFO WHERE GAMEID = '{gameid}';"
        self.conn.execute(query)
        rows = self.conn.fetchone()
        return rows

    def get_gamecategories(self, gameid):
        query = f"SELECT * FROM GETBOARD.GAMECATEGORIES WHERE GAMEID = '{gameid}';"
        self.conn.execute(query)
        rows = self.conn.fetchall()
        return rows

    def games_info(self, gameids):
        gameids_string = ",".join([str(gameid) for gameid in gameids])
        query = f"""select 
                gameid, primaryname, yearpublished, gamerank,
                usersrated, bayesaverage, minplayers, maxplayers,
                playingtime, minplaytime, maxplaytime, thumbnail
                from getboard.gamesinfo
                where gameid in ({gameids_string});"""

        self.conn.execute(query)
        rows = self.conn.fetchall()

        names = [
            "gameid", "primaryname", "yearpublished", 
            "gamerank", "usersrated", "bayesaverage",
            "minplayers", "maxplayers", "playingtime",
            "minplaytime", "maxplaytime", "thumbnail"]

        return makedict(rows, names)

    def get_usergames(self, username):
        query = f"""select getboard.userinfo.gameid, 
            case when userrating is null then 0 else userrating end as userrating, 
            primaryname, yearpublished, gamerank, usersrated,
            bayesaverage, minplayers, maxplayers, playingtime,
            minplaytime, maxplaytime, thumbnail
            from getboard.userinfo
            join getboard.gamesinfo
            on getboard.userinfo.gameid = getboard.gamesinfo.gameid
            where username = '{username}'
            order by userrating desc;
        """
        self.conn.execute(query)
        rows = self.conn.fetchall()

        names = ["gameid", "userrating", "primaryname", "yearpublished", "gamerank", 
            "usersrated", "bayesaverage", "minplayers", "maxplayers", "playingtime",
            "minplaytime", "maxplaytime", "thumbnail"]
        return makedict(rows, names)

    def get_categories(self, category, sorting):
        if sorting == "popular":
            orderby = "count(1) desc"
        if sorting == "alphabetical":
            orderby = "category" 

        query = f"""select category as frequency
        from getboard.gamecategories
        where categorytype = '{category}'
        group by category
        order by {orderby};
        """
        self.conn.execute(query)
        rows = self.conn.fetchall()

        return [row[0] for row in rows]

    def popular_games(self, k=12, top=100, percentile=0.90):
        """Method returns popular games based on bayesaverage rating 

        Parameters:
        -----------
        k: Int
            Number of games to be returned 

        top: Int; percentile: Float
            percentile of games to be limited to top games. For example, if 
            top = 100 and percentile = 0.90, then 90% of the games be will returned
            from top 100 games and rest 10% will be from ranks > 100. These 
            parameters are included to introduce some randomness. If randomness is not 
            preferred, use top = k and percentile = 1.0

        Returns:
        --------
        A list of dictionaries. Each dictionary has information about games like 
        gameid, primaryname, yearpublished etc. Returned games are randomly sorted

        """
        topx = int(np.ceil(percentile * k))
        bottomx = max(k - topx, 0)

        query = f"""
            select gameid, primaryname, yearpublished, gamerank,
            usersrated, bayesaverage, minplayers, maxplayers,
            playingtime, minplaytime, maxplaytime, thumbnail

            from (
                (select *, random() as random from getboard.gamesinfo
                where gamerank <= {top}
                order by random
                limit {topx})

                union all

                (select *, random() as random from getboard.gamesinfo
                where gamerank > {top}
                order by random
                limit {bottomx})
            ) a;
        """

        self.conn.execute(query)
        rows = self.conn.fetchall()

        names = [
            "gameid", "primaryname", "yearpublished", 
            "gamerank", "usersrated", "bayesaverage",
            "minplayers", "maxplayers", "playingtime",
            "minplaytime", "maxplaytime", "thumbnail"]

        return makedict(rows, names)


    def search_games(self, searchstring, k=None):
        """Method for searching games by a provided searchstring. The method is 
        case-insensitive. It also takes an optional parameter k that limits the number 
        of search results. The results are sorted in descending order of usersrated column
        
        Parameters:
        ----------
        searchstring: String for machine the name of a game (primaryname)
        k: Number of results to be returns

        Return:
        -------
        A list of dictionaries. Each dictionary has information about games like 
        gameid, primaryname, yearpublished etc. 
        """
        if k:
            limitby = f"limit {k}"
        else:
            limitby = ""

        query = f"""select
        gameid, primaryname, yearpublished, gamerank,
        usersrated, bayesaverage, minplayers, maxplayers,
        playingtime, minplaytime, maxplaytime, thumbnail
        from getboard.gamesinfo
        where lower(primaryname) like '%{searchstring.lower()}%'
        order by usersrated desc
        {limitby};
        """

        self.conn.execute(query)
        rows = self.conn.fetchall()

        names = [
            "gameid", "primaryname", "yearpublished", 
            "gamerank", "usersrated", "bayesaverage",
            "minplayers", "maxplayers", "playingtime",
            "minplaytime", "maxplaytime", "thumbnail"]

        return makedict(rows, names)


if __name__ == "__main__":
    db = Database("ashok", "ashok", "localhost")
    api = BGGAPI()

    item_model = tc.load_model("models/itemsimilarity_2020-03-15")
    factorization_model = tc.load_model("models/factorization_2020-04-11")

    model = RecommendationEngine(item_model)

    
    # games = db.search_games("Catan")
    # for game in games:
    #     print(game["primaryname"])

    # recos = model.recommendations_newuser([29, 30549])
    # print(recos[0])

    # games = db.popular_games(k=12, top=50, percentile=0.5)
    # for game in games:
    #     print(game["gamerank"], game["primaryname"])


# filters = {
#     "gamerank": a, # will return games with rank higher than a
#     "usersrated": b, # will return games with userrated > b
#     "yearpublished": (c, d), # will return games released between years a and b
#     "playingtime": (e, f), # will return games with playing time between e ad f
#     "minplayers": (g, h), # will return games with minplayers between g and h
#     "maxplayers": (j, k), # will return games with maxplayers between j and k
#     "category": [x, y, z], # will return games in selected categories
#     "mechanic": [u, v, w], # will return games in selected mechanics
# }