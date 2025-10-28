sampleTestFile = """
import time
import pytest
import os
from time import sleep
from dotenv import load_dotenv
from nodes.agent_utils import find_element_across_frames

load_dotenv()

LAN_ID = os.getenv("LAN_ID")
LAN_PASSWORD = os.getenv("LAN_PASSWORD")

# Import global remote timeout from conftest
try:
    from tests.conftest import REMOTE_TIMEOUT
except ImportError:
    REMOTE_TIMEOUT = REMOTE_TIMEOUT  # Fallback if import fails

def screenshot(page, name):
    screenshot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", 'screenshots'))
    os.makedirs(screenshot_dir, exist_ok=True)
    print(f"[SCREENSHOT] {name}.png")
    page.screenshot(path=os.path.join(screenshot_dir, f"{name}.png"))

def test_express_scripts_aws_stealth(page_with_video_and_network_monitoring):
    page = page_with_video_and_network_monitoring

    # Apply stealth techniques
    page.add_init_script(\"\"\"
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // Mock languages and plugins
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
    \"\"\")

    page.set_extra_http_headers({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua-platform": "Windows"
    })

    express_sites = [
        "https://spcrmqa-internal.express-scripts.com/spcrm88",
        "https://clearance-qa.express-scripts.com/spclr",
        "https://sprxp-qa.express-scripts.com/sprxp",
        "https://spcia-qa.express-scripts.com/spcia",
    ]

    for target in express_sites:
        try:
            print(f"[STEALTH] Testing {target}...")
            start_time = time.time()

            # Try with different wait conditions
            response = page.goto(target, wait_until="domcontentloaded", timeout=REMOTE_TIMEOUT)
            end_time = time.time()

            print(f"[STEALTH] Navigation completed in {end_time - start_time:.2f} seconds")
            print(f"[STEALTH] Response status: {response.status if response else 'No response'}")
            print(f"[STEALTH] URL after navigation: {page.url}")

            # Additional wait to see if content loads
            page.wait_for_timeout(3000)
            title = page.title()
            print(f"[STEALTH] Page title: {title}")

        except Exception as e:
            print(f"[STEALTH] Failed to navigate to {target}: {str(e)}")
            # Try alternative approach - just wait for networkidle
            try:
                print(f"[STEALTH] Trying networkidle approach for {target}...")
                response = page.goto(target, wait_until="networkidle", timeout=REMOTE_TIMEOUT)
                print(f"[STEALTH] Networkidle approach succeeded for {target}")
            except Exception as e2:
                print(f"[STEALTH] Networkidle approach also failed: {str(e2)}")
        finally:
            # Small delay between tests
            time.sleep(2)
            
    
    # Step 2: Launch and Login to CRM
    print("[LOG] Starting CRM login")
    
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD

    initial_url = "https://spcrmqa-internal.express-scripts.com/spcrm88"

    print(f"[LOG] Navigating to {initial_url}")
    page.goto(initial_url, wait_until="domcontentloaded", timeout=REMOTE_TIMEOUT)
    print("[LOG] Navigated to CRM URL")

    # Additional wait to see if content loads
    page.wait_for_timeout(3000)  

    screenshot(page, "step_1_navigated_to_crm_url.png")
    sleep(5)

    username = page.locator("#txtUserID")
    if not username:
        print("[ERROR] Username input not found")
        raise Exception("Username input not found")
    username.fill(USERNAME)
    print("[LOG] Filled username")
    screenshot(page, "step_2_filled_username.png")
    sleep(3)

    password = page.locator("#txtPassword")
    if not password:
        print("[ERROR] Password input not found")
        raise Exception("Password input not found")
    password.fill(PASSWORD)
    print("[LOG] Filled password")
    screenshot(page, "step_3_filled_password.png")
    sleep(3)

    login_btn = page.locator("#sub")
    if not login_btn:
        print("[ERROR] Login button not found")
        raise Exception("Login button not found")
    login_btn.click()
    print("[LOG] Clicked Login button")
    screenshot(page, "step_4_clicked_login.png")
    sleep(8)

def test_step_crm(page_with_video_and_network_monitoring):
    PATIENT_ID = "17164197"

    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD

    initial_url = "https://spcrmqa-internal.express-scripts.com/spcrm88"

    # Step 1: Launch and Login to CRM
    page = page_with_video_and_network_monitoring

    # Apply stealth techniques
    page.add_init_script(\"\"\"
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });

        // Mock languages and plugins
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
    \"\"\")

    page.set_extra_http_headers({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
        "sec-ch-ua-platform": "Windows"
    })

    res = page.goto(initial_url, wait_until="domcontentloaded", timeout=REMOTE_TIMEOUT)
    print("[LOG] Navigated to CRM URL", res)

    # Additional wait to see if content loads
    page.wait_for_timeout(3000)  

    screenshot(page, "step_1_navigated_to_crm_url.png")
    sleep(5)

    username = page.locator("#txtUserID")
    if not username:
        print("[ERROR] Username input not found")
        raise Exception("Username input not found")
    username.fill(USERNAME)
    print("[LOG] Filled username")
    screenshot(page, "step_2_filled_username.png")
    sleep(3)

    password = page.locator("#txtPassword")
    if not password:
        print("[ERROR] Password input not found")
        raise Exception("Password input not found")
    password.fill(PASSWORD)
    print("[LOG] Filled password")
    screenshot(page, "step_3_filled_password.png")
    sleep(3)

    login_btn = page.locator("#sub")
    if not login_btn:
        print("[ERROR] Login button not found")
        raise Exception("Login button not found")
    login_btn.click()
    print("[LOG] Clicked Login button")
    screenshot(page, "step_4_clicked_login.png")
    sleep(8)

    screenshot(page, "step_5_clicked_new.png")
    sleep(4)

"""