import pytest


@pytest.mark.django_db
def test_board_detail(
    get_auth_client,
    board_participant_factory,
):
    board_participant = board_participant_factory()

    expected_response = {
        "id": board_participant.board.id,
        "title": board_participant.board.title,
        "is_deleted": False,
        "created": board_participant.board.created.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "updated": board_participant.board.created.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "participants": [
            {
                "id": board_participant.id,
                "role": board_participant.role,
                "user": board_participant.user.username,
                "created": board_participant.created.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                "updated": board_participant.updated.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                "board": board_participant.board.id,
            },
        ],
    }

    auth_client = get_auth_client(board_participant.user)

    response = auth_client.get(f"/goals/board/{board_participant.board.id}")

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_board_detail_with_not_auth_user(board_participant_factory, client):
    board_participant = board_participant_factory()

    response = client.get(f"/goals/board/{board_participant.board.id}")

    assert response.status_code == 403
    assert response.data == {
        "detail": "Authentication credentials were not provided."
    }


@pytest.mark.django_db
def test_board_detail_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
    client,
):
    board_participant = board_participant_factory()
    user2 = user_factory()

    auth_client = get_auth_client(user2)

    response = auth_client.get(f"/goals/board/{board_participant.board.id}")

    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}
