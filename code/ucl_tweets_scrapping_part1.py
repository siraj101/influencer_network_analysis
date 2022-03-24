# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 14:34:03 2022

@author: Mehdi
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 12:14:13 2022

@author: Mehdi
"""


from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import matplotlib.pyplot as plt
# NLTK VADER for sentiment analysis
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
from datetime import datetime, timedelta
import requests
import pandas as pd
import re

from datetime import datetime, timedelta
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import datetime, timedelta


BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAANeNZAEAAAAAWqEd3GXb3R8V%2FdhbCITAL%2BHA9RM%3D32FXQSrOUqzLm0LSmsKnq75B9CwIZLtsH3OAoG8HsgyC08Jrra'



# setup the API request
ref= 'https://api.twitter.com/2/tweets/search/recent'

headers= {'authorization': f'Bearer {BEARER_TOKEN}'}
params= {
    'query': '(Champions league OR UCL) (lang:en)',
    'max_results': '100',
    'tweet.fields': 'created_at,lang,author_id',
    #'expansions': 'entities.mentions.username',
    #'user.fields': 'username'
}

#Function to get data from the requests
def get_data(tweet):
    data = {'id':tweet['id'],
            'author_id':tweet['author_id'],
            #'username':tweet['entities']['mentions'][0]['username'],
            #'username_id': tweet['entities']['mentions'][0]['id'],
        'created_at':tweet['created_at'],
        'text':tweet['text']}
    return data

#tweet['entities']['mentions'][0]['username']



dtformat = '%Y-%m-%dT%H:%M:%SZ'  # Setting the date format required by twitter API

# function that subtracts 60 min from the current datetime
def time_slots(end_date, mins):
    date = datetime.strptime(end_date, dtformat)
    back_in_time = date - timedelta(minutes=mins)
    return back_in_time.strftime(dtformat)

#date = '2022-03-16T23:55:55Z'

#Defining current hour
date = '16/03/22 23:59:00'
date = datetime.strptime(date, '%d/%m/%y %H:%M:%S') # get current datetime

last_week = date - timedelta(days=2)  # datetime 7 days ago
date = date.strftime(dtformat)  # convert current datetime to format for twitter API


df = pd.DataFrame()  # initialize dataframe

while True:
    
    if (datetime.strptime(date, dtformat) < last_week):
        # break the loop when we reach one week ago
        break
    
    go_back = time_slots(date, 55)  # get 60 minutes before 'now'
    
    # setting starting and end time for the API
    params['start_time'] = go_back
    params['end_time'] = date
    
    #Sending request
    response = requests.get(ref,
                            params=params,
                            headers=headers)
    
    date = go_back  # moving back the window by 60 min
    
    # Adding the tweets data to the dataframe
    for tweet in response.json()['data']:
        row = get_data(tweet)  # we defined this function earlier
        df = df.append(row, ignore_index=True)
        

#converting 'created_at' to date time
df.created_at = pd.to_datetime(df['created_at'])

df.to_csv('C:/Users/Mehdi/Desktop/tweets_ucl_noUsername.csv')



from twitterUsernameviaUserID import getHandles as gH
temp = gH.getHandles(df.author_id.tolist(), 10)

id_to_username_df = pd.DataFrame(list(temp.items()), columns=['author_id', 'username'])
id_to_username_df.to_csv('C:/Users/Mehdi/Desktop/id_to_username_df.csv')



df_final = pd.merge(df,id_to_username_df, how='left', on='author_id')

#Check
print(df_final.isnull().sum())

df_final.to_csv('C:/Users/Mehdi/Desktop/final_tweets_df.csv')



