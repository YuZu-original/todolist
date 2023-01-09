import random

import factory
import pytest

from goals.models import BoardParticipant


def get_expected_response(goals, do_sort=True):
    expected_response = []

    for goal in goals:
        expected_response.append(
            {
                "id": goal.id,
                "title": goal.title,
                "category": goal.category.id,
                "description": goal.description,
                "due_date": goal.due_date.strftime("%Y-%m-%d")
                if goal.due_date
                else None,
                "status": goal.status,
                "priority": goal.priority,
                "created": goal.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updated": goal.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "user": {
                    "id": goal.user.id,
                    "username": goal.user.username,
                    "first_name": goal.user.first_name,
                    "last_name": goal.user.last_name,
                    "email": goal.user.email,
                },
            }
        )
    if do_sort:
        return sorted(
            expected_response, key=lambda x: (x["priority"], x["due_date"])
        )
    return expected_response


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

    expected_response = get_expected_response(goals)

    auth_client = get_auth_client(user)

    response = auth_client.get("/goals/goal/list")

    assert response.status_code == 200
    assert response.data == expected_response


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

    expected_response = get_expected_response(all_goals, do_sort=False)

    for user in (user1, user2, user3):
        auth_client = get_auth_client(user)

        response = auth_client.get(
            "/goals/goal/list",
        )
        assert response.status_code == 200
        assert (
            sorted(response.data, key=lambda x: x["id"]) == expected_response
        )


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
