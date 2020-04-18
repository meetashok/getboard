# getboard
Get Board: Table-top boardgames recommendation engine 

Link to the boardgamegeek API page 
https://boardgamegeek.com/wiki/page/BGG_XML_API2

## Data
For extracting data from boardgamegeek website, we used web-scrapping as well as their API. 

The first step was to build a list of users. The website allows public users to search for users based on zipcode. Only those users shows up in the list who have opted-in to be searched. There are more than 33k zipcodes in the US. We picked the top 10k based on population and then scrapped all users within 25 miles of each zipcode. This yielded us about 36k users. 

The API allows querying different types of data associated with each users. It includes their board-games collection, game-play information, ratings and comments for board-games. Extracting this data took about 4 days as we limited ourselves to about 1 call per 2 seconds.  

The datasets are located on Google Drive at https://drive.google.com/drive/folders/13yZQzZsj2ad2QZEvdno1Ivj3cXESJIJ9

- **userinfo.zip**
  - Comma separated file containing user level data
  - Zipped size = 75 MB, Unzipped = 449 MB
  - Number of records: 7,713,598
  - Number of records with ratings: 4,745,923
  - Number of users: 31,541
  - On average, each user has rated ~150 board-games
  - Fields: username, gameid, userrating, own, prevowned, fortrade, want, wanttoplay, wanttobuy, wishlist, wishlistpriority, preordered, numplays, lastmodified
- **usercomments.zip**
  - File containing user comments
  - Zipped size = 83 MB, Unzipped = 246 MB
  - Number of records: 1,153,529 
  - Fields: username, gameid, userrating, comment


Other files aren't likely to be useful for further processing

<hr>

## Set-up process

1. Clone the repository (https://github.gatech.edu/akumar627/getboard.git)
2. Download data from [Google Drive](https://drive.google.com/drive/folders/13yZQzZsj2ad2QZEvdno1Ivj3cXESJIJ9) and put it in the data folder
3. Install Postgres.app from [https://postgresapp.com/](https://postgresapp.com/)
4. Open Postgres.app and start Postgres server
5. Change directory to getboard directory and run the following command to set up the database: `psql -f postgres_setup.sql`
6. Create a new conda environment with `conda create -n getboard python=3.7`
7. Run `conda activate getboard`
8. Install requirments using `pip install -r requirements.txt`
9. Edit `app.py` on line 14 by replacing the quoted `"db"` and `"dbuser"` in `db, dbuser, dbhost = "db", "dbuser", "localhost"` to correspond to your db and dbuser.
10. Run the app using `python app.py`.
11. Open your web browser and navigate to the listed url. (eg. http://127.0.0.1:5001/)

*incase port 5001 is already assigned you can change the last line in `app.py` to another port. 