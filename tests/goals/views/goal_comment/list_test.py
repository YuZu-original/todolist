import random

import factory
import pytest

from goals.models import BoardParticipant


@pytest.mark.django_db
def test_goal_comment_list(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_comment_factory,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    goal_comments = goal_comment_factory.create_batch(
        8,
        goal__category__board=board_participant.board,
        goal__category__user=user,
        goal__user=user,
        user=user,
    )

    auth_client = get_auth_client(user)

    response = auth_client.get("/goals/goal_comment/list")

    assert response.status_code == 200
    assert len(response.data) == 8


@pytest.mark.django_db
def test_goal_comment_list_with_many_users_and_one_board(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_comment_factory,
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

    comments = goal_comment_factory.create_batch(
        8,
        goal__category__board=board,
        goal__category__user=factory.LazyFunction(
            lambda: random.choice([user1, user2])
        ),
        goal__user=factory.LazyFunction(lambda: random.choice([user1, user2])),
        user=factory.LazyFunction(lambda: random.choice([user1, user2])),
    )

    for user in (user1, user2, user3):
        auth_client = get_auth_client(user)

        response = auth_client.get(
            "/goals/goal_comment/list",
        )
        assert response.status_code == 200
        assert len(response.data) == 8


@pytest.mark.django_db
def test_goal_comment_list_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_comment_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    board_participant = board_participant_factory(user=user1)
    goal_comments = goal_comment_factory.create_batch(
        8,
        goal__category__board=board_participant.board,
        goal__category__user=user1,
        goal__user=user1,
        user=user1,
    )

    auth_client = get_auth_client(user2)

    response = auth_client.get("/goals/goal_comment/list")

    assert response.status_code == 200
    assert response.data == []
