
from dataclasses import dataclass
from typing import Any
from auth.models import AccessTokenData
from auth.utils import create_access_token, decode_token, get_roles_from


def test_jwt_tokens_data():
  data = {"user_id": 1, "roles": "admin superadmin"}

  token = create_access_token(data)
  decoded = decode_token(token)

  for key in data:
    assert decoded.get(key) is not None
    assert decoded.get(key) == data[key]


def test_get_roles_from():
  
  @dataclass
  class TestCase:
    want: list[str]
    payload: dict[str, str]
    name: str

  test_cases: list[TestCase] = [
    TestCase(name="Test #1", payload={"data1": "1", "roles": "admin superadmin"}, want=["admin", "superadmin"]),
    TestCase(name="Test #2", payload={}, want=[]),
  ]
  
  for test_case in test_cases:
    assert get_roles_from(test_case.payload) == test_case.want


def test_AccessTokenData_serialization():
  
  @dataclass
  class TestCase:
    want: dict[str, Any]
    accessTokenData: AccessTokenData
    
  test_cases: list[TestCase] = [
    TestCase(accessTokenData=AccessTokenData(user_id=1, roles=[]), want={"user_id":1, "roles": ""}),
    TestCase(
      accessTokenData=AccessTokenData(user_id=1, roles=["admin", "superadmin"]), 
      want={"user_id":1, "roles": "admin superadmin"}
    ),
  ]
  
  for test_case in test_cases:
    assert test_case.accessTokenData.model_dump() == test_case.want