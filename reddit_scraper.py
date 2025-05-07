import praw
from datetime import datetime, timezone
import json
import time
import os

CLIENT_ID = os.environ.get("XFKnWibpr5kxt0uaSNV1jA")
CLIENT_SECRET = os.environ.get("WCr1KOCXn7pA8hgAIACXsPMr5j5iRQ")
USER_AGENT = os.environ.get("Vercel:OEL:v1.0 (by /u/TheBourneGuy")

if not all([CLIENT_ID, CLIENT_SECRET, USER_AGENT]):
    print("Error: Reddit API credentials not found in environment variables.")
    exit()

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    user_agent=USER_AGENT
)

subreddit = reddit.subreddit("worldnews")

DATA_FILENAME = "worldnews_data.json"

try:
    with open(DATA_FILENAME, "r", encoding='utf-8') as f:
        results = json.load(f)
except FileNotFoundError:
    results = []
except json.JSONDecodeError:
    print("Warning: Could not decode existing JSON data. Starting with an empty list.")
    results = []

# Track existing titles to compare
existing_titles = {post["title"] for post in results}

call_counter = 0

def fetch_new_posts():
    global existing_titles, call_counter
    new_posts = []
    new_posts_count = 0

    call_counter += 1
    print(f"Making API call number {call_counter} to fetch latest 10 posts...")

    try:
        for post in subreddit.new(limit=10):
            if post.title in existing_titles:
                continue

            existing_titles.add(post.title)

            try:
                post.comments.replace_more(limit=0)
                all_comments = [comment.body for comment in post.comments.list()]
            except Exception as e:
                print(f"Error fetching comments for post {post.id}: {e}")
                all_comments = []

            post_data = {
                "title": post.title,
                "upvotes": post.score,
                "timestamp": datetime.fromtimestamp(post.created_utc, timezone.utc).isoformat(),
                "all_comments": all_comments
            }

            new_posts.append(post_data)
            new_posts_count += 1

        if new_posts:
            results.extend(new_posts)
            with open(DATA_FILENAME, "w", encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4, default=str)
            print(f"✅ {new_posts_count} new post(s) added.")
        else:
            print("No new posts.")
    except Exception as e:
        print(f"Error fetching posts: {e}")

if __name__ != "__main__":
    fetch_new_posts()