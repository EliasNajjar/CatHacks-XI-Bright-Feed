from http.client import NOT_FOUND
import sys
import os
import joblib
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs
from BullyingAdultContentAnalyzer import q_predict, load_q_learning_model
import nltk
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from youtube_transcript_api import YouTubeTranscriptApi

# Argument handling
arguments = sys.argv
current_pid = os.getpid()
if len(arguments) > 2:
    arg1 = arguments[1]
    arg2 = arguments[2]

    print(arg1)
    print(arg2)

    with open(f"response-{current_pid}", "w") as file:
        file.write("Hello, world!\n")
        #file.write("Video URL: " + arg1 + "\n")
        file.write("Check For: " + arg2 + "\n")
        file.write(f"ID: {current_pid}" + "\n")
else:
    print("Insufficient arguments provided. Please pass two arguments.")
    sys.exit(1)

# YouTube video ID extractor
def get_video_id(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ''
    if hostname.endswith('youtu.be'):
        return str(parsed_url.path[1:])
    elif 'youtube' in hostname:
        if parsed_url.path == '/watch':
            query_params = parse_qs(parsed_url.query)
            return str(query_params.get('v', [None])[0])
        elif parsed_url.path.startswith('/embed/'):
            return str(parsed_url.path.split('/')[2])
        elif parsed_url.path.startswith('/v/'):
            return str(parsed_url.path.split('/')[2])
    return None

# Sentence splitting
def split_into_sentences(text):
    return nltk.sent_tokenize(text)

# Flagging logic
def flagposts(sentences, result):
    flagged_possible, flagged_certain = [], []
    for sentence in sentences:
        if result['top_class'] == 'strongly inappropriate':
            flagged_certain.append(sentence)
        elif result['top_class'] != 'neutral':
            flagged_possible.append(sentence)
    return flagged_possible, flagged_certain

q_table, vectorizer = load_q_learning_model()

# Main logic
def main():
    url = arg1
    video_id = get_video_id(url)
    video_id = str(video_id)

    if arg2 == "AI Generated Content":
        # Load AI detector
        model_name = "Juner/AI-generated-text-detection-pair"
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("🧠 AI Detection Model Loaded")

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join(entry["text"] for entry in transcript_list)
        sentences = split_into_sentences(transcript_text)

        limit = 20
        i = 0
        aicheck = 0
        aioutputs = []

        for x in sentences:
            inputs = tokenizer(
                x,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding="max_length"
            )
            with torch.no_grad():
                outputs = model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=1)
            label_map = {0: "Human-written", 1: "AI-generated", 3: "Human-written"}
            output = label_map.get(predictions.item(), "Unknown")

            if output == "AI-generated":
                aicheck += 1
                aioutputs.append(x)
            else:
                aicheck -= 1

            i += 1
            if i >= limit:
                break

        ai_average = aicheck / max(i, 1)

        with open(f"response-{current_pid}", "w", encoding="utf-8") as file:
            if ai_average > 0.5:
                file.write("We believe there is a considerable amount of AI-generated content in the transcript.\n\nExamples:\n")
                for idx, example in enumerate(aioutputs[:2]):
                    file.write(f"\nExample {idx+1}:\n{example}\n")
            else:
                file.write("We believe there is not a considerable amount of AI-generated content in the transcript.")

    else:
        # Regular content filter
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        print("Evaluating Transcript...")
        transcript_text = " ".join(entry["text"] for entry in transcript_list)
        sentences = split_into_sentences(transcript_text)
        result = q_predict(transcript_text, q_table, vectorizer)
        flagged_possible, flagged_certain = flagposts(sentences, result)

        # Writing results to a response file
        with open(f"response-{current_pid}", "w") as file:
            responselength = 1000
        
            if len(flagged_certain) >= 5:
                i = 1
                file.write("Here are some concerning phrases we found!")
                while(i <= len(flagged_certain) and i <= 5):
                    file.write(f"Phrase{i}\n")
                    file.write(f"{flagged_certain[i-1][:responselength]}\n")
                    i += 1
            elif len(flagged_certain) > 0:
                for i, post in enumerate(flagged_certain):
                    file.write(f"Phrase{i}\n")
                    file.write(post[:responselength])
            elif len(flagged_possible) > 0:
                i = 1
                file.write("Here are some slightly concerning phrases we found!\n")
                while(i <= len(flagged_possible) and i <= 5):
                    file.write(f"Phrase{i}\n")
                    file.write(f"{flagged_possible[i-1][:responselength]}\n")
                    i += 1
            else:
                file.write("We found nothing concerning in the video transcript")

if __name__ == "__main__":
    main()
  

