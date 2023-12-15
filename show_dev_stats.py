import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
import json


# checkpoint restore:
with open("github_dev_activity/repo_commit_data.json", "r") as f:
    repo_data = json.load(f)


dev_activity = {}
repo_activity = {}

# Process each repository and contributor
for repo, repo_data in repo_data.items():
    repo_activity[repo] = {'commits': 0, 'lines_added': 0, 'lines_removed': 0}
    contributors = repo_data.get('contributors', {})

    for dev, commits in contributors.items():
        if dev not in dev_activity:
            dev_activity[dev] = {'commits': 0, 'lines_added': 0, 'lines_removed': 0}

        for commit in commits:
            dev_activity[dev]['commits'] += 1
            dev_activity[dev]['lines_added'] += commit['added']
            dev_activity[dev]['lines_removed'] += commit['removed']

            repo_activity[repo]['commits'] += 1
            repo_activity[repo]['lines_added'] += commit['added']
            repo_activity[repo]['lines_removed'] += commit['removed']

# Convert to DataFrame for easy plotting
dev_df = pd.DataFrame.from_dict(dev_activity, orient='index')
repo_df = pd.DataFrame.from_dict(repo_activity, orient='index')

# Plotting
# Popular Developers based on commit count
plt.figure(figsize=(10, 6))
dev_df.sort_values(by='commits', ascending=False).head(10).plot(kind='bar', y='commits', title='Popular Developers by Commit Count')
plt.show()

# Popular Repositories based on commit count
plt.figure(figsize=(10, 6))
repo_df.sort_values(by='commits', ascending=False).head(10).plot(kind='bar', y='commits', title='Popular Repositories by Commit Count')
plt.show()