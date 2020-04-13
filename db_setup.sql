create schema getboard;

-- Create staging table for userinfo
drop table if exists getboard.userinfo_stg;
create table getboard.userinfo_stg (
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
);

-- Copy data from CSV file to usernameinfo_stg table 
COPY getboard.userinfo_stg
FROM '/Users/ashok/Documents/MS/10-Data-and-visual-analytics/project/data/userinfo.csv' WITH (FORMAT csv);


-- Create permanent table for userinfo
drop table if exists getboard.userinfo;
create table getboard.userinfo (
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
    primary key (username, gameid)
);

-- Insert data into userinfo permanent table 
truncate getboard.userinfo;
insert into getboard.userinfo 
select 
	username,
	gameid,
	max(case when userrating = 'N/A' then null else cast(userrating as float) end) as userrating,
	max(own) as own,
	max(prevowned) as prevowned,
	max(fortrade) as fortrade,
    max(want) as want,
    max(wanttoplay) as wanttoplay,
    max(wanttobuy) as wanttobuy,
	max(wishlist) as wishlist,
    max(wishlistpriority) as wishlistpriority,
    max(preordered) as preordered,
    max(numplays) as numplays,
    max(lastmodified) as lastmodified
from 
	getboard.userinfo_stg
group by
	username, gameid;

-- create index on userinfo_username
drop index if exists getboard.index_userinfo_username;
create index index_userinfo_username on getboard.userinfo (username);

-- create staging table for gamesinfo
drop table if exists getboard.gamesinfo_stg;
create table getboard.gamesinfo_stg (
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

-- create permanent table for gamesinfo 
drop table if exists getboard.gamesinfo;
create table getboard.gamesinfo (
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

-- copy data from CSV to gamesinfo staging table 
COPY getboard.gamesinfo_stg
FROM '/Users/ashok/Documents/MS/10-Data-and-visual-analytics/project/data/gamesinfo.csv' WITH (FORMAT csv);

truncate getboard.gamesinfo;
insert into getboard.gamesinfo 
select 
	gameid,
	substring (primaryname, 2, length(primaryname)-2) as primaryname,
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
from getboard.gamesinfo_stg;	
	
drop index getboard.index_gamesinfo_gameid;
create index index_gamesinfo_gameid on getboard.gamesinfo (gameid);

-- Create staging table for userinfo
drop table if exists getboard.userinfo_stg;
create table getboard.userinfo_stg (
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
);

-- Create permanent table for userinfo
drop table if exists getboard.gamecategories_stg;
create table getboard.gamecategories_stg (
	gameid int not null,
    categorytype varchar(20),
    category varchar(60)
);

drop table if exists getboard.gamecategories;
create table getboard.gamecategories (
	gameid int not null,
    categorytype varchar(20),
    category varchar(60)
);

COPY getboard.gamecategories_stg
FROM '/Users/ashok/Documents/MS/10-Data-and-visual-analytics/project/data/gamescategories.csv' WITH (FORMAT csv);

truncate getboard.gamecategories;
insert into getboard.gamecategories
select 
	gameid,
	categorytype,
	substring (category, 2, length(category)-2) as category
from getboard.gamecategories_stg;