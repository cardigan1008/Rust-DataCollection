import argparse
import logging

from crawler.IssueCrawler import IssueCrawler
from crawler.PrCrawler import PrCrawler
from util.FileMerger import FileMerger


def issue_cmd(args):
    logging.info("Collect issues.")
    issue_crawler = IssueCrawler(args.output_path, args.token)
    issue_crawler.crawl_issues()


def pr_cmd(args):
    logging.info("Collect pull requests.")
    pr_crawler = PrCrawler(args.input_path, args.output_path, args.token)
    pr_crawler.crawl_prs()


def merge_files_cmd(args):
    logging.info("Merge CSV files.")
    file_merger = FileMerger(args.input_directory, args.output_file)
    file_merger.merge_files()


def parse_and_run():
    parser = argparse.ArgumentParser(description='A web crawler tool to collect issues and their associated pull '
                                                 'requests (PRs) from Rust repositories.')
    subparsers = parser.add_subparsers(dest='operation', help='Operation to perform')

    issue_crawler = subparsers.add_parser('issue', help='Collect issues.')
    issue_crawler.add_argument('output_path', help='Output path for the collected issues.')
    issue_crawler.add_argument("token", help='Github token for authentication.')
    issue_crawler.set_defaults(func=issue_cmd)

    pr_crawler = subparsers.add_parser('pr', help='Collect pull requests.')
    pr_crawler.add_argument("input_path", help='Input path for the pull requests to be collected.')
    pr_crawler.add_argument('output_path', help='Output path for the collected pull requests.')
    pr_crawler.add_argument("token", help='Github token for authentication.')
    pr_crawler.set_defaults(func=pr_cmd)

    merge_parser = subparsers.add_parser('merge', help='Merge CSV files.')
    merge_parser.add_argument('input_directory', help='Directory containing CSV files to merge.')
    merge_parser.add_argument('output_file', help='Output CSV file path for the merged data.')
    merge_parser.set_defaults(func=merge_files_cmd)

    args = parser.parse_args()
    args.func(args)
