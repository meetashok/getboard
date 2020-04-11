import psycopg2
import requests
import xml.etree.ElementTree as ET

def makedict(rows, names):
    return [dict(zip(names, row)) for row in rows]

class RecommendationEngine(object):
    def __init__(self, model):
        self.model = model
    
    def recommendations(self, username, k):
        games = self.model.recommend(users=[username], k=k)
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
        
        s = sorted(userinfo, key=lambda x: x[1])[::-1]

        names = ["gameid", "userrating", "primaryname", "yearpublished", "thumbnail"]
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
            primaryname, yearpublished, thumbnail
            from getboard.userinfo
            join getboard.gamesinfo
            on getboard.userinfo.gameid = getboard.gamesinfo.gameid
            where username = '{username}'
            order by userrating desc;
        """
        self.conn.execute(query)
        rows = self.conn.fetchall()

        names = ["gameid", "userrating", "primaryname", "yearpublished", "thumbnail"]
        return makedict(rows, names)

if __name__ == "__main__":
    db = Database("ashok", "ashok", "localhost")

    # print(db.get_userinfo("$teve"))

    api = BGGAPP()
    print(api.get_userinfo("$teve"))