"""
Tests for the Mergington High School API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivities:
    """Tests for getting activities"""
    
    def test_get_activities(self):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check that Basketball is in activities
        assert "Basketball" in activities
        assert "description" in activities["Basketball"]
        assert "schedule" in activities["Basketball"]
        assert "max_participants" in activities["Basketball"]
        assert "participants" in activities["Basketball"]
    
    def test_get_activities_has_participants(self):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # Basketball should have alex@mergington.edu
        assert "alex@mergington.edu" in activities["Basketball"]["participants"]


class TestSignUp:
    """Tests for signing up for activities"""
    
    def test_signup_for_activity(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_duplicate_email(self):
        """Test that duplicate signup is rejected"""
        # First signup
        client.post("/activities/Tennis%20Club/signup?email=duplicate@mergington.edu")
        
        # Try to signup again with same email
        response = client.post(
            "/activities/Tennis%20Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_updates_participants(self):
        """Test that signup updates participant list"""
        email = "testuser@mergington.edu"
        activity = "Programming%20Class"
        
        # Get initial state
        response = client.get("/activities")
        initial_participants = len(response.json()["Programming Class"]["participants"])
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get updated state
        response = client.get("/activities")
        final_participants = len(response.json()["Programming Class"]["participants"])
        
        # Verify participant was added
        assert final_participants == initial_participants + 1
        assert email in response.json()["Programming Class"]["participants"]


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_from_activity(self):
        """Test successful unregister from an activity"""
        email = "unreg@mergington.edu"
        activity = "Gym%20Class"
        
        # First, sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_not_signed_up(self):
        """Test unregister for student not signed up"""
        response = client.post(
            "/activities/Basketball/unregister?email=notfound@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_updates_participants(self):
        """Test that unregister updates participant list"""
        email = "unreg2@mergington.edu"
        activity = "Chess%20Club"
        
        # Sign up first
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get state after signup
        response = client.get("/activities")
        participants_after_signup = len(response.json()["Chess Club"]["participants"])
        
        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Get state after unregister
        response = client.get("/activities")
        participants_after_unregister = len(response.json()["Chess Club"]["participants"])
        
        # Verify participant was removed
        assert participants_after_unregister == participants_after_signup - 1
        assert email not in response.json()["Chess Club"]["participants"]


class TestRootRoute:
    """Tests for root route"""
    
    def test_root_redirect(self):
        """Test that root route redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
