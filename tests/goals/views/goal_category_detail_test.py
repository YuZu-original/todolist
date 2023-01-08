import pytest


@pytest.mark.django_db
def test_goal_category_detail(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_category_factory,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    category = goal_category_factory(board=board_participant.board, user=user)

    expected_response = {
        "id": category.id,
        "title": category.title,
        "is_deleted": False,
        "board": board_participant.board.id,
        "created": category.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "updated": category.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "user": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        },
    }

    auth_client = get_auth_client(user)

    response = auth_client.get(f"/goals/goal_category/{category.id}")

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_goal_category_detail_with_not_auth_user(
    user_factory,
    board_participant_factory,
    goal_category_factory,
    client,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    category = goal_category_factory(board=board_participant.board, user=user)

    response = client.get(f"/goals/goal_category/{category.id}")

    assert response.status_code == 403
    assert response.data == {
        "detail": "Authentication credentials were not provided."
    }


@pytest.mark.django_db
def test_goal_category_detail_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_category_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    board_participant = board_participant_factory(user=user1)
    category = goal_category_factory(board=board_participant.board, user=user1)

    auth_client = get_auth_client(user2)

    response = auth_client.get(f"/goals/goal_category/{category.id}")

    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}
