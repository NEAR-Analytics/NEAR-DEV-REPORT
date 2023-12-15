import os
import json
import time
from commit_helper import *

token1 = os.environ["token1"]
token2 = os.environ["token2"]
token3 = os.environ["token3"]

ACCESS_TOKENS = [token1, token2, token3]  # Replace with actual tokens


main_path = '../'

ec_csv_near_dev_profiles = main_path + 'github_devs_EC/ec_csv_near_dev_profiles.json'
ec_near_dev_profiles = main_path + 'github_devs_EC/ec_near_dev_profiles.json'
csv_contributors = main_path + 'github_devs_EC/csv_contributors.json'
search_q_near_dev_profiles = main_path + 'github_devs_y3k/search_q_near_dev_profiles.json'

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


# load all repo urls:
with open("github_forks_finder/fork_urls_list.json", "r") as f:
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



# checkpoint restore:
with open("repo_commit_data.json", "r") as f:
    repo_data = json.load(f)



for REPO_URL in NEAR_REPOS_ALL_UNIQ:
    if REPO_URL in repo_data:
        print("Skipping", REPO_URL)
        continue
    print("Fetching data for", REPO_URL)
    time.sleep(1)
    fetcher = GithubRepoDataFetcher(REPO_URL, ACCESS_TOKENS)
    data = fetcher.fetch_repo_data()
    repo_data[REPO_URL] = data


# save repo_data to a json file:
# open a file in write mode
with open("repo_commit_data.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(repo_data, f)