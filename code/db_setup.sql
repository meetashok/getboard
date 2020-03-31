--create schema getboard;
--
--select * from pg_catalog.pg_tables
--where schemaname = 'getboard';
--
--select * from pg_catalog.pg_table;

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

COPY getboard.userinfo_stg
FROM '/Users/ashok/Documents/MS/10-Data-and-visual-analytics/project/getboard/data/userinfo.csv' WITH (FORMAT csv);


drop table if exists getboard.userinfo;
create table getboard.userinfo as 
(select 
	username,
	gameid,
	max(userrating) as userrating,
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
	username, gameid);

select * from getboard.userinfo;

select count(1) from getboard.userinfo;