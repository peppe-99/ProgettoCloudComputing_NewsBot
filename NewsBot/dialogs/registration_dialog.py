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
from help_modules import RegisteredUser, DatabaseHelper
from help_modules.help_function import check_email


class RegistrationDialog(ComponentDialog):
    def __init__(self, database_helper: DatabaseHelper):
        super(RegistrationDialog, self).__init__(RegistrationDialog.__name__)

        self._database_heper = database_helper

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.get_email_user,
                    self.check_email_user,
                    self.add_category,
                    self.add_category_two,
                    self.add_category_three,
                    self.confirm_registration,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.is_finished = False
        self.choices = ["Business", "Entertainment", "ScienceAndTechnology", "Sports", "World", "Culture", "Education", "Italy"]
        self.registered_user = RegisteredUser("", [])

    async def get_email_user(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = False
        self.choices = ["Business", "Entertainment", "ScienceAndTechnology", "Sports", "World", "Culture", "Education", "Italy"]

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci la tua email")),
        )

    async def check_email_user(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if check_email(step_context.result):
            user = self._database_heper.find_by_id(step_context.result)
            if user is None:
                step_context.values["email"] = step_context.result
                return await step_context.prompt(
                    ConfirmPrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text(f"L'email \"{step_context.result}\" è corretta?"),
                    )
                )
            else:
                await step_context.context.send_activity(
                    MessageFactory.text(f"Sei già iscritto. I tuoi interessi sono {user.preferenze[0]}, {user.preferenze[1]} e {user.preferenze[2]}")
                )
                self.is_finished = True
                return await step_context.end_dialog()
        else:
            await step_context.context.send_activity(
                MessageFactory.text(f"L'email \"{step_context.result}\" non è valida"),
            )
            self.is_finished = True
            return await step_context.end_dialog()

    async def add_category(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            self.registered_user.set_email(step_context.values["email"])
            possible_choices = []
            for choice in self.choices:
                possible_choices.append(Choice(choice))

            await step_context.context.send_activity(MessageFactory.text("Sentiamo, quali sono i tuoi interessi?"))

            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Seleziona il primo interesse"),
                    choices=possible_choices,
                ),
            )
        else:
            self.is_finished = True
            await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Ricomincia da capo"))
            )
            return await step_context.end_dialog()

    async def add_category_two(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            self.choices.remove(step_context.result.value)
            self.registered_user.add_preferenza(step_context.result.value)
            possible_choices = []
            for choice in self.choices:
                possible_choices.append(Choice(choice))

            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Seleziona il secondo interesse"),
                    choices=possible_choices,
                ),
            )
        return await step_context.end_dialog()

    async def add_category_three(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.registered_user.add_preferenza(step_context.result.value)
        self.choices.remove(step_context.result.value)
        possible_choices = []
        for choice in self.choices:
            possible_choices.append(Choice(choice))

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Seleziona l'ultimo interesse"),
                choices=possible_choices,
            ),
        )

    async def confirm_registration(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.registered_user.add_preferenza(step_context.result.value)
        self.is_finished = True
        self._database_heper.insert_data(self.registered_user)
        await step_context.context.send_activity(f"Registrazione completata. Riceverai ogni sera notizie sui tuoi "
                                                     f"interessi ({self.registered_user.preferenze[0]}, "
                                                     f"{self.registered_user.preferenze[1]}, "
                                                     f"{self.registered_user.preferenze[2]}) "
                                                     f"all'email \"{self.registered_user.email}\"")
        await step_context.context.send_activity("In qualsiasi momento puoi cancellare la tua iscrizione o modificare i tuoi interessi")
        return await step_context.end_dialog()
