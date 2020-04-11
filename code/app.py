from flask import Flask, render_template, redirect, url_for, request

import sys
import datetime

from helper import Database, BGGAPI

db, dbuser, dbhost = "ashok", "ashok", "localhost"
database = Database(db, dbuser, dbhost)

api = BGGAPI()

app = Flask(__name__)
app.secret_key = 'development key'

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route('/user/<string:username>', methods=["GET"])
def username(username):
    topgames = database.get_topgames(username)
    print(topgames)
    if len(topgames) == 0:
        topgames = api.get_userinfo(username)

    print(topgames)
    return render_template("username.html", username=username, topgames=topgames)


if __name__ == "__main__":
    app.run(debug=True)