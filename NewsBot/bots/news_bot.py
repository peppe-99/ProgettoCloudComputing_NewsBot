from botbuilder.core import ActivityHandler, TurnContext, MessageFactory, UserState, ConversationState
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes
from help_modules import ContactLUIS, WelcomeUserState, help_function, DialogHelper
from config import DefaultConfig

import requests
from threading import Thread
from dialogs.clickbait_dialog import ClickbaitDialog


class NewsBot(ActivityHandler):
    def __init__(self, user_state: UserState, conversation_state: ConversationState, luis_recognizer: ContactLUIS,
                 clickbait_dialog: ClickbaitDialog):
        self.HELLO_MESSAGE = "Ciao sono NewsBot. Come posso esserti d\'aiuto?"
        self.HELP_MESSAGES = ["Sono ancora in fase di sviluppo, per ora ecco cosa posso fare:",
                              "1 - Fornirti notizie su ciò che desideri. Ad esempio, prova a dire \"Vorrei delle notizie sui vaccini\" oppure \"Ultimi aggiornamenti sul calcio mercato\"",
                              "2 - Controllare se il titolo di un articolo è clickbait o meno. Ad esempio, prova a dire \"Puoi controllare se questo titolo è clickbait?\" oppure seplicemente \"Clickbait\""]
        self.ERROR_MESSAGE = "ops...qualcosa è andato storto :("

        self._user_state = user_state
        self.user_state_accessor = self._user_state.create_property("WelcomeUserState")
        self._conversation_state = conversation_state
        self._luis_recognizer = luis_recognizer
        self._clickbait_dialog = clickbait_dialog
        self._config = DefaultConfig()
        self.calls_luis = True

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        await self._user_state.save_changes(turn_context)
        await self._conversation_state.save_changes(turn_context)

    async def on_message_activity(self, turn_context: TurnContext):
        welcome_user_state = await self.user_state_accessor.get(turn_context, WelcomeUserState)

        if not welcome_user_state.did_welcome_user and turn_context.activity.channel_id == "telegram":
            welcome_user_state.did_welcome_user = True
            await turn_context.send_activity(self.HELLO_MESSAGE)

        if self._luis_recognizer.is_configured:
            try:
                intent = None
                if self.calls_luis:
                    recognizer_result = await self._luis_recognizer.recognize(turn_context)

                    intent = help_function.get_intent(recognizer_result)
                    print(intent)

                if not self.calls_luis or intent == "Clickbait":
                    self.calls_luis = False
                    await DialogHelper.run_dialog(
                        self._clickbait_dialog,
                        turn_context,
                        self._conversation_state.create_property("DialogState")
                    )
                    if self._clickbait_dialog.is_finished:
                        self.calls_luis = True

                elif intent == "NotizieBySoggetto":
                    result = recognizer_result.entities.get('$instance')
                    result = result.get('SoggettoNotizia')
                    result = result[0]
                    soggetto_notizia = result.get("text")
                    print(soggetto_notizia)

                    Thread(
                        target=help_function.run_async_function,
                        args=(self.send_news(turn_context, soggetto_notizia),)
                    ).start()
                    return

                elif intent == "Saluto":
                    await turn_context.send_activity(self.HELLO_MESSAGE)

                elif intent == "Aiuto" or intent == "None":
                    for message in self.HELP_MESSAGES:
                        await turn_context.send_activity(message)

            except Exception as exception:
                await turn_context.send_activity(self.ERROR_MESSAGE)
                print(exception)
        else:
            await turn_context.send_activity(self.ERROR_MESSAGE)

    async def on_members_added_activity(self, members_added: ChannelAccount, turn_context: TurnContext):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(self.HELLO_MESSAGE)

    async def send_news(self, context: TurnContext, soggetto_notizia):
        await context.send_activity(Activity(type=ActivityTypes.typing))
        response = requests.get(self._config.NEWS_BY_SUBJECT_FUNCTION_URL, {"subject": soggetto_notizia})
        response.raise_for_status()
        notizie = dict(response.json())

        await context.send_activity(f"Ecco cosa ho trovato riguardo \"{soggetto_notizia}\"")
        for nome in notizie.keys():
            await context.send_activity(nome + "\n\n" + notizie[nome])
