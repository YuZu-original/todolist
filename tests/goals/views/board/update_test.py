import pytest

from goals.models import BoardParticipant


@pytest.mark.django_db
def test_board_update(
    user_factory,
    get_auth_client,
    board_participant_factory,
):
    owner = user_factory()
    board_participant = board_participant_factory(user=owner)
    board_participant2 = board_participant_factory(
        board=board_participant.board, role=BoardParticipant.Role.writer
    )
    user3 = user_factory()

    data = {
        "title": "test board",
        "participants": [
            {
                "user": board_participant2.user.username,
                "role": BoardParticipant.Role.reader,  # change from writer to reader
            },
            {
                "user": user3.username,
                "role": BoardParticipant.Role.writer,  # add new participant board
            },
        ],
        "user": "test",
    }

    auth_client = get_auth_client(owner)

    response = auth_client.patch(
        f"/goals/board/{board_participant.board.id}",
        data=data,
        content_type="application/json",
    )

    expected_response = {
        "id": board_participant.board.id,
        "title": "test board",
        "is_deleted": False,
        "created": board_participant.board.created.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ),
        "updated": response.data["updated"],
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
            {
                "id": board_participant2.id,
                "role": BoardParticipant.Role.reader,
                "user": board_participant2.user.username,
                "created": board_participant2.created.strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                "updated": response.data["participants"][1]["updated"],
                "board": board_participant.board.id,
            },
            {
                "id": board_participant2.id + 1,
                "role": BoardParticipant.Role.writer,
                "user": user3.username,
                "created": response.data["participants"][2]["created"],
                "updated": response.data["participants"][2]["updated"],
                "board": board_participant.board.id,
            },
        ],
    }

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_board_update_with_another_auth_user(
    user_factory,
    get_auth_client,
    board_participant_factory,
):
    user1 = user_factory()
    user2 = user_factory()
    board_participant = board_participant_factory(user=user1)

    data = {
        "title": "test board",
    }

    auth_client = get_auth_client(user2)

    response = auth_client.put(
        f"/goals/board/{board_participant.board.id}",
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 404
    assert response.data == {"detail": "Not found."}
