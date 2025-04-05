from http.client import NOT_FOUND
import sys
import os
import joblib
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs
from BullyingAdultContentAnalyzer import q_predict, load_q_learning_model
import nltk

arguments = sys.argv
current_pid = os.getpid()
if len(arguments) > 2:
    arg1 = arguments[1]  # Fixed typo
    arg2 = arguments[2]  # Fixed typo

    print(arg1)
    print(arg2)

    with open(f"response-{current_pid}", "w") as file:
        file.write("Hello, world!\n")
        file.write("Video URL: " + arg1 + "\n")
        file.write("Check For: " + arg2 + "\n")
        file.write(f"ID: {current_pid}" + "\n")
else:
    print("Insufficient arguments provided. Please pass two arguments.")
    sys.exit(1)

def get_video_id(url):
    """
    Extract the video ID from a YouTube URL.
    Handles standard, short, and embed URL formats.
    """
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ''
    if hostname.endswith('youtu.be'):
        return str(parsed_url.path[1:])  # Ensure it's a string
    elif 'youtube' in hostname:
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return str(query_params.get('v', [None])[0])  # Ensure it's a string
        elif parsed_url.path.startswith('/embed/'):
            return str(parsed_url.path.split('/')[2])  # Ensure it's a string
        elif parsed_url.path.startswith('/v/'):
            return str(parsed_url.path.split('/')[2])  # Ensure it's a string
    return None  # Return None if no valid video ID is found

# Function to split transcript text into sentences using NLTK
def split_into_sentences(text):
    return nltk.sent_tokenize(text)

# Function to flag posts based on content analysis with a confidence threshold
def flagposts(sentences, confidence_threshold=0.5):
    flagged_possible, flagged_certain = [], []
    
    
    for sentence in sentences:
        result = q_predict(sentences, q_table, vectorizer)
        
        '''
        # Ensure the confidence is a float or handle it as needed
        try:
            confidence = float(result.get('confidence', 0))  # Default to 0 if no confidence value
        except ValueError:
            confidence = 0  # Default to 0 if there's an issue converting to float
        '''
        if result['top_class'] == 'strongly inappropriate':
            flagged_certain.append(sentence)
        elif result['top_class'] != 'neutral':  # Allowing some leeway for "offensive" content
            flagged_possible.append(sentence)

    return flagged_possible, flagged_certain

q_table, vectorizer = load_q_learning_model()

def main():
    url = arg1
    video_id = get_video_id(url)
   
    from youtube_transcript_api import YouTubeTranscriptApi
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)    
    print("Evaluating Transcript")
    # Combine all transcript text into a single string
    transcript_text = " ".join(entry["text"] for entry in transcript_list)
    # Split the transcript into sentences
    sentences = split_into_sentences(transcript_text)
    result = q_predict(sentences, q_table, vectorizer)
    print(result)
    # Flag posts based on the transcript sentences
    flagged_possible, flagged_certain = flagposts(sentences)
    
    # Writing results to a response file
    with open(f"response-{current_pid}", "w") as file:
        responselength = 1000
        if len(flagged_certain) >= 5:
            i = 1
            file.write("Here are some concerning phrases we found!")
            while(i <= 5):
                file.write(f"Phrase{i}\n")
                file.write(f"{flagged_certain[i][:responselength]}\n")
                i += 1
        elif len(flagged_certain) > 0:
            for i, post in enumerate(flagged_certain):
                file.write(f"Phrase{i}\n")
                file.write(post[:responselength])
        elif len(flagged_possible) > 0:
            i = 1
            while(i <= 5):
                file.write(f"Phrase{i}\n")
                file.write(f"{flagged_possible[i][:responselength]}\n")
                i += 1
        else:
            file.write("We found nothing concerning in the video transcript")

if __name__ == "__main__":
    main()
