from pytest_factoryboy import register

from tests.factories import BoardFactory
from tests.factories import BoardParticipantFactory
from tests.factories import GoalCategoryFactory
from tests.factories import GoalCommentFactory
from tests.factories import GoalFactory
from tests.factories import UserFactory

pytest_plugins = "tests.fixtures"

register(UserFactory)
register(BoardFactory)
register(BoardParticipantFactory)
register(GoalCategoryFactory)
register(GoalFactory)
register(GoalCommentFactory)
