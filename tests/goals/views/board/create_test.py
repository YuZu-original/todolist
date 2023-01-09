import pytest


@pytest.mark.django_db
def test_board_create(
    user_factory,
    get_auth_client,
):
    user = user_factory()

    data = {
        "title": "test board",
    }

    auth_client = get_auth_client(user)

    response = auth_client.post(
        "/goals/board/create",
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 201

    expected_response = {
        "id": response.data["id"],
        "title": "test board",
        "is_deleted": False,
        "created": response.data["created"],
        "updated": response.data["updated"],
    }

    assert response.data == expected_response


@pytest.mark.django_db
def test_board_create_with_not_auth_user(
    user_factory,
    client,
):
    user = user_factory()

    data = {
        "title": "test board",
    }

    response = client.post(
        "/goals/board/create",
        data=data,
        content_type="application/json",
    )

    assert response.status_code == 403
    assert response.data == {
        "detail": "Authentication credentials were not provided."
    }
