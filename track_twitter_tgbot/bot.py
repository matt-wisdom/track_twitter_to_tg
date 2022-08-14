import asyncio
import multiprocessing
import os
from telethon import TelegramClient, events

def run_bot(queue: multiprocessing.Queue, creds: dict):
    """
        Create bot, register events and launch.

        :param queue: multiprocessing.Queue object to read tweets from
        :param creds: Dictionary of telegram credentials. keys
         API_ID, API_HASH and BOT_TOKEN must be present.
    """
    async def main():
        """Start the bot."""
        print("Running bot, send a /start to the bot to start receiving updates")
        bot = await TelegramClient('bot', creds['API_ID'], creds['API_HASH']).start(bot_token=creds['BOT_TOKEN'])
        
        @bot.on(events.NewMessage(pattern='/cancel'))
        async def cancel(event):
            event.respond("Cancelled")
            os._exit(0)

        @bot.on(events.NewMessage(pattern='/start'))
        async def start(event):
            """Send a message when the command /start is issued."""
            await event.respond('Hi!')
            while True:
                tweet = queue.get()
                await asyncio.sleep(1.0)
                try:
                    if tweet['img']:
                        await event.respond(f"{tweet['content']}\n\nVia | [{tweet['username']}]({tweet['url']}) |", file=tweet['img'])
                    else:
                        await event.respond(f"{tweet['content']}\n\nVia | [{tweet['username']}]({tweet['url']}) |")
                except Exception as e:
                    break
            raise events.StopPropagation

        await bot.run_until_disconnected()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
