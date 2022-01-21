import os
import urllib.request
from threading import Thread

import requests
from botbuilder.core import MessageFactory
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ConfirmPrompt,
    PromptOptions,
    ChoicePrompt,
    AttachmentPrompt,
)
from botbuilder.schema import Activity, ActivityTypes

from config import DefaultConfig
from help_modules import help_function, ContactOCR


class ClickbaitDialog(ComponentDialog):
    def __init__(self, default_config: DefaultConfig, contact_ocr: ContactOCR):
        super(ClickbaitDialog, self).__init__(ClickbaitDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.get_send_modality,
                    self.get_news_step,
                    self.check_news_step,
                    self.result_step
                ]
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(AttachmentPrompt(AttachmentPrompt.__name__))
        self.config = default_config
        self._contact_ocr = contact_ocr
        self.is_finished = False
        self.is_photo = False

    async def get_send_modality(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = False
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Come vuoi inviarmi il titolo da controllare?"),
                choices=[Choice("Foto"), Choice("Testo")]
            )
        )

    async def get_news_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        modality = step_context.result.value

        if modality == "Foto":
            self.is_photo = True
            return await step_context.prompt(
                AttachmentPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Inviami l'immagine. Estrarrò il testo"))
            )

        elif modality == "Testo":
            await step_context.context.send_activity(Activity(type=ActivityTypes.typing))
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Dimmi il titolo dell'articolo")),
            )

    async def check_news_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if self.is_photo:
            self.is_photo = False
            attachment = step_context.result[0]
            url_attachment = attachment.content_url
            urllib.request.urlretrieve(url_attachment, "attachment")
            image_data = open("attachment", "rb").read()
            os.remove("attachment")

            title = self._contact_ocr.send_request(image_data)
        else:
            title = step_context.result

        step_context.values["title"] = title
        await step_context.context.send_activity(MessageFactory.text(f"Titolo: \"{title}\""),)

        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Il titolo è corretto?"),
            )
        )

    async def result_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = True
        if step_context.result:
            await step_context.context.send_activity(MessageFactory.text("Adesso controllo, ci metterò un po'"))
            Thread(
                target=help_function.run_async_function,
                args=(self.call_clickbait_function(step_context),)
            ).start()
        else:
            await step_context.context.send_activity(MessageFactory.text("Ricomincia da capo"))

        return await step_context.end_dialog()

    async def call_clickbait_function(self, step_context: WaterfallStepContext):
        title = step_context.values["title"]
        response = requests.get(self.config.CLICKBAIT_FUNCTION_URL, {"title": title})
        response.raise_for_status()
        is_clickbait = True if response.text == "True" else False

        if is_clickbait:
            await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text(f"Secondo me l'articolo \"{title}\" è clickbait")),
            )
        else:
            await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text(f"Mi sa che l'articolo \"{title}\" non è clickbait")),
            )
