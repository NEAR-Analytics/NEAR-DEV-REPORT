import requests
import json
import os
ACCESS_TOKEN = os.environ["GITHUB_TOKEN"]


def get_forks(repo_url, access_token):
    repo_parts = repo_url.replace("https://github.com/", "").split("/")
    api_url = f"https://api.github.com/repos/{repo_parts[0]}/{repo_parts[1]}/forks"
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }



    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            response.raise_for_status()
            forks = response.json()
            return [fork['html_url'] for fork in forks]
        elif response.status_code == 403:
            # break loop if we hit the rate limit
            print("Hit rate limit")
            return 403
        else:
            print(f"Failed to fetch contributors for {repo_url}. Status Code: {response.status_code}")
            print(response.text)
            return []

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err} - URL: {api_url}")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return []


def find_valid_repos(dictionary):
    valid_repos = []
    for key, value in dictionary.items():
        if value:  # This checks if the value is an empty list
            valid_repos.append(key)
    return valid_repos


# load all repo urls:
with open("valid_repos_devs_final.json", "r") as f:
    all_repos = json.load(f)

valid_repos = find_valid_repos(all_repos)

fork_urls_dict = {}

for orig_url in valid_repos:
    if orig_url in fork_urls_dict:
        continue
    fork_urls = get_forks(orig_url, ACCESS_TOKEN)
    fork_urls_dict[orig_url] = fork_urls

# save fork_urls_dict to a json file:
# open a file in write mode
with open("fork_urls_dict.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(fork_urls_dict, f)


combined_list = []
for key, values in fork_urls_dict.items():
    combined_list.extend(values)

# save forks to a json file:
# open a file in write mode
with open("fork_urls_list.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(combined_list, f)