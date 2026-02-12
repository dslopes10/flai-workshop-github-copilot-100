"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    global activities
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Check structure of one activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify student was added
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        # First signup
        response1 = client.post(
            "/activities/Gym Class/signup?email=test@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup (should fail)
        response2 = client.post(
            "/activities/Gym Class/signup?email=test@mergington.edu"
        )
        assert response2.status_code == 400
        
        data = response2.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_activity_full(self, client):
        """Test signup when activity is at max capacity"""
        # Create an activity with max 2 participants and 2 already signed up
        activities["Full Activity"] = {
            "description": "Test activity",
            "schedule": "Test",
            "max_participants": 2,
            "participants": ["student1@mergington.edu", "student2@mergington.edu"]
        }
        
        # Try to add one more
        response = client.post(
            "/activities/Full Activity/signup?email=student3@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "full" in data["detail"].lower()


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_remove_participant_success(self, client):
        """Test successful removal of a participant"""
        response = client.delete(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        
        # Verify student was removed
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_remove_participant_nonexistent_activity(self, client):
        """Test removal from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_remove_participant_not_in_activity(self, client):
        """Test removal of a participant who is not in the activity"""
        response = client.delete(
            "/activities/Chess Club/signup?email=notaparticipant@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_only_participant(self, client):
        """Test removal when participant is the only one in activity"""
        # Create activity with one participant
        activities["Solo Activity"] = {
            "description": "Test",
            "schedule": "Test",
            "max_participants": 10,
            "participants": ["solo@mergington.edu"]
        }
        
        response = client.delete(
            "/activities/Solo Activity/signup?email=solo@mergington.edu"
        )
        assert response.status_code == 200
        assert len(activities["Solo Activity"]["participants"]) == 0


class TestIntegrationScenarios:
    """Integration tests for common user workflows"""
    
    def test_signup_and_remove_workflow(self, client):
        """Test the complete workflow of signing up and then removing"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify in activity
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Remove
        remove_response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )
        assert remove_response.status_code == 200
        
        # Verify removed
        activities_response2 = client.get("/activities")
        assert email not in activities_response2.json()[activity]["participants"]
    
    def test_multiple_students_signup(self, client):
        """Test multiple students signing up for the same activity"""
        activity = "Gym Class"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        initial_count = len(activities[activity]["participants"])
        
        for student in students:
            response = client.post(
                f"/activities/{activity}/signup?email={student}"
            )
            assert response.status_code == 200
        
        # Verify all were added
        final_count = len(activities[activity]["participants"])
        assert final_count == initial_count + len(students)
        
        for student in students:
            assert student in activities[activity]["participants"]
