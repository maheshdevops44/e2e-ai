#!/usr/bin/env python3
"""
Simple CLI to run pytest on the latest generated Playwright script
"""

import os
import sys
import subprocess
from pathlib import Path
import glob

def find_latest_script():
    """Find the most recent generated Playwright script"""
    scripts_dir = Path("generated_scripts")
    if not scripts_dir.exists():
        print("❌ No generated_scripts directory found")
        return None
    
    # Find all generated Playwright scripts
    scripts = list(scripts_dir.glob("generated_playwright_*.py"))
    if not scripts:
        print("❌ No generated Playwright scripts found")
        return None
    
    # Get the most recent one
    latest_script = max(scripts, key=lambda x: x.stat().st_mtime)
    print(f"📁 Latest script: {latest_script.name}")
    return latest_script

def convert_to_pytest(script_content: str):
    """Convert Playwright script to pytest format"""
    # Add pytest imports and decorators
    pytest_header = '''import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import time
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Configuration from environment variables
USERNAME = os.getenv('USERNAME', 'C9G5JS')
PASSWORD = os.getenv('PASSWORD', 'Emphatic-Award1-Tinker')
PATIENT_ID = os.getenv('PATIENT_ID', '17045254')
COMMON_INTAKE_ID = os.getenv('COMMON_INTAKE_ID', '17045254')
DRUG_NDC = os.getenv('DRUG_NDC', '00074055402')
TDM_TOOL_URL = os.getenv('TDM_TOOL_URL', 'https://tdm-tool-qa.express-scripts.com/')
INTAKE_URL = os.getenv('INTAKE_URL', 'https://spcia-qa.express-scripts.com/spcia')
CLEARANCE_URL = os.getenv('CLEARANCE_URL', 'https://clearance-qa.express-scripts.com/spclr')
RXP_URL = os.getenv('RXP_URL', 'https://sprxp-qa.express-scripts.com/sprxp/')
CRM_URL = os.getenv('CRM_URL', 'https://spcrmqa-internal.express-scripts.com/spcrm88/')

def delay():
    time.sleep(5)

def handle_error(page, step, e):
    print(f"[ERROR] Step: {step} - {e}")
    screenshot(page, f"error_{step}")
    traceback.print_exc()
    pytest.fail(f"Test failed at step {step}: {e}")

def login(page, url, step_prefix):
    try:
        page.goto(url, timeout=60000)
        delay()
        screenshot(page, f"{step_prefix}_login_page")
        page.fill("#txtUserID", USERNAME)
        page.fill("#txtPassword", PASSWORD)
        screenshot(page, f"{step_prefix}_credentials_filled")
        page.click("#sub")
        delay()
        screenshot(page, f"{step_prefix}_after_login")
    except Exception as e:
        handle_error(page, f"{step_prefix}_login", e)

'''
    
    # Replace main() function with pytest test function
    script_content = script_content.replace('def main():', '@pytest.mark.slow\ndef test_workflow():')
    
    # Remove the main() call at the end if it exists
    script_content = script_content.replace('if __name__ == "__main__":\n    main()', '')
    
    # Combine header with modified script
    pytest_script = pytest_header + script_content
    
    return pytest_script

def main():
    print("🚀 Running pytest on latest generated script...")
    
    # Find the latest script
    script_path = find_latest_script()
    if not script_path:
        return
    
    try:
        # Read the script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Convert to pytest format
        pytest_content = convert_to_pytest(script_content)
        
        # Create pytest file
        temp_dir = Path("temp_pytest")
        temp_dir.mkdir(exist_ok=True)
        
        pytest_file = temp_dir / f"test_{script_path.stem}.py"
        with open(pytest_file, 'w') as f:
            f.write(pytest_content)
        
        print(f"✅ Created pytest file: {pytest_file}")
        
        # Run pytest
        print(f"🔄 Running pytest...")
        result = subprocess.run(
            ["python", "-m", "pytest", str(pytest_file), "-v", "-x","--tb=short"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        print(f"✅ Pytest completed with return code: {result.returncode}")
        
        if result.stdout:
            print("\n📋 Pytest Output:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ Pytest Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Test execution successful!")
        else:
            print("❌ Test execution failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
