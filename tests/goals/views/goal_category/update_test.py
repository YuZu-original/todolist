import pytest


@pytest.mark.django_db
def test_goal_category_update(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_category_factory,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    category = goal_category_factory(board=board_participant.board, user=user)

    data = {
        "title": "test cat!",
    }

    auth_client = get_auth_client(user)

    response = auth_client.put(
        f"/goals/goal_category/{category.id}",
        data=data,
        content_type="application/json",
    )

    expected_response = {
        "id": category.id,
        "title": "test cat!",
        "is_deleted": False,
        "board": category.board.id,
        "created": category.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
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
def test_goal_category_update_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_category_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    board_participant = board_participant_factory(user=user1)
    category = goal_category_factory(board=board_participant.board, user=user1)

    data = {
        "title": "test cat!",
    }

    auth_client = get_auth_client(user2)

    response = auth_client.put(
        f"/goals/goal_category/{category.id}",
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}
