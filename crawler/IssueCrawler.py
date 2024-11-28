from util.IssueDataCrawler import IssueDataCrawler
from util.IssueDataProcessor import IssueDataProcessor


class IssueCrawler:
    def __init__(self, output_path, token):
        self.output_path = output_path
        self.token = token

    def crawl_issues(self):
        data_crawler = IssueDataCrawler(self.output_path, self.token)
        issues = data_crawler.fetch_issues_data()
        data_processor = IssueDataProcessor(self.output_path, self.token, issues)
        data_processor.process_issues()
