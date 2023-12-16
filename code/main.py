import logging
import coloredlogs

from command import parse_and_run

coloredlogs.install(level='INFO', fmt='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logging.info("Start to collect!")
    parse_and_run()


if __name__ == '__main__':
    main()
