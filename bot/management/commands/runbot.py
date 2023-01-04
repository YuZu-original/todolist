from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from django.conf import settings

from bot.tg.dc import Message
from goals.models import Goal


class Command(BaseCommand):
    help = "start bot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

    def handle(self, *args, **options):
        offset = 0
        tg_client = TgClient("")
        while True:
            res = tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, message: Message):
        tg_user, created = TgUser.objects.get_or_create(
            tg_id=message.from_.id,
            defaults={
                "tg_chat_id": message.chat.id,
                "username": message.from_.username,
            }
        )
        if created:
            self.tg_client.send_message(message.chat.id, "Привет!")

        if tg_user.user:
            self.handle_verified_user(message, tg_user)
        else:
            self.handle_unverified_user(message, tg_user)

    def handle_verified_user(self, message: Message, tg_user: TgUser):
        if message.text == "/goals":
            self.send_tasks(message, tg_user)
        else:
            self.tg_client.send_message(message.chat.id, "Неизвестная команда :V")

    def send_tasks(self, message: Message, tg_user: TgUser):
        goals = Goal.objects.filter(user=tg_user.user)
        if goals.count() > 0:
            msg = "\n".join(f"#{goal.id} {goal.title}" for goal in goals)
            self.tg_client.send_message(message.chat.id, msg)
        else:
            self.tg_client.send_message(message.chat.id, "У вас нет целей ( ・ˍ・)")

    def handle_unverified_user(self, message: Message, tg_user: TgUser):
        tg_user.set_verification_code()
        tg_user.save(update_fields=["verification_code"])
        self.tg_client.send_message(message.chat.id, f"Код подтверждения -> {tg_user.verification_code}")



