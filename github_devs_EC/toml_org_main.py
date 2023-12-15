import requests
import os
import json
import toml

token = os.environ["GITHUB_TOKEN"]


def get_org_repos(org_url, token):
    api_url = org_url.replace("https://github.com/", "https://api.github.com/orgs/") + "/repos"
    headers = {'Authorization': f'token {token}'}
    repos = []

    while True:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            repos.extend(response.json())
            # Check if there is a next page
            if 'next' in response.links.keys():
                api_url = response.links['next']['url']
            else:
                break
        elif response.status_code == 403:
            print("Hit rate limit")
            break
        else:
            print(f"Failed to fetch repositories for {org_url}. Status Code: {response.status_code}")
            print(response.text)
            break

    return [repo['html_url'] for repo in repos]


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



def load_repos_from_toml(file_path):
    with open(file_path, "r") as file:
        data = toml.load(file)
        return [repo['url'] for repo in data.get('repo', [])]


def load_github_orgs_from_toml(file_path):
    with open(file_path, 'r') as file:
        data = toml.load(file)
        return data.get('github_organizations', [])


# Replace with the path to your TOML file
file_path = 'near.toml'
# toml_repositories = load_repos_from_toml(file_path)

org_urls = load_github_orgs_from_toml(file_path)

# load existing data:
# with open("github_devs_EC/ec_csv_near_dev_profiles.json", "r") as f:
#     toml_contributors = json.load(f)


all_repos = []
for org_url in org_urls:
    org_repos = get_org_repos(org_url, token)
    all_repos.extend(org_repos)

# save all_repos to a json file:
# open a file in write mode
with open("csv_repos.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(all_repos, f)



toml_contributors = {}

for repo in all_repos:
    if repo in toml_contributors:
        print("Skipping", repo)
        continue
    contributors = get_contributors(repo, token)
    if contributors == 403:
        print("Hit rate limit. Stopping.")
        break
    toml_contributors[repo] = contributors



# save all_contributors to a json file:
# open a file in write mode
with open("ec_csv_near_dev_profiles.json", "w") as f:
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