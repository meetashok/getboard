import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

def displayuserstats(data, type="overall"):
    if type == "rated":
        df = data.query("userrating != userrating")
    else:
        df = data.copy()

    print(f"Number of records:      {len(df.index):,.0f}")
    print(f"Number of unique users: {len(df.username.unique()):,.0f}")
    print(f"Number of unique games: {len(df.gameid.unique()):,.0f}")

    games = df\
        .groupby("username", as_index=False)["gameid"]\
        .count()\
        .gameid.values

    print(f"Average games per user = {np.mean(games):,.0f}")
    print(f"Median games per user  = {np.median(games):,.0f}")

    print(f"Users with 1 game      = {np.sum(games == 1):7,.0f} \
        ({np.mean(games == 1)*100:5.2f}%)")
    print(f"Users with 2 games     = {np.sum(games == 2):7,.0f} \
        ({np.mean(games == 2)*100:5.2f}%)")
    print(f"Users with <5 games    = {np.sum(games <5):7,.0f} \
        ({np.mean(games <5)*100:5.2f}%)")
    print(f"Users with >10 games   = {np.sum(games >10):7,.0f} \
        ({np.mean(games >10)*100:5.2f}%)")
    print(f"Users with >100 games  = {np.sum(games >100):7,.0f} \
        ({np.mean(games >100)*100:5.2f}%)")
    print(f"Users with >1000 games = {np.sum(games >1000):7,.0f} \
        ({np.mean(games >1000)*100:5.2f}%)")

    f, ax = plt.subplots(1, 1)
    ax.plot(np.cumsum(np.bincount(games))/ len(games))
    ax.set_xlim(0,1000)
    ax.set_xlabel("Number of games")
    ax.set_ylabel("Cumulative proportion of users")
    formatter = mpl.ticker.FuncFormatter(lambda y, _: '{:.0%}'.format(y))
    ax.yaxis.set_major_formatter(formatter)
    ax.set_title(f"For {typeof} games")

    plt.show()

def displaygamestats(data, typeof="overall"):
    if typeof == "rated":
        df = data.query("userrating == userrating")
    else:
        df = data.copy()

    print(f"Number of records:      {len(df.index):,.0f}")
    print(f"Number of unique users: {len(df.username.unique()):,.0f}")
    print(f"Number of unique games: {len(df.gameid.unique()):,.0f}")

    users = df\
        .groupby("gameid", as_index=False)["username"]\
        .count()\
        .username.values

    print(f"Average users per game = {np.mean(users):,.0f}")
    print(f"Median users per game  = {np.median(users):,.0f}")

    print(f"Games with 1 user      = {np.sum(users == 1):7,.0f} \
        ({np.mean(users == 1)*100:5.2f}%)")
    print(f"Games with 2 users     = {np.sum(users == 2):7,.0f} \
        ({np.mean(users == 2)*100:5.2f}%)")
    print(f"Games with <5 users    = {np.sum(users <5):7,.0f} \
        ({np.mean(users <5)*100:5.2f}%)")
    print(f"Games with >10 users   = {np.sum(users >10):7,.0f} \
        ({np.mean(users >10)*100:5.2f}%)")
    print(f"Games with >100 users  = {np.sum(users >100):7,.0f} \
        ({np.mean(users >100)*100:5.2f}%)")
    print(f"Games with >1000 users = {np.sum(users >1000):7,.0f} \
        ({np.mean(users >1000)*100:5.2f}%)")

    f, ax = plt.subplots(1, 1)
    ax.plot(np.cumsum(np.bincount(users))/ len(users))
    ax.set_xlim(0,1000)
    ax.set_xlabel("Number of users")
    ax.set_ylabel("Cumulative proportion of games")
    formatter = mpl.ticker.FuncFormatter(lambda y, _: '{:.0%}'.format(y))
    ax.yaxis.set_major_formatter(formatter)
    ax.set_title(f"For {typeof} games")

    plt.show()

def ratingDistribution(data):
    f, ax = plt.subplots(1, 1)
    data\
        .query("userrating == userrating")\
        .assign(ratingRounded=lambda row: row["userrating"].round())\
        .groupby("ratingRounded")["gameid"]\
        .count()\
        .plot.bar(ax=ax)

    def yFormatting(value):
        if value == 0:
            return f"0"
        else:
            return "{0:.0f}k".format(np.round(value/1000))

    yformatter = mpl.ticker.FuncFormatter(lambda y, _: yFormatting(y))
    ax.yaxis.set_major_formatter(yformatter)

    xformatter = mpl.ticker.FuncFormatter(lambda x, _: f"{x:.0f}")
    ax.xaxis.set_major_formatter(xformatter)

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    ax.set_title("Distribution of user ratings")
    ax.set_xlabel("User rating")
    ax.set_ylabel("Number of users")

    for tick in ax.get_xticklabels():
        tick.set_rotation(0)

    plt.show()

if __name__ == "__main__":
    datalocation = "../../data/userinfo.csv"

    names = [
        "username", "gameid", "userrating", "own", "prevowned", 
        "fortrade", "want", "wanttoplay", "wanttobuy", "wishlist", 
        "wishlistpriority", "preordered", "numplays", "lastmodified"
    ]

    userinfo = pd.read_csv(datalocation, names=names)

    print("-----Printing users status-----")
    displayuserstats(userinfo, type="overall")

    print("-----Printing user stats for rated games-----")
    displayuserstats(userinfo, type="rated")

    print("-----Printing games status-----")
    displaygamestats(userinfo, type="overall")

    print("-----Printing games stats for rated games-----")
    displaygamestats(userinfo, type="rated")

    print("-----Distribution of ratings-----")
    ratingDistribution(userinfo)
