import csv
import json
from datetime import datetime
import logging
import os

import requests
from tqdm import tqdm


class PrCrawler:
    def __init__(self, pr_path, output_path, token):
        self.token = token
        self.header = {
            'X-GitHub-Api-Version': '2022-11-28',
            'Authorization': "Bearer " + self.token
        }
        self.pr_path = pr_path
        self.output_path = output_path

    def fetch_pr(self, pr_id):
        response = requests.get("https://api.github.com/repos/rust-lang/rust/pulls/" + pr_id, headers=self.header)
        return json.loads(response.text)
    
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

    def crawl_prs(self):
        pr_ids = []

        with open(self.pr_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0]:
                    pr_ids.append(row[0])

        with open(self.output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['PR ID', 'PR URL', 'PR Title', 'PR create date', 'PR closed date', 'Fix loc', 'Fix files', 'Fix modules'])

            for pr_id in tqdm(pr_ids, desc="Processing PRs"):
                pr_data = self.fetch_pr(pr_id)

                pr_url = pr_data['html_url']
                pr_title = pr_data['title']
                pr_created_at = datetime.strptime(pr_data['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime(
                    "%Y-%m-%d %H:%M")
                pr_closed_at = datetime.strptime(pr_data['closed_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")

                merge_commit_sha = pr_data['merge_commit_sha']
                _, fix_loc, fix_files, fix_modules = self.process_commit_data(merge_commit_sha)

                writer.writerow([pr_id, pr_url, pr_title, pr_created_at, pr_closed_at, fix_loc, fix_files, fix_modules])
