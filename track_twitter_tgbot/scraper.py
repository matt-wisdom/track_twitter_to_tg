import logging
from datetime import datetime, timedelta
import multiprocessing
from random import randrange
from typing import Dict, Generator

import pytz
import snscrape.modules.twitter as sntwitter

from . import sqlite
from conf import MAX_TWEET_AGE_MINUTES

logger = logging.getLogger(__name__)


def scrape_tweets(accounts: str) -> Generator[Dict]:
    """ 
        Poll accounts for recent tweets i.e tweets not older than
        MAX_TWEET_AGE_MINUTES minutes. Defaults to 3 minutes.
    """
    conn = sqlite.create_connection(sqlite.db_file)
    while True:
        for account in accounts:
            counts += 1
            for i, tweet in enumerate(
                sntwitter.TwitterSearchScraper(f"from:{account}").get_items()
            ):
                if (
                    tweet.date
                    < pytz.UTC.localize(datetime.utcnow() - timedelta(minutes=MAX_TWEET_AGE_MINUTES))
                    or i > 15
                ):
                    break
                if tweet.inReplyToTweetId:
                    continue
                if not sqlite.select(conn, tweet.id):
                    try:
                        sqlite.insert(conn, [tweet.id])
                    except Exception as e:
                        logger.exception(e)
                else:
                    continue
                img = None
                if tweet.media:
                    try:
                        img = tweet.media[0].fullUrl
                    except:
                        try:
                            img = tweet.media[0].previewUrl
                        except:
                            img = ""
                yield {
                    "content": tweet.renderedContent[:1000],
                    "username": tweet.user.username,
                    "url": tweet.url,
                    "img": img,
                }


def scrape(accounts: str, queue: multiprocessing.Queue):
    """ Get scraped tweets and add to queue """
    id = randrange(1, 444444444)
    logger.info(f"Starting #{id}")
    try:
        tweets = scrape_tweets(accounts)
        for tweet in tweets:
            logger.info(f"#{id}: Got tweet from {tweet['username']}")
            queue.put(tweet)
    except Exception as e:
        logger.exception(f"#{id}: Received Exception {e}")
