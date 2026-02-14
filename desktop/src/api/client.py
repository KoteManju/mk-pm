import requests
from typing import Optional, Dict, List, Any
import json

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self, username: str, password: str) -> bool:
        """Login and get access token"""
        try:
            print(f"Attempting login for user: {username}")
            print(f"API URL: {self.base_url}/api/auth/token")
            
            data = {
                "username": username,
                "password": password
            }
            response = requests.post(
                f"{self.base_url}/api/auth/token",
                data=data,  # Form data for OAuth2
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                print(f"Login successful, token: {self.token[:20]}..." if self.token else "No token received")
                return True
            else:
                print(f"Login failed with status: {response.status_code}, response: {response.text}")
        except Exception as e:
            print(f"Login error: {e}")
            import traceback
            traceback.print_exc()
        return False
    
    def register(self, username: str, email: str, password: str, full_name: str = "") -> bool:
        """Register new user"""
        try:
            data = {
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name
            }
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=data,
                headers=self.get_headers()
            )
            return response.status_code == 201
        except Exception as e:
            print(f"Registration error: {e}")
        return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current user info"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/me",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get current user error: {e}")
        return None
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        try:
            response = requests.get(
                f"{self.base_url}/api/projects/",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get projects error: {e}")
        return []
    
    def create_project(self, name: str, description: str = "") -> Optional[Dict[str, Any]]:
        """Create a new project"""
        try:
            data = {
                "name": name,
                "description": description
            }
            response = requests.post(
                f"{self.base_url}/api/projects/",
                json=data,
                headers=self.get_headers()
            )
            if response.status_code == 201:
                return response.json()
        except Exception as e:
            print(f"Create project error: {e}")
        return None
    
    def get_tasks(self, project_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get tasks, optionally filtered by project"""
        try:
            url = f"{self.base_url}/api/tasks/"
            if project_id:
                url += f"?project_id={project_id}"
            
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get tasks error: {e}")
        return []
    
    def create_task(self, title: str, description: str = "", project_id: Optional[int] = None,
                   priority: str = "medium", status: str = "todo", assignee_id: Optional[int] = None,
                   due_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new task with detailed information"""
        try:
            # Get a default project if none specified
            if project_id is None:
                projects = self.get_projects()
                if projects:
                    project_id = projects[0]["id"]
                else:
                    # Create a default project if none exists
                    default_project = self.create_project("Default Project", "Auto-created project for tasks")
                    if default_project:
                        project_id = default_project["id"]
                    else:
                        print("Error: Could not create or find a project for the task")
                        return None
            
            data = {
                "title": title,
                "description": description,
                "priority": priority,
                "status": status,
                "project_id": project_id
            }
            if assignee_id:
                data["assignee_id"] = assignee_id
            if due_date:
                data["due_date"] = due_date
            
            print(f"Creating task with data: {data}")
                
            response = requests.post(
                f"{self.base_url}/api/tasks/",
                json=data,
                headers=self.get_headers()
            )
            
            print(f"Task creation response: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Create task failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Create task error: {e}")
            import traceback
            traceback.print_exc()
        return None
    
    def update_task_status(self, task_id: int, status: str) -> Optional[Dict[str, Any]]:
        """Update task status"""
        try:
            data = {
                "status": status
            }
            response = requests.put(
                f"{self.base_url}/api/tasks/{task_id}",
                json=data,
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Update task status error: {e}")
        return None