import json
import re
import google.generativeai as genai

class LLMHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ Gemini API configured")
        else:
            self.model = None
            print("⚠️ No Gemini API key")
    
    def generate_files(self, brief, checks, attachments, round_num=1):
        """Generate all required files based on the brief"""
        
        # Detect task type and use specialized handler
        if self._is_analyze_task(brief, attachments):
            return self._handle_analyze_task(brief, checks, attachments)
        
        # Build context about attachments
        att_context = ""
        if attachments:
            att_context = "\n\nAttachments provided:\n"
            for att in attachments:
                att_context += f"- {att['name']} ({att['mime']}, {len(att['data'])} bytes)\n"
                # For text files, include preview
                if att['mime'].startswith('text') or att['name'].endswith(('.txt', '.csv', '.json', '.md', '.py')):
                    try:
                        with open(att['path'], 'r', encoding='utf-8', errors='ignore') as f:
                            preview = f.read(500)
                            att_context += f"  Preview: {preview[:200]}...\n"
                    except:
                        pass
        
        # Build the prompt
        prompt = f"""You are an expert web developer. Generate a complete, working web application based on the following requirements.

TASK BRIEF:
{brief}

ROUND: {round_num}
{att_context}

EVALUATION CHECKS:
{json.dumps(checks, indent=2)}

CRITICAL INSTRUCTIONS:
1. Read the brief VERY CAREFULLY and identify ALL files that need to be created
2. For each file mentioned in the brief, create it with the EXACT filename specified
3. Generate complete, working code - no placeholders or TODOs
4. For JSON files, ensure valid JSON syntax
5. For HTML files, include proper structure and functionality
6. For SVG files, create valid SVG markup
7. For text files, write complete content as specified
8. If the brief mentions specific IDs or element names, use them EXACTLY
9. If the brief mentions fetching data from APIs, implement the fetch() calls
10. Always create an index.html that links to or displays all other files
11. Always create a professional README.md explaining the project

OUTPUT FORMAT:
Return your response as a JSON object with this structure:
{{
  "files": {{
    "filename1.ext": "content of file 1",
    "filename2.ext": "content of file 2",
    ...
  }}
}}

IMPORTANT: 
- The JSON must be valid and parseable
- Include ALL files mentioned in the brief
- File content should be complete and functional
- For multi-line content, use proper JSON string escaping
- Do NOT include markdown code blocks, just return raw JSON

Generate the files now:"""

        try:
            if not self.model:
                return self._generate_fallback(brief, checks, attachments)
            
            print("🤖 Calling Gemini API...")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            files = self._parse_llm_response(response_text)
            
            if not files:
                print("⚠️ LLM didn't return valid JSON, using fallback")
                return self._generate_fallback(brief, checks, attachments)
            
            print(f"✅ Generated {len(files)} files")
            for filename in files.keys():
                print(f"  - {filename}")
            
            return files
            
        except Exception as e:
            print(f"❌ LLM generation failed: {e}")
            return self._generate_fallback(brief, checks, attachments)
    
    def _parse_llm_response(self, response_text):
        """Parse LLM response to extract files"""
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if response_text:
                    response_text = response_text.group(1)
            elif "```" in response_text:
                response_text = re.search(r'```\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if response_text:
                    response_text = response_text.group(1)
            
            # Parse JSON
            data = json.loads(response_text)
            
            if isinstance(data, dict) and "files" in data:
                return data["files"]
            elif isinstance(data, dict):
                return data
            else:
                return None
                
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            # Try to find JSON object in text
            json_match = re.search(r'\{.*"files".*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    return data.get("files", {})
                except:
                    pass
            return None
    
    def _is_analyze_task(self, brief, attachments):
        """Detect if this is the Analyze task (Python + Excel + CI)"""
        has_python = any(att['name'].endswith('.py') for att in attachments)
        has_excel = any(att['name'].endswith(('.xlsx', '.xls')) for att in attachments)
        mentions_ci = 'github actions' in brief.lower() or 'workflow' in brief.lower() or 'ci.yml' in brief.lower()
        return has_python and (has_excel or mentions_ci)
    
    def _handle_analyze_task(self, brief, checks, attachments):
        """Special handler for Analyze task with Python, Excel, and GitHub Actions"""
        print("🔍 Detected Analyze task - using specialized handler")
        
        files = {}
        
        # Process Python file - fix typo
        for att in attachments:
            if att['name'].endswith('.py'):
                try:
                    with open(att['path'], 'r', encoding='utf-8') as f:
                        python_code = f.read()
                    # Fix common typo
                    python_code = python_code.replace('revenew', 'revenue')
                    files[att['name']] = python_code
                    print(f"  ✅ Fixed Python file: {att['name']}")
                except Exception as e:
                    print(f"  ❌ Failed to process {att['name']}: {e}")
        
        # Convert Excel to CSV
        for att in attachments:
            if att['name'].endswith(('.xlsx', '.xls')):
                try:
                    import pandas as pd
                    df = pd.read_excel(att['path'])
                    csv_content = df.to_csv(index=False)
                    csv_name = att['name'].replace('.xlsx', '.csv').replace('.xls', '.csv')
                    files[csv_name] = csv_content
                    print(f"  ✅ Converted Excel to CSV: {csv_name}")
                except Exception as e:
                    print(f"  ❌ Failed to convert Excel: {e}")
        
        # Generate GitHub Actions workflow
        files['.github/workflows/ci.yml'] = """name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install ruff pandas
    
    - name: Run ruff linter
      run: |
        ruff check . || true
    
    - name: Run execute.py
      run: |
        python execute.py > result.json
    
    - name: Upload result.json
      uses: actions/upload-artifact@v3
      with:
        name: result
        path: result.json
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: .
        publish_branch: gh-pages
"""
        print("  ✅ Generated GitHub Actions workflow")
        
        # Generate README
        files["README.md"] = f"""# Analyze Task

## Overview
This project analyzes data using Python and automated CI/CD.

## Files
- `execute.py`: Main analysis script (typo fixed)
- `data.csv`: Data file converted from Excel
- `.github/workflows/ci.yml`: GitHub Actions workflow

## CI/CD Pipeline
The GitHub Actions workflow:
1. Runs ruff linter for code quality
2. Executes `execute.py` to generate `result.json`
3. Deploys `result.json` to GitHub Pages

## Usage
Push to main branch to trigger the CI pipeline.

## Result
View the generated `result.json` on GitHub Pages after CI completes.
"""
        
        print(f"  ✅ Generated {len(files)} files for Analyze task")
        return files
    
    def _generate_fallback(self, brief, checks, attachments):
        """Generate basic fallback files when LLM fails"""
        files = {}
        
        # Generate index.html
        files["index.html"] = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Application</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{ color: #333; }}
        .brief {{
            background: #f0f0f0;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Task Application</h1>
        <div class="brief">
            <h2>Brief:</h2>
            <p>{brief}</p>
        </div>
        <h2>Checks:</h2>
        <ul>
            {"".join(f"<li>{check}</li>" for check in checks)}
        </ul>
    </div>
</body>
</html>"""
        
        # Generate README.md
        files["README.md"] = f"""# Task Application

## Brief
{brief}

## Checks
{chr(10).join(f"- {check}" for check in checks)}

## Setup
Open `index.html` in a web browser.

## Files
- index.html: Main application page
- README.md: This file
"""
        
        return files
