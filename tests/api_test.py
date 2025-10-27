from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from httpx import ASGITransport, AsyncClient
import pytest_asyncio
import pytest

from db.connection import _ConnectionManager, ConnectionManager
from roles.models import AvailableRoles
from roles.repository import RolesRepository
from tests.module_test import conn_manager #noqa
from main import app
from users.repository import UsersRepository
from users_roles.models import RegisterUserRole
from users_roles.repository import UsersRolesRepository


client = TestClient(app)


@pytest_asyncio.fixture(scope="module")
async def dependencies_overrider(conn_manager: _ConnectionManager):

  async def override_session_dependency():
    async with conn_manager.get_session_ctx() as session:
      yield session

  app.dependency_overrides[ConnectionManager.get_session] = override_session_dependency

  async with conn_manager.get_session_ctx() as session:
      await RolesRepository.insert_default_roles(session)

  yield

  app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_getter(dependencies_overrider):
  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize("email,password, status_code", [
  ("admin@mail.ru", "qwerty", status.HTTP_200_OK),
  ("user@mail.ru", "qwerty", status.HTTP_200_OK),
  ("user@mail.ru", "qwerty", status.HTTP_400_BAD_REQUEST),
])
async def test_user_singup(client_getter: AsyncClient, email: str, password: str, status_code: int):
  
    payload = dict(email=email, password=password)
    
    response = await client_getter.post("/auth/signup", json=payload)

    assert response.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize("email,password, status_code", [
  ("admin@mail.ru", "qwerty", status.HTTP_200_OK),
  ("user@mail.ru", "qwerty", status.HTTP_200_OK),
  ("user@mail.ru", "qwerty2", status.HTTP_401_UNAUTHORIZED),
  ("user1@mail.ru", "qwerty", status.HTTP_401_UNAUTHORIZED),
])
async def test_login(client_getter: AsyncClient, email: str, password: str, status_code: int):
  payload = dict(email=email, password=password)

  response = await client_getter.post("/auth/login", json=payload)

  assert response.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize("email,is_admin,status_code", [
  ("admin@mail.ru", True, status.HTTP_200_OK),
  ("user@mail.ru", False, status.HTTP_400_BAD_REQUEST),
])
async def test_users_roles_add(
  conn_manager: _ConnectionManager, 
  client_getter: AsyncClient, 
  email: str, 
  is_admin: bool, 
  status_code: int
):
  async with conn_manager.get_session_ctx() as session:
    resp = await RolesRepository.get_role(session, AvailableRoles.ADMIN if is_admin else AvailableRoles.USER)

    assert resp is not None

    user = await UsersRepository.get_user(session, email=email)

    assert user is not None

    registerUserRole = RegisterUserRole(user_id=user.user_id, role_id=resp.role_id)

    try:
      resp = await UsersRolesRepository.add(session, registerUserRole)
    except HTTPException as e:
      assert e.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize("email, password, login_status_code, get_user_status_code", [
  ("admin@mail.ru", "qwerty", status.HTTP_200_OK, status.HTTP_200_OK),
  ("user@mail.ru", "qwerty", status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED),
])
async def test_get_all_users(
  client_getter: AsyncClient, 
  email: str, password: str, 
  login_status_code: int, 
  get_user_status_code:int
):
  payload = dict(email=email, password=password)

  resp = await client_getter.post("/auth/login", json=payload)

  assert resp.status_code == login_status_code

  current_user = resp.json()

  access_token = current_user.get("access_token")

  assert access_token is not None

  headers = {
    "Authorization": f"Bearer {access_token}"
  }

  resp = await client_getter.get("/users", headers=headers)

  assert resp.status_code == get_user_status_code