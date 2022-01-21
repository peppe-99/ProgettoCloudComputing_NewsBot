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


class UpdateRegistrationDialog(ComponentDialog):
    def __init__(self, database_helper: DatabaseHelper):
        super(UpdateRegistrationDialog, self).__init__(UpdateRegistrationDialog.__name__)

        self.registered_user = RegisteredUser("", [])
        self._database_helper = database_helper

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.get_email_user,
                    self.check_email_user,
                    self.new_category_one,
                    self.new_category_two,
                    self.new_category_three,
                    self.confirm_update,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.choices = ["Business", "Entertainment", "ScienceAndTechnology", "Sports", "World", "Culture", "Education", "Italy"]
        self.is_finished = False

    async def get_email_user(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = False
        self.choices = ["Business", "Entertainment", "ScienceAndTechnology", "Sports", "World", "Culture", "Education", "Italy"]
        self.registered_user = RegisteredUser("", [])

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci l'email con cui sei registrato")),
        )

    async def check_email_user(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if check_email(step_context.result):
            user = self._database_helper.find_by_id(step_context.result)
            if user is not None:
                self.registered_user.set_email(user.email)
                self.registered_user.set_preferenze(user.preferenze)
                return await step_context.prompt(
                    ConfirmPrompt.__name__,
                    PromptOptions(
                        prompt=MessageFactory.text("Sei sicuro di voler modificare le tue preferenze?"),
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

    async def new_category_one(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            await step_context.context.send_activity(
                MessageFactory.text(f"I tuoi attuali interessi sono {self.registered_user.preferenze[0]}, "
                                    f"{self.registered_user.preferenze[1]} e {self.registered_user.preferenze[2]}")
            )
            self.registered_user.preferenze = []
            possible_choices = []
            for choice in self.choices:
                possible_choices.append(Choice(choice))

            await step_context.context.send_activity(
                MessageFactory.text(f"I tuoi attuali interessi sono {self.registered_user.preferenze[0]}, "
                                    f"{self.registered_user.preferenze[1]} e {self.registered_user.preferenze[2]}")
            )
            await step_context.context.send_activity(MessageFactory.text("Scegli i tuoi nuovi interessi"))

            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Seleziona il primo interesse"),
                    choices=possible_choices,
                ),
            )
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Aggiornamento annullato")
            )
            self.is_finished = True
            return await step_context.end_dialog()

    async def new_category_two(self, step_context: WaterfallStepContext) -> DialogTurnResult:
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

    async def new_category_three(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.choices.remove(step_context.result.value)
        self.registered_user.add_preferenza(step_context.result.value)
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

    async def confirm_update(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.registered_user.add_preferenza(step_context.result.value)
        self.is_finished = True
        self._database_helper.insert_data(self.registered_user)
        await step_context.context.send_activity(MessageFactory.text(f"I tuoi nuovi interessi sono: "
                                                                     f"{self.registered_user.preferenze[0]}, "
                                                                     f"{self.registered_user.preferenze[1]} e"
                                                                     f"{self.registered_user.preferenze[2]}"))
        return await step_context.end_dialog()
