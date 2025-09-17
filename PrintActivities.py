import json
import itertools
import networkx as nx

user_activities = {}
open("raw_graph.txt", 'w').close()

with open("users_activities.jsonl", 'r') as file:
    for line in file:
        line_data = json.loads(line)
        user = list(line_data.keys())[0]
        if user in user_activities:
            continue
        posts = list(line_data.values())[0]
        user_activities[user] = set()
        for post in posts:
            user_activities[user].add(post['subreddit'])

        type  = 0
        if 'ChatGPT' in user_activities[user]:
            type |= 1
            user_activities[user].remove('ChatGPT')
        if 'ClaudeAI' in user_activities[user]:
            type |= 2
            user_activities[user].remove('ClaudeAI')


        if len(user_activities[user]) < 1:
            continue

        with open("raw_graph.txt", 'a') as f:
            f.write(f'{user},{type}')
            for subreddits in user_activities[user]:
                f.write(f',{subreddits}')
            f.write('\n')


