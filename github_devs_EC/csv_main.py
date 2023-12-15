import requests
import os
import json
import toml
import csv



def load_csv_to_dict(file_path):
    data_dict = {}
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Use 'link' as the key and the rest of the row as the value
            key = row.pop('link')
            data_dict[key] = row
    return data_dict

token = os.environ["GITHUB_TOKEN"]

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


# Replace 'your_file.csv' with the path to your CSV file
file_path = 'NEAR_added_repos_since_June2023.csv'

# Call the function and print the resulting dictionary
csv_repositories = list(load_csv_to_dict(file_path).keys())

# # load existing data:
# with open("github_devs_EC/ec_near_dev_profiles.json", "r") as f:
#     toml_contributors = json.load(f)

# since we are reusing a check-pointed file, we need to remove the repos that have already been processed:
csv_contributors = {}

for repo in csv_repositories:
    if repo in csv_contributors:
        print("Skipping", repo)
        continue
    contributors = get_contributors(repo, token)
    if contributors == 403:
        print("Hit rate limit. Stopping.")
        break
    csv_contributors[repo] = contributors





# save all_contributors to a json file:
# open a file in write mode
with open("csv_contributors.json", "w") as f:
    # write the dictionary to the file in JSON format
    json.dump(csv_contributors, f)







# Function to find keys with empty values
def find_empty_values(dictionary):
    empty_keys = []
    for key, value in dictionary.items():
        if not value:  # This checks if the value is an empty list
            empty_keys.append(key)
    return empty_keys

# Use the function and print the result
empty_keys = find_empty_values(csv_contributors)
print("Keys with empty values:", empty_keys)