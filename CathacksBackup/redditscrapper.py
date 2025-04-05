'''
This will be the file tha scrapes reddit and takes
'''

import ollama
import praw
import subprocess
import sys
import os
import os
import joblib
import pandas as pd
import numpy as np
from BullyingAdultContentAnalyzer import q_predict,load_q_learning_model


# All of the functions
def scrapecomments(subredname):
    scrapedcomments = []
    subred = reddit.subreddit(subredname)
    for submission in subred.hot(limit=1):  # Just take one post for demo
        # Load all comments (replace MoreComments objects)
        
            submission.comments.replace_more(limit=10)
            comments = submission.comments.list()
            # Iterate through top-level comments
            comment_list = [comment.body for comment in submission.comments.list()]
    return comment_list

def scrapecontent(subredname):
    subred = reddit.subreddit(subredname)
    postcontent = []
    #get top 10 posts
    for post in subred.hot(limit = 10):
        #write it all into one file
        
            if post.selftext:
                
                postcontent.append(post.selftext)
            else:
                postcontent.append("No text available")
    return postcontent

def flagposts(posts):
 for x in posts:
    result = q_predict(x,q_table,vectorizer)
    if result['top_class'] != 'neutral':
        if result['top_class'] == 'strongly inappropriate':
            flagged_posts_certain.append(x)
        else:
            flagged_posts_possible.append(x)   
 return flagged_posts_possible, flagged_posts_certain

def flagcomments(comments):
 for x in comments:
    result = q_predict(x,q_table,vectorizer)
    if result['top_class'] != 'neutral':
        if result['top_class'] == 'strongly inappropriate':
            flagged_comments_certain.append(x)
        else:
            flagged_comments_possible.append(x)   
 return flagged_comments_possible, flagged_comments_certain

#tesing the model output
# for posts in posts:
#     result = q_predict(posts,q_table,vectorizer)
#     print(f"\n Prediction: {result['top_class']} (Confidence: {result['confidence']} | Margin: {result['margin']:.4f})")
#     print()

#initializing the reddit api
client_id = "G0gqyUzguU7lmP3D7JUcvw"
client_secret = "iSXaeSblUp7uaGgHHxVvWMzfmrhVNg"
user_agent = "tesingapi"

#initialize reddit object
reddit = praw.Reddit(
    client_id = client_id,
    client_secret = client_secret,
    user_agent = user_agent,
    )
subredname = "learnpython"


q_table, vectorizer = load_q_learning_model()

comments = scrapecomments(subredname)
posts = scrapecontent(subredname)
flagged_posts_possible, flagged_posts_certain = [],[]
flagged_comments_possible, flagged_comments_certain =[],[]
#functions to filter our posts and shit

posts = scrapecontent(subredname)
comments = scrapecontent(subredname)
flagged_posts_possible, flagged_posts_certain = flagposts(posts)
flagged_comments_possible, flagged_comments_certain = flagcomments(comments)



