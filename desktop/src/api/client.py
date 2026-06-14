import requests
import os
import mimetypes
from typing import Optional, Dict, List, Any

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.current_user = None
        self.last_error = None
        self._username = None
        self._password = None
        self.session = requests.Session()
    
    def clear_auth(self) -> None:
        self.token = None
        self.current_user = None
        self._username = None
        self._password = None

    def refresh_auth(self) -> bool:
        if not self._username or not self._password:
            return False
        return self.login(self._username, self._password)

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
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            print(f"Response status code: {response.status_code}")
            print(f"Response text: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                self.token = result.get("access_token")
                self._username = username
                self._password = password
                print(f"Login successful, token: {self.token[:20]}..." if self.token else "No token received")
                self.current_user = self.get_current_user()
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
    
    def get_users(self) -> List[Dict[str, Any]]:
        """Get all users for assignee selection"""
        try:
            response = requests.get(
                f"{self.base_url}/api/users/",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get users error: {e}")
        return []
    
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
                   priority: str = "medium", status: str = "todo", assignee_ids: Optional[List[int]] = None,
                   assignee_emails: Optional[List[str]] = None, due_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
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
                "project_id": project_id,
                "assignee_ids": assignee_ids or [],
                "assignee_emails": assignee_emails or [],
            }
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
    
    def get_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a single task with assignees"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks/{task_id}",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get task error: {e}")
        return None
    
    def update_task(self, task_id: int, **fields) -> Optional[Dict[str, Any]]:
        """Update task fields"""
        try:
            data = {}
            for key, value in fields.items():
                if value is not None or key in ("assignee_emails", "due_date"):
                    data[key] = value
            headers = self.get_headers()

            for attempt in range(2):
                response = requests.put(
                    f"{self.base_url}/api/tasks/{task_id}",
                    json=data,
                    headers=headers,
                )
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 401 and attempt == 0 and self.refresh_auth():
                    headers = self.get_headers()
                    continue
                self.last_error = response.text
                print(f"Update task failed: {response.status_code} - {response.text}")
                break
        except Exception as e:
            self.last_error = str(e)
            print(f"Update task error: {e}")
        return None
    
    def get_task_comments(self, task_id: int) -> List[Dict[str, Any]]:
        """Get comments for a task"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks/{task_id}/comments",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Get task comments error: {e}")
        return []
    
    def post_task_comment(
        self,
        task_id: int,
        body: str,
        file_paths: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Post a comment on a task, optionally with image attachments."""
        for attempt in range(2):
            result = self._post_task_comment_once(task_id, body, file_paths)
            if result is not None:
                return result
            if attempt == 0 and self.last_error and "401" in self.last_error and self.refresh_auth():
                continue
            break
        return None

    def _post_task_comment_once(
        self,
        task_id: int,
        body: str,
        file_paths: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base_url}/api/tasks/{task_id}/comments"
        file_handles = []
        self.last_error = None

        try:
            headers = {}
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"

            data = {"body": body or ""}
            files = []
            for path in file_paths or []:
                if not os.path.exists(path):
                    self.last_error = f"File not found: {path}"
                    return None
                mime_type = mimetypes.guess_type(path)[0] or "image/png"
                handle = open(path, "rb")
                file_handles.append(handle)
                files.append(("files", (os.path.basename(path), handle, mime_type)))

            response = requests.post(
                url,
                data=data,
                files=files if files else [("files", ("", b"", "application/octet-stream"))],
                headers=headers,
                timeout=60,
            )

            if response.status_code == 201:
                return response.json()

            self.last_error = response.text
            print(f"Post comment failed: {response.status_code} - {response.text}")
        except Exception as e:
            self.last_error = str(e)
            print(f"Post task comment error: {e}")
        finally:
            for handle in file_handles:
                handle.close()
        return None
    
    def get_attachment_url(self, attachment_id: int) -> str:
        return f"{self.base_url}/api/tasks/attachments/{attachment_id}"

    def fetch_attachment_bytes(self, attachment_id: int) -> Optional[bytes]:
        try:
            response = requests.get(
                self.get_attachment_url(attachment_id),
                headers=self.get_headers(),
            )
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Fetch attachment error: {e}")
        return None

    def update_task_status(self, task_id: int, status: str) -> Optional[Dict[str, Any]]:
        """Update task status"""
        try:
            headers = self.get_headers()
            for attempt in range(2):
                response = requests.put(
                    f"{self.base_url}/api/tasks/{task_id}",
                    json={"status": status},
                    headers=headers,
                )
                if response.status_code == 200:
                    return response.json()
                if response.status_code == 401 and attempt == 0 and self.refresh_auth():
                    headers = self.get_headers()
                    continue
                break
        except Exception as e:
            print(f"Update task status error: {e}")
        return None

    def check_backend_features(self) -> Dict[str, Any]:
        """Check if backend supports latest features."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Health check error: {e}")
        return {}