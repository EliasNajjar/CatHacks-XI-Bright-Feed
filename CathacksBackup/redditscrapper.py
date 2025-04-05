'''
This will be the file tha scrapes reddit and takes
'''


from http.client import NOT_FOUND
import praw
import subprocess
import sys
import os
import joblib
import pandas as pd
import numpy as np
from praw.models.reddit.subreddit import Redirect
from prawcore import Forbidden
from BullyingAdultContentAnalyzer import q_predict,load_q_learning_model
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

#talking to the node

#initialed flagged variables
flagged_posts_possible, flagged_posts_certain = [],[]
flagged_comments_possible, flagged_comments_certain =[],[]
# All of the functions
def scrapecomments(subredname):
    scrapedcomments = []
    subred = reddit.subreddit(subredname)
    for submission in subred.hot(limit=10):  # Just take one post for demo
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
    for post in subred.hot(limit = 20):
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

def validatesubred(subreddit):
    try:
        subred = reddit.subreddit(subreddit)
        subred.id
        print("validated")
        return True
    except (NOT_FOUND, Forbidden, Redirect) as e:
        return False

#tesing the model output
# for posts in posts:
#     result = q_predict(posts,q_table,vectorizer)
#     print(f"\n Prediction: {result['top_class']} (Confidence: {result['confidence']} | Margin: {result['margin']:.4f})")
#     print()
#initializing the reddit api
client_id = "G0gqyUzguU7lmP3D7JUcvw"
client_secret = "iSXaeSblUp7uaGgHHxVvWMzfmrhVNg"
user_agent = "tesingapi"
limit = 10
current_pid = os.getpid()
#initialize reddit object
reddit = praw.Reddit(
    client_id = client_id,
    client_secret = client_secret,
    user_agent = user_agent,
    )


#initialize the model
q_table, vectorizer = load_q_learning_model()

#talking to the node
arguments = sys.argv
subredname = "learnpython"
if len(arguments) > 2:
    subredname = arguments[1]  # reddit name
    arg2 = arguments[2]  # what we are looking for

    
arg2 = "AI Generated content"  
#initialed flagged variables

if validatesubred(subredname) == True:
    if (arg2 == "AI Generated content"):
        model_name = "Juner/AI-generated-text-detection-pair"
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        posts = scrapecontent(subredname)
        i = 0
        aicheck = 0
        print("AI is processing")
        for input in posts:
            input_text = input
            inputs = tokenizer(  
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding="max_length"
            )
            i += 1
            with torch.no_grad():
                outputs = model(**inputs)

            # Get predictions
            predictions = torch.argmax(outputs.logits, dim=1)

            # Interpret the prediction
            label_map = {0: "Human-written", 1: "AI-generated", 3: "Human-written"}
            output = label_map[predictions.item()]
            if (output == "AI-generated"):
                aicheck += 1
            else:
                aicheck -= 1

            if (i > limit):
                break
        ai_average = aicheck/i
        print("writing the file")
        with open(f"response-{current_pid}", "w",encoding = "utf-8") as file:
            if (ai_average > 0.5):
            
                file.write("We believe there is a considerable amount of AI generated content on the page")
            else:
                file.write("We believe there is not a considerable amount of AI generated content on the page")
    else:
        print("Scrapping Content")
        #scrape website content
        comments = scrapecomments(subredname)
        posts = scrapecontent(subredname)
        flagged_posts_possible, flagged_posts_certain = [],[]
        flagged_comments_possible, flagged_comments_certain =[],[]
        #functions to filter our posts and shit
        posts = scrapecontent(subredname)
        comments = scrapecomments(subredname)
        flagged_posts_possible, flagged_posts_certain = flagposts(posts)
        flagged_comments_possible, flagged_comments_certain = flagcomments(comments)
        
        #writing to the output file
        with open(f"response-{current_pid}", "w",encoding = "utf-8") as file:
         responselength = 700
         if len(flagged_posts_certain) >= 5:
            i = 1
            file.write("Here are some concerning posts we found!\n")
            while(i<=5):
                file.write(f"\nPost{i}\n\n")
                file.write(f"{flagged_posts_certain[i][:responselength]}\n")
                i += 1
         elif len(flagged_posts_certain) > 0:
             file.write("Here are some concerning posts we found!\n")
             for i,posts in enumerate(flagged_posts_certain):
                file.write(f"\nPost{i-1}\n\n")
                file.write(f"{posts[:responselength]}\n")
         elif len(flagged_posts_possible) >= 5:
             i = 1
             file.write("Here are some slightly concerning posts we found!\n")
             while(i<=5):           
                file.write(f"\nPost{i}\n\n")
                file.write(f"{flagged_posts_possible[i][:responselength]}\n")
                i += 1
         else:
             file.write("We found nothing concerning in the subreddit's posts")
         commentlength = 100
         if(len(flagged_comments_certain) > 0):
        
            file.write("Also here are some concering comments\n")
            for i,comment in enumerate(flagged_comments_certain):
                file.write(f"\nComment{i+1}\n\n")
                file.write(comment[:commentlength])
                if (i>3):
                    break
         elif(len(flagged_comments_possible) > 0):
            file.write("Also here are some slightly concering comments\n")
            for i,comment in enumerate(flagged_comments_possible):
                file.write(f"\nComment{i+1}\n\n")
                file.write(comment[:commentlength])
                if (i>3):
                    break



    



