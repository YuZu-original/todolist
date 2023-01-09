import pytest


@pytest.mark.django_db
def test_goal_comment_create(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_factory,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    goal = goal_factory(user=user, category__board=board_participant.board)

    data = {
        "goal": goal.id,
        "text": "test comment",
    }

    auth_client = get_auth_client(user)

    response = auth_client.post(
        "/goals/goal_comment/create",
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 201

    expected_response = {
        "id": response.data["id"],
        "text": "test comment",
        "goal": goal.id,
        "created": response.data["created"],
        "updated": response.data["updated"],
    }

    assert response.data == expected_response


@pytest.mark.django_db
def test_goal_comment_create_with_not_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_factory,
    client,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    goal = goal_factory(user=user, category__board=board_participant.board)

    data = {
        "goal": goal.id,
        "text": "test comment",
    }

    response = client.post(
        "/goals/goal/create",
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 403
    assert response.data == {
        "detail": "Authentication credentials were not provided."
    }
