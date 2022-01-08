# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from pprint import pprint

from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
from ContactLUIS import ContactLUIS


class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.
    def __init__(self, luis_recognizer: ContactLUIS):
        self._luis_recognizer = luis_recognizer

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
                    text = result.get("text")
                    print(result)
                    print(type(result))
                    await turn_context.send_activity(f"Vuoi cercare notizie sul {text}")

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
