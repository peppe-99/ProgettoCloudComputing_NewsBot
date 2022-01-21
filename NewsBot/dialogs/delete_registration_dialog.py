from botbuilder.core import MessageFactory
import re
from botbuilder.dialogs.choices import Choice
from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    ChoicePrompt,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    ConfirmPrompt,
    PromptOptions,
)
from help_modules import DatabaseHelper
from help_modules.help_function import check_email


class DeleteRegistrationDialog(ComponentDialog):
    def __init__(self, database_helper: DatabaseHelper):
        super(DeleteRegistrationDialog, self).__init__(DeleteRegistrationDialog.__name__)

        self._database_heper = database_helper

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.recive_email,
                    self.check_email_delete,
                    self.remove_email,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.is_finished = False

    async def recive_email(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = False

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci l'email con cui sei registrato")),
        )

    async def check_email_delete(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if check_email(step_context.result):
            user = self._database_heper.find_by_id(step_context.result)
            if user is not None:
                step_context.values["email"] = step_context.result
                return await step_context.prompt(
                    ConfirmPrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text("Sei sicuro di voler cancellare la tua iscrizione?"),
                    )
                )
            else:
                await step_context.context.send_activity(
                    MessageFactory.text(f"Non esiste alcuna iscrizione con l'email \"{step_context.result}\"")
                )
                self.is_finished = True
                return await step_context.end_dialog()
        else:
            await step_context.context.send_activity(
                MessageFactory.text(f"L'email \"{step_context.result}\" non è valida"),
            )
            self.is_finished = True
            return await step_context.end_dialog()

    async def remove_email(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = True
        if step_context.result:
            email = step_context.values["email"]
            self._database_heper.delete_by_id(email)
            await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Iscrizione cancellata con successo"))
            )
            return await step_context.end_dialog()
        else:
            await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Cancellazione annullata"))
            )
            return await step_context.end_dialog()
