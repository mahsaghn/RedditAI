import json
import itertools
import networkx as nx

nodes = []
edges = []
user_activities = {}

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
        if 'ClaudeAI' in user_activities[user]:
            type |= 2

        nodes.append({"id": user, "label" : user, "type" : type})

for (user1, subreddits1), (user2, subreddits2) in itertools.combinations(user_activities.items(), 2):
    intersection = len(subreddits1 & subreddits2)
    if intersection > 0:
        edges.append({"source" : user1, "target" : user2, "weight" : intersection})

G = nx.Graph()
# Add nodes with attributes
for n in nodes:
    G.add_node(n["id"], label=n.get("label", n["id"]), type=n.get("type"))

# Add weighted edges
for e in edges:
    G.add_edge(e["source"], e["target"], weight=float(e.get("weight", 1.0)))

# Save to GEXF
nx.write_gexf(G, "graph.gexf")

print("✅ Wrote graph.gexf (undirected)")