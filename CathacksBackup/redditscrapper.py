'''
This will be the file tha scrapes reddit and takes
'''

import praw
import sys
import os
client_id = "G0gqyUzguU7lmP3D7JUcvw"
client_secret = "iSXaeSblUp7uaGgHHxVvWMzfmrhVNg"
user_agent = "tesingapi"

#initialize reddit object
reddit = praw.Reddit(
    client_id = client_id,
    client_secret = client_secret,
    user_agent = user_agent,
    )
subredname = "learningpython" 
def getargs():
    for i,argument in enumerate(sys.arg):
        print(f"{i} argument is {argument}")
    
# save as a textfile
def scrapecomments(subredname,filenum):
    subred = reddit.subreddit(subredname)
    for submission in subred.hot(limit=1):  # Just take one post for demo
        # Load all comments (replace MoreComments objects)
        filename = f"{submission.id}{filenum}_comments.txt"
        with open(filename,"w",encoding = "utf-8") as f:
            submission.comments.replace_more(limit=10)
            comments = submission.comments.list()
            # Iterate through top-level comments
            for idx, comment in enumerate(submission.comments.list()):
                f.write(f"{idx + 1}. {comment.body}\n")

def scrapecontent(subredname,filenum):
    subred = reddit.subreddit(subredname)
    #get t0p 10 posts
    for post in subred.hot(limit = 10):
        #write it all into one file
        filename = f"{post.id}{filenum}_content.txt"
        with open(filename,"w",encoding = "utf-8") as f:
            if post.selftext:
                f.write(f"{post.author} wrote \n {post.selftext}\n")
            else:
                f.write("No text body")
getargs()