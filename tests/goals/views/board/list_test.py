import pytest


@pytest.mark.django_db
def test_board_list(
    user_factory,
    get_auth_client,
    board_participant_factory,
):
    user = user_factory()
    board_participant = board_participant_factory.create_batch(5, user=user)

    auth_client = get_auth_client(user)

    response = auth_client.get("/goals/board/list")

    assert response.status_code == 200
    assert len(response.data) == 5


@pytest.mark.django_db
def test_board_list_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
):
    board_participant = board_participant_factory.create_batch(5)
    user2 = user_factory()

    auth_client = get_auth_client(user2)

    response = auth_client.get("/goals/board/list")

    assert response.status_code == 200
    assert response.data == []
