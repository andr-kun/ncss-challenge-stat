import urllib
import json
import sqlite3
import time
import random
import copy

include_user_stat = False
json_url = 'http://andr-kun.github.io/ncss-challenge-stat/challenge-message-stats-2014.json'

try:
    data = json.load(urllib.urlopen(json_url))
except:
    print("Unable to contact server for json update")
    exit()

user_posts = data["by_nick"]

cur_time = time.time()

# Connect to db
conn = sqlite3.connect('ncss-message-stats.db')
c = conn.cursor()

# Create tables and index if they do not exist
c.execute("CREATE TABLE IF NOT EXISTS user_post_over_time (date_time integer, user varchar(30), post integer);")
c.execute("CREATE INDEX IF NOT EXISTS user_post_over_time_index ON user_post_over_time(date_time)")
c.execute("CREATE INDEX IF NOT EXISTS user_post_over_time_user_index ON user_post_over_time(user)")

conn.commit()

# Update post by user entry (store the difference between user current post and user previous post)
for user,post in user_posts.items():
    c.execute("SELECT sum(post) FROM user_post_over_time WHERE user = ? GROUP BY user", (user,))
    result = c.fetchone()
    if result:
        prev_post = result[0]
        #new_post = post-prev_post
        new_post = random.randint(1,20)
    else:
        #new_post = post
        new_post = random.randint(1,20)
    c.execute("INSERT INTO user_post_over_time VALUES (?,?,?)", (cur_time,user,new_post,))

conn.commit()

# Produce timeline dictionary
combined_time_series = []
for row in c.execute("SELECT date_time, sum(post) FROM user_post_over_time GROUP BY date_time"):
    time_count = {"x": row[0], "y": row[1]}
    combined_time_series.append(time_count)

all_time_series = []
if include_user_stat:
    current_user = ""
    current_user_series = []
    for row in c.execute("SELECT date_time, user, post FROM user_post_over_time ORDER BY user ASC, date_time ASC"):
        user = row[1]
        if current_user != user:
            if current_user != "":
                all_time_series.append({"name": row[1], "data":current_user_series})

            current_user = user
            current_user_series = []

        user_time_count = {"x": row[0], "y": row[2]}
        current_user_series.append(user_time_count)

all_time_series.append({"name": "overall", "data": combined_time_series})
json.dump(all_time_series, open("time-series-stats.json","w"))
json.dump(data, open("challenge-message-stats.json","w"))
