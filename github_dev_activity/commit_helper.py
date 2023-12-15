import os
import json
import requests
import time
from itertools import cycle

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