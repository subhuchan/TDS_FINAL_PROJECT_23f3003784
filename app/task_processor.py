import os
import json
import base64
import time
from pathlib import Path
from dotenv import load_dotenv
from app.github_manager import GitHubManager
from app.llm_handler import LLMHandler
from app.notifier import notify_evaluation

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def decode_attachments(attachments):
    """Decode base64 attachments and save to temp directory"""
    saved_files = []
    temp_dir = Path("/tmp/attachments")
    temp_dir.mkdir(exist_ok=True)
    
    for att in attachments or []:
        try:
            name = att.get("name", "file")
            url = att.get("url", "")
            
            if url.startswith("data:"):
                # Parse data URL
                header, b64_data = url.split(",", 1)
                mime_type = header.split(";")[0].replace("data:", "")
                
                # Decode base64
                file_data = base64.b64decode(b64_data)
                
                # Save file
                file_path = temp_dir / name
                with open(file_path, "wb") as f:
                    f.write(file_data)
                
                saved_files.append({
                    "name": name,
                    "path": str(file_path),
                    "data": file_data,
                    "mime": mime_type
                })
                print(f"✅ Decoded attachment: {name} ({len(file_data)} bytes)")
        except Exception as e:
            print(f"❌ Failed to decode attachment {att.get('name')}: {e}")
    
    return saved_files

def process_task_background(data):
    """Background task processor"""
    try:
        print(f"\n{'='*60}")
        print(f"🚀 Processing Task: {data.get('task')}")
        print(f"📧 Email: {data.get('email')}")
        print(f"🔄 Round: {data.get('round', 1)}")
        print(f"{'='*60}\n")
        
        task_name = data.get("task")
        round_num = data.get("round", 1)
        brief = data.get("brief", "")
        checks = data.get("checks", [])
        attachments = data.get("attachments", [])
        evaluation_url = data.get("evaluation_url")
        
        # Decode attachments
        saved_attachments = decode_attachments(attachments)
        
        # Initialize managers
        github_mgr = GitHubManager(GITHUB_TOKEN, GITHUB_USERNAME)
        llm_handler = LLMHandler(GEMINI_API_KEY)
        
        # Create or get repository
        repo = github_mgr.create_repository(task_name, f"Task: {task_name}")
        
        # Generate files using LLM
        print("🤖 Generating files with LLM...")
        generated_files = llm_handler.generate_files(
            brief=brief,
            checks=checks,
            attachments=saved_attachments,
            round_num=round_num
        )
        
        # Commit all files to GitHub
        print("📤 Committing files to GitHub...")
        for file_path, content in generated_files.items():
            github_mgr.commit_file(repo, file_path, content, f"Add {file_path}")
        
        # Commit attachments (skip if already processed by specialized handler)
        processed_files = set(generated_files.keys())
        for att in saved_attachments:
            if att["name"] not in processed_files:
                github_mgr.commit_binary_file(
                    repo, 
                    att["name"], 
                    att["data"], 
                    f"Add attachment {att['name']}"
                )
            else:
                print(f"  ⏭️  Skipped {att['name']} (already processed)")
        
        # Add MIT LICENSE
        license_text = github_mgr.generate_mit_license()
        github_mgr.commit_file(repo, "LICENSE", license_text, "Add MIT LICENSE")
        
        # Enable GitHub Pages
        print("🌐 Enabling GitHub Pages...")
        github_mgr.enable_pages(task_name)
        
        # Get commit SHA
        commits = list(repo.get_commits())
        commit_sha = commits[0].sha if commits else None
        
        # Prepare notification payload
        pages_url = f"https://{GITHUB_USERNAME}.github.io/{task_name}/"
        payload = {
            "email": data.get("email"),
            "task": task_name,
            "round": round_num,
            "nonce": data.get("nonce"),
            "repo_url": repo.html_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url
        }
        
        # Wait a bit for Pages to deploy
        print("⏳ Waiting for GitHub Pages deployment...")
        time.sleep(10)
        
        # Notify evaluation server
        print("📨 Notifying evaluation server...")
        notify_evaluation(evaluation_url, payload)
        
        print(f"\n✅ Task {task_name} completed successfully!")
        print(f"📁 Repo: {repo.html_url}")
        print(f"🌐 Pages: {pages_url}\n")
        
    except Exception as e:
        print(f"\n❌ Error processing task: {e}")
        import traceback
        traceback.print_exc()
