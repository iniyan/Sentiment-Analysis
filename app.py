from flask import Flask, request, jsonify
import re
from googleapiclient.discovery import build
from textblob import TextBlob

app = Flask(__name__)

# Set your YouTube API key here
API_KEY = 'YOUR_YOUTUBE_API_KEY'

# Function to extract comments from a YouTube video
def get_video_comments(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []

    # Get video comments
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    )

    while request:
        response = request.execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)

        request = youtube.commentThreads().list_next(request, response)

    return comments

# Function to perform sentiment analysis on comments
def analyze_sentiment(comments):
    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for comment in comments:
        analysis = TextBlob(comment)
        # Classify sentiment as positive, negative, or neutral
        if analysis.sentiment.polarity > 0:
            positive_count += 1
        elif analysis.sentiment.polarity < 0:
            negative_count += 1
        else:
            neutral_count += 1

    total_comments = len(comments)
    result = {
        "Total Comments": total_comments,
        "Positive Comments": positive_count,
        "Negative Comments": negative_count,
        "Neutral Comments": neutral_count
    }
    return result

# Flask route for handling sentiment analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    video_url = data.get('video_url')
    video_id_match = re.search(r"(?<=v=)[a-zA-Z0-9_-]+", video_url)

    if video_id_match:
        video_id = video_id_match.group(0)
        comments = get_video_comments(API_KEY, video_id)
        result = analyze_sentiment(comments)
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid YouTube video URL"}), 400

if __name__ == '__main__':
    app.run(debug=True)
