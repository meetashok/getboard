import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

def run_query(conn, query):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)

queries = [
    """drop table if exists userinfo_stg;
    """,
    
    """create table userinfo_stg (
	username varchar(30) not null,
    gameid int not null,
    userrating varchar(20),
    own int,
    prevowned int, 
	fortrade int, 
    want int, 
    wanttoplay int, 
    wanttobuy int, 
	wishlist int, 
    wishlistpriority int, 
    preordered int, 
    numplays int, 
    lastmodified varchar(20)
    );""",

    """drop table if exists userinfo;
    """,

    """create table userinfo (
	username varchar(30) not null,
    gameid int not null,
    userrating float,
    own int,
    prevowned int, 
	fortrade int, 
    want int, 
    wanttoplay int, 
    wanttobuy int, 
	wishlist int, 
    wishlistpriority int, 
    preordered int, 
    numplays int, 
    lastmodified varchar(20),
    primary key (username, gameid));
    """,

    """delete from userinfo;
    """,

    # """insert into userinfo 
    # select 
    #     username,
    #     gameid,
    #     max(case when userrating = 'N/A' then null else cast(userrating as float) end) as userrating,
    #     max(own) as own,
    #     max(prevowned) as prevowned,
    #     max(fortrade) as fortrade,
    #     max(want) as want,
    #     max(wanttoplay) as wanttoplay,
    #     max(wanttobuy) as wanttobuy,
    #     max(wishlist) as wishlist,
    #     max(wishlistpriority) as wishlistpriority,
    #     max(preordered) as preordered,
    #     max(numplays) as numplays,
    #     max(lastmodified) as lastmodified
    # from 
    #     userinfo_stg
    # group by
    #     username, gameid;
    # """,

    """drop table if exists gamesinfo_stg;
    """,

    """create table gamesinfo_stg (
        gameid int,
        primaryname varchar(300),
        yearpublished int,
        gamerank varchar(10),
        usersrated int,
        average float,
        bayesaverage float,
        minplayers int,
        maxplayers int,
        playingtime int,
        minplaytime int,
        maxplaytime int,
        thumbnail varchar(100)	
    );
    """,

    """drop table if exists gamesinfo;
    """,

    """create table gamesinfo (
        gameid int,
        primaryname varchar(300),
        yearpublished int,
        gamerank int,
        usersrated int,
        average float,
        bayesaverage float,
        minplayers int,
        maxplayers int,
        playingtime int,
        minplaytime int,
        maxplaytime int,
        thumbnail varchar(100),
        primary key (gameid)
    );
    """,


    """delete from gamesinfo;
    """,

    """insert into gamesinfo 
    select 
        gameid,
        substr (primaryname, 2, length(primaryname)-2) as primaryname,
        yearpublished,
        (case when gamerank = 'Not Ranked' then null else cast(gamerank as integer) end) as gamerank,
        usersrated,
        average,
        bayesaverage,
        minplayers,
        maxplayers,
        playingtime,
        minplaytime,
        maxplaytime,
        thumbnail
    from gamesinfo_stg;
    """,

    """drop table if exists gamecategories_stg;
    """,

    """create table gamecategories_stg (
        gameid int not null,
        categorytype varchar(20),
        category varchar(60)
    );
    """,
    
    """drop table if exists gamecategories;
    """,

    """create table gamecategories (
        gameid int not null,
        categorytype varchar(20),
        category varchar(60)
    );
    """,

    """delete from gamecategories;
    """,

    """insert into gamecategories
    select 
        gameid,
        categorytype,
        substr (category, 2, length(category)-2) as category
    from gamecategories_stg;
    """
]


def main(dbfile, queries):
    conn = create_connection(dbfile)

    for query in queries:
        run_query(conn, query)
        
if __name__ == "__main__":
    dbfile = "getboard.db"
    main(dbfile, queries)
