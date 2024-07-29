import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from backend.main import app
from backend.src.util.schemas.user import UserCreate, User
from backend.src.util.crud.user import create_user, get_user_by_email, delete_user
from backend.src.util.db import get_db
from backend.src.config.security import get_current_user
from backend.src.config.jwt import create_access_token
from backend.src.util.crud.token import add_token_to_blacklist
from backend.src.util.crud import user as crud_user

# Sample data with all required fields
sample_user_create = {"email": "test@example.com", "password": "password123", "disabled":"False", "role": "admin"}
sample_user = User(id=1, email="test@example.com", disabled=False, role="admin")
user_id = None

# Override the dependency to use a mock database session
@pytest.fixture
def client():
    app.dependency_overrides[get_db] = async_mock_get_db
    app.dependency_overrides[get_current_user] = mock_current_user
    with TestClient(app) as client:
        yield client

async def async_mock_get_db():
    # Create an AsyncMock for the database session
    db = AsyncMock(spec=AsyncSession)
    db.execute = AsyncMock()
    return db

def mock_current_user():
    return sample_user

# Mock CRUD functions and security functions
create_user = AsyncMock(return_value=sample_user)
get_user_by_email = AsyncMock(return_value=None)
create_access_token = AsyncMock(return_value="fake_access_token")
add_token_to_blacklist = AsyncMock()
#delete_user = AsyncMock()
crud_user.delete_user = AsyncMock(return_value=sample_user)

# Test signup
@pytest.mark.asyncio
async def test_signup(client):
    # Execute the signup endpoint
    response = client.post("/signup", json=sample_user_create)
    
    # Extract the response JSON
    actual_result = response.json()
    
    # Print actual result for debugging
    print("Actual result:", actual_result)
    
    # Extract the ID from the response JSON
    global user_id 
    user_id = actual_result.get("id")
    
    # Print extracted ID for debugging
    print("Extracted User ID:", user_id)
    
    # Remove `disabled` if it exists and any other unexpected fields
    actual_result_cleaned = {k: v for k, v in actual_result.items() if k not in ["disabled", "id"]}
    
    # Expected result without ID
    expected_result = {
        "email": sample_user.email,
        "role": sample_user.role
    }
    
    # Print actual result without unexpected fields for debugging
    print("Actual result cleaned:", actual_result_cleaned)
    print("Expected result:", expected_result)
    
    assert actual_result_cleaned == expected_result

# Test delete user
#@pytest.mark.asyncio
#async def test_delete_user(client):
#    # Mock the delete_user function to simulate successful deletion
#    delete_user.return_value = None  # Simulate successful deletion
    
#    # Execute the delete endpoint
#    response = client.delete(f"/{user_id}")
    
#    # Check that the status code indicates success
#    assert response.status_code == 204  # Assuming successful deletion returns HTTP 204 No Content
    
#    # Verify the delete_user function was called with the correct user ID
#    delete_user.assert_awaited_once_with(user_id)

#    # You may also want to test handling of non-existing users or other edge cases


# Test delete_user
#@pytest.mark.asyncio
#async def test_delete_user(client):
#    print('TEST {}'.format(user_id))
#    response = client.delete("/{}".format(user_id))
#    print('TEST2')
#    print(response.json())  
#    assert response.status_code == 200
#    assert response.json() == sample_user.dict() 

