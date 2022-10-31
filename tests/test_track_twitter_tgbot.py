import os
from datetime import datetime, timedelta
import multiprocessing
import threading
import pytest
import pytz
from conf import MAX_TWEET_AGE_MINUTES

from main import orchestrate_scrapers, scrape_tweets
from track_twitter_tgbot import __version__

os.environ["TESTING"] = "1"


def test_version():
    assert __version__ == "0.1.0"


@pytest.mark.timeout(30)
def test_scrape_tweets():
    queue = multiprocessing.Queue()
    threads = scrape_tweets([" ", " ", " "], queue, 2)
    assert len(threads) == 2

    for thread in threads:
        assert isinstance(thread, threading.Thread)

    tweet = queue.get()
    # IMG can be none
    keys = ["content", "username", "url", "date"]
    for key in keys:
        print(key)
        assert tweet.get(key) != None

    assert tweet["date"] >= pytz.UTC.localize(
        datetime.utcnow() - timedelta(minutes=MAX_TWEET_AGE_MINUTES)
    )


@pytest.mark.timeout(30)
def test_orchestrate_scrapers():
    os.unlink("test.db")
    queue = multiprocessing.Queue()
    processes = orchestrate_scrapers([" ", " ", " ", " "], queue, 2)
    assert len(processes) == 2

    for proc in processes:
        assert isinstance(proc, multiprocessing.Process)

    processes[0].start()

    tweet = queue.get()
    keys = ["content", "username", "url", "date"]
    for key in keys:
        assert tweet.get(key) != None

    assert tweet["date"] >= pytz.UTC.localize(
        datetime.utcnow() - timedelta(minutes=MAX_TWEET_AGE_MINUTES)
    )

    processes[0].kill()
