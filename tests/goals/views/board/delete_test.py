import pytest


@pytest.mark.django_db
def test_board_delete(
    get_auth_client,
    board_participant_factory,
):
    board_participant = board_participant_factory()

    auth_client = get_auth_client(board_participant.user)

    response = auth_client.delete(f"/goals/board/{board_participant.board.id}")

    assert response.status_code == 204
    assert response.data is None


@pytest.mark.django_db
def test_board_delete_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_category_factory,
):
    board_participant = board_participant_factory()
    user2 = user_factory()

    auth_client = get_auth_client(user2)

    response = auth_client.delete(f"/goals/board/{board_participant.board.id}")

    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}
