from http.client import NOT_FOUND
import sys
import os
import joblib
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs
from BullyingAdultContentAnalyzer import q_predict, load_q_learning_model
from youtube_transcript_api import YouTubeTranscriptApi
import re

# Get arguments from the command line
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

# Function to extract video ID from a YouTube URL
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

# Function to flag posts based on content analysis with a confidence threshold
def flagposts(transcript_text, confidence_threshold=0.5):
    flagged_possible, flagged_certain = [], []
    
    for x in transcript_text:
        result = q_predict(x, q_table, vectorizer)
        
        # Get the prediction confidence level
        confidence = result['confidence']
        
        # Flagging based on confidence threshold
        if confidence >= confidence_threshold:
            if result['top_class'] == 'strongly inappropriate':
                flagged_certain.append(x)
            elif result['top_class'] != 'neutral':  # Allowing some leeway for "offensive" content
                flagged_possible.append(x)

    return flagged_possible, flagged_certain

# Load the Q-learning model
q_table, vectorizer = load_q_learning_model()

def clean_and_split_into_sentences(text):
    """
    This function ensures we split the text into proper sentences by looking for sentence boundaries.
    It also removes unnecessary newlines or spaces.
    """
    text = text.replace("\n", " ").strip()  # Clean up any unwanted newlines or spaces
    # Simple sentence boundary detection using regular expression
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences

# Main function to execute the script
def main():
    url = arg1
    video_id = get_video_id(url)

    # Fetch transcript using YouTubeTranscriptApi
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)    
    transcript_text = " ".join(entry["text"] for entry in transcript_list)

    # Clean and split the transcript into sentences
    sentences = clean_and_split_into_sentences(transcript_text)

    # Flag posts based on content analysis with a 50% confidence threshold
    flagged_possible, flagged_certain = flagposts(sentences, confidence_threshold=0.5)

    # Write the results to a file
    with open(f"response-{current_pid}", "w") as file:
        responselength = 1000
        if len(flagged_certain) >= 5:
            i = 0
            file.write("Here are some concerning phrases we found!\n")
            while i < 5 and i < len(flagged_certain):
                file.write(f"Phrase {i+1}:\n")
                file.write(f"{flagged_certain[i][:responselength]}\n")
                i += 1

        elif len(flagged_certain) > 0:
            for i, post in enumerate(flagged_certain):
                file.write(f"Phrase {i+1}:\n")
                file.write(post[:responselength])

        elif len(flagged_possible) >= 5:
            i = 0
            file.write("Here are some phrases that could be concerning:\n")
            while i < 5 and i < len(flagged_possible):
                file.write(f"Phrase {i+1}:\n")
                file.write(f"{flagged_possible[i][:responselength]}\n")
                i += 1
        else:
            file.write("We found nothing concerning in the video's transcript.")

if __name__ == "__main__":
    main()
