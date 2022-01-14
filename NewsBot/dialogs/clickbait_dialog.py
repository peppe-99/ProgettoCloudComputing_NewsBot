from threading import Thread

import requests
from botbuilder.core import MessageFactory
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ConfirmPrompt,
    PromptOptions,
)
from botbuilder.schema import Activity, ActivityTypes

from config import DefaultConfig
from help_modules import help_function


class ClickbaitDialog(ComponentDialog):
    def __init__(self, default_config: DefaultConfig):
        super(ClickbaitDialog, self).__init__(ClickbaitDialog.__name__)

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.get_news_step,
                    self.check_news_step,
                    self.result_step
                ]
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.config = default_config
        self.is_finished = False

    async def get_news_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = False
        await step_context.context.send_activity(Activity(type=ActivityTypes.typing))
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Dimmi il titolo dell'articolo")),
        )

    async def check_news_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["title"] = step_context.result

        await step_context.context.send_activity(
            MessageFactory.text(f"Titolo: \"{step_context.result}\""),
        )

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
            await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Ricomincia da capo"))
            )

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
