import json

import requests
import logging

# 准备 Github Token
tokens = []
currentTokenIndex = 0
GithubToken = tokens[currentTokenIndex]
header = {
    'X-GitHub-Api-Version': '2022-11-28',
    'Authorization': "Bearer " + GithubToken
}

logging.basicConfig(level=logging.INFO)
file_path = "../Data/multi/issues-2020-2023.txt"


def fetch_issues():
    base_url = 'https://api.github.com/repos/rust-lang/rust/issues'
    params = {
        'state': 'closed',
        'per_page': 100,
        'page': 1,
        'labels': 'T-Compiler',
        'since': '2020-01-01T00:00:00Z',
    }
    issues = []

    while True:
        response = requests.get(base_url, headers=header, params=params)
        if response.status_code != 200:
            logging.error(f"Failed to fetch issues. Status code: {response.status_code}")
            break

        fetched_issues = response.json()

        # Filter out items with non-null "pull_request" field
        filtered_issues = [issue for issue in fetched_issues if issue.get('pull_request') is None]

        issues.extend(filtered_issues)
        logging.info(f"Fetched {len(issues)} filtered issues")

        # Check if there are more pages
        link_header = response.headers.get('Link', '')
        if 'rel="next"' not in link_header:
            break

        # Increment the page number
        params['page'] += 1

    return issues


def write_issues_to_file(issues, file_path):
    with open(file_path, 'w') as file:
        json.dump(issues, file)

    logging.info(f"Issues written to {file_path}")


if __name__ == '__main__':
    issues = fetch_issues()
    write_issues_to_file(issues, file_path)
