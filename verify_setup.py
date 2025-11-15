"""
Setup verification script
Checks if everything is configured correctly before deployment
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"  ✅ {description}: Found")
        return True
    else:
        print(f"  ❌ {description}: Missing")
        return False

def check_env_var(var_name, allow_default=False):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    
    if not value:
        print(f"  ❌ {var_name}: Not set")
        return False
    
    # Check for default/placeholder values
    defaults = ["your_", "your-", "ghp_your", "AIza"]
    if not allow_default and any(d in value for d in defaults):
        print(f"  ⚠️  {var_name}: Still using default value")
        return False
    
    # Mask the value for security
    if len(value) > 10:
        masked = value[:4] + "..." + value[-4:]
    else:
        masked = "***"
    
    print(f"  ✅ {var_name}: Set ({masked})")
    return True

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"  ✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ⚠️  Python version: {version.major}.{version.minor}.{version.micro} (3.11+ recommended)")
        return False

def check_imports():
    """Check if required packages are installed"""
    packages = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "github": "PyGithub",
        "httpx": "HTTPX",
        "google.generativeai": "Google Generative AI",
        "dotenv": "python-dotenv"
    }
    
    all_ok = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"  ✅ {name}: Installed")
        except ImportError:
            print(f"  ❌ {name}: Not installed")
            all_ok = False
    
    return all_ok

def main():
    print("\n" + "="*60)
    print("🔍 TDS PROJECT 1 - SETUP VERIFICATION")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    all_checks_passed = True
    
    # Check Python version
    print("\n📦 Python Version:")
    if not check_python_version():
        all_checks_passed = False
    
    # Check required files
    print("\n📁 Required Files:")
    required_files = [
        ("app/main.py", "Main application"),
        ("app/task_processor.py", "Task processor"),
        ("app/llm_handler.py", "LLM handler"),
        ("app/github_manager.py", "GitHub manager"),
        ("app/notifier.py", "Notifier"),
        ("requirements.txt", "Requirements"),
        (".env", "Environment variables"),
        ("README.md", "README"),
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check environment variables
    print("\n🔐 Environment Variables:")
    env_vars = [
        "GITHUB_TOKEN",
        "GITHUB_USERNAME",
        "GEMINI_API_KEY",
        "USER_SECRET"
    ]
    
    for var in env_vars:
        if not check_env_var(var):
            all_checks_passed = False
    
    # Check installed packages
    print("\n📦 Python Packages:")
    if not check_imports():
        all_checks_passed = False
        print("\n  💡 Install packages with: pip install -r requirements.txt")
    
    # Check app structure
    print("\n🏗️  Application Structure:")
    app_files = [
        "app/__init__.py",
        "app/main.py",
        "app/task_processor.py",
        "app/llm_handler.py",
        "app/github_manager.py",
        "app/notifier.py"
    ]
    
    for filepath in app_files:
        check_file_exists(filepath, filepath)
    
    # Final summary
    print("\n" + "="*60)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print("="*60)
        print("\n🚀 You're ready to:")
        print("  1. Test locally: python test_local.py")
        print("  2. Start server: uvicorn app.main:app --reload")
        print("  3. Deploy to Render")
        print("\n📚 Next steps:")
        print("  - Read QUICKSTART.md for quick setup")
        print("  - Read DEPLOYMENT_GUIDE.md for deployment")
        print("  - Read WHAT_WENT_WRONG.md to understand fixes")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("="*60)
        print("\n⚠️  Please fix the issues above before proceeding")
        print("\n📚 Common fixes:")
        print("  - Missing .env: Copy .env.example to .env and fill in values")
        print("  - Missing packages: pip install -r requirements.txt")
        print("  - Wrong Python version: Install Python 3.11+")
        print("\n💡 For help, check:")
        print("  - QUICKSTART.md")
        print("  - DEPLOYMENT_GUIDE.md")
        return 1

if __name__ == "__main__":
    exit_code = main()
    print()
    sys.exit(exit_code)
