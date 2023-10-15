import csv
import json
import logging
import os
import re
from datetime import datetime

import requests

# 准备 Github Tokens
tokens = []
currentTokenIndex = 0
GithubToken = tokens[currentTokenIndex]
header = {
    'X-GitHub-Api-Version': '2022-11-28',
    'Authorization': "Bearer " + GithubToken
}

logging.basicConfig(level=logging.INFO)

issue_path = "../Data/multi/issues-2020-2023.txt"


def read_json_array_from_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read()
        # 使用 json.loads 解析为 JSON 对象列表
        json_array = json.loads(data)
        return json_array


def filter_issues_by_time_range(issues, start_time, end_time):
    filtered_issues = []
    for issue in issues:
        updated_at = datetime.strptime(issue['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        if start_time <= updated_at <= end_time:
            filtered_issues.append(issue)
    return filtered_issues


closed_issues = read_json_array_from_file(issue_path)
# 设定时间范围
start_time = datetime(2021, 1, 1, 0, 0, 0)
end_time = datetime(2022, 1, 1, 0, 0, 0)

# 进行时间筛选
filtered_issues = filter_issues_by_time_range(closed_issues, start_time, end_time)


def fetch_events(events_url):
    params = {
        'per_page': 100,
        'page': 1,
    }
    events = []

    while True:
        response = requests.get(events_url, params=params, headers=header)
        if response.status_code != 200:
            logging.error(f"Failed to fetch events. Status code: {response.status_code}")
            break

        fetched_events = response.json()
        events.extend(fetched_events)

        # Check if there are more pages
        link_header = response.headers.get('Link', '')
        if 'rel="next"' not in link_header:
            break

        # Increment the page number
        params['page'] += 1

    return events


def calculate_bug_duration(issue):
    created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    closed_at = datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
    bug_duration = (closed_at - created_at).days
    return bug_duration


def select_priority_label(issue):
    if any(label['name'].startswith("P-") for label in issue['labels']):
        priority = next((label for label in issue['labels'] if label['name'].startswith("P-")), None)['name']
        return priority
    return None


with open("../Data/single/results-2021.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['Issue ID', 'Issue URL', 'Issue Title', 'Issue create date', 'Issue closed date',
                     'PR ID', 'PR URL', 'PR Title', 'PR create date', 'PR closed date', 'Bug duration',
                     'Fix loc', 'Fix files', 'Fix modules', 'Bug priority', 'Reopen?'])

    for issue in filtered_issues:
        issue_id = issue['number']
        issue_url = issue['html_url']
        issue_title = issue['title']
        bug_duration = calculate_bug_duration(issue)
        priority = select_priority_label(issue)

        events = fetch_events(issue['events_url'])

        reopen = 0
        pr_id = None
        pr_url = None
        pr_title = None
        pr_created_at = None
        pr_closed_at = None
        fix_loc = None
        fix_files = None
        fix_modules = None

        for event in events:
            if event['event'] == 'reopened':
                reopen = 1
                break

        event = None
        for item in events[::-1]:
            if item['event'] == 'closed':
                event = item
                break
        try:
            if event['commit_id']:
                response = requests.get(
                    "https://api.github.com/repos/rust-lang/rust/commits/" + event['commit_id'],
                    headers=header)
                data = json.loads(response.text)

                commit_msg = data['commit']['message']
                fix_loc = data['stats']['total']
                fix_files = []
                fix_modules = []
                for file in data['files']:
                    directory, name = os.path.split(file['filename'])
                    fix_files.append(name)
                    fix_modules.append(directory)

                pattern = r"merge of #(\d+)"
                match = re.search(pattern, commit_msg, re.IGNORECASE)

                if match:
                    pr_id = match.group(1)
                    pr_url = 'https://github.com/rust-lang/rust/pull/' + str(pr_id)
                    response = requests.get("https://api.github.com/repos/rust-lang/rust/pulls/"
                                            + str(pr_id), headers=header)
                    data = json.loads(response.text)

                    pr_title = data['title']
                    pr_created_at = datetime.strptime(data['created_at'],
                                                      "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
                    pr_closed_at = datetime.strptime(data['closed_at'],
                                                     "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
                    bug_duration = (datetime.strptime(pr_closed_at, "%Y-%m-%d %H:%M") -
                                    datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')).days
        except Exception as e:
            print(e)
            print(issue_id)

        writer.writerow(
            [issue_id if issue_id else "", issue_url if issue_url else "", issue_title if issue_title else "",
             issue['created_at'], issue['closed_at'],
             pr_id if pr_id else "", pr_url if pr_url else "",
             pr_title if pr_title else "", pr_created_at if pr_created_at else "",
             pr_closed_at if pr_closed_at else "",
             bug_duration if bug_duration else "", fix_loc if fix_loc else "", fix_files if fix_files else "",
             fix_modules if fix_modules else "", priority if priority else "", reopen if reopen else ""])
