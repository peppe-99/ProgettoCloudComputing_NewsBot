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


class UpdateRegistrationDialog(ComponentDialog):
    def __init__(self, database_helper: DatabaseHelper):
        super(UpdateRegistrationDialog, self).__init__(UpdateRegistrationDialog.__name__)

        self.registered_user = RegisteredUser("", [])
        self._database_helper = database_helper

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.get_email,
                    self.check_email,
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

        self.choices = ["Business", "Entertainment", "ScienceAndTechnology", "Sports", "World", "Culture", "Education",
                        "Italy"]
        self.is_finished = False

    async def get_email(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = False
        self.choices = ["Business", "Entertainment", "ScienceAndTechnology", "Sports", "World", "Culture", "Education",
                        "Italy"]
        self.registered_user = RegisteredUser("", [])

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci l'email con cui sei registrato")),
        )

    async def check_email(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        pattern = re.compile(
            "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])")

        if pattern.match(step_context.result):
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
                    MessageFactory.text(
                        f"Non esiste alcuna email {step_context.result} essere registrata al servizio.")
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
                MessageFactory.text(f"Le tue attuali preferenze sono: {self.registered_user.preferenze}")
            )
            self.registered_user.preferenze = []
            scelte = []
            for stringa in self.choices:
                scelte.append(Choice(stringa))

            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Scegli i tuoi nuovi interessi"),
                    choices=scelte,
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
            scelte = []
            for stringa in self.choices:
                scelte.append(Choice(stringa))

            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Scegli i tuoi nuovi interessi"),
                    choices=scelte,
                ),
            )
        return await step_context.end_dialog()

    async def new_category_three(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.choices.remove(step_context.result.value)
        self.registered_user.add_preferenza(step_context.result.value)
        scelte = []
        for stringa in self.choices:
            scelte.append(Choice(stringa))

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Scegli i tuoi nuovi interessi"),
                choices=scelte,
            ),
        )

    async def confirm_update(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.registered_user.add_preferenza(step_context.result.value)
        self.is_finished = True
        await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Interessi aggiornati"))
        )
        self._database_helper.insert_data(self.registered_user)
        print(f"Email: {self.registered_user.email}\nPreferenze: {self.registered_user.preferenze}")
        return await step_context.end_dialog()
