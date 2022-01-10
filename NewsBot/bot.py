# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import asyncio
import os
import threading
from pprint import pprint
from threading import Thread

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from ContactLUIS import ContactLUIS
from config import DefaultConfig

import requests


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.
    def __init__(self, luis_recognizer: ContactLUIS):
        self._luis_recognizer = luis_recognizer
        self._config = DefaultConfig()

    async def on_message_activity(self, turn_context: TurnContext):
        if self._luis_recognizer.is_configured:
            result = None
            intent = None

            try:
                recognizer_result = await self._luis_recognizer.recognize(turn_context)

                intent = (
                    sorted(
                        recognizer_result.intents,
                        key=recognizer_result.intents.get,
                        reverse=True,
                    )[:1][0]
                    if recognizer_result.intents
                    else None
                )

                if intent == "NotizieBySoggetto":
                    result = recognizer_result.entities.get('$instance')
                    result = result.get('SoggettoNotizia')
                    result = result[0]
                    soggetto_notizia = result.get("text")
                    print(result)

                    def run_async_function(function):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop=loop)
                        loop.run_until_complete(function)
                        loop.close()

                    thread = threading.Thread(target=run_async_function, args=(self.send_news(turn_context, soggetto_notizia), ))
                    thread.start()
                    await turn_context.send_activity(Activity(type=ActivityTypes.typing))

            except Exception as exception:
                print("eccezzione")
                print(exception)
        else:
            await turn_context.send_activity(f"LUIS non è configurato bene")

    async def on_members_added_activity(
            self,
            members_added: ChannelAccount,
            turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")

    async def send_news(self, context: TurnContext, soggetto_notizia):
        response = requests.get(self._config.NEWS_BY_SUBJECT_FUNCTION_URL, {"subject": soggetto_notizia})
        response.raise_for_status()
        notizie = dict(response.json())

        await context.send_activity(f"Ecco cosa ho trovato riguardo \"{soggetto_notizia}\"")
        for nome in notizie.keys():
            await context.send_activity(nome + "\n\n" + notizie[nome])
