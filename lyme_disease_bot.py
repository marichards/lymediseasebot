import tweepy
import re
import requests
import json
import csv
import sqlite3
import os
import smtplib

# Set important parameters
SECRETS_FILE = "secrets.json"

def main():
    # Twitter API Token Import
    with open(SECRETS_FILE) as f:
        secrets = json.load(f)

    # Use the token to setup the Twitter API
    auth = tweepy.OAuthHandler(secrets['consumer_key'], secrets['consumer_secret'])
    auth.set_access_token(secrets['access_token'], secrets['access_secret'])
    api = tweepy.API(auth)

    # Create the MyStreamListener object class
    class MyStreamListener(tweepy.StreamListener):

        def __init__(self, *args, **kwargs):

            # Create an authors list
            self.authors = []

            # Create a sqlite database and connect
            sqlite_file = "lyme_authors_db.sqlite"
            self.conn = sqlite3.connect(sqlite_file)
            self.c = self.conn.cursor()

            # Add tables to the database
            self.c.execute('CREATE TABLE IF NOT EXISTS authors\
            (author text, name text, followers int, friends int, tweets int, lyme_tweets int)')
            self.conn.commit()

            # Add this to the __init__ in the initial StreamListener
            super().__init__(*args, **kwargs)

        # When it connects, print "Connected"
        def on_connect(self):
            print("Connected")

        # This captures the tweet itself and says what to do with it
        # Note: A tweet is a "status" here
        def on_status(self, status):
            # print(status.text.encode("utf8"))
            # print(dir(status))

            # Catch re-tweets
            if not re.search('^RT', status.text):

                # Print out the author's twitter handle
                # print(status.author.screen_name)

                # Create an author list from the existing database
                self.c.execute("select distinct(author) from authors;")
                tuple_list = self.c.fetchall()
                author_list = []
                for item in tuple_list:
                    author_list.append(item[0])

                # If it's not in the list, add it and print the list
                if status.author.screen_name not in author_list:
                    self.authors.append(status.author.screen_name)
                    # print(self.authors)

                    # Add the author's information to the sqlite database
                    try:
                        self.c.execute("INSERT INTO authors ('author','name','followers','friends','tweets','lyme_tweets')\
                        VALUES ('{v0}', '{v1}', {v2}, {v3}, {v4}, 1)" \
                                       .format(v0=status.author.screen_name, v2=status.author.followers_count,
                                               v1=status.author.name.replace("'", " "), v3=status.author.friends_count,
                                               v4=status.author.statuses_count))
                        self.conn.commit()
                    except:
                        print("Error: {} and {}" \
                              .format(status.author.screen_name.encode("utf8"), status.author.name.encode("utf8")))

                else:
                    # Print the author's name if it's not new
                    print(status.author.screen_name)

                    # Update the number of lyme tweets by adding 1
                    # Update the followers, friends, and tweets too
                    self.c.execute("UPDATE authors set lyme_tweets = lyme_tweets + 1,\
                    followers = {v2},\
                    friends = {v3},\
                    tweets = {v4}\
                    where author = '{v0}'" \
                                   .format(v0=status.author.screen_name, v2=status.author.followers_count,
                                           v3=status.author.friends_count, v4=status.author.statuses_count))

                    self.conn.commit()

    # Create a MyStreamListener Object and filter for #LymeDisease and #Lyme
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
    myStream.filter(track=['#LymeDisease', '#Lyme'])


# If running script by itself, call the main function
if __name__ == '__main__':
    main()
