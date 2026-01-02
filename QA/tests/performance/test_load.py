"""
Performance and Load Testing using Locust
"""

from locust import HttpUser, task, between, events
import random
import json
from io import BytesIO
from PIL import Image


class CrimeDetectionUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts - login."""
        # Register user
        username = f"loadtest_user_{random.randint(1, 10000)}"
        response = self.client.post("/api/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "LoadTest@123",
            "role": "operator"
        })
        
        # Login
        login_response = self.client.post("/api/auth/login", json={
            "username": username,
            "password": "LoadTest@123"
        })
        
        if login_response.status_code == 200:
            data = json.loads(login_response.text)
            self.token = data.get("access_token")
        else:
            self.token = None
    
    @task(3)
    def view_criminals(self):
        """View criminals list - most common operation."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/criminals", headers=headers)
    
    @task(2)
    def view_criminal_detail(self):
        """View specific criminal details."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            # Random criminal ID
            criminal_id = random.randint(1, 100)
            self.client.get(f"/api/criminals/{criminal_id}", headers=headers)
    
    @task(1)
    def search_criminals(self):
        """Search/filter criminals."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            status = random.choice(['wanted', 'caught', 'released'])
            self.client.get(f"/api/criminals?status={status}", headers=headers)
    
    @task(1)
    def create_criminal(self):
        """Create new criminal."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            criminal_data = {
                "name": f"Load Test Criminal {random.randint(1, 10000)}",
                "age": random.randint(18, 70),
                "gender": random.choice(['Male', 'Female']),
                "crime_type": random.choice(['Theft', 'Assault', 'Fraud']),
                "status": "wanted",
                "danger_level": random.choice(['low', 'medium', 'high'])
            }
            self.client.post("/api/criminals", json=criminal_data, headers=headers)
    
    @task(1)
    def upload_detection(self):
        """Upload image for detection - resource intensive."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Create small test image
            img = Image.new('RGB', (200, 200), color='blue')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            files = {
                'image': ('test.jpg', img_bytes, 'image/jpeg')
            }
            data = {
                'location': 'Load Test Location',
                'camera_id': f'CAM-{random.randint(1, 100)}'
            }
            
            self.client.post(
                "/api/detection/upload",
                files=files,
                data=data,
                headers=headers
            )
    
    @task(2)
    def view_dashboard(self):
        """View dashboard statistics."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/dashboard/stats", headers=headers)


class AdminUser(HttpUser):
    """Simulated admin user with higher privileges."""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login as admin."""
        # Would need pre-created admin account
        login_response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "Admin@123"
        })
        
        if login_response.status_code == 200:
            data = json.loads(login_response.text)
            self.token = data.get("access_token")
        else:
            self.token = None
    
    @task(2)
    def manage_users(self):
        """Admin user management tasks."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            # Get users list
            self.client.get("/api/users", headers=headers)
    
    @task(3)
    def review_detections(self):
        """Review detection logs."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/detections", headers=headers)
    
    @task(2)
    def review_alerts(self):
        """Review alerts."""
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/alerts", headers=headers)


# Performance Benchmarks
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("Starting load test...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops - print results."""
    print("\n" + "="*50)
    print("Load Test Complete!")
    print("="*50)
    
    stats = environment.stats
    
    print(f"\nTotal Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min Response Time: {stats.total.min_response_time:.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per Second: {stats.total.total_rps:.2f}")
    
    # Performance targets
    print("\n" + "="*50)
    print("Performance Targets:")
    print("="*50)
    print(f"✓ Average response time < 1000ms: {stats.total.avg_response_time < 1000}")
    print(f"✓ 95th percentile < 2000ms: {stats.total.get_response_time_percentile(0.95) < 2000}")
    print(f"✓ Failure rate < 1%: {(stats.total.num_failures / stats.total.num_requests * 100) < 1 if stats.total.num_requests > 0 else True}")
    print(f"✓ Requests/sec > 10: {stats.total.total_rps > 10}")


# Run locust with:
# locust -f test_performance.py --host=http://localhost:5000 --users 50 --spawn-rate 5 --run-time 5m
