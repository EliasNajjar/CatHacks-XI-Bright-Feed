'''
This will be the file tha scrapes reddit and takes
'''

import ollama
import praw
import subprocess
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
subredname = "learnpython"
'''
def getargs():
    for i,argument in enumerate(sys.arg):
        print(f"{i} argument is {argument}")
'''
    
# save as a textfile
def scrapecomments(subredname):
    subred = reddit.subreddit(subredname)
    for submission in subred.hot(limit=1):  # Just take one post for demo
        # Load all comments (replace MoreComments objects)
        filename = f"content.txt"
        with open(filename,"a",encoding = "utf-8") as f:
            submission.comments.replace_more(limit=10)
            comments = submission.comments.list()
            # Iterate through top-level comments
            for idx, comment in enumerate(submission.comments.list()):
                f.write(f"{idx + 1}. {comment.body}\n")

def scrapecontent(subredname):
    subred = reddit.subreddit(subredname)
    #get t0p 10 posts
    for post in subred.hot(limit = 10):
        #write it all into one file
        filename = f"content.txt"
        with open(filename,"a",encoding = "utf-8") as f:
            if post.selftext:
                f.write(f"{post.author} wrote \n {post.selftext}\n")
            else:
                f.write("No text body")
#getargs()

with open("content.txt","w",encoding = "utf-8") as file:
    pass
scrapecomments(subredname)
scrapecontent(subredname)
with open("content.txt","r",encoding = "utf-8") as file:
    file_content = file.read()
    contentToRecognize = "topics of hate speech"
    '''
    # Customize this part: lines 61-77 written by ChatGPT with changes
    model = "llama3.2"
    system_message = "Talk like a pirate."
    user_prompt = f"Determine if the text \"{file_content}\" contains {contentToRecognize}"

    # Build the command
    cmd = [
        "ollama", "run", "llama3.2",
    ]

    prompt = f"Determine if the text \"{file_content}\" contains {contentToRecognize}"

    result = subprocess.run(cmd, input=prompt, capture_output=True, text=True)
    print(result.stdout)
    '''
    result = subprocess.run(["ollama", "chat", "llama3.2", "--system", "You are a pirate", "--prompt", f"Determine if the text \"{file_content}\" contains {contentToRecognize}"], capture_output=True, text=True)
    print(result.stdout)
    '''
    response = ollama.chat(model='llama3.2', messages=[
        {
            'role': 'system',
            'content': 'Talk like a priate',
        },
        {
            'role': 'user',
            'content': f'Determine if the text \"{file_content}\" contains {contentToRecognize}',
        },
    ])
    '''
    #output = ollama.generate(model="llama3.2",prompt=f"Determine if the text \"{file_content}\" contains {contentToRecognize}")
    
