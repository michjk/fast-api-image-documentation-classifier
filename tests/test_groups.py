from uuid import uuid4


def test_group_not_found(client):
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "group@example.com", "password": "secret123"},
    )
    token = register.json()["access_token"]

    res = client.get(f"/api/v1/groups/{uuid4()}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 404
