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


class ClickbaitDialog(ComponentDialog):
    def __init__(self):
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

        self.is_finished = False

    async def get_news_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = False
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
            # Chiamo la funzione
            await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Clickbait")),
            )
            return await step_context.end_dialog()
        else:
            await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Ricomincia da capo"))
            )
            return await step_context.end_dialog()
