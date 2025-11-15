import os
import httpx
from datetime import datetime
from github import Github, Auth, GithubException

class GitHubManager:
    def __init__(self, token, username):
        self.token = token
        self.username = username
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.user = self.github.get_user()
    
    def create_repository(self, repo_name, description=""):
        """Create or get existing repository"""
        try:
            repo = self.user.get_repo(repo_name)
            print(f"📁 Repository exists: {repo.full_name}")
            return repo
        except GithubException:
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=False,
                auto_init=False
            )
            print(f"📁 Created repository: {repo.full_name}")
            return repo
    
    def commit_file(self, repo, file_path, content, message):
        """Create or update a text file"""
        try:
            # Try to get existing file
            try:
                existing = repo.get_contents(file_path)
                repo.update_file(file_path, message, content, existing.sha)
                print(f"  ✅ Updated: {file_path}")
            except GithubException as e:
                if e.status == 404:
                    repo.create_file(file_path, message, content)
                    print(f"  ✅ Created: {file_path}")
                else:
                    raise
        except Exception as e:
            print(f"  ❌ Failed to commit {file_path}: {e}")
    
    def commit_binary_file(self, repo, file_path, binary_data, message):
        """Create or update a binary file"""
        try:
            try:
                existing = repo.get_contents(file_path)
                repo.update_file(file_path, message, binary_data, existing.sha)
                print(f"  ✅ Updated binary: {file_path}")
            except GithubException as e:
                if e.status == 404:
                    repo.create_file(file_path, message, binary_data)
                    print(f"  ✅ Created binary: {file_path}")
                else:
                    raise
        except Exception as e:
            print(f"  ❌ Failed to commit binary {file_path}: {e}")
    
    def enable_pages(self, repo_name, branch="main"):
        """Enable GitHub Pages"""
        url = f"https://api.github.com/repos/{self.username}/{repo_name}/pages"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {"source": {"branch": branch, "path": "/"}}
        
        try:
            response = httpx.post(url, headers=headers, json=data, timeout=30.0)
            if response.status_code in (201, 204, 409):  # 409 = already enabled
                print(f"  ✅ GitHub Pages enabled")
                return True
            else:
                print(f"  ⚠️ Pages API returned: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Failed to enable Pages: {e}")
            return False
    
    def generate_mit_license(self):
        """Generate MIT LICENSE text"""
        year = datetime.utcnow().year
        return f"""MIT License

Copyright (c) {year} {self.username}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
