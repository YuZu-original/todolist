import random

import factory
import pytest

from goals.models import BoardParticipant


@pytest.mark.django_db
def test_goal_list(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_factory,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    goals = goal_factory.create_batch(
        8,
        category__board=board_participant.board,
        category__user=user,
        user=user,
    )

    auth_client = get_auth_client(user)

    response = auth_client.get("/goals/goal/list")

    assert response.status_code == 200
    assert len(response.data) == 8


@pytest.mark.django_db
def test_goal_list_with_many_users_and_one_board(
    user_factory,
    get_auth_client,
    board_participant_factory,
    board_factory,
    goal_category_factory,
    goal_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    user3 = user_factory()
    board = board_factory()
    board_participant1 = board_participant_factory(
        board=board, user=user1, role=BoardParticipant.Role.owner
    )
    board_participant2 = board_participant_factory(
        board=board, user=user2, role=BoardParticipant.Role.writer
    )
    board_participant3 = board_participant_factory(
        board=board, user=user3, role=BoardParticipant.Role.reader
    )
    categories_by_user1 = goal_category_factory.create_batch(
        3, board=board, user=user1
    )
    categories_by_user2 = goal_category_factory.create_batch(
        3, board=board, user=user2
    )
    all_categories = categories_by_user1 + categories_by_user2

    goals_by_user1 = goal_factory.create_batch(
        4,
        category=factory.LazyFunction(lambda: random.choice(all_categories)),
        user=user1,
    )
    goals_by_user2 = goal_factory.create_batch(
        4,
        category=factory.LazyFunction(lambda: random.choice(all_categories)),
        user=user2,
    )
    all_goals = goals_by_user1 + goals_by_user2

    for user in (user1, user2, user3):
        auth_client = get_auth_client(user)

        response = auth_client.get(
            "/goals/goal/list",
        )
        assert response.status_code == 200
        assert len(response.data) == 8


@pytest.mark.django_db
def test_goal_list_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    board_participant = board_participant_factory(user=user1)
    goals = goal_factory.create_batch(
        8,
        category__board=board_participant.board,
        category__user=user1,
        user=user1,
    )

    auth_client = get_auth_client(user2)

    response = auth_client.get("/goals/goal/list")

    assert response.status_code == 200
    assert response.data == []
