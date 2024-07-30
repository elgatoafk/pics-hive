import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

from backend.main import app  # Import your FastAPI app
from backend.src.util.schemas import user as schema_user
from backend.src.util.crud import user as crud_user
from backend.src.util.db import get_db
from backend.src.config.security import get_current_active_user

# Sample data
sample_user = schema_user.User(id=1, email="test5@example.com", disabled=False, role="admin")
sample_update_user = schema_user.User(id=1, email="newemail@example.com", disabled=False, role="user")

# Override the dependency to use a mock database session
@pytest.fixture
def client():
    app.dependency_overrides[get_db] = async_mock_get_db
    app.dependency_overrides[get_current_active_user] = mock_current_user
    with TestClient(app) as client:
        yield client

async def async_mock_get_db():
    yield AsyncMock(spec=AsyncSession)

def mock_current_user():
    return schema_user.User(id=1, email="test5@example.com", disabled=False, role="admin")

# Mock CRUD functions
crud_user.get_users = AsyncMock(return_value=[sample_user])
crud_user.get_user = AsyncMock(side_effect=lambda db, user_id: sample_user if user_id == 1 else None)
crud_user.update_user = AsyncMock(return_value=sample_update_user)
crud_user.delete_user = AsyncMock(return_value=sample_user)

# Test read_users
@pytest.mark.asyncio
async def test_read_users(client):
    response = client.get("/")
    print(response.json())  # Add debugging info
    assert response.status_code == 200
    assert response.json() == [sample_user.dict()]

# Test read_user
@pytest.mark.asyncio
async def test_read_user(client):
    response = client.get("/1")
    print(response.json())  # Add debugging info
    assert response.status_code == 200
    assert response.json() == sample_user.dict()

# Test update_user
@pytest.mark.asyncio
async def test_update_user(client):
    update_data = {"email": "newemail@example.com", "role": "user"}
    response = client.put("/1", json=update_data)
    #print(response.json())  # Add debugging info
    assert response.status_code == 200
    assert response.json()["email"] == "newemail@example.com"
    assert response.json()["role"] == "user"  # Check role attribute

# Test delete_user
@pytest.mark.asyncio
async def test_delete_user(client):
    response = client.delete("/1")
    print(response.json())  
    assert response.status_code == 200
    assert response.json() == sample_user.dict() 
