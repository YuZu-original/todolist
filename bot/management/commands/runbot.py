from enum import Flag, auto

from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from django.conf import settings

from bot.tg.dc import Message
from goals.models import Goal, GoalCategory


class States(Flag):
    start = auto()
    verification = auto()
    idle = auto()
    input_cat_for_create_goal = auto()
    input_title_for_create_goal = auto()


class Command(BaseCommand):
    help = "start bot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)
        self.states_storage = {}
        self.goals_for_create = {}

    def handle(self, *args, **options):
        offset = 0

        while True:
            res = self.tg_client.get_updates(offset=offset)
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
        tg_user_id = message.from_.id

        # States
        if created:
            self.states_storage[tg_user_id] = States.start
        elif not tg_user.user:
            self.states_storage[tg_user_id] = States.verification
        elif self.states_storage.get(tg_user_id, States.verification) == States.verification:
            self.states_storage[tg_user_id] = States.idle

        match self.states_storage.get(tg_user_id, States.idle):
            case States.start:
                self.tg_client.send_message(message.chat.id, "Привет!")
            case States.verification:
                self.verification_state(message, tg_user)
            case States.idle:
                self.idle_state(message, tg_user)
            case States.input_cat_for_create_goal:
                self.input_cat_for_create_goal_state(message, tg_user)
            case States.input_title_for_create_goal:
                self.input_title_for_create_goal_state(message, tg_user)

    def verification_state(self, message: Message, tg_user: TgUser):
        tg_user.set_verification_code()
        tg_user.save(update_fields=["verification_code"])
        self.tg_client.send_message(message.chat.id, f"Код подтверждения -> {tg_user.verification_code}")

    def idle_state(self, message: Message, tg_user: TgUser):
        if message.text == "/goals":
            self.send_tasks(message, tg_user)
        elif message.text == "/create":
            self.states_storage[tg_user.tg_id] = States.input_cat_for_create_goal
            self.send_all_categories(message, tg_user)
        else:
            self.tg_client.send_message(message.chat.id, "Неизвестная команда :V")

    def send_tasks(self, message: Message, tg_user: TgUser):
        goals = Goal.objects.filter(user=tg_user.user)
        if goals.count() > 0:
            msg = "\n".join(f"#{goal.id} {goal.title}" for goal in goals)
            self.tg_client.send_message(message.chat.id, msg)
        else:
            self.tg_client.send_message(message.chat.id, "У вас нет целей ( ・ˍ・)")

    def send_all_categories(self, message: Message, tg_user: TgUser):
        categories = GoalCategory.objects.filter(board__participants__user=tg_user.user, is_deleted=False)
        if categories.count() > 0:
            msg = "Ваши категории\n" + "\n".join(f"#{cat.id} `{cat.title}`" for cat in categories)
            self.tg_client.send_message(message.chat.id, msg, parse_mode='Markdown')
        else:
            self.tg_client.send_message(message.chat.id, "У вас нет категорий ( ・ˍ・)")
            self.states_storage[tg_user.tg_id] = States.idle

    def input_cat_for_create_goal_state(self, message: Message, tg_user: TgUser):
        if message.text == '/cancel':
            self.goals_for_create.pop(tg_user.tg_id, None)
            self.cancel(message, tg_user)
            return

        category = GoalCategory.objects.filter(title=message.text, board__participants__user=tg_user.user,
                                               is_deleted=False).first()
        self.goals_for_create[tg_user.tg_id] = {"cat": None}
        if category:
            self.goals_for_create[tg_user.tg_id]["cat"] = category
            self.tg_client.send_message(message.chat.id, "Отлично!")
            self.tg_client.send_message(message.chat.id, "Теперь придумайте название цели")
            self.states_storage[tg_user.tg_id] = States.input_title_for_create_goal
            return
        else:
            self.tg_client.send_message(message.chat.id, "У вас нет такой категории :V\nПопробуйте еще раз :D")

    def input_title_for_create_goal_state(self, message: Message, tg_user: TgUser):
        if message.text == '/cancel':
            self.goals_for_create.pop(tg_user.tg_id, None)
            self.cancel(message, tg_user)
            return

        category: GoalCategory = self.goals_for_create[tg_user.tg_id]["cat"]
        goal = Goal.objects.create(user=category.user, title=message.text, category=category)
        self.tg_client.send_message(message.chat.id,
                                    "Ура! Ваша цель создана:\n" +
                                    f"http://yuzudev.ga/boards/{category.board.id}/goals?goal={goal.id}")
        self.states_storage[tg_user.tg_id] = States.idle

    def cancel(self, message: Message, tg_user: TgUser):
        self.tg_client.send_message(message.chat.id, "Операция отменена")
        self.states_storage[tg_user.tg_id] = States.idle
