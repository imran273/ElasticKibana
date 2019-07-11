#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import tweepy           # To consume Twitter's API
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob #predict the sentiment of Tweet, see 'https://textblob.readthedocs.io/en/dev/'
from elasticsearch import Elasticsearch #pip install Elasticsearch if not intalled yet
from datetime import datetime
import calendar
import numpy as np
from Tkinter import *
import webbrowser
#from django.utils.dateparse import parse_datetime
#from http.client import IncompleteRead

#log in to your Twitter Application Management to create an App, url: 'https://apps.twitter.com'

CONSUMER_KEY="*****************"  
CONSUMER_SECRET="*****************"
ACCESS_TOKEN="*****************-*****************"  
ACCESS_SECRET="*****************"
# create instance of elasticsearch
es = Elasticsearch()


class TweetStreamListener(StreamListener):
    
    # re-write the on_data function in the TweetStreamListener
    # This function enables more functions than 'on_status', see 'https://stackoverflow.com/questions/31054656/what-is-the-difference-between-on-data-and-on-status-in-the-tweepy-library'        
    def on_data(self, data):
        # To understand the key-values pulled from Twitter, see 'https://dev.twitter.com/overview/api/tweets'
        dict_data = json.loads(data)
        # pass Tweet into TextBlob to predict the sentiment
        tweet = TextBlob(dict_data["text"]) if "text" in dict_data.keys() else None
        
        # if the object contains Tweet
        if tweet:
            # determine if sentiment is positive, negative, or neutral
            if tweet.sentiment.polarity < 0:
                sentiment = "negative"
            elif tweet.sentiment.polarity == 0:
                sentiment = "neutral"
            else:
                sentiment = "positive"
            
            # print the predicted sentiment with the Tweets
            print(sentiment, tweet.sentiment.polarity, dict_data["text"])
            
    
            # extract the first hashtag from the object
            # transform the Hashtags into proper case
            if len(dict_data["entities"]["hashtags"])>0:
                hashtags=dict_data["entities"]["hashtags"][0]["text"].title()
            else:
                #Elasticeach does not take None object
                hashtags="None"
                      
            # add text and sentiment info to elasticsearch
            #tzinfo=+0100
            es.index(index="logstash-a",
                     # create/inject data into the cluster with index as 'logstash-a'
                     # create the naming pattern in Management/Kinaba later in order to push the data to a dashboard
                     doc_type="test-type",
                     body={"author": dict_data["user"]["screen_name"],
                           "followers":dict_data["user"]["followers_count"],
                           #parse the milliscond since epoch to elasticsearch and reformat into datatime stamp in Kibana later
                           "date": datetime.strptime(dict_data["created_at"], '%a %b %d %H:%M:%S +0000 %Y'),
                           "message": dict_data["text"]  if "text" in dict_data.keys() else " ",
                           "hashtags":hashtags,
                           "polarity": tweet.sentiment.polarity,
                           "subjectivity": tweet.sentiment.subjectivity,
                           "sentiment": sentiment})
        return True
        
    # on failure, print the error code and do not disconnect
    def on_error(self, status):
        printstat='this is ur status failed'
        print(printstat)
        print(status)

def clicked():
    
        stock_quote =txt.get()
        w2.configure(text=stock_quote+" is the value entered")
        webbrowser.open('file:///home/aibot/Desktop/GIT_folder/Sentiment_Analysis_using_Python_Twitter_Kibana/index.html', new=2)
        listener = TweetStreamListener()
        # set twitter keys/tokens
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        # The most exception break up the kernel in my test is ImcompleteRead. This exception handler ensures
        # the stream to resume when breaking up by ImcompleteRead
        while True:
            try:
                # create instance of the tweepy stream
                stream = Stream(auth, listener)
                # search twitter for keyword "facebook"
                stream.filter(track=[stock_quote])
            #except IncompleteRead:
            #    continue
            except KeyboardInterrupt:
                    # or however you want to exit this loop
                stream.disconnect()
                break

#main code


#component definations and initializations 
window = Tk()
window.title('Sentiment Analyzer')
window.geometry('720x480')


w2=Label(window, text="")
w = Label(window, text="Masukan Kata Kunci")
btn = Button(window, text="Pemetaan Sentiment Sosial", command=clicked )
txt = Entry(window,width=15)
btn2=Button(window, text="Quit", command=quit )



#final packing of items in the applications

w.pack()
txt.pack()
btn.pack()
btn2.pack()
w2.pack()

window.mainloop()


# In[ ]:




