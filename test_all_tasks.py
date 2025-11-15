"""
Comprehensive test script that simulates all 3 evaluation tasks
"""
import requests
import json
import base64
import os
import time
from dotenv import load_dotenv

load_dotenv()

USER_SECRET = os.getenv("USER_SECRET")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
API_URL = "http://localhost:8000/api-endpoint"

# Sample 1x1 PNG image
SAMPLE_PNG = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

# Sample Python file with typo
EXECUTE_PY = """import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Calculate total revenew (typo here!)
total_revenew = df['revenue'].sum()

# Output result
result = {
    'total_revenue': total_revenew,
    'count': len(df)
}

print(json.dumps(result))
"""

# Sample Excel data (as CSV for simplicity)
DATA_CSV = """product,revenue,quantity
Widget A,1000,10
Widget B,2000,20
Widget C,1500,15
"""

def create_base64_attachment(content, mime_type):
    """Create base64 data URL from content"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    b64 = base64.b64encode(content).decode('utf-8')
    return f"data:{mime_type};base64,{b64}"

def test_task_1_analyze():
    """Test Task 1: Analyze (Python + Excel + GitHub Actions)"""
    print("\n" + "="*70)
    print("🧪 TEST 1: ANALYZE TASK")
    print("="*70)
    
    # Create Excel file attachment (simulated as CSV for now)
    import io
    import pandas as pd
    
    # Create a simple DataFrame
    df = pd.DataFrame({
        'product': ['Widget A', 'Widget B', 'Widget C'],
        'revenue': [1000, 2000, 1500],
        'quantity': [10, 20, 15]
    })
    
    # Save to Excel bytes
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine='openpyxl')
    excel_bytes = excel_buffer.getvalue()
    
    request_data = {
        "email": "23f3003784@ds.study.iitm.ac.in",
        "secret": USER_SECRET,
        "task": "Analyze-Test-001",
        "round": 1,
        "nonce": "test-analyze-001",
        "brief": """You are given two attachments: execute.py and data.xlsx.

- Commit execute.py after fixing the non-trivial error in it.
- Ensure it runs on Python 3.11+ with Pandas 2.3.
- Convert data.xlsx to data.csv and commit it.
- Add a GitHub Actions push workflow at .github/workflows/ci.yml that:
  - Runs ruff and shows its results in the CI log
  - Runs: python execute.py > result.json
  - Publishes result.json via GitHub Pages
- Do not commit result.json; it must be generated in CI.""",
        "checks": [
            "execute.py, data.csv, and .github/workflows/ci.yml exist",
            "result.json is NOT committed",
            "execute.py does not contain the typo 'revenew'",
            "data.csv content equals data.xlsx",
            "CI YAML has steps for ruff, executing execute.py, and Pages deploy",
            "GitHub Actions ran for this commit"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": [
            {
                "name": "execute.py",
                "url": create_base64_attachment(EXECUTE_PY, "text/x-python")
            },
            {
                "name": "data.xlsx",
                "url": f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(excel_bytes).decode('utf-8')}"
            }
        ]
    }
    
    print(f"📝 Task: {request_data['task']}")
    print(f"📎 Attachments: execute.py, data.xlsx")
    print(f"🎯 Goal: Fix Python typo, convert Excel, create CI workflow")
    
    try:
        response = requests.post(API_URL, json=request_data, timeout=10)
        print(f"\n✅ Status: {response.status_code}")
        print(f"📦 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print(f"\n🎉 Task 1 accepted!")
            print(f"🔍 Check repo: https://github.com/{GITHUB_USERNAME}/Analyze-Test-001")
            print(f"📋 Expected files:")
            print(f"   - execute.py (typo fixed)")
            print(f"   - data.csv (converted from xlsx)")
            print(f"   - .github/workflows/ci.yml")
            print(f"   - README.md")
            print(f"   - LICENSE")
            return True
        else:
            print(f"\n❌ Task 1 failed!")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_task_2_llmpages():
    """Test Task 2: LLMPages (Multiple creative files)"""
    print("\n" + "="*70)
    print("🧪 TEST 2: LLMPAGES TASK")
    print("="*70)
    
    # Create uid.txt
    uid_content = "23f3003784@ds.study.iitm.ac.in"
    
    request_data = {
        "email": "23f3003784@ds.study.iitm.ac.in",
        "secret": USER_SECRET,
        "task": "LLMPages-Test-001",
        "round": 1,
        "nonce": "test-llmpages-001",
        "brief": """
Create and publish these files as a public GitHub Pages site:

- ashravan.txt: Write a 300-400 word Brandon Sanderson short story
  on what happens to Ashravan after Shai restores him. Build up to a dramatic climax.
- dilemma.json: An autonomous vehicle must choose between hitting
  2 people or swerving to hit 1 person. Should it swerve?
  If the 2 people are criminals and the 1 person is a child, should it swerve?
  Fill in {
    people: 3,
    case_1: {swerve: bool, reason: str},
    case_2: {swerve: bool, reason: str}
  }
- about.md: Describe yourself in three words.
- pelican.svg: Generate an SVG of a pelican riding a bicycle.
- restaurant.json: Recommend a good restaurant in Delhi.
  Fill in `{city: "Delhi", lat: float, long: float, name: str, what_to_eat: str}`
- prediction.json: What will the Fed Funds rate by on December 2025?
  Fill in `{rate: float (0-1, e.g. 0.04), reason: str}`
- index.html: A homepage linking to all the above files explaining what they are.
- LICENSE: An MIT license file.
- uid.txt: Upload the uid attachment as-is
""",
        "checks": [
            "Each required file exists on GitHub",
            "uid.txt matches the attached uid.txt",
            "LICENSE contains the MIT License text",
            "index.html links to all required assets",
            "ashravan.txt meets content requirements",
            "dilemma.json matches the assigned scenario",
            "about.md contains exactly three words",
            "pelican.svg is valid SVG",
            "restaurant.json data is consistent",
            "prediction.json contains a reasonable forecast"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": [
            {
                "name": "uid.txt",
                "url": create_base64_attachment(uid_content, "text/plain")
            }
        ]
    }
    
    print(f"📝 Task: {request_data['task']}")
    print(f"📎 Attachments: uid.txt")
    print(f"🎯 Goal: Create 9 different files (story, JSON, SVG, etc.)")
    
    try:
        response = requests.post(API_URL, json=request_data, timeout=10)
        print(f"\n✅ Status: {response.status_code}")
        print(f"📦 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print(f"\n🎉 Task 2 accepted!")
            print(f"🔍 Check repo: https://github.com/{GITHUB_USERNAME}/LLMPages-Test-001")
            print(f"📋 Expected files:")
            print(f"   - ashravan.txt (300-400 word story)")
            print(f"   - dilemma.json (ethical dilemma)")
            print(f"   - about.md (3 words)")
            print(f"   - pelican.svg (SVG image)")
            print(f"   - restaurant.json (Delhi restaurant)")
            print(f"   - prediction.json (Fed rate)")
            print(f"   - index.html (links to all)")
            print(f"   - LICENSE (MIT)")
            print(f"   - uid.txt (attachment)")
            return True
        else:
            print(f"\n❌ Task 2 failed!")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_task_3_sharevolume():
    """Test Task 3: ShareVolume (SEC API + Dynamic page)"""
    print("\n" + "="*70)
    print("🧪 TEST 3: SHAREVOLUME TASK")
    print("="*70)
    
    # Create uid.txt
    uid_content = "23f3003784@ds.study.iitm.ac.in"
    
    request_data = {
        "email": "23f3003784@ds.study.iitm.ac.in",
        "secret": USER_SECRET,
        "task": "ShareVolume-Test-001",
        "round": 1,
        "nonce": "test-sharevolume-001",
        "brief": """Your assigned company: APA Corporation (APA), CIK 0001841666.

Fetch https://data.sec.gov/api/xbrl/companyconcept/CIK0001841666/dei/EntityCommonStockSharesOutstanding.json (set a descriptive User-Agent per SEC guidance).
Read `.entityName`. Filter `.units.shares[]` for entries whose `fy` > "2020" and
includes a numeric `val`.
Save `data.json` with this structure:
`{"entityName": "APA Corporation", "max": {"val": ..., "fy": ...}, "min": {"val": ..., "fy": ...}}`
where `max` and `min` refer to the highest and lowest `.val`. Break ties however you like.

Render a visually appealing `index.html` where:
- `<title>` and `<h1>` must include the live `entityName`.
- The max/min figures are clearly marked with these IDs:
  `share-entity-name`,
  `share-max-value`, `share-max-fy`,
  `share-min-value`, `share-min-fy`.

If the page is opened as `index.html?CIK=0001018724` (or any other 10-digit CIK),
`fetch()` from the SEC endpoint for that CIK using any proxy, e.g. AIPipe,
replace every ID listed above and the title and H1 without reloading the page.

Also commit the attachment uid.txt as-is.""",
        "checks": [
            "Each required file exists on GitHub",
            "uid.txt matches the attached uid.txt",
            "LICENSE contains the MIT License text",
            "data.json exists and is valid JSON",
            "data.json has 'entityName' field matching 'APA Corporation'",
            "data.json has 'max' and 'min' objects with 'val' and 'fy' fields",
            "index.html exists and is valid HTML",
            "index.html has required element IDs",
            "index.html supports ?CIK= query parameter",
            "index.html uses fetch() API"
        ],
        "evaluation_url": "https://httpbin.org/post",
        "attachments": [
            {
                "name": "uid.txt",
                "url": create_base64_attachment(uid_content, "text/plain")
            }
        ]
    }
    
    print(f"📝 Task: {request_data['task']}")
    print(f"📎 Attachments: uid.txt")
    print(f"🎯 Goal: Fetch SEC API, create data.json, dynamic HTML with ?CIK=")
    
    try:
        response = requests.post(API_URL, json=request_data, timeout=10)
        print(f"\n✅ Status: {response.status_code}")
        print(f"📦 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print(f"\n🎉 Task 3 accepted!")
            print(f"🔍 Check repo: https://github.com/{GITHUB_USERNAME}/ShareVolume-Test-001")
            print(f"📋 Expected files:")
            print(f"   - data.json (SEC data with max/min)")
            print(f"   - index.html (with specific IDs, ?CIK= support)")
            print(f"   - LICENSE (MIT)")
            print(f"   - uid.txt (attachment)")
            print(f"   - README.md")
            return True
        else:
            print(f"\n❌ Task 3 failed!")
            return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🚀 TDS PROJECT 1 - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print(f"\n📍 API URL: {API_URL}")
    print(f"👤 GitHub User: {GITHUB_USERNAME}")
    print(f"🔐 Secret: {'*' * len(USER_SECRET)}")
    
    print("\n" + "="*70)
    print("⚠️  IMPORTANT: Make sure your server is running!")
    print("   uvicorn app.main:app --reload")
    print("="*70)
    
    input("\nPress Enter to start testing...")
    
    results = []
    
    # Test all 3 tasks
    print("\n🧪 Running all 3 evaluation tasks...\n")
    
    results.append(("Analyze", test_task_1_analyze()))
    time.sleep(2)  # Wait between tests
    
    results.append(("LLMPages", test_task_2_llmpages()))
    time.sleep(2)
    
    results.append(("ShareVolume", test_task_3_sharevolume()))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for task_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {task_name}")
    
    print(f"\n🎯 Score: {passed}/{total} tasks accepted")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n📋 Next steps:")
        print("   1. Wait 2-3 minutes for processing")
        print("   2. Check GitHub repos:")
        print(f"      - https://github.com/{GITHUB_USERNAME}/Analyze-Test-001")
        print(f"      - https://github.com/{GITHUB_USERNAME}/LLMPages-Test-001")
        print(f"      - https://github.com/{GITHUB_USERNAME}/ShareVolume-Test-001")
        print("   3. Verify files are committed")
        print("   4. Check GitHub Pages are enabled")
        print("   5. Visit Pages URLs:")
        print(f"      - https://{GITHUB_USERNAME}.github.io/Analyze-Test-001/")
        print(f"      - https://{GITHUB_USERNAME}.github.io/LLMPages-Test-001/")
        print(f"      - https://{GITHUB_USERNAME}.github.io/ShareVolume-Test-001/")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("   - Verify server is running")
        print("   - Check .env configuration")
        print("   - Review server logs for errors")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
