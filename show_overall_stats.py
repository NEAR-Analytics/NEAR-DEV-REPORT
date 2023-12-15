import os
import json
from github_dev_activity.commit_helper import *
import matplotlib.pyplot as plt
import pandas as pd


main_path = './'

ec_csv_near_dev_profiles = main_path + 'github_devs_EC/ec_csv_near_dev_profiles.json'
ec_near_dev_profiles = main_path + 'github_devs_EC/ec_near_dev_profiles.json'
csv_contributors = main_path + 'github_devs_EC/csv_contributors.json'
search_q_near_dev_profiles = main_path + 'github_devs_y3k/search_q_near_dev_profiles.json'

forks_list = main_path + 'github_forks_finder/fork_urls_list.json'


# load existing data:
with open(ec_csv_near_dev_profiles, "r") as f:
    org_devs = json.load(f)

with open(ec_near_dev_profiles, "r") as f:
    ec_repo_devs = json.load(f)

with open(csv_contributors, "r") as f:
    ext_csv_devs = json.load(f)


with open(search_q_near_dev_profiles, "r") as f:
    q_csv_devs = json.load(f)

combined_dict = {**org_devs, **ec_repo_devs, **ext_csv_devs, **q_csv_devs}


with open(forks_list, "r") as f:
    fork_urls_list = json.load(f)




repos_combined = find_valid_repos(combined_dict)
NEAR_REPOS_ALL = repos_combined + fork_urls_list

NEAR_REPOS_ALL_UNIQ = set(NEAR_REPOS_ALL)

print("ec_org_devs : ", len(org_devs))
print("ec_repo_devs : ", len(ec_repo_devs))
print("ec_ext_csv_devs : ", len(ext_csv_devs))
print("y3k_q_csv_devs : ", len(q_csv_devs))
print("--------------------")
print("repos_combined : ", len(repos_combined))
print("fork_repos : ", len(fork_urls_list))
print("repos_combined + fork_repos : ", len(NEAR_REPOS_ALL_UNIQ))






# Data from your script
data = {
    "ec_org_devs": len(org_devs),
    "ec_repo_devs": len(ec_repo_devs),
    "ec_ext_csv_devs": len(ext_csv_devs),
    "y3k_q_csv_devs": len(q_csv_devs),
    "repos_combined": len(repos_combined),
    "fork_repos": len(fork_urls_list),
    "combined_repos": len(NEAR_REPOS_ALL_UNIQ)
}

# Convert data to a pandas DataFrame for easy plotting
df = pd.DataFrame(list(data.items()), columns=['Category', 'Count'])

# Plotting
plt.figure(figsize=(10, 6))
bars = plt.bar(df['Category'], df['Count'], color='blue')

# Adding the count above each bar
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval, int(yval), ha='center', va='bottom')

plt.xlabel('Categories')
plt.ylabel('Counts')
plt.title('Developer and Repository Counts')
plt.xticks(rotation=45)
plt.tight_layout()

# Show the plot
plt.show()

