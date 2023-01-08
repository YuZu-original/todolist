import pytest

from goals.models import BoardParticipant


def get_expected_response(categories, do_sort=True):
    expected_response = []

    for category in categories:
        expected_response.append(
            {
                "id": category.id,
                "title": category.title,
                "is_deleted": False,
                "board": category.board.id,
                "created": category.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "updated": category.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                "user": {
                    "id": category.user.id,
                    "username": category.user.username,
                    "first_name": category.user.first_name,
                    "last_name": category.user.last_name,
                    "email": category.user.email,
                },
            }
        )
    if do_sort:
        return sorted(expected_response, key=lambda x: x["title"])
    return expected_response


@pytest.mark.django_db
def test_goal_category_list(
    user_factory,
    get_auth_client,
    board_participant_factory,
    goal_category_factory,
):
    user = user_factory()
    board_participant = board_participant_factory(user=user)
    categories = goal_category_factory.create_batch(
        5, board=board_participant.board, user=user
    )

    expected_response = get_expected_response(categories)

    auth_client = get_auth_client(user)

    response = auth_client.get(f"/goals/goal_category/list")

    assert response.status_code == 200
    assert response.data == expected_response


@pytest.mark.django_db
def test_goal_category_list_with_many_users_and_one_board(
    user_factory,
    get_auth_client,
    board_factory,
    board_participant_factory,
    goal_category_factory,
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

    expected_response = get_expected_response(all_categories)

    for user in (user1, user2, user3):
        auth_client = get_auth_client(user)

        response = auth_client.get(f"/goals/goal_category/list")

        assert response.status_code == 200
        assert response.data == expected_response
