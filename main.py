import os
import multiprocessing
import threading
from typing import List
import logging

import dotenv

from track_twitter_tgbot.bot import run_bot
from track_twitter_tgbot.scraper import scrape
from conf import ACCOUNTS_FILES, THREADS, PROCESSES

dotenv.load_dotenv(dotenv.find_dotenv())


def scrape_tweets(
    accounts: list, queue: multiprocessing.Queue
) -> List[threading.Thread]:
    """
    Start threads to get tweets to put in queue.

    :param accounts: List of accounts to poll for recent tweets.
    :param queue: multiprocessing.Queue object to put scraped tweets in.
    """
    per_t = round(len(accounts) / THREADS)
    scraper_threads = []
    for i in range(THREADS - 1):
        scraper_threads.append(
            threading.Thread(
                target=scrape, args=(accounts[i * per_t : (i + 1) * per_t], queue)
            )
        )
    scraper_threads.append(
        threading.Thread(
            target=scrape,
            args=(accounts[(THREADS - 1) * per_t : ((THREADS)) * per_t], queue),
        )
    )
    for thread in scraper_threads:
        thread.start()
    return scraper_threads


def orchestrate_scrapers(
    accounts: list, queue: multiprocessing.Queue
) -> List[multiprocessing.Process]:
    """
    Create `PROCESSES` processes with accounts divides 'equally' among them
    for running scrapers.

    :param accounts: List of accounts to poll for recent tweets.
    """
    scraper_processes = []
    per_p = round(len(accounts) / PROCESSES)
    for i in range(PROCESSES - 1):
        scraper_processes.append(
            multiprocessing.Process(
                target=scrape, args=(accounts[i * per_p : (i + 1) * per_p], queue)
            )
        )
    scraper_processes.append(
        multiprocessing.Process(
            target=scrape, args=(accounts[(PROCESSES - 1) * per_p :], queue)
        )
    )
    return scraper_processes


if __name__ == "__main__":
    # All non empty lines in `ACCOUNTS_FILES` are usernames
    queue = multiprocessing.Queue()
    accounts = [i for i in open(ACCOUNTS_FILES).read().split("\n") if i]
    processes = orchestrate_scrapers(accounts, queue)

    try:
        # Launch processes
        for process in processes:
            process.start()

        # Credentials are stored as environment variables.
        run_bot(queue, os.environ)
    except KeyboardInterrupt:
        # Kill processes still running after interrupt is recieved
        for process in processes:
            if process.is_alive:
                process.kill()
