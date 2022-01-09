# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
from pprint import pprint

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

                await turn_context.send_activities([
                    Activity(type=ActivityTypes.typing),
                    Activity(type="delay", value=3000),
                ])

                if intent == "NotizieBySoggetto":
                    result = recognizer_result.entities.get('$instance')
                    result = result.get('SoggettoNotizia')
                    result = result[0]
                    soggetto_notizia = result.get("text")
                    print(result)

                    response = requests.get(self._config.NEWS_BY_SUBJECT_FUNCTION_URL, {"subject": soggetto_notizia})
                    response.raise_for_status()
                    notizie = dict(response.json())

                    message = "Ecco cosa ho trovato:\n\n"
                    for notizia in notizie.keys():
                        message += notizia + " " + notizie[notizia] + "\n\n"

                    await turn_context.send_activity(f"{message}")

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
