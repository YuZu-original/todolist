import factory
from django.utils import timezone

from core.models import User
from goals.models import Board
from goals.models import BoardParticipant
from goals.models import Goal
from goals.models import GoalCategory
from goals.models import GoalComment


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker("name")
    password = factory.Faker("password")

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class BoardFactory(DatesFactoryMixin):
    class Meta:
        model = Board

    title = factory.Faker("sentence", nb_words=5)


class BoardParticipantFactory(DatesFactoryMixin):
    class Meta:
        model = BoardParticipant

    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)


class GoalCategoryFactory(DatesFactoryMixin):
    class Meta:
        model = GoalCategory

    board = factory.SubFactory(BoardFactory)
    title = factory.Faker("sentence", nb_words=3)
    user = factory.SubFactory(UserFactory)


class GoalFactory(DatesFactoryMixin):
    class Meta:
        model = Goal

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)
    title = factory.Faker("sentence", nb_words=5)


class GoalCommentFactory(DatesFactoryMixin):
    class Meta:
        model = GoalComment

    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(GoalFactory)
    text = factory.Faker("sentence", nb_words=10)
