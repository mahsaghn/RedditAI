import json
import requests
from datetime import datetime, timezone
import multiprocessing
import pickle
import os

checked_users = dict()
checked_users["[deleted]"] = True

def de_duplicate(posts):
    seen = dict()
    unique_posts = []
    for post in posts:
        if post["created_utc"] not in seen:
            unique_posts.append(post)
            seen["created_utc"] = True
    return unique_posts


def get_all_posts_of_user(user, start_time, end_time):

    dt = datetime.strptime(start_time, "%Y-%m-%d")
    # Attach UTC timezone
    dt = dt.replace(tzinfo=timezone.utc)
    # Convert to Unix timestamp (int)
    start_time = int(dt.timestamp())

    dt = datetime.strptime(end_time, "%Y-%m-%d")
    # Attach UTC timezone
    dt = dt.replace(tzinfo=timezone.utc)
    # Convert to Unix timestamp (int)
    end_time = int(dt.timestamp())


    # print(start_time)
    iso_start_time = datetime.fromtimestamp(start_time, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00",
                                                                                                               "Z")
    iso_end_time = datetime.fromtimestamp(end_time - 1, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00",
                                                                                                               "Z")

    # iso_start_time = start_time
    # iso_end_time = end_time

    all_posts = []
    # print(user)
    params = {"author": user, "after": iso_start_time, "before": iso_end_time, "limit": "auto", "sort": "asc"}

    while datetime.fromisoformat(iso_start_time.replace("Z", "+00:00")) < datetime.fromisoformat(
            iso_end_time.replace("Z", "+00:00")):
        # print(params['after'])
        r = requests.get("https://arctic-shift.photon-reddit.com/api/posts/search", params=params, timeout=60)
        r.raise_for_status()

        all_posts += [post for post in r.json()["data"]]
        # print(len(all_posts))
        # print(user)
        if len(r.json()["data"]) < 100:
            break

        iso_start_time = datetime.fromtimestamp(all_posts[-1]["created_utc"] + 2, tz=timezone.utc).isoformat(
            timespec="seconds").replace("+00:00", "Z")
        params["after"] = iso_start_time

    return (de_duplicate(all_posts))

def get_user_activities(user):
    all_posts = get_all_posts_of_user(user, "2025-08-01", "2025-09-16")
    pickle.dump(all_posts, open(f"data/{user}.pkl", "wb"), protocol=pickle.HIGHEST_PROTOCOL)


def check_users(file_path):
    user_set = {}
    with open(file_path, 'r') as file:
        for line in file:
            post_info = json.loads(line)
            author = post_info['author']
            user_set.add(author)
    os.makedirs("data", exist_ok=True)
    pool = multiprocessing.Pool(processes=16)
    pool.map(get_user_activities, list(user_set))

open("users_activities.jsonl", "w").close()
check_users("./Data/r_ChatGPT_posts.jsonl")
check_users("./Data/r_ClaudeAI_posts.jsonl")