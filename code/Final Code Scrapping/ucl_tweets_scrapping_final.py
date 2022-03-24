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


#######################################################################
# Get Posts (statuses count), follower count, listed count

df = pd.read_csv('C:/Users/Mehdi/Desktop/Social Media/As1_group/final_tweets_df.csv')


ref= 'https://api.twitter.com/1.1/users/lookup.json'

params= {
    'user_id': '38776130,6473894,6483994'
}


response = requests.get(ref,params=params,headers=headers)

#function to get the id_s to the right format
chars = [']','[',' ']
def remove_chars_iter(subj, chars):
    sc = set(chars)
    return ''.join([c for c in subj if c not in sc])

#test
test = str(df.author_id[:2].tolist())
remove_chars_iter(test,chars)

#function to split the list into sublists of x=100 elements
def split_list (big_list, x):
   return [big_list[i:i+x] for i in range(0,len(big_list), x)]

#Get list of ids
list_ids = df.author_id.tolist()
sub_lists = split_list(list_ids, 100)

#test
sub_lists[0]

#requests for all the sublists (getting the user objects as return)

chars = [']','[',' '] #char to remove
ref= 'https://api.twitter.com/1.1/users/lookup.json'


df_authors = pd.DataFrame()  # initialize dataframe

def get_data_2(user):
    data = {'id':user['id'],
            'screen_name':user['screen_name'],
        'followers_count':user['followers_count'],
        'friends_count':user['friends_count'],
        'listed_count':user['listed_count'],
        'statuses_count':user['statuses_count'],}
    return data

for sub in sub_lists:
    
    #transform it into strings with no space and no '[', ']'
    sub = remove_chars_iter(str(sub), chars)
    
    params= {
        'user_id': sub
    }
    
    response = requests.get(ref,params=params,headers=headers)

    for i in range(len(response.json())):
        user = response.json()[i]
        row = get_data_2(user)  # we defined this function earlier
        df_authors = df_authors.append(row, ignore_index=True)    
    
df_authors.to_csv('C:/Users/Mehdi/Desktop/authors_data.csv')






##################################################################
#Retweeted persons

df_tweet_table = pd.read_csv('C:/Users/Mehdi/Documents/SocialMediaAnalytics_Github/data/Tweet_table.csv')
retweeted_users = df_tweet_table.col2.unique()

#retweeted_users = remove_chars_iter(retweeted_users, ['@',' '])

retweeted_users = [remove_chars_iter(user,['@']) for user in retweeted_users]

sub_lists = split_list(retweeted_users, 100)



chars = [']','[',' ',"'"]

retweeted_users = remove_chars_iter(str(retweeted_users), chars)



df_retweeted = pd.DataFrame()

for sub in sub_lists:
    
    #transform it into strings with no space and no '[', ']'
    sub = remove_chars_iter(str(sub), chars)
    
    params= {
        'screen_name': sub
    }
    
    response = requests.get(ref,params=params,headers=headers)

    for i in range(len(response.json())):
        user = response.json()[i]
        row = get_data_2(user)  # we defined this function earlier
        #df_authors = df_authors.append(row, ignore_index=True)    
        df_retweeted = df_retweeted.append(row, ignore_index=True) 


df_retweeted.to_csv('C:/Users/Mehdi/Desktop/retweeted_users_data.csv')


#Concatenate into a single data frame

users_info_df = pd.concat([df_authors,df_retweeted])

users_info_df.to_csv('C:/Users/Mehdi/Desktop/users_info_df.csv')








