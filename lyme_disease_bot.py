import tweepy
import re
import requests
import json

# Set important parameters
SECRETS_FILE = "secrets.json"

def main(): 
    # Twitter API Token Import
    with open(SECRETS_FILE) as f:
        secrets = json.load(f)
    
    # Use the token to setup the Twitter API
    auth = tweepy.OAuthHandler(secrets['consumer_key'],secrets['consumer_secret'])
    auth.set_access_token(secrets['access_token'],secrets['access_secret'])
    api = tweepy.API(auth)

    # Create the MyStreamListener object class
    class MyStreamListener(tweepy.StreamListener):    
        # Define a method "on_status" that prints the status text
        def on_connect(self):
            print("Connected")
        
		# This captures the tweet itself
        def on_status(self,status):
            print(status.text.encode("utf8"))
            #print(dir(status))

    # Create a MyStreamListener Object and filter for #LymeDisease
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
    myStream.filter(track=['#LymeDisease','#Lyme','Lyme'])
    
	# Grab the infos!
	
## If running script by itself, call the main function	
if __name__ == '__main__':
    main()