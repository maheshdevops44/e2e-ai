export const tempScript = `
import re
import os
import uuid
import pytest
from playwright.sync_api import Page, expect
import time
from utils import screenshot, highlight


@pytest.fixture
# Reuse the page_with_video fixture from example_test.py if possible, else define it here
# (Assume browser fixture is available from pytest-playwright)
def page_with_video(browser):
    video_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'videos'))
    os.makedirs(video_dir, exist_ok=True)
    context = browser.new_context(record_video_dir=video_dir)
    page = context.new_page()
    yield page
    page.close()
    context.close()

def test_login_saucelabs(page_with_video):
    page = page_with_video
    page.goto("https://www.saucedemo.com/")
    print("[LOG] Navigated to https://www.saucedemo.com/")
    time.sleep(1)

    screenshot(page, "step1_goto")
    print("[LOG] Screenshot taken: step1_goto")
    time.sleep(1)
    highlight(page, 'input[data-test="username"]')
    print("[LOG] Highlighted username input")
    time.sleep(1)
    
    page.get_by_placeholder("Username").fill("standard_user")
    print("[LOG] Filled username")
    time.sleep(1)
    highlight(page, 'input[data-test="password"]')
    print("[LOG] Highlighted password input")
    time.sleep(1)
    page.get_by_placeholder("Password").fill("secret_sauce")
    print("[LOG] Filled password")
    time.sleep(1)
    screenshot(page, "step2_filled")
    print("[LOG] Screenshot taken: step2_filled")
    time.sleep(1)
    
    highlight(page, 'input[data-test="login-button"]')
    print("[LOG] Highlighted login button")
    time.sleep(1)
    page.get_by_role("button", name="Login").click()
    print("[LOG] Clicked login button")
    time.sleep(1)
    
    screenshot(page, "step3_loggedin")
    print("[LOG] Screenshot taken: step3_loggedin")
    time.sleep(1)
    
    expect(page.get_by_text("Products")).to_be_visible()
    print("[LOG] Products text is visible")
    time.sleep(1)
`