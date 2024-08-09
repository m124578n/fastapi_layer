import pytest
from httpx import AsyncClient


@pytest.mark.asyncio(scope="session")
async def test_login(test_client: AsyncClient):
    # Test login
    response = await test_client.post(
        "/auth/login", json={"username": "testuser", "password": "testpassword"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    assert response.json()["is_use_otp"] == False


@pytest.mark.parametrize(
    "username, password",
    [("wrongusername", "testpassword"), ("testuser", "wrongpassword")],
)
@pytest.mark.asyncio(scope="session")
async def test_login_fail(test_client: AsyncClient, username, password):
    # Test incorrect username
    response = await test_client.post(
        "/auth/login", json={"username": username, "password": password}
    )

    assert response.status_code == 400


@pytest.mark.asyncio(scope="session")
async def test_logout(test_client: AsyncClient):
    # Test login
    response = await test_client.post(
        "/auth/login", json={"username": "testuser", "password": "testpassword"}
    )

    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Test logout with token
    response = await test_client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200

    # Test logout with same token
    response = await test_client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401
