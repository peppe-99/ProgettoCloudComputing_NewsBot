from pprint import pprint

import requests
from config import DefaultConfig
from botbuilder.schema import Activity, ActivityTypes
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
from help_modules import RegisteredUser


class RegistrationDialog(ComponentDialog):
    def __init__(self):
        super(RegistrationDialog, self).__init__(RegistrationDialog.__name__)

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
        self.choises = ["Sport", "Financial", "Healt"]
        self.registered_user = RegisteredUser("", [])

    async def get_email_user(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.is_finished = False
        self.choises = ["Sport", "Financial", "Healt"]

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Inserisci la tua mail per ricevere aggiornamenti")),
        )

    async def check_email_user(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        pattern = re.compile(
            "(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])")

        if pattern.match(step_context.result):
            # TODO: controllare se l'utente è già registrato, ovvero se la mail sta nel db

            await step_context.context.send_activity(
                MessageFactory.text(f"Email: \"{step_context.result}\""),
            )
            step_context.values["email"] = step_context.result
            return await step_context.prompt(
                ConfirmPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("L'email è corretta?"),
                )
            )
        else:
            await step_context.context.send_activity(
                MessageFactory.text(f"L'email: \"{step_context.result}\" non è valida"),
            )
            self.is_finished = True
            return await step_context.end_dialog()

    async def add_category(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            self.registered_user.set_email(step_context.values["email"])
            scelte = []
            for stringa in self.choises:
                scelte.append(Choice(stringa))

            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Inserisci quali sono i tuoi interessi"),
                    choices=scelte,
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
            self.choises.remove(step_context.result.value)
            self.registered_user.add_preferenza(step_context.result.value)
            scelte = []
            for stringa in self.choises:
                scelte.append(Choice(stringa))

            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Inserisci quali sono i tuoi interessi"),
                    choices=scelte,
                ),
            )
        return await step_context.end_dialog()

    async def add_category_three(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.registered_user.add_preferenza(step_context.result.value)
        self.choises.remove(step_context.result.value)
        scelte = []
        for stringa in self.choises:
            scelte.append(Choice(stringa))

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Inserisci quali sono i tuoi interessi"),
                choices=scelte,
            ),
        )

    async def confirm_registration(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        self.registered_user.add_preferenza(step_context.result.value)
        self.is_finished = True
        await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Registrazione completata"))
        )
        # TODO: salvare veramente l'utente sul db

        print(f"Email: {self.registered_user.email}\nPreferenze: {self.registered_user.preferenze}")
        return await step_context.end_dialog()
