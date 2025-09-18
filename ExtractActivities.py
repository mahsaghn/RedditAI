import json
import requests
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


checked_users = {"[deleted]": True}

def de_duplicate(posts):
    seen = set()
    unique = []
    for post in posts:
        t = post["created_utc"]
        if t not in seen:
            unique.append(post)
            seen.add(t)
    return unique

def to_utc_int(date_str: str) -> int:
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())

def get_all_posts_of_user(user, start_date, end_date):
    start_ts = to_utc_int(start_date)
    end_ts   = to_utc_int(end_date)

    iso_start = datetime.fromtimestamp(start_ts, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")
    iso_end   = datetime.fromtimestamp(end_ts - 1, tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

    params = {"author": user, "after": iso_start, "before": iso_end, "limit": "auto", "sort": "asc"}
    all_posts = []

    while datetime.fromisoformat(params["after"].replace("Z","+00:00")) < datetime.fromisoformat(iso_end.replace("Z","+00:00")):
        r = requests.get("https://arctic-shift.photon-reddit.com/api/posts/search", params=params, timeout=60)
        r.raise_for_status()
        data = r.json().get("data", [])
        if not data:
            break
        all_posts.extend(data)

        # advance window by latest post timestamp (+2s to avoid duplicates at same second)
        next_after = datetime.fromtimestamp(all_posts[-1]["created_utc"] + 2, tz=timezone.utc)\
                             .isoformat(timespec="seconds").replace("+00:00","Z")
        if next_after >= iso_end:
            break
        params["after"] = next_after

        # optional fast-exit if small page
        if len(data) < 100:
            break

    return de_duplicate(all_posts)

def get_user_activities(user):

    posts = get_all_posts_of_user(user, "2025-08-01", "2025-09-16")
    return {user: posts}

def check_users(file_path):
    # load already-processed users (if file exists)
    out_path = Path("users_activities.jsonl")
    if out_path.exists():
        with out_path.open("r") as f:
            for line in f:
                try:
                    info = json.loads(line)
                except json.JSONDecodeError:
                    continue
                for key in info.keys():
                    checked_users[key] = True

    # collect new authors
    authors = []
    with open(file_path, "r") as f:
        for line in f:
            post_info = json.loads(line)
            author = post_info.get("author")
            if not author or author in checked_users:
                continue
            checked_users[author] = True
            authors.append(author)

    if not authors:
        return

    # parallel fetch (threads) + single-writer
    with ThreadPoolExecutor(max_workers=16) as ex, out_path.open("a") as fh:
        futures = [ex.submit(get_user_activities, a) for a in authors]
        for fut in as_completed(futures):
            res = fut.result()
            print(res.keys())
            fh.write(json.dumps(res) + "\n")
            print(f'finish {res.keys()}')
            # fh.flush()   # optional

if __name__ == "__main__":
    check_users("./Data/r_ChatGPT_posts.jsonl")
    check_users("./Data/r_ClaudeAI_posts.jsonl")
    check_users("./Data/r_Bard_posts.jsonl")

