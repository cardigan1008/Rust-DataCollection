import csv
import json
import logging
import os
import re
from datetime import datetime
import requests
from tqdm import tqdm


def calculate_bug_duration(issue):
    created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    closed_at = datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
    return (closed_at - created_at).days


def select_priority_label(issue):
    priority_label = next((label for label in issue['labels'] if label['name'].startswith("P-")), None)
    return priority_label['name'] if priority_label else None


def filter_issues_by_date(issues, start_time, end_time):
    return [issue for issue in issues if
            start_time <= datetime.strptime(issue['updated_at'], '%Y-%m-%dT%H:%M:%SZ') <= end_time]


class IssueDataProcessor:
    def __init__(self, output_path, token, issues):
        self.token = token
        self.GithubToken = self.token
        self.header = {'Authorization': "Bearer " + self.GithubToken}
        self.issues = issues
        self.output_path = output_path

    def fetch_events(self, events_url):
        params = {
            'per_page': 100,
            'page': 1,
        }
        events = []

        while True:
            response = requests.get(events_url, params=params, headers=self.header)
            if response.status_code != 200:
                logging.error(f"Failed to fetch events. Status code: {response.status_code}")
                break

            fetched_events = response.json()
            events.extend(fetched_events)

            link_header = response.headers.get('Link', '')
            if 'rel="next"' not in link_header:
                break

            params['page'] += 1

        return events

    def process_commit_data(self, commit_id):
        response = requests.get(
            f"https://api.github.com/repos/rust-lang/rust/commits/{commit_id}",
            headers=self.header)

        if not response.ok:
            logging.error(f"Failed to fetch commit data for {commit_id}. Status code: {response.status_code}")
            return None

        data = json.loads(response.text)
        commit_msg = data['commit']['message']
        fix_loc = data['stats']['total']
        fix_files = [os.path.split(file['filename'])[1] for file in data['files']]
        fix_modules = [os.path.split(file['filename'])[0] for file in data['files']]

        return commit_msg, fix_loc, fix_files, fix_modules

    def extract_pull_request_info(self, commit_msg):
        pattern = r"merge of #(\d+)"
        match = re.search(pattern, commit_msg, re.IGNORECASE)
        if match:
            pr_id = match.group(1)
            return pr_id
        else:
            # print("No PR ID found in commit message.")
            return None

    def fetch_pr_data(self, pr_id):
        url = f"https://api.github.com/repos/rust-lang/rust/pulls/{pr_id}"

        response = requests.get(url, headers=self.header)
        if response.ok:
            return json.loads(response.text)
        else:
            return None

    def process_issue(self, issue):
        issue_id = issue['number']
        issue_url = issue['html_url']
        issue_title = issue['title']
        bug_duration = calculate_bug_duration(issue)
        priority = select_priority_label(issue)

        events = self.fetch_events(issue['events_url'])
        reopen = 1 if any(event['event'] == 'reopened' for event in events) else 0

        closing_event = next((item for item in reversed(events) if item['event'] == 'closed'), None)

        pr_id = ""
        pr_url = ""
        pr_title = ""
        pr_created_at = ""
        pr_closed_at = ""
        fix_loc = ""
        fix_files = ""
        fix_modules = ""

        if closing_event['commit_id'] and 'commit_id' in closing_event:
            commit_msg, fix_loc, fix_files, fix_modules = self.process_commit_data(closing_event['commit_id'])

            if self.process_commit_data(closing_event['commit_id']):
                pr_id_match = self.extract_pull_request_info(commit_msg)
            if pr_id_match:
                pr_data = self.fetch_pr_data(pr_id_match)
                if pr_data:
                    pr_id = pr_id_match
                    pr_url = pr_data['html_url']
                    pr_title = pr_data['title']
                    pr_created_at = datetime.strptime(pr_data['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime(
                        "%Y-%m-%d %H:%M")
                    pr_closed_at = datetime.strptime(pr_data['closed_at'], "%Y-%m-%dT%H:%M:%SZ").strftime(
                        "%Y-%m-%d %H:%M")
                    bug_duration = (datetime.strptime(pr_closed_at, "%Y-%m-%d %H:%M") -
                                    datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')).days
            
        return [issue_id, issue_url, issue_title, issue['created_at'], issue['closed_at'],
                pr_id, pr_url, pr_title, pr_created_at, pr_closed_at, bug_duration,
                fix_loc, fix_files, fix_modules, priority, reopen]

    def process_issues(self):
        start_time = datetime(2023, 10, 1, 0, 0, 0)
        end_time = datetime(2024, 10, 31, 0, 0, 0)
        filtered_issues = filter_issues_by_date(self.issues, start_time, end_time)

        with open(self.output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['Issue ID', 'Issue URL', 'Issue Title', 'Issue create date', 'Issue closed date',
                             'PR ID', 'PR URL', 'PR Title', 'PR create date', 'PR closed date', 'Bug duration',
                             'Fix loc', 'Fix files', 'Fix modules', 'Bug priority', 'Reopen?'])

            for issue in tqdm(filtered_issues, desc="Processing Issues"):
                issue_data = self.process_issue(issue)
                writer.writerow(issue_data)
