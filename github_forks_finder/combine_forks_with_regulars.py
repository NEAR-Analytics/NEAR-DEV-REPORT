import os
import json
import requests

ec_csv_near_dev_profiles = 'github_devs_EC/ec_csv_near_dev_profiles.json'
ec_near_dev_profiles = 'github_devs_EC/ec_near_dev_profiles.json'
csv_contributors = 'github_devs_EC/csv_contributors.json'

search_q_near_dev_profiles = 'github_devs_y3k/search_q_near_dev_profiles.json'

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




# Function to find keys with empty values
def find_valid_repos(dictionary):
    valid_repos = []
    for key, value in dictionary.items():
        if value:  # This checks if the value is an empty list
            valid_repos.append(key)
    return valid_repos

valid_repos = find_valid_repos(combined_dict)



# load all repo urls:
with open("fork_urls_list.json", "r") as f:
    fork_urls_list = json.load(f)

# how to combine two lists:
valid_repos = fork_urls_list + valid_repos

