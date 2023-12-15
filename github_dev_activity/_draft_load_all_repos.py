import os
import json
import requests
from time import sleep

import time
from itertools import cycle

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


# load all repo urls:
with open("github_forks_finder/fork_urls_list.json", "r") as f:
    fork_urls_list = json.load(f)


# Function to find keys with empty values
def find_valid_repos(dictionary):
    valid_repos = []
    for key, value in dictionary.items():
        if value:  # This checks if the value is an empty list
            valid_repos.append(key)
    return valid_repos



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


# Function to find keys with empty values
def find_empty_values(dictionary):
    empty_keys = []
    for key, value in dictionary.items():
        if not value:  # This checks if the value is an empty list
            empty_keys.append(key)
    return empty_keys


# Function to find keys with empty values
def find_valid_repos(dictionary):
    valid_repos = []
    for key, value in dictionary.items():
        if value:  # This checks if the value is an empty list
            valid_repos.append(key)
    return valid_repos

valid_repos = find_valid_repos(combined_dict)

# save combined_dict to a json file:
# open a file in write mode

# with open("valid_repos_devs_final.json", "w") as f:
#     # write the dictionary to the file in JSON format
#     json.dump(combined_dict, f)

# Use the function and print the result
# empty_keys = find_empty_values(combined_dict)
# print("Keys with empty values:", empty_keys)



class GithubRepoDataFetcher:
    BASE_URL = "https://api.github.com/repos"

    def __init__(self, repo_url: str, access_tokens: list):
        self.repo_url = repo_url
        self.access_tokens = cycle(access_tokens)  # Use itertools.cycle for rotating tokens
        self.set_next_token()

    def set_next_token(self):
        # Rotate to the next token
        self.access_token = next(self.access_tokens)
        self.headers = {
            "Authorization": f"token {self.access_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def parse_repo_url(self):
        parts = self.repo_url.replace("https://github.com/", "").split("/")
        return parts[0], parts[1]  # Returns owner, repo

    def fetch_repo_data(self):
        owner, repo = self.parse_repo_url()
        api_repo_url = f"{self.BASE_URL}/{owner}/{repo}"
        contributor_data = {}

        try:
            contributors_url = f"{api_repo_url}/contributors"
            contributors_resp = self.make_request(contributors_url)
            contributors = contributors_resp.json()

            for contributor in contributors:
                commits_url = f"{api_repo_url}/commits?author={contributor['login']}"
                commits_resp = self.make_request(commits_url)
                commits = commits_resp.json()
                commit_data = []

                for commit in commits:
                    detailed_commit_url = f"{api_repo_url}/commits/{commit['sha']}"
                    detailed_commit_resp = self.make_request(detailed_commit_url)
                    detailed_commit = detailed_commit_resp.json()
                    commit_data.append({
                        "timestamp": detailed_commit["commit"]["author"]["date"],
                        "added": detailed_commit["stats"]["additions"],
                        "removed": detailed_commit["stats"]["deletions"],
                    })

                contributor_data[contributor["login"]] = commit_data

        except Exception as e:
            print(f"Error: {e}")
            return {}

        return {
            "contributors": contributor_data
        }

    def make_request(self, url):
        # Introduce delay to avoid hitting rate limit
        time.sleep(1)  # Sleep for 1 second; adjust as needed
        response = requests.get(url, headers=self.headers)
        if response.status_code == 403:  # Rate limit exceeded
            print("Switching tokens due to rate limit...")
            self.set_next_token()
            return self.make_request(url)
        response.raise_for_status()
        return response

token1 = os.environ["token1"]
token2 = os.environ["token2"]
token3 = os.environ["token3"]

ACCESS_TOKENS = [token1, token2, token3]  # Replace with actual tokens

# repo_data = {}
# load json:


# with open("valid_repos_devs_final.json", "r") as f:
#     valid_repos = json.load(f)

### load all repo urls:

combined_dict = {**org_devs, **ec_repo_devs, **ext_csv_devs, **q_csv_devs}

valid_repos = find_valid_repos(combined_dict)

# load all repo urls:
with open("github_forks_finder/fork_urls_list.json", "r") as f:
    fork_urls_list = json.load(f)

# how to combine two lists:
valid_repos = fork_urls_list + valid_repos

valid_repos = list(set(valid_repos))



with open("repo_commit_data.json", "r") as f:
    repo_data = json.load(f)

# remove value if it's does not contain "contributors":
# for key, value in repo_data.copy().items():
#     if 'contributors' not in value:
#         print("Removing", repo_data[key])
#         del repo_data[key]


for REPO_URL in valid_repos:
    if REPO_URL in repo_data:
        print("Skipping", REPO_URL)
        continue
    print("Fetching data for", REPO_URL)
    sleep(1.5)
    fetcher = GithubRepoDataFetcher(REPO_URL, ACCESS_TOKENS)
    data = fetcher.fetch_repo_data()
    repo_data[REPO_URL] = data


# save repo_data to a json file:
# open a file in write mode
with open("repo_commit_data.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(repo_data, f)