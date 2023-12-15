import requests
import os
import json
import toml

token = os.environ["GITHUB_TOKEN"]


def get_repositories(search_query, token):
    url = f"https://api.github.com/search/code?q={search_query}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json()["items"]
        repos = set()
        for item in results:
            repo_url = item["repository"]["html_url"]
            repos.add(repo_url)
        return repos
    else:
        print(f"Failed to fetch code search results. Status Code: {response.status_code}")
        print(response.text)
        return set()

def get_contributors(repo_url, token):
    api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + "/contributors"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        contributors = response.json()
        return [contributor["login"] for contributor in contributors]
    elif response.status_code == 403:
        # break loop if we hit the rate limit
        print("Hit rate limit")
        return 403
    else:
        print(f"Failed to fetch contributors for {repo_url}. Status Code: {response.status_code}")
        print(response.text)
        return []

# Replace these with your actual query and token
search_query = "near-sdk&type=code"
search_query = "use+near_sdk+language%3ARust"

repositories = get_repositories(search_query, token)


all_contributors = {}

for repo in repositories:
    contributors = get_contributors(repo, token)
    all_contributors[repo] = contributors

# save all_contributors to a json file:
# open a file in write mode
with open("search_q_near_dev_profiles.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(all_contributors, f)




def load_repos_from_toml(file_path):
    with open(file_path, "r") as file:
        data = toml.load(file)
        return [repo['url'] for repo in data.get('repo', [])]

# Replace with the path to your TOML file
file_path = 'github_devs_EC/near.toml'
toml_repositories = load_repos_from_toml(file_path)
# load existing data:
with open("github_devs_EC/ec_near_dev_profiles.json", "r") as f:
    toml_contributors = json.load(f)

toml_contributors = {}

for repo in toml_repositories:
    if repo in toml_contributors:
        print("Skipping", repo)
        continue
    contributors = get_contributors(repo, token)
    if contributors == 403:
        print("Hit rate limit. Stopping.")
        break
    toml_contributors[repo] = contributors


new_list = []
for repo in toml_repositories:
    if repo not in toml_contributors:
        new_list.append(repo)



# save all_contributors to a json file:
# open a file in write mode
with open("github_devs_EC/ec_near_dev_profiles.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(toml_contributors, f)







# Function to find keys with empty values
def find_empty_values(dictionary):
    empty_keys = []
    for key, value in dictionary.items():
        if not value:  # This checks if the value is an empty list
            empty_keys.append(key)
    return empty_keys

# Use the function and print the result
empty_keys = find_empty_values(toml_contributors)
print("Keys with empty values:", empty_keys)