from enum import Enum

from botbuilder.core import ActivityHandler, TurnContext, MessageFactory, UserState, ConversationState, CardFactory
from botbuilder.schema import ChannelAccount, Activity, ActivityTypes, CardImage, HeroCard, ReceiptCard
from help_modules import ContactLUIS, WelcomeUserState, help_function
from config import DefaultConfig
import requests
from threading import Thread
from dialogs import ClickbaitDialog, DialogHelper, DeleteRegistrationDialog, UpdateRegistrationDialog
from dialogs import RegistrationDialog


class NewsBot(ActivityHandler):
    def __init__(self, user_state: UserState, conversation_state: ConversationState, luis_recognizer: ContactLUIS,
                 clickbait_dialog: ClickbaitDialog, registration_dialog: RegistrationDialog,
                 delete_registration_dialog: DeleteRegistrationDialog,
                 update_registration_dialog: UpdateRegistrationDialog):
        self.last_intent = None
        self.HELLO_MESSAGE = "Ciao sono NewsBot. Come posso esserti d\'aiuto?"
        self.HELP_CARD = HeroCard(
            title="Ecco cosa posso fare per te:",
            text='1 - Fornirti notizie su ciò che desideri. Ad esempio, dimmi: \"Vorrei delle notizie sulla situazione covid\".\n\n'
                 '2 - Controlliamo insieme se il titolo di un articolo è clickbait o meno. Ad esempio, prova a dire: \"Puoi controllare se questo titolo è clickbait?\" oppure seplicemente \"Clickbait\".\n\n'
                 '3 - Puoi anche registrarti al servizio \"Daily-News\" che ti aggiornerà via email ogni giorno con le notizie relative ai tuoi interessi.\n\n'
                 '4 - Se dimentichi qualcosa basta dirmi: \"Aiutami\" oppure \"Cosa sai fare?\".',
            images=[CardImage(
                url="https://raw.githubusercontent.com/peppe-99/ProgettoCloudComputing_NewsBot/main/NewsBot/images/help_image.png")]
        )
        self.WELCOME_CARD = HeroCard(
            title="Benvenuto su NewsBot!",
            text="Ciao, sono NewsBot. Usami per ottenere informazioni in qualunque momento dove e quando vuoi!\n\n"
                 "Ecco cosa posso fare per te:\n\n"
                 "1 - Fornirti notizie su ciò che desideri. Ad esempio, dimmi: \"Vorrei delle notizie sulla situazione covid\".\n\n"
                 "2 - Controlliamo insieme se il titolo di un articolo è clickbait o meno. Ad esempio, prova a dire: \"Puoi controllare se questo titolo è clickbait?\" oppure seplicemente \"Clickbait\".\n\n"
                 "3 - Puoi anche registrarti al servizio \"Daily-News\" che ti aggiornerà via email ogni giorno con le notizie relative ai tuoi interessi.\n\n"
                 "4 - Se dimentichi qualcosa basta dirmi: \"Aiutami\" oppure \"Cosa sai fare?\".\n\n"
                 "Il Team di NewsBot ricorda che il servizio è ancora in fase di sviluppo.",
            images=[CardImage(
                url="https://raw.githubusercontent.com/peppe-99/ProgettoCloudComputing_NewsBot/main/NewsBot/images/welcome_image.jpg")]
        )
        self.ERROR_MESSAGE = "ops...qualcosa è andato storto \U0001F915"
        self.THANKS_MESSAGE = "Non c'è di che! \U0001F601"
        self.COMPLIMENTS_MESSAGE = "Aww! Così mi fai arrossire... \U0001F970"
        self.INSULTS_MESSAGE = "Che cosa ho fatto di male? \U0001F62D"
        self._user_state = user_state
        self.user_state_accessor = self._user_state.create_property("WelcomeUserState")
        self._conversation_state = conversation_state
        self._luis_recognizer = luis_recognizer
        self._clickbait_dialog = clickbait_dialog
        self._registration_dialog = registration_dialog
        self._delete_registration_dialog = delete_registration_dialog
        self._update_registration_dialog = update_registration_dialog
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
            return await turn_context.send_activity(MessageFactory.attachment(CardFactory.hero_card(self.WELCOME_CARD)))

        if self._luis_recognizer.is_configured:
            try:
                if self.calls_luis:
                    recognizer_result = await self._luis_recognizer.recognize(turn_context)

                    self.last_intent = help_function.get_intent(recognizer_result)

                if self.last_intent == "NuovaRegistrazione":
                    self.calls_luis = False
                    await DialogHelper.run_dialog(
                        self._registration_dialog,
                        turn_context,
                        self._conversation_state.create_property("DialogState")
                    )
                    if self._registration_dialog.is_finished:
                        self.calls_luis = True

                elif self.last_intent == "ModificaRegistrazione":
                    self.calls_luis = False
                    await DialogHelper.run_dialog(
                        self._update_registration_dialog,
                        turn_context,
                        self._conversation_state.create_property("DialogState")
                    )
                    if self._update_registration_dialog.is_finished:
                        self.calls_luis = True

                elif self.last_intent == "EliminaRegistrazione":
                    self.calls_luis = False
                    await DialogHelper.run_dialog(
                        self._delete_registration_dialog,
                        turn_context,
                        self._conversation_state.create_property("DialogState")
                    )
                    if self._delete_registration_dialog.is_finished:
                        self.calls_luis = True

                elif self.last_intent == "Clickbait":
                    self.calls_luis = False
                    await DialogHelper.run_dialog(
                        self._clickbait_dialog,
                        turn_context,
                        self._conversation_state.create_property("DialogState")
                    )
                    if self._clickbait_dialog.is_finished:
                        self.calls_luis = True

                elif self.last_intent == "NotizieBySoggetto":
                    result = recognizer_result.entities.get('$instance')
                    result = result.get('SoggettoNotizia')
                    result = result[0]
                    subject = result.get("text")
                    await self.send_news(turn_context, subject)

                elif self.last_intent == "Saluto":
                    await turn_context.send_activity(self.HELLO_MESSAGE)

                elif self.last_intent == "Grazie":
                    await turn_context.send_activity(self.THANKS_MESSAGE)

                elif self.last_intent == "Complimento":
                    await turn_context.send_activity(self.COMPLIMENTS_MESSAGE)

                elif self.last_intent == "Insulto":
                    await turn_context.send_activity(self.INSULTS_MESSAGE)

                elif self.last_intent == "Aiuto" or self.last_intent == "None":
                    return await turn_context.send_activity(
                        MessageFactory.attachment(CardFactory.hero_card(self.HELP_CARD))
                    )

            except Exception as exception:
                await turn_context.send_activity(str(exception))
                print(exception)
        else:
            await turn_context.send_activity(self.ERROR_MESSAGE)

    async def on_members_added_activity(self, members_added: ChannelAccount, turn_context: TurnContext):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.attachment(CardFactory.hero_card(self.WELCOME_CARD))
                )

    async def send_news(self, context: TurnContext, subject):
        await context.send_activity(Activity(type=ActivityTypes.typing))
        response = requests.get(self._config.NEWS_BY_SUBJECT_FUNCTION_URL, {"subject": subject})
        response.raise_for_status()
        news = dict(response.json())

        if not bool(news):
            await context.send_activity(f"Non ho trovato nulla riguardo \"{subject}\"")
        else:
            await context.send_activity(f"Ecco cosa ho trovato riguardo \"{subject}\"")
            for name in news.keys():
                await context.send_activity(name + "\n\n" + news[name])
