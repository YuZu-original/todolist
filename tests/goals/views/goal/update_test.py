import pytest


@pytest.mark.django_db
def test_goal_update(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_factory,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    goal = goal_factory(
        category__board=board_participant.board, category__user=user, user=user
    )

    data = {
        "title": "test goal!",
    }

    auth_client = get_auth_client(user)

    response = auth_client.patch(
        f"/goals/goal/{goal.id}",
        data=data,
        content_type="application/json",
    )

    expected_response = {
        "id": goal.id,
        "title": "test goal!",
        "category": goal.category.id,
        "description": None,
        "due_date": None,
        "status": 1,
        "priority": 2,
        "created": goal.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated": response.data["updated"],
        "user": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        },
    }

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_goal_update_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    board_participant = board_participant_factory(user=user1)
    goal = goal_factory(
        category__board=board_participant.board,
        category__user=user1,
        user=user1,
    )

    data = {
        "title": "test goal!",
    }

    auth_client = get_auth_client(user2)

    response = auth_client.patch(
        f"/goals/goal_category/{goal.id}",
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}
