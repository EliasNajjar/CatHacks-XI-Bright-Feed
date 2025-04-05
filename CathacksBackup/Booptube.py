import sys
import os
import joblib
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs
from BullyingAdultContentAnalyzer import q_predict,load_q_learning_model

def get_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    Handles standard, short, and embed URL formats.
    """
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ''
    if hostname.endswith('youtu.be'):
        return parsed_url.path[1:]
    elif 'youtube' in hostname:
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return query_params.get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return None

def flagposts(transcript_text):
    flagged_possible, flagged_certain =[],[]
    for x in transcript_text:
        result = q_predict(x,q_table,vectorizer)
        if result['top_class'] != 'neutral':
            if result['top_class'] == 'strongly inappropriate':
                flagged_certain.append(x)
            else:
                flagged_possible.append(x)   
    return flagged_possible, flagged_certain

q_table, vectorizer = load_q_learning_model()
 
def main():
    url = input("\n➡ Enter YouTube URL, then press Enter: ").strip()
    video_id = get_video_id(url)

    from youtube_transcript_api import YouTubeTranscriptApi
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)    
    transcript_text = " ".join(entry["text"] for entry in transcript_list)

    # Load trained Q-table and vectorizer
    current_pid = os.getpid()
    flagged_possible, flagged_certain = flagposts(transcript_text)

    with open(f"response-{current_pid}", "w") as file:
        responselength = 1000
        if len(flagged_certain) >= 5:
            i = 1
            file.write("Here are some concerning posts we found!")
            while(i<=5):
                file.write(f"Post{i}\n")
                file.write(f"{flagged_certain[i][:responselength]}\n")
            i += 1

        elif len(flagged_certain) > 0:
            for i,posts in enumerate(flagged_certain):
                file.write(f"Post{i}\n")
                file.write(posts[:responselength])
        elif len(flagged_possible) >= 5:
            i = 1
            while(i<=5):
                file.write(f"Post{i}\n")
                file.write(f"{flagged_possible[i][:responselength]}\n")
                i += 1
        else:
            file.write("We found nothing concerning in the subreddit's posts")



if __name__ == "__main__":
    main()