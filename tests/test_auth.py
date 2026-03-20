def test_register_and_login(client):
    register_res = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "secret123"},
    )
    assert register_res.status_code == 201
    register_body = register_res.json()
    assert "access_token" in register_body
    assert "refresh_token" in register_body

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "secret123"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
