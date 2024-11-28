import csv
import json
from datetime import datetime

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

    def crawl_prs(self):
        pr_ids = []

        with open(self.pr_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0]:
                    pr_ids.append(row[0])

        with open(self.output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['PR ID', 'PR URL', 'PR Title', 'PR create date', 'PR closed date'])

            for pr_id in tqdm(pr_ids, desc="Processing PRs"):
                pr_data = self.fetch_pr(pr_id)

                pr_url = pr_data['html_url']
                pr_title = pr_data['title']
                pr_created_at = datetime.strptime(pr_data['created_at'], "%Y-%m-%dT%H:%M:%SZ").strftime(
                    "%Y-%m-%d %H:%M")
                pr_closed_at = datetime.strptime(pr_data['closed_at'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")

                writer.writerow([pr_id, pr_url, pr_title, pr_created_at, pr_closed_at])
