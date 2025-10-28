from ast import parse
from adapters.llm_adapters import get_azure_llm
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from pprint import pprint
import re
import dotenv
import json
#from nodes.rxp_agent_utils import iterative_search_for_element


dotenv.load_dotenv()

# Define tools that the LLM can use to understand Playwright functions
def create_playwright_tools():
    """
    Create tool definitions for Playwright functions that the LLM can understand.
    These tools describe the available functions and their usage.
    """
    
    # Tool 1: RxP Element Reference Database
    @tool
    def rxp_element_reference_database():
        """
        Comprehensive database of working RxP selectors with data-test-id attributes.
        These are proven selectors from working automation code.
        
        **Login Elements:**
        - Username: input#txtUserID
        - Password: input#txtPassword  
        - Login Button: button#sub
        
        **Advanced Search Elements:**
        - Advanced Search Link: //*[text()='Advanced Search']
        - RxHome ID Field: [data-test-id="20180715225236062436158"]
        - Search Button: //*[@node_name='DisplayAdvanceSearchParameters']//following::*[@name='DisplaySearchWrapper_D_AdvanceSearch_15']
        - Open Case Button: [data-test-id='20201119155820006856367']
        
        **Order Entry Elements (in Advanced Search page after opening case):**
        - Begin Button: [data-test-id='201609091025020567152987']
        - Begin Button (alternative): //button[normalize-space()='Begin']
        - Begin Button (partial): //button[contains(text(), 'Begin')]
        - Begin Button (Advanced Search context): //div[contains(@class,'AdvancedSearch')]//button[normalize-space()='Begin']
        - Begin Button (iframe context): //iframe//button[normalize-space()='Begin']
        - Link Image Button: //button[normalize-space(.)='Link Image in Viewer']
        - DAW Dropdown: //*[normalize-space(text())='DAW Code']/ancestor-or-self::*[contains(@class,'dataLabelFor')]/following-sibling::*//select
        - DAW Code Option: "0 - No Product Selection Indicated" (IMPORTANT: Use full text, not just "0")
        - Search Drug Button: [data-test-id='20170901173456065136464']
        - NDC Dropdown: [data-test-id='20200925062850019643650'] (CRITICAL: Must select "NDC" option AFTER clicking Search Drug button BEFORE Drug Search Input appears)
        - Drug Search Input: //input[@name='$PDrugSearch$ppySearchText'] (IMPORTANT: Only appears AFTER selecting NDC dropdown)
        - Drug Search Button: //button[normalize-space(text())='Search']
        - Drug Result Row: //*[@id="$PDrugSearchResults$ppxResults$l1"]/td[3]
        - Submit Drug Button: //button[@data-test-id='201707060845020891147506' and normalize-space()='Submit']
        
        **CRITICAL DRUG SEARCH WORKFLOW:**
        1. Click Search Drug Button and wait for modal to open (sleep 5 seconds)
        2. Check if Drug Search Input is already available (some versions don't need dropdown)
        3. If not available, select NDC Dropdown and choose "NDC" option
        4. Wait for Drug Search Input to appear (after NDC selection or directly)
        5. Fill Drug Search Input with NDC code (e.g., "00074055402")
        6. Click Search Button in modal
        7. Select Drug Result Row from results
        8. Click Submit Drug Button
        
        **IMPORTANT NOTES:**
        - Always use sleep(5) after clicking Search Drug button to allow modal to load
        - NDC Dropdown may not exist in all versions - check for Drug Search Input first
        - Use find_element_across_frames() as modal may be in iframe
        - Include multiple fallback selectors for both dropdown and input
        
        **CONSISTENCY TIPS:**
        - ALWAYS have 2-3 fallback selectors for each element
        - Use iterative_search_for_element() for critical elements that may take time to load
        - Take screenshots when elements not found for debugging
        - Use page.wait_for_load_state("networkidle") instead of fixed sleep() where possible
        - Wrap critical operations in retry loops with wait_between_attempts
        
        **CLICK TIMEOUT WORKAROUND:**
        When hover() times out (common with Common SIG button), use multi-strategy click:
        ```python
        # Try multiple click strategies
        try:
            robust_click(page, element)  # Strategy 1: hover + click
        except:
            try:
                element.click(force=True)  # Strategy 2: force click (skip hover)
            except:
                try:
                    element.evaluate("(el) => el.click()")  # Strategy 3: JS click
                except:
                    element.scroll_into_view_if_needed()  # Strategy 4: scroll + click
                    sleep(1)
                    element.click()
        ```
        
        **Prescription Details:**
        - Common SIG Button: //button[normalize-space(.)='Common SIG']
        - SIG Option: //span[normalize-space(text())='INJECT 40 MG (0.4 ML) UNDER THE SKIN EVERY 2 WEEKS']
        - Quantity Input: input[data-test-id="2019062103515309648629"]
        - Days Supply Input: input[data-test-id="20190621040342079260489"]
        - Doses Input: input[data-test-id="20190621040342079263702"]
        - Refills Input: input[data-test-id="2019062104034207926431"]
        - Apply Rules Button: //button[normalize-space(.)='Apply Rules']
        - Reviewed Button: //button[normalize-space(.)='Reviewed']
        
        **Validation Checkboxes:**
        - Patient Checkbox: //input[@data-test-id='202303231536300910155360']
        - Medication Checkbox: //input[@data-test-id='20230324144929033857959']
        - Rx Details Checkbox: //input[@data-test-id='20230324171608002687320']
        - Prescriber Checkbox: //input[@data-test-id='202303271403440493899139']
        
        **Navigation:**
        - Next Button: //button[normalize-space()='Next >>']
        - Close Button: //button[normalize-space() = 'Close']
        - Submit Button: //button[normalize-space()='Submit' or normalize-space()='submit']
        
        **Session Management:**
        - End Other Session Button: //button[contains(text(), 'End other session to release lock')]
        - Session Lock Warning: //div[contains(text(), 'is currently being modified by')]
        
        **RPh Verification:**
        - Verify Buttons: //button[normalize-space()='Verify']
        - DUR Resolution: "RPh Approved Professional Judgement"
        
        Usage: Always prefer these proven selectors over generic ones.
        """
        return "RxP Element Reference Database with working data-test-id selectors"
    
    # Tool 2: Utility functions reference
    @tool
    def rxp_utility_functions():
        """
        Reference for pre-built RxP utility functions available in rxp_agent_utils.py
        
        Available functions:
        
        1. find_element_across_frames(page: Page, selector: str) -> Locator | None
           - Searches for element across all frames including iframes
           - Returns first matching locator or None
           - IMPORTANT: Pass the correct page object (main page or popup page)
           
        2. robust_click(page: Page, element_locator: Locator, requires_navigation: bool = False)
           - Waits for element, hovers, then clicks
           - Use instead of direct .click()
           
        3. robust_fill(page: Page, element_locator: Locator, value: str, select_suggestion: bool = False)
           - Fills input field with value
           - Can handle autocomplete suggestions
           
        4. robust_select_option(page: Page, element_locator: Locator, text: str)
           - Selects dropdown option by visible text
           
        5. wait_for_new_window(page: Page, action: Callable, timeout: int = 10000) -> Page
           - Executes action that opens new window and returns new page
           
        6. switch_to_window_by_index(page: Page, index: int) -> Page
           - Switches to window by index
           
        7. find_and_click_begin_button_with_retry(page, button_description="Begin")
           - Finds and clicks Begin button with retry logic
           
        8. validate_section_and_check(page, fields_to_check, checkbox_selector, optional_fields=None)
           - Validates fields are populated and checks checkbox
           
        9. advanced_search(page, element_name, status_name, db_status_name, PATIENT_ID)
           - Performs advanced search in RxP application
           - This function ALREADY handles window switching internally
           - It clicks Advanced Search, switches to popup, performs search, closes popup
           - **ALWAYS USE THIS FUNCTION for Advanced Search workflow** - DO NOT manually handle windows
           - element_name: selector for Open Case button e.g. '[data-test-id="20201119155820006856367"]'
           - status_name: status to search for (e.g. "New-Unassigned", "Pending-EditMessages")
           - db_status_name: database status name (same as status_name usually)
           
        **CRITICAL: Window/Popup Context**
        When manually handling popups (not using advanced_search function):
        - After clicking Advanced Search, get windows: windows = page.context.pages
        - Find new window: for win in windows if win != page
        - Switch to it: adv_search_page.bring_to_front()
        - Use adv_search_page for ALL searches in that popup
        - Close popup: adv_search_page.close()
           
        Usage in generated code:
            from rxp_agent_utils import find_element_across_frames, robust_click, robust_fill
            from time import sleep
            
            # For elements in main page
            element = find_element_across_frames(page, '[data-test-id="123"]')
            robust_click(page, element)
            
            # For Advanced Search popup
            adv_search_link = find_element_across_frames(page, "[name='AccredoPortalHeader_pyDisplayHarness_15']")
            robust_click(page, adv_search_link)
            sleep(5)
            windows = page.context.pages
            adv_search_page = [w for w in windows if w != page][-1]
            adv_search_page.bring_to_front()
            
            # Now use adv_search_page for popup elements
            rxhome_field = find_element_across_frames(adv_search_page, '[data-test-id="20180715225236062436158"]')
            robust_fill(adv_search_page, rxhome_field, PATIENT_ID)
        """
        return "Reference for RxP utility functions"
    
    # Tool 3: Selector priority guidance
    @tool  
    def selector_priority_guide():
        """
        Guide for choosing the best selector strategy in Playwright automation.
        
        Priority order (best to worst):
        1. data-test-id attributes: Most stable, e.g., '[data-test-id="20180715225236062436158"]'
        2. name attributes: Good for form fields, e.g., '[name="UserIdentifier"]'
        3. id attributes: Good if unique, e.g., '#login-button'
        4. xpath: Use for complex navigation or button text, e.g., '//button[text()="Begin"]'
        5. CSS selectors: Use for complex queries, e.g., 'div.class > button'
        
        Best practices:
        - Always try data-test-id first from inspect_current_page results
        - Use find_element_across_frames to search across iframes
        - For buttons with text, use xpath: '//button[normalize-space()="Button Text"]'
        - Avoid fragile selectors like nth-child or complex CSS paths
        """
        return "Selector priority guidance"
    
    # Tool 4: Window and popup handling
    @tool
    def window_popup_handling_guide():
        """
        CRITICAL guide for handling popups, new windows, and context switching in RxP.
        
        **The Problem:**
        When Advanced Search is clicked, it opens a NEW WINDOW/POPUP. Elements like
        RxHome ID field, Search button, and Open Case button exist ONLY in that popup,
        NOT in the main page. You MUST switch to the popup window before searching.
        
        **The Solution - Manual Approach:**
        ```python
        from time import sleep
        
        # Step 1: Click Advanced Search on main page
        adv_search_link = find_element_across_frames(page, "[name='AccredoPortalHeader_pyDisplayHarness_15']")
        robust_click(page, adv_search_link)
        print("[LOG] Clicked Advanced Search")
        
        # Step 2: Wait for popup to open
        sleep(5)
        
        # Step 3: Get all open windows
        windows = page.context.pages
        if len(windows) < 2:
            sleep(5)  # Wait longer if needed
            windows = page.context.pages
        
        # Step 4: Find the new popup (not the main page)
        adv_search_page = None
        for win in windows[::-1]:
            if win != page:
                adv_search_page = win
                break
        
        if not adv_search_page:
            raise Exception("Advanced Search window did not open")
        
        # Step 5: Switch to the popup
        adv_search_page.bring_to_front()
        adv_search_page.wait_for_load_state("networkidle")
        print("[LOG] Switched to Advanced Search popup window")
        
        # Step 6: NOW use adv_search_page for ALL popup elements
        print("[DEBUG] Searching for RxHome ID field in POPUP window")
        rxhome_id_field = find_element_across_frames(adv_search_page, '[data-test-id="20180715225236062436158"]')
        if not rxhome_id_field:
            print("[DEBUG] RxHome ID field not found in popup")
            raise Exception("RxHome ID field not found")
        
        robust_fill(adv_search_page, rxhome_id_field, PATIENT_ID)
        print(f"[LOG] Entered Patient ID: {PATIENT_ID}")
        
        # Step 7: Search button also in popup
        search_btn = find_element_across_frames(adv_search_page, "//button[text()='Search']")
        robust_click(adv_search_page, search_btn)
        adv_search_page.wait_for_load_state("networkidle")
        
        # Step 8: Open Case button also in popup
        open_case_btn = find_element_across_frames(adv_search_page, '[data-test-id="20201119155820006856367"]')
        robust_click(adv_search_page, open_case_btn)
        
        # Step 9: Close popup and return to main page
        adv_search_page.close()
        print("[LOG] Closed Advanced Search window")
        page.bring_to_front()
        page.wait_for_load_state("networkidle")
        ```
        
        **The Solution - Using Utility Function:**
        ```python
        from rxp_agent_utils import advanced_search
        
        # This handles all window switching internally
        advanced_search(
            page=page,
            element_name='[data-test-id="20201119155820006856367"]',
            status_name="New-Unassigned",
            db_status_name="New-Unassigned",
            PATIENT_ID=PATIENT_ID
        )
        ```
        
        **Common Mistakes to Avoid:**
        1. ❌ Searching for RxHome ID using 'page' (wrong - it's in popup)
        2. ❌ Not switching to popup window before searching
        3. ❌ Forgetting to close popup and return to main page
        4. ❌ Using wrong page context for find_element_across_frames()
        
        **Correct Pattern:**
        1. ✅ Click Advanced Search on main 'page'
        2. ✅ Switch to popup 'adv_search_page'
        3. ✅ Use 'adv_search_page' for ALL popup elements
        4. ✅ Close popup and return to main 'page'
        """
        return "Window and popup handling guide"
    
    # Tool 5: Playwright wait strategies
    @tool
    def playwright_wait_strategies():
        """
        Comprehensive guide to Playwright wait strategies - CRITICAL for robust automation.
        
        **Page-level waits (use instead of sleep):**
        
        1. page.wait_for_load_state(state, timeout=30000)
           States: 'load', 'domcontentloaded', 'networkidle'
           - 'load': Wait for page load event (default)
           - 'domcontentloaded': Wait for DOM to be ready (faster, usually sufficient)
           - 'networkidle': Wait for no network activity for 500ms (use for AJAX-heavy pages)
           
           Example:
           page.goto("https://example.com")
           page.wait_for_load_state('domcontentloaded')
           page.wait_for_load_state('networkidle')  # For AJAX/dynamic content
        
        2. page.wait_for_timeout(milliseconds)
           - Use SPARINGLY, only as last resort
           - Example: page.wait_for_timeout(2000)  # Wait 2 seconds
        
        3. page.wait_for_url(url_pattern, timeout=30000)
           - Wait for navigation to specific URL
           - Example: page.wait_for_url('**/dashboard')
        
        **Element-level waits (PREFERRED):**
        
        4. locator.wait_for(state='visible', timeout=30000)
           States: 'attached', 'detached', 'visible', 'hidden'
           - Example: 
             element = page.locator('[data-test-id="123"]')
             element.wait_for(state='visible')
        
        5. page.wait_for_selector(selector, state='visible', timeout=30000)
           - Wait for element to appear
           - Example: page.wait_for_selector('button.submit', state='visible')
        
        6. page.wait_for_function(js_function, timeout=30000)
           - Wait for custom JS condition
           - Example: page.wait_for_function('document.querySelectorAll("div").length > 10')
        
        **Auto-waiting (Playwright does this automatically):**
        - click(), fill(), select_option() auto-wait for:
          * Element to be attached to DOM
          * Element to be visible
          * Element to be stable (not animating)
          * Element to receive events (not covered)
          * Element to be enabled
        
        **Best practices:**
        1. Use page.wait_for_load_state('networkidle') after navigation/actions that trigger AJAX
        2. Use element.wait_for(state='visible') before interacting with dynamic elements
        3. AVOID sleep()/wait_for_timeout() - use specific wait conditions
        4. Set reasonable timeouts (default 30s is usually fine)
        5. For RxP specifically: Use wait_for_load_state('networkidle') after clicks/searches
        
        **Common patterns for RxP:**
        ```python
        # After navigation
        page.goto(url)
        page.wait_for_load_state('networkidle')
        
        # After clicking search/submit
        search_btn = find_element_across_frames(page, selector)
        robust_click(page, search_btn)
        page.wait_for_load_state('networkidle')
        
        # Waiting for dynamic element
        element = page.locator('[data-test-id="results"]')
        element.wait_for(state='visible', timeout=10000)
        
        # Instead of sleep(5)
        page.wait_for_load_state('networkidle')
        ```
        """
        return "Playwright wait strategies guide"
    
    # Tool 5: Additional Playwright functions
    @tool
    def additional_playwright_functions():
        """
        Additional useful Playwright functions for robust automation.
        
        **Context and Window Management:**
        
        1. page.context.pages
           - Get all open pages/tabs
           - Example: all_pages = page.context.pages
        
        2. page.bring_to_front()
           - Bring page to front
           
        3. page.context.expect_page(timeout=30000)
           - Expect new page to open
           - Example:
             with page.context.expect_page() as new_page_info:
                 page.click('a[target="_blank"]')
             new_page = new_page_info.value
        
        **Element State Checks:**
        
        4. element.is_visible()
           - Check if element is visible
        
        5. element.is_enabled()
           - Check if element is enabled
        
        6. element.is_checked()
           - Check if checkbox/radio is checked
        
        7. element.count()
           - Count matching elements
           - Example: button_count = page.locator('button').count()
        
        **Element Interaction:**
        
        8. element.hover()
           - Hover over element (triggers tooltips/menus)
        
        9. element.focus()
           - Focus on element
        
        10. element.press(key)
            - Press keyboard key
            - Example: element.press('Enter'), element.press('ArrowDown')
        
        11. element.type(text, delay=50)
            - Type text with delay between keystrokes
        
        12. element.evaluate(js_expression)
            - Execute JavaScript on element
            - Example: element.evaluate('el => el.scrollIntoView()')
        
        13. element.click(force=True)
            - Force click even if not visible
            - Use as fallback when normal click fails
        
        **Data Extraction:**
        
        14. element.inner_text()
            - Get visible text
        
        15. element.text_content()
            - Get all text including hidden
        
        16. element.get_attribute(name)
            - Get attribute value
            - Example: element.get_attribute('href')
        
        17. element.input_value()
            - Get input field value
        
        **Frames and iframes:**
        
        18. page.frames
            - Get all frames
        
        19. page.frame(name_or_url)
            - Get specific frame
        
        20. frame.locator(selector)
            - Find element in frame
        
        **Screenshots and Debugging:**
        
        21. page.screenshot(path='screenshot.png')
            - Take full page screenshot
        
        22. element.screenshot(path='element.png')
            - Screenshot specific element
        
        23. page.pause()
            - Pause execution for debugging
        
        **Network and Cookies:**
        
        24. page.wait_for_response(url_pattern, timeout=30000)
            - Wait for specific API response
            - Example: page.wait_for_response('**/api/data')
        
        25. page.wait_for_request(url_pattern)
            - Wait for specific request
        
        26. page.context.cookies()
            - Get all cookies
        
        **Keyboard and Mouse:**
        
        27. page.keyboard.press(key)
            - Press keyboard key globally
        
        28. page.keyboard.type(text)
            - Type text globally
        
        29. page.mouse.click(x, y)
            - Click at coordinates
        
        **Evaluation and Scripts:**
        
        30. page.evaluate(js_code)
            - Execute JavaScript in page context
            - Example: page.evaluate('() => document.title')
        
        31. page.add_init_script(script)
            - Add script that runs before page loads
        
        **Best practices for RxP:**
        - Use element.wait_for(state='visible') for dynamic elements
        - Use page.wait_for_load_state('networkidle') after navigation
        - Use element.evaluate() for complex interactions
        - Use force=True click as fallback
        - Check element.is_visible() before interaction
        - Use element.count() to verify elements exist
        """
        return "Additional Playwright functions reference"
    
    # Tool 6: Intelligent selector fallback logic
    @tool
    def intelligent_selector_fallback():
        """
        Intelligent fallback logic for element selection when data-test-id is not available.
        Provides a systematic approach to finding elements with multiple selector strategies.
        
        **Fallback Strategy Pattern:**
        ```python
        # Step 1: Try data-test-id first (most stable)
        element = find_element_across_frames(page, '[data-test-id="specific-id"]')
        
        # Step 2: Try name attribute (good fallback)
        if not element:
            element = find_element_across_frames(page, '[name="fieldName"]')
        
        # Step 3: Try ID attribute (decent fallback)
        if not element:
            element = find_element_across_frames(page, '#elementId')
        
        # Step 4: Try xpath (last resort)
        if not element:
            element = find_element_across_frames(page, '//button[normalize-space()="Button Text"]')
        
        # Step 5: Fail with descriptive error
        if not element:
            raise Exception("Element not found with any selector strategy")
        ```
        
        **Common RxP Element Fallback Patterns:**
        
        1. Login Username:
           - Primary: [data-test-id*="username"]
           - Fallback: [name="UserIdentifier"]
           - Last resort: //input[@placeholder*="username" i]
        
        2. Login Password:
           - Primary: [data-test-id*="password"]
           - Fallback: [name="Password"]
           - Last resort: //input[@type="password"]
        
        3. Search Buttons:
           - Primary: [data-test-id*="search"]
           - Fallback: //button[normalize-space()="Search"]
           - Last resort: button[type="submit"]
        
        4. Form Fields:
           - Primary: [data-test-id*="field-name"]
           - Fallback: [name="fieldName"]
           - Last resort: //input[@placeholder*="field" i]
        
        **Best Practices:**
        - Always implement the full fallback chain
        - Use descriptive error messages with all attempted selectors
        - Log which selector strategy succeeded
        - Prefer semantic selectors over positional ones
        """
        return "Intelligent selector fallback patterns"
    
    # Tool 7: Timeout and debugging strategies
    @tool
    def timeout_and_debugging_strategies():
        """
        Comprehensive timeout management and debugging strategies for RxP automation.
        
        **Timeout Configuration:**
        ```python
        # Set extended timeouts at the beginning of test
        page.set_default_timeout(60000)  # 60 seconds for element operations
        page.set_default_navigation_timeout(60000)  # 60 seconds for navigation
        
        print("[LOG] Starting RxP automation test with extended timeouts...")
        ```
        
        **Enhanced Wait Strategies:**
        ```python
        # Page navigation with extended timeout
        try:
            print("[LOG] Navigating to RxP login page...")
            page.goto(initial_url)
            print("[LOG] Navigated to RxP login page")
            page.wait_for_load_state("networkidle", timeout=60000)
            print("[LOG] Page loaded successfully")
        except Exception as e:
            print(f"[WARNING] Page load timeout: {e}")
            print("[LOG] Attempting to continue with current page state...")
            page.wait_for_timeout(5000)
        
        # Login with extended timeout
        try:
            print("[LOG] Waiting for login to complete...")
            page.wait_for_load_state("networkidle", timeout=60000)
            print("[SUCCESS] Login completed successfully")
        except Exception as e:
            print(f"[WARNING] Login wait timeout: {e}")
            print("[LOG] Attempting to continue with current page state...")
            page.wait_for_timeout(5000)
        ```
        
        **Debug Element Search Function:**
        ```python
        def debug_element_search(selector, description):
            print(f"[DEBUG] Searching for {description} with selector: {selector}")
            element = find_element_across_frames(page, selector)
            if element:
                print(f"[DEBUG] Found {description} successfully")
                return element
            else:
                print(f"[DEBUG] {description} not found with selector: {selector}")
                return None
        
        # Usage with multiple fallbacks
        username_field = debug_element_search('input#txtUserID', 'username field (proven selector)')
        if not username_field:
            username_field = debug_element_search('[name="UserIdentifier"]', 'username field (fallback)')
        if not username_field:
            raise Exception("[ERROR] Username field not found with any selector")
        ```
        
        **Available Elements Debugging:**
        ```python
        def debug_available_buttons():
            try:
                print("[DEBUG] Listing available buttons on page...")
                buttons = page.locator('button, input[type="button"], input[type="submit"]').all()
                for i, button in enumerate(buttons[:10]):
                    try:
                        text = button.inner_text() or button.get_attribute('value') or 'No text'
                        print(f"[DEBUG] Button {i+1}: '{text}'")
                    except:
                        print(f"[DEBUG] Button {i+1}: Could not get text")
            except Exception as e:
                print(f"[DEBUG] Could not list buttons: {e}")
        ```
        
        **Screenshot for Debugging:**
        ```python
        # Take screenshot after important operations
        try:
            page.screenshot(path="advanced_search_window.png")
            print("[DEBUG] Screenshot saved as 'advanced_search_window.png'")
        except Exception as e:
            print(f"[DEBUG] Could not take screenshot: {e}")
        ```
        
        **Multiple Selector Fallback Pattern:**
        ```python
        # Clear button with multiple fallbacks
        clear_btn = debug_element_search('//button[normalize-space()="Clear"]', 'Clear button (primary)')
        if not clear_btn:
            clear_btn = debug_element_search('button[normalize-space()="Clear"]', 'Clear button (alternative)')
        if not clear_btn:
            clear_btn = debug_element_search('//input[@type="button" and normalize-space()="Clear"]', 'Clear button (input type)')
        if not clear_btn:
            clear_btn = debug_element_search('[data-test-id*="clear"]', 'Clear button (data-test-id)')
        if not clear_btn:
            print("[WARNING] Clear button not found, listing available buttons for debugging...")
            debug_available_buttons()
            print("[WARNING] Attempting to continue without clearing...")
        ```
        
        **Best Practices:**
        - Always set extended timeouts at the beginning
        - Use try-except blocks for all wait operations
        - Provide detailed debug logging for element searches
        - Include fallback strategies for critical elements
        - Take screenshots at key points for debugging
        - List available elements when expected elements are not found
        """
        return "Timeout and debugging strategies for robust RxP automation"
    
    # Tool 8: Enhanced element finding patterns
    @tool
    def enhanced_element_finding_patterns():
        """
        Enhanced element finding patterns for robust automation with multiple fallback strategies.
        
        **Multiple Selector Fallback Pattern:**
        ```python
        # Define multiple selectors in priority order
        element_selectors = [
            "[data-test-id='specific-id']",           # Proven selector (highest priority)
            "//button[normalize-space()='Button Text']", # XPath with exact text
            "//button[contains(text(), 'Partial')]",   # XPath with partial text
            "button:has-text('Button Text')",         # CSS with text match
            "//input[@type='button' and @value='Text']", # Input button
            "//button[@title='Button Title']",        # Title attribute
        ]
        
        element = None
        for i, selector in enumerate(element_selectors):
            print(f"[DEBUG] Trying selector {i+1}: {selector}")
            element = debug_element_search(selector, f'Element (selector {i+1})')
            if element:
                print(f"[LOG] Found element with selector {i+1}")
                break
        
        if not element:
            # Advanced search through all buttons/inputs
            print("[WARNING] Element not found with standard selectors, trying advanced search...")
            all_elements = page.locator('button, input[type="button"], input[type="submit"]').all()
            for i, el in enumerate(all_elements):
                try:
                    text = el.inner_text() or el.get_attribute('value') or el.get_attribute('name') or ''
                    if 'target_text' in text.lower():
                        print(f"[LOG] Found element by text search: '{text}'")
                        element = el
                        break
                except:
                    pass
        ```
        
        **Enhanced Click with Multiple Strategies:**
        ```python
        if element:
            try:
                element.click()
                print("[LOG] Clicked element successfully")
            except Exception as e:
                print(f"[WARNING] Normal click failed: {e}, trying force click...")
                try:
                    element.click(force=True)
                    print("[LOG] Clicked element with force click")
                except Exception as e2:
                    print(f"[WARNING] Force click failed: {e2}, trying JS click...")
                    element.evaluate("(el) => el.click()")
                    print("[LOG] Clicked element with JS click")
        ```
        
        **Frame-Aware Element Search:**
        ```python
        def search_in_all_frames(selector, description):
            # Try main page first
            element = find_element_across_frames(page, selector)
            if element:
                return element
            
            # If not found, search in each frame explicitly
            try:
                frames = page.frames
                for i, frame in enumerate(frames):
                    try:
                        frame_element = frame.locator(selector)
                        if frame_element.count() > 0:
                            print(f"[LOG] Found {description} in frame {i}")
                            return frame_element.first
                    except:
                        pass
            except Exception as e:
                print(f"[DEBUG] Could not search frames: {e}")
            
            return None
        ```
        
        **Best Practices:**
        - Always use multiple selector fallbacks
        - Include text-based searches as last resort
        - Use enhanced click strategies for stubborn elements
        - Search across frames when elements aren't found
        - Provide detailed debugging information
        """
        return "Enhanced element finding patterns with multiple fallback strategies"
    
    # Tool 9: Advanced Search workflow guidance
    @tool
    def advanced_search_workflow_guidance():
        """
        Guidance for Advanced Search workflow in RxP automation.
        
        **Critical Workflow Understanding:**
        The Begin button is located in the MAIN PAGE, NOT in the Advanced Search page after opening a case.
        
        **Correct Advanced Search Workflow:**
        1. Click Advanced Search link (opens new window/tab)
        2. Fill RxHome ID field in Advanced Search window
        3. Click Search button in Advanced Search window
        4. Click Open Case button in search results
        5. **IMPORTANT**: Advanced Search window closes/navigates back to main page
        6. **IMPORTANT**: The Begin button appears in the MAIN PAGE after opening case
        7. Click Begin button in main page
        8. Continue with order entry process
        
        **Common Mistake:**
        ❌ Looking for Begin button in Advanced Search window after opening case
        ✅ Looking for Begin button in main page after opening case
        
        **Window Management:**
        ```python
        # After opening case, close Advanced Search window and return to main page
        page.close()  # Close Advanced Search window
        main_page = page.context.pages[0]  # Get main page
        main_page.bring_to_front()  # Switch to main page
        page = main_page  # Update page reference
        ```
        
        **Main Page Context Selectors:**
        ```python
        # After returning to main page, look for Begin button in main page context
        begin_selectors = [
            "[data-test-id='201609091025020567152987']",  # Proven selector
            "//button[normalize-space()='Begin']",        # Generic
            "//div[contains(@class,'Referral')]//button[normalize-space()='Begin']",  # Referral context
            "//iframe//button[normalize-space()='Begin']",  # Iframe context
            "//*[contains(@class,'Contents')]//button[normalize-space()='Begin']"  # Contents context
        ]
        ```
        
        **Verification Steps:**
        ```python
        # Verify you're in the main page
        main_page_indicators = [
            "//*[text()='Advanced Search']",  # Should be present in main page
            "//button[normalize-space()='Begin']",
            "//*[contains(@class,'Referral')]",
            "//*[contains(@class,'Contents')]"
        ]
        ```
        
        **Best Practices:**
        - Close Advanced Search window after opening case
        - Switch back to main page before looking for Begin button
        - Use main page context selectors for Begin button
        - Verify page context before looking for elements
        """
        return "Advanced Search workflow guidance for RxP automation"
    
    # Tool 10: Consistency and reliability patterns
    @tool
    def consistency_and_reliability_patterns():
        """
        CRITICAL: Patterns to achieve consistency and reliability in Playwright automation.
        
        **The Problem:**
        Tests fail intermittently because:
        - Elements load at different speeds
        - Network conditions vary
        - Elements are in iframes or modals
        - JavaScript rendering takes time
        
        **The Solution - Use Existing iterative_search_for_element:**
        ```python
        from rxp_agent_utils import iterative_search_for_element
        
        # This utility is ALREADY in your codebase - USE IT!
        success, element = iterative_search_for_element(
            page,
            selectors=[
                "[data-test-id='20200925062850019643650']",  # Primary
                "//select[contains(@name, 'SearchBy')]",     # Fallback 1
                "//select",                                   # Fallback 2
            ],
            element_name="NDC Dropdown",
            max_attempts=10,      # Retry 10 times
            delay=2,              # Wait 2 seconds between attempts
            click_on_found=False, # Don't click, just find
            screenshot_on_found=True
        )
        
        if success and element:
            robust_select_option(page, element, "NDC")
        else:
            # Take screenshot for debugging
            page.screenshot(path="ndc_dropdown_not_found.png")
            raise Exception("NDC Dropdown not found after retries")
        ```
        
        **Pattern 1: Multiple Selector Fallbacks (ALWAYS USE THIS)**
        ```python
        # BAD - Single selector (fragile)
        element = find_element_across_frames(page, "[data-test-id='123']")
        
        # GOOD - Multiple fallback selectors
        element = None
        selectors = [
            "[data-test-id='123']",           # Most reliable
            "[name='fieldName']",             # Good fallback
            "//button[text()='Submit']",      # Last resort
        ]
        
        for selector in selectors:
            element = find_element_across_frames(page, selector)
            if element and element.is_visible():
                print(f"[LOG] Found element with selector: {selector}")
                break
        
        if not element:
            page.screenshot(path="element_not_found.png")
            raise Exception("Element not found with any selector")
        ```
        
        **Pattern 2: Retry with Exponential Backoff**
        ```python
        max_attempts = 5
        wait_time = 2  # Start with 2 seconds
        
        for attempt in range(max_attempts):
            element = find_element_across_frames(page, selector)
            if element and element.is_visible():
                print(f"[LOG] Found element on attempt {attempt + 1}")
                break
            
            if attempt < max_attempts - 1:
                print(f"[LOG] Attempt {attempt + 1} failed, waiting {wait_time}s...")
                sleep(wait_time)
                # Wait for page to stabilize
                page.wait_for_load_state("networkidle", timeout=10000)
                wait_time = min(wait_time * 1.5, 10)  # Exponential backoff, max 10s
        
        if not element:
            raise Exception("Element not found after retries")
        ```
        
        **Pattern 3: Proper Waits (Instead of sleep)**
        ```python
        # BAD - Fixed sleep (wastes time or insufficient)
        sleep(5)  # Always waits 10 seconds even if page loads in 2
        
        # GOOD - Dynamic wait for network to be idle
        page.wait_for_load_state("networkidle", timeout=30000)  # Waits only as long as needed
        
        # GOOD - Wait for specific element
        element = find_element_across_frames(page, selector)
        if element:
            element.wait_for(state='visible', timeout=10000)  # Waits until visible or timeout
        
        # ACCEPTABLE - Combination for stability
        page.wait_for_load_state("networkidle")
        sleep(2)  # Small additional buffer for JS to finish
        ```
        
        **Pattern 4: Screenshot on Failure (CRITICAL for debugging)**
        ```python
        try:
            element = find_element_across_frames(page, selector)
            if not element:
                raise Exception("Element not found")
        except Exception as e:
            # Take screenshot showing current state
            page.screenshot(path=f"debug_{element_name}_not_found.png")
            print(f"[ERROR] {e}")
            print(f"[DEBUG] Screenshot saved for debugging")
            raise
        ```
        
        **Pattern 5: Check Element State Before Interaction**
        ```python
        element = find_element_across_frames(page, selector)
        
        if not element:
            raise Exception("Element not found")
        
        # Check if element is ready for interaction
        if not element.is_visible():
            print("[WARNING] Element exists but not visible, waiting...")
            element.wait_for(state='visible', timeout=5000)
        
        if not element.is_enabled():
            print("[WARNING] Element visible but disabled, waiting...")
            sleep(2)
            if not element.is_enabled():
                raise Exception("Element is disabled")
        
        # Now safe to interact
        robust_click(page, element)
        ```
        
        **Pattern 6: Modal/Popup Handling with Retry**
        ```python
        # Click button that opens modal
        search_drug_btn = find_element_across_frames(page, selector)
        robust_click(page, search_drug_btn)
        print("[LOG] Clicked Search Drug button")
        
        # Wait for modal to fully load
        page.wait_for_load_state("networkidle", timeout=30000)
        sleep(5)  # Additional buffer for modal animations
        
        # Try to find element in modal with retries
        max_attempts = 5
        modal_element = None
        
        for attempt in range(max_attempts):
            modal_element = find_element_across_frames(page, modal_selector)
            if modal_element and modal_element.is_visible():
                break
            print(f"[LOG] Modal element not ready, attempt {attempt + 1}/{max_attempts}")
            sleep(2)
            page.wait_for_load_state("networkidle", timeout=5000)
        
        if not modal_element:
            page.screenshot(path="modal_element_not_found.png")
            raise Exception("Modal element not found")
        ```
        
        **Complete Example - Consistent Drug Search:**
        ```python
        # Step 1: Click Search Drug with fallbacks
        search_drug_selectors = [
            "[data-test-id='20170901173456065136464']",
            "//button[normalize-space()='Search Drug']",
        ]
        search_drug_btn = None
        for selector in search_drug_selectors:
            search_drug_btn = find_element_across_frames(page, selector)
            if search_drug_btn:
                break
        
        if not search_drug_btn:
            page.screenshot(path="search_drug_btn_not_found.png")
            raise Exception("Search Drug button not found")
        
        robust_click(page, search_drug_btn)
        print("[LOG] Clicked Search Drug button")
        
        # Step 2: Wait for modal with networkidle + buffer
        page.wait_for_load_state("networkidle", timeout=30000)
        sleep(5)
        
        # Step 3: Find NDC dropdown with retries using iterative_search
        success, ndc_dropdown = iterative_search_for_element(
            page,
            selectors=[
                "[data-test-id='20200925062850019643650']",
                "//select[contains(@name, 'SearchBy')]",
                "//select",
            ],
            element_name="NDC Dropdown",
            max_attempts=10,
            delay=2,
            click_on_found=False,
            screenshot_on_found=True
        )
        
        if not success or not ndc_dropdown:
            page.screenshot(path="ndc_dropdown_not_found_after_retry.png")
            raise Exception("NDC Dropdown not found after multiple attempts")
        
        robust_select_option(page, ndc_dropdown, "NDC")
        print("[LOG] Selected NDC option")
        page.wait_for_load_state("networkidle", timeout=30000)
        sleep(2)
        
        # Step 4: Find Drug Search Input with retries
        success, drug_input = iterative_search_for_element(
            page,
            selectors=[
                "//input[@name='$PDrugSearch$ppySearchText']",
                "//input[contains(@placeholder, 'Search')]",
                "//input[@type='text']",
            ],
            element_name="Drug Search Input",
            max_attempts=10,
            delay=2,
            click_on_found=False,
            screenshot_on_found=True
        )
        
        if not success or not drug_input:
            page.screenshot(path="drug_input_not_found_after_retry.png")
            raise Exception("Drug Search Input not found")
        
        robust_fill(page, drug_input, "00074055402")
        print("[LOG] Entered NDC code")
        ```
        
        **Best Practices Summary:**
        1. ✅ ALWAYS provide 2-3 fallback selectors
        2. ✅ Use iterative_search_for_element() for critical elements
        3. ✅ Use page.wait_for_load_state("networkidle") after actions
        4. ✅ Check element.is_visible() and element.is_enabled()
        5. ✅ Take screenshots on failure for debugging
        6. ✅ Add retry loops with reasonable delays
        7. ✅ Print detailed log messages for troubleshooting
        8. ✅ Combine networkidle wait + small sleep() for stability
        """
        return "Consistency and reliability patterns for robust automation"
    
    # Tool 11: Error handling and retry patterns
    @tool
    def error_handling_and_retry_patterns():
        """
        Error handling and retry patterns for robust Playwright automation.
        
        **Try-Except Patterns:**
        
        1. Basic error handling:
        ```python
        try:
            element = find_element_across_frames(page, selector)
            if element:
                robust_click(page, element)
            else:
                raise Exception(f"Element not found: {selector}")
        except Exception as e:
            print(f"[ERROR] Failed to click element: {e}")
            # Fallback or raise
        ```
        
        2. Retry pattern:
        ```python
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                element = find_element_across_frames(page, selector)
                if element and element.is_visible():
                    robust_click(page, element)
                    break
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                print(f"Attempt {attempt + 1} failed, retrying...")
                page.wait_for_timeout(2000)
        ```
        
        3. Multiple selector fallback:
        ```python
        selectors = [
            '[data-test-id="123"]',
            '[name="submit"]',
            '//button[text()="Submit"]'
        ]
        element = None
        for selector in selectors:
            element = find_element_across_frames(page, selector)
            if element:
                print(f"Found element with: {selector}")
                break
        
        if not element:
            raise Exception("Element not found with any selector")
        ```
        
        4. Conditional interaction:
        ```python
        element = find_element_across_frames(page, selector)
        if element:
            if element.is_visible() and element.is_enabled():
                robust_click(page, element)
            else:
                print("[WARNING] Element found but not interactive")
        ```
        
        **Common RxP error scenarios:**
        
        1. Element in iframe not found:
           - Solution: Use find_element_across_frames()
        
        2. Element not ready:
           - Solution: Use wait_for_load_state('networkidle')
        
        3. Button disabled:
           - Solution: Check element.is_enabled() or use retry with wait
        
        4. Stale element:
           - Solution: Re-query the element after page changes
        
        5. Multiple windows:
           - Solution: Use switch_to_window_by_index() or wait_for_new_window()
        
        **Logging best practices:**
        ```python
        print(f"[LOG] Step 1: Navigate to login")
        print(f"[ERROR] Failed to find element: {selector}")
        print(f"[WARNING] Element not visible, waiting...")
        print(f"[SUCCESS] Login completed")
        ```
        """
        return "Error handling and retry patterns"
    
    return [
        rxp_element_reference_database,
        rxp_utility_functions, 
        selector_priority_guide,
        playwright_wait_strategies,
        additional_playwright_functions,
        intelligent_selector_fallback,
        timeout_and_debugging_strategies,
        enhanced_element_finding_patterns,
        advanced_search_workflow_guidance,
        consistency_and_reliability_patterns,
        error_handling_and_retry_patterns
    ]


def extract_python_code(llm_output: str) -> str:
	"""
	Extract and return just the Python code block from a string with potential markdown/code wrapping.
	Works with fenced code blocks (```python ... ```) or raw code.
	"""
	# Look for ```python ... ``` or ``` ... ``` fenced code block first
	match = re.search(
		r"```python(.*?)```",
		llm_output,
		re.DOTALL | re.IGNORECASE
	)
	if match:
		code = match.group(1)
	else:
		# Fallback: any ``` ... ``` block
		match = re.search(r"```(.*?)```", llm_output, re.DOTALL)
		if match:
			code = match.group(1)
		else:
			# No fences found, return the whole text
			code = llm_output

	# Remove any leading/trailing whitespace
	return code.strip()

steps = """•	Step 1: Launch and Login to RxP
o	Open Chrome or Edge browser
o	Navigate to the RxP application:
URL: https://sprxp-qa.express-scripts.com/sprxp/
o	Enter valid credentials (LAN ID and Password)
o	Click on Login
o	Expected Result: User should land on the RxP homepage

•	Step 2: Search Patient Case in Advanced Search
o	Click on Advanced Search on top right of the page beside search box
o	Go to Advanced search page
o	Click on Clear Button
o	Enter Patient ID in RxHome ID field.
o	Click on Search 
o	Expected Result: Search Results should appear with case details of the corresponding searched patient. 

•	Step 3: Open Case 
o	Click on Open Case from the results for the corresponding patient.
o	Minimize the advanced search window
o	Expected Result: User navigates to the Referral Task page



•	Step 4: Begin Order Entry Completion
o	In the Referral Contents section, click Begin
o	Click Link image in Viewer
o	Select DAW code: 0
o	Search and select drug: HUMIRA 40 MG/0.4 ML PEN 2'S (NDC: 00074055402)
o	Click Common SIG (Note: Common SIG will be populated for Humira but not every drug will have a Common SIG) and select: INJECT 40 MG (0.4 ML) UNDER THE SKIN EVERY 2 WEEKS
o	Enter: Qty = 1, Days' Supply = 14, Doses = 1, Refills = 1
o	Click Apply Rules, then Reviewed

•	Step 5: Validate Auto populated data for Each Section
o	For each of the following sections, Agentic AI should perform the following:
o	Cross-check each field against previously captured or stored values in the system
o	Confirm data is complete, correctly formatted, and consistent
o	Upon successful validation, tick the associated checkbox on the right side of the section
 
Patient Section
•	Verify that the following fields are correctly auto populated:
o	Full Name
o	DOB
o	Gender
o	Age
o	Address
o	Phone
•	→ If all values are populated/not null, tick the Patient section checkbox

Medication Section
•	Verify that the following fields are correctly auto populated:
o	Prescribed Drug
o	Dispensed Drug
o	Dispensed Drug Comments (Humira will have comments but not every drug will have comments)
•	→ If all values are populated, tick the Medication section checkbox

Rx Details Section
•	Verify that the following fields are correctly auto populated:
o	SIG Text
o	Prescribed Quantity
o	Prescribed Days' Supply
o	Prescribed Doses
o	Prescribed Refills
o	Dispensed Quantity
o	Dispensed Days' Supply
o	Dispensed Doses
o	Dispensed Refills
o	Date Written
o	Rx Expires
o	DAW Code
o	Rx Origin Code
•	→ If all values are populated, tick the Rx Details section checkbox

Prescriber Section
•	Verify that the following fields are correctly auto populated:
o	Prescriber
o	Prescriber ID
o	Address
o	Phone
o	FAX - If no fax#, check “Fax N/A” box.
o	NPI
o	DEA 
o	License (Not required)
o	State (Not required)
•	→ If all required values are populated, tick the Prescriber section checkbox
 
•	Confirm All Checkboxes
o	Agent should ensure that all four checkboxes (one per section) are selected
o	If any values are unpopulated, leave that section’s checkbox unchecked, and flag the section for manual review
o	Click Next which will invoke Trend Processing logic in the background of RxP Order Entry for this test case scenario.
o	Expected Result: Confirmation banner: "Case submitted to Pending - Trend work Queue. Click Close to proceed to next case"

•	Step 6: Close and Return to Homepage
o	Click Close
o	Expected Result: Navigates to RxP homepage (if no other cases are assigned)

•	Step 7: Trend Processing – Background Biosimilar Conversion Logic
o	RxP Ref Case moves on Status=Pending Trend Hold 
o	Trend conversion logic runs in the background. If the case is eligible based on the Client Inclusion Table, DAW code is 0, and Drug Pair List, then the drug will be systematically 	converted to a biosimilar alternative (e.g., Humira → ADALIMUMAB-ADBM).

•	Step 8: REF Case Moves to RxP Order Entry 
o	Retrieve REF Case by clicking Begin
o	Case lands in Order Summary Screen
o	Confirm Prescribed Drug = Humira and Dispensed Drug = Biosimiliar
o	Click Submit
o	Wait 1 to 2 minutes before moving to next step with RPh Verification (DV)

5.5 RxP Application – RPh Verification (DV)
Preconditions:
•	Case submitted in RxP Order Entry (OE)
•	Step 1: RxP Referral Case Status 
o	Open Advanced Search
o	Enter REF Id case in Case Id field 
o	Click Search button
o	Click Open Case for result returned

•	Step 2: Access Referral Case 
o	Click Begin 
o	Expected Result: User navigates to the RPh Verification main page
•	Step 3: Validate Annotation
o	Confirm red letter “A” appears on image
o	Validate verbiage such as “20250516 04:29:44 CDT SYSTEM - The Interchangeable Biosimilar ADALIMUMAB-ADBM 40 MG / 0.8 ML PEN 2'S has been substituted in place of the HUMIRA 40 MG/0.4 ML PEN 2'S” 
Note: (1) Date/Time stamp should match the date test case was automatically executed and (2) Specific drug details will differ based on the Test Case executed
o	Expected Result: User navigates to verification of Five Areas

•	Step 4: Verify Five Areas
The below five areas do not have pre-defined subheadings/labels on the screen, but information is grouped in blocks. There will be five blocks in total with a Verify button. When the first Verify button is clicked, an additional block of details will be displayed/expanded on the screen. This will continue until the fifth Verify button is clicked.
o	Click first Verify in Patient Details area
o	Expected Result: Navigates to Prescription Info area
o	Click second Verify in Prescription Info area
o	Expected Result: Navigates to Prescription Details area
o	Click third Verify to proceed to the Prescription Details area
o	Expected Result: Navigates to RPE area
o	Click fourth Verify to the Additional Details area
o	Expected Result: Navigates to Prescriber area
o	Click fifth Verify in the Prescriber area 
o	Expected Result: Navigates to Task page
•	Step 5: Complete RPh Verification
o	Click Submit (if available) 
o	Expected Result: Referral Case successfully completed.
o	If Submit is not available, then click Next 
o	Expected Result: Drug Rules Screen is displayed
o	Click Submit (if available) 
o	Expected Result: Referral Case successfully completed.
o	If Submit is not available, then click Next 
o	Expected Result: RxSnapshot Screen is displayed
o	Click Submit (if available) 
o	Expected Result:Referral Case successfully completed.
o	If Submit is not available, then click Next 
o	Expected Result: DUR Screen is displayed. Resolve DUR Alert(s). For each alert, Enter/Type “RPh Approved Professional Judgement” in the drop-down menu to select option.
o	Click Submit 
o	Expected Result: REF Case is submitted successfully
•	Step 6: Verify Completion Status
o	If not already open, access Advanced Search
o	Enter REF Id case in Case Id field
o	Click Search button
o	Click Open Case for result returned
o	Expected Result: Pop-up shows REF-ID with status: Resolved-Completed

Note (If Applicable): If REF-ID status is “Pending Awaiting Clearance” and not in “Resolved-Completed”. Navigate to Advanced Search and follow below steps:
o	Enter REF Id case in Case Id field 
o	Click Search button
o	Expand the case (Click on the expand arrow button)
o	Select “Re-Adjudicate” under Rx-Level Action drop down.
o	Click on Submit
o	Expected Result: User should be able to Re-Adjudicate successfully and Case moved to “Resolved Completed” Status
"""

def generate_rxp_code(patient_id, steps=steps, page_elements=None):
    """
    Generate RxP automation code using LLM with tool/function calling support.
    
    Args:
        patient_id: Patient ID for the test case
        steps: Test steps to automate
        page_elements: Optional dict of page elements from inspect_current_page()
    
    Returns:
        Generated Python Playwright code
    """
    
    # Create tools for the LLM to understand available functions
    tools = create_playwright_tools()
    
    # Get LLM with tool binding
    llm = get_azure_llm("ai-coe-gpt41", temperature=0.0)
    llm_with_tools = llm.bind_tools(tools)
    
    output_example = """
    You are an expert Python Playwright automation engineer. Your job is to generate a complete Python Playwright function that automates a given scenario. You must follow all instructions and best practices outlined below.

    **Important: You have access to tool functions that describe:**
    - rxp_element_reference_database: PROVEN working RxP selectors with data-test-id attributes
    - rxp_utility_functions: Pre-built utility functions for robust automation
    - selector_priority_guide: Best practices for choosing selectors
    - intelligent_selector_fallback: Systematic fallback strategies
    - timeout_and_debugging_strategies: Comprehensive timeout management and debugging approaches
    - enhanced_element_finding_patterns: Multiple selector fallback strategies with advanced search techniques
    - advanced_search_workflow_guidance: CRITICAL - Advanced Search workflow understanding and Begin button location

    **Instructions:**
	1) Read the given {steps} and extract only steps for RxP application.
    2) Use {steps} only for input fields. DO NOT ADD ANY NEW STEP in element_reference_code.
    3) Read the {steps} and extract elements either data-test-id or name or xpath in this priority order.
    4) ALWAYS use find_element_across_frames() to locate elements as they may be in iframes.
    5) For buttons, prefer xpath with text matching: '//button[normalize-space()="Button Text"]'
    6) **CRITICAL FOR DROPDOWNS**: When steps say "Select DAW code: 0", look up the FULL option text from Navigation_steps or rxp_element_reference_database. Use "0 - No Product Selection Indicated" not "0".
    7) Use the pre-built utility functions from rxp_agent_utils.py: 

        Available Prebuilt Functions (USE THESE INSTEAD OF WRITING YOUR OWN):
        - find_element_across_frames(page, locator) - searches across all iframes
        - robust_click(page, element) - reliable click with hover
        - robust_fill(page, element, text) - reliable fill with waits
        - robust_select_option(page, element, option) - reliable select dropdown
        - **advanced_search(page, element_name, status_name, db_status_name, patient_id)** - **USE THIS FOR ADVANCED SEARCH WORKFLOW**
        - find_and_click_begin_button_with_retry(page, button_text) - clicks Begin button with retry
        - validate_section_and_check(page, fields, checkbox, optional_fields) - validates and checks sections
        - post_order_entry_advanced_search(page, element_name, status_name, db_status_name, patient_id) - for post-order searches
        - handle_session_lock(page) - checks for and resolves session locks automatically
        - switch_to_window_by_index(page, index) - switches to window by index (avoid if possible)
        - wait_for_new_window(page, click_action, timeout) - waits for new window (avoid if possible, use advanced_search instead)
    
    8) **CRITICAL - Wait Strategies**: Use proper Playwright waits instead of sleep():
       - After page.goto(): Use page.wait_for_load_state('networkidle')
       - After clicks/actions that trigger AJAX: Use page.wait_for_load_state('networkidle')
       - For dynamic elements: Use element.wait_for(state='visible', timeout=10000)
       - NEVER use time.sleep() - use page.wait_for_timeout() only as last resort
       - For element checks: Use element.is_visible(), element.is_enabled()
    
    9) ALWAYS Verify the input fields in the {steps} for example check values for SIG,NDC etc. and use it in the script.
    
    10) These input will change in the automation script according to the scenario.
    
    11) ALWAYS Replace patient id given in the {steps} with {patient_id} passed as input in this function. DO NOT PUT ANY PLACEHOLDERS. The {patient_id} will be replaced with the actual value later.
    
    12) Generate a Python function named `def test_step_rxp(page_with_video): ...` that performs the scenario steps provided. DO NOT add any parameters to the function signature.
    
    13) Always begin the function by navigating to the initial page using `page.goto(initial_url)` (the initial_url will be given as a variable).
    
    14) If an element is not found, raise an Exception with a clear message.
    
    15) Only output valid Python code for the full function (imports plus function) and nothing else -- no explanation or markdown.
    
    16) **IMPORTANT** DO NOT INCLUDE ADDITIONAL FUNCTION FOR SCREENSHOTS. THESE UTILITY FUNCTIONS WILL BE ADDED AS IMPORTS LATER MANUALLY.
    
    17) **IMPORTANT** Use try-except blocks for retry logic on critical elements that may take time to load.
   
    18. **LOGIN**
    * USERNAME will be always LAN_ID and password is always LAN_PASSWORD

    19.  **Output Format**: Only output valid, complete Python code that includes the necessary imports and the full function definition. Do not add any explanations or markdown formatting.
    
    20. ** IMPORTANT ** DO NOT INCLUDE ADDITIONAL LOGIC FOR SCREENSHOTS, Sleep etc. 
    
    21. **CRITICAL WINDOW/POPUP HANDLING**
    * **PREFERRED: Use the advanced_search() utility function**
      ```python
      from rxp_agent_utils import advanced_search
      from time import sleep
      
      # This handles ALL window switching internally - ALWAYS use this!
      advanced_search(
          page=page,
          element_name='[data-test-id="20201119155820006856367"]',  # Open Case button
          status_name="",  # Empty string searches all statuses
          db_status_name="New-Unassigned",
          PATIENT_ID=PATIENT_ID
      )
      print("[LOG] Advanced search completed, case opened, returned to main page")
      sleep(20)  # Wait for main page to load after opening case
      ```
    
    * **ONLY if you cannot use advanced_search(), do manual handling:**
      ```python
      from time import sleep
      
      # Click Advanced Search on main page
      adv_search_link = find_element_across_frames(page, "[name='AccredoPortalHeader_pyDisplayHarness_15']")
      robust_click(page, adv_search_link)
      print("[LOG] Clicked Advanced Search")
      sleep(10)
      
      # Wait for and get the new window
      windows = page.context.pages
      if len(windows) < 2:
          sleep(5)
          windows = page.context.pages
      
      adv_search_page = None
      for win in windows[::-1]:
          if win != page:
              adv_search_page = win
              break
      
      if not adv_search_page:
          raise Exception("Advanced Search window did not open")
      
      adv_search_page.bring_to_front()
      adv_search_page.wait_for_load_state("networkidle")
      sleep(20)
      print("[LOG] Switched to Advanced Search window")
      
      # NOW use adv_search_page for ALL popup elements
      rxhome_id_field = find_element_across_frames(adv_search_page, '[data-test-id="20180715225236062436158"]')
      robust_fill(adv_search_page, rxhome_id_field, PATIENT_ID)
      
      search_btn = find_element_across_frames(adv_search_page, "//button[text()='Search']")
      robust_click(adv_search_page, search_btn)
      adv_search_page.wait_for_load_state("networkidle")
      sleep(15)
      
      open_case_btn = find_element_across_frames(adv_search_page, '[data-test-id="20201119155820006856367"]')
      robust_click(adv_search_page, open_case_btn)
      sleep(13)
      
      # Close popup and return to main page
      adv_search_page.close()
      print("[LOG] Closed Advanced Search window")
      page.bring_to_front()
      page.wait_for_load_state("networkidle")
      sleep(20)
      ```
    ---

    ### **EXAMPLE**

    **Given:**

    `initial_url` = "https://example.com/login"

    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD

    PATIENT_ID = {patient_id}
    
    ---

    **Required Output:**

    def test_step_rxp(page_with_video):
        from nodes.rxp_agent_utils import find_element_across_frames, robust_click, robust_fill
        from time import sleep
        
        page = page_with_video
        
        # Set extended timeouts for robust automation
        page.set_default_timeout(60000)  # 60 seconds
        page.set_default_navigation_timeout(60000)  # 60 seconds
        
        USERNAME = LAN_ID
        PASSWORD = LAN_PASSWORD
        PATIENT_ID = {patient_id}

        print("[LOG] Starting RxP automation test with extended timeouts...")

        # Debug function for element searching
        def debug_element_search(selector, description):
            print(f"[DEBUG] Searching for {description} with selector: {selector}")
            element = find_element_across_frames(page, selector)
            if element:
                print(f"[DEBUG] Found {description} successfully")
                return element
            else:
                print(f"[DEBUG] {description} not found with selector: {selector}")
                return None
        
        # Multi-strategy click function to handle timeout errors
        def enhanced_click(element, element_name="element"):
            """Try multiple click strategies when hover() times out."""
            print(f"[ENHANCED_CLICK] Attempting to click '{element_name}'")
            
            # Strategy 1: Standard robust_click (hover + click)
            try:
                robust_click(page, element)
                print(f"[ENHANCED_CLICK] ✅ robust_click successful")
                return True
            except Exception as e1:
                print(f"[ENHANCED_CLICK] robust_click failed, trying force click...")
            
            # Strategy 2: Force click (skip hover)
            try:
                element.click(force=True)
                print(f"[ENHANCED_CLICK] ✅ Force click successful")
                return True
            except Exception as e2:
                print(f"[ENHANCED_CLICK] Force click failed, trying JavaScript click...")
            
            # Strategy 3: JavaScript click
            try:
                element.evaluate("(el) => el.click()")
                print(f"[ENHANCED_CLICK] ✅ JavaScript click successful")
                return True
            except Exception as e3:
                print(f"[ENHANCED_CLICK] JavaScript click failed, trying scroll + click...")
            
            # Strategy 4: Scroll into view then click
            try:
                element.scroll_into_view_if_needed()
                sleep(1)
                element.click()
                print(f"[ENHANCED_CLICK] ✅ Scroll + click successful")
                return True
            except Exception as e4:
                print(f"[ENHANCED_CLICK] ❌ All click strategies failed")
            
            return False
        
        # Validation checkbox click function (handles off-screen checkboxes)
        def click_validation_checkbox(checkbox, checkbox_name):
            """Enhanced checkbox clicking with zoom + scroll + multiple strategies."""
            print(f"[LOG] Clicking {checkbox_name}...")
            
            try:
                # Zoom out to see checkbox
                page.evaluate("document.body.style.zoom = '0.75'")
                sleep(1)
                
                # Scroll into view
                checkbox.scroll_into_view_if_needed()
                sleep(2)
                
                # Try JavaScript click (most reliable)
                checkbox.evaluate("(el) => { el.checked = true; el.click(); }")
                print(f"[LOG] ✅ {checkbox_name} checked (JavaScript)")
                
                # Reset zoom
                page.evaluate("document.body.style.zoom = '1.0'")
                sleep(1)
                return True
                
            except Exception as e1:
                print(f"[WARNING] JavaScript click failed: {e1}")
                try:
                    # Try force click
                    checkbox.click(force=True, timeout=10000)
                    print(f"[LOG] ✅ {checkbox_name} checked (force click)")
                    page.evaluate("document.body.style.zoom = '1.0'")
                    return True
                except Exception as e2:
                    print(f"[WARNING] Force click failed: {e2}")
                    try:
                        # Try enhanced_click
                        if enhanced_click(checkbox, checkbox_name):
                            print(f"[LOG] ✅ {checkbox_name} checked (enhanced_click)")
                            page.evaluate("document.body.style.zoom = '1.0'")
                            return True
                    except:
                        pass
                    
                    # Always reset zoom
                    try:
                        page.evaluate("document.body.style.zoom = '1.0'")
                    except:
                        pass
                    
                    print(f"[WARNING] Could not check {checkbox_name}")
                    return False

        # Step 1: Navigate to the login page with enhanced error handling
        try:
            print("[LOG] Navigating to RxP login page...")
        page.goto("https://example.com/login")
        print("[LOG] Navigated to https://example.com/login")
            page.wait_for_load_state("networkidle", timeout=60000)
            print("[LOG] Page loaded successfully")
        except Exception as e:
            print(f"[WARNING] Page load timeout: {e}")
            print("[LOG] Attempting to continue with current page state...")
            page.wait_for_timeout(5000)
        
        # Step 2: Fill username with debug logging and fallbacks
        print("[LOG] Looking for username field...")
        username_field = debug_element_search('input#txtUserID', 'username field (proven selector)')
        if not username_field:
            username_field = debug_element_search('[name="UserIdentifier"]', 'username field (fallback)')
        if not username_field:
            raise Exception("[ERROR] Username field not found with any selector")
        
        print("[LOG] Filling username field...")
        username_field.wait_for(state='visible', timeout=30000)
        robust_fill(page, username_field, USERNAME)
        print("[LOG] Filled username successfully")
        
        # Step 3: Fill password with debug logging and fallbacks
        print("[LOG] Looking for password field...")
        password_field = debug_element_search('input#txtPassword', 'password field (proven selector)')
        if not password_field:
            password_field = debug_element_search('[name="Password"]', 'password field (fallback)')
        if not password_field:
            raise Exception("[ERROR] Password field not found with any selector")
        
        print("[LOG] Filling password field...")
        password_field.wait_for(state='visible', timeout=30000)
        robust_fill(page, password_field, PASSWORD)
        print("[LOG] Filled password successfully")
        
        # Step 4: Click login with enhanced error handling
        print("[LOG] Looking for login button...")
        login_btn = debug_element_search('button#sub', 'login button (proven selector)')
        if not login_btn:
            login_btn = debug_element_search('//button[normalize-space()="Login"]', 'login button (fallback)')
        if not login_btn:
            raise Exception("[ERROR] Login button not found with any selector")
        
        print("[LOG] Clicking login button...")
        robust_click(page, login_btn)
        
        # Wait for login with extended timeout and error handling
        try:
            print("[LOG] Waiting for login to complete...")
            page.wait_for_load_state("networkidle", timeout=60000)
            print("[SUCCESS] Login completed successfully")
        except Exception as e:
            print(f"[WARNING] Login wait timeout: {e}")
            print("[LOG] Attempting to continue with current page state...")
            page.wait_for_timeout(5000)
        
        sleep(5)  # Wait 5 seconds after login for stability
        
        # Step 2: Advanced Search workflow
        advanced_search(
            page=page,
            element_name='[data-test-id="20201119155820006856367"]',
            status_name="New-Unassigned",
            db_status_name="New-Unassigned",
            PATIENT_ID=PATIENT_ID
        )
        print("[LOG] Advanced search completed")
        sleep(5)  # Wait 10 seconds after advanced search
        
        # Step 3: Click Begin button
        begin_btn = debug_element_search("[data-test-id='201609091025020567152987']", "Begin button")
        if not begin_btn:
            begin_btn = debug_element_search("//button[normalize-space()='Begin']", "Begin button (fallback)")
        if not begin_btn:
            raise Exception("[ERROR] Begin button not found")
        robust_click(page, begin_btn)
        page.wait_for_load_state("networkidle")
        sleep(5)  # Wait 10 seconds after Begin
        
        # Step 4: Link Image in Viewer
        link_image_btn = debug_element_search("//button[normalize-space(.)='Link Image in Viewer']", "Link Image button")
        if link_image_btn:
            robust_click(page, link_image_btn)
            print("[LOG] Clicked Link Image in Viewer")
            sleep(5)  # Wait 10 seconds after Link Image
        
        # Step 5: Select DAW Code
        daw_dropdown = debug_element_search("//*[normalize-space(text())='DAW Code']/ancestor-or-self::*[contains(@class,'dataLabelFor')]/following-sibling::*//select", "DAW dropdown")
        if daw_dropdown:
            robust_select_option(page, daw_dropdown, "0 - No Product Selection Indicated")
            print("[LOG] Selected DAW code")
            sleep(5)  # Wait 10 seconds after DAW selection
        
        # Step 6: Search Drug workflow
        search_drug_btn = debug_element_search("[data-test-id='20170901173456065136464']", "Search Drug button")
        if search_drug_btn:
            robust_click(page, search_drug_btn)
            page.wait_for_load_state("networkidle")
            sleep(5)  # Wait 5 seconds for modal to load
        
        # Step 7: Select NDC and enter drug code
        ndc_dropdown = debug_element_search("[data-test-id='20200925062850019643650']", "NDC dropdown")
        if ndc_dropdown:
            robust_select_option(page, ndc_dropdown, "NDC")
            sleep(5)  # Wait 5 seconds for input to appear
        
        drug_input = debug_element_search("//input[@name='$PDrugSearch$ppySearchText']", "Drug Search input")
        if drug_input:
            robust_fill(page, drug_input, "00074055402")
            sleep(5)  # Wait 5 seconds after entering NDC
        
        # Step 8: Validation checkboxes (CRITICAL - use click_validation_checkbox for ALL 4)
        patient_checkbox = debug_element_search("//input[@data-test-id='202303231536300910155360']", "Patient checkbox")
        if patient_checkbox:
            click_validation_checkbox(patient_checkbox, "Patient checkbox")
        sleep(5)
        
        medication_checkbox = debug_element_search("//input[@data-test-id='20230324144929033857959']", "Medication checkbox")
        if medication_checkbox:
            click_validation_checkbox(medication_checkbox, "Medication checkbox")
        sleep(5)
        
        rx_details_checkbox = debug_element_search("//input[@data-test-id='20230324171608002687320']", "Rx Details checkbox")
        if rx_details_checkbox:
            click_validation_checkbox(rx_details_checkbox, "Rx Details checkbox")
        sleep(5)
        
        prescriber_checkbox = debug_element_search("//input[@data-test-id='202303271403440493899139']", "Prescriber checkbox")
        if prescriber_checkbox:
            click_validation_checkbox(prescriber_checkbox, "Prescriber checkbox")
        sleep(5)
        
        # Pattern continues with sleep(5) after each major action... """

    system_prompt_script_generation = f"""{output_example}"""

    Navigation_steps = """
## RxP System Navigation Steps

### **Phase 1: Initial Login and Setup**
1. **Navigate to Login Page**
   - Go to RxP login URL
   - Wait for page load

2. **Login Process**
   - Fill Username field
   - Fill Password field
   - Click Login button
   - Wait for authentication: page.wait_for_load_state("networkidle")
   - **CRITICAL: sleep(5) after login**
   - Check for and resolve session locks

### **Phase 2: Patient Case Search and Selection**
3. **Advanced Search for Patient Case - CRITICAL WINDOW HANDLING**
   - Click Advanced Search link (on main page)
   - **WAIT for new window/popup to open**
   - **Get all windows using: windows = page.context.pages**
   - **Switch to the NEW window (adv_search_page = windows[-1] or the one that's not the main page)**
   - **Bring new window to front: adv_search_page.bring_to_front()**
   - **ALL subsequent searches MUST use adv_search_page, NOT page**
   - Fill RxHome ID field **on adv_search_page**
   - Click Search button **on adv_search_page**
   - Click Open Case button **on adv_search_page**
   - Close Advanced Search window: adv_search_page.close()
   - Switch back to main page

4. **Begin Order Entry**
   - **CRITICAL: sleep(5) after advanced search**
   - Check for and resolve session locks before proceeding
   - Click Begin button with retry mechanism
   - **CRITICAL: sleep(5) after clicking Begin**

### **Phase 3: Order Entry Process**
5. **Link Image in Viewer**
   - Click "Link Image in Viewer" button
   - **CRITICAL: sleep(5) after Link Image**

6. **Set DAW Code**
   - Select DAW dropdown
   - Choose: "0 - No Product Selection Indicated"
   - **CRITICAL: sleep(5) after DAW selection**

7. **Drug Search and Selection (CRITICAL SEQUENCE)**
   - Click Search Drug button
   - **WAIT: page.wait_for_load_state('networkidle') + sleep(5)**
   - Select NDC dropdown (data-test-id='20200925062850019643650')
   - Choose "NDC" option from dropdown
   - **WAIT: sleep(5) for Drug Search Input to appear**
   - Enter NDC code: "00074055402" in Drug Search Input
   - **WAIT: sleep(5) after entering NDC**
   - Click Search button in modal
   - **WAIT: sleep(5) for results to load**
   - Select drug row from results
   - **WAIT: sleep(5) after selecting drug**
   - Click Submit
   - **WAIT: sleep(5) after submitting drug**

8. **SIG Configuration**
   - Click Common SIG button
   - Select SIG: "INJECT 40 MG (0.4 ML) UNDER THE SKIN EVERY 2 WEEKS"
   - **WAIT: sleep(5) after SIG selection**
   - **WAIT: sleep(5) before entering prescription details**
   - Set Quantity: "1"
   - **WAIT: sleep(5) after Quantity**
   - Set Days Supply: "14"
   - **WAIT: sleep(5) after Days Supply**
   - Set Doses: "1"
   - **WAIT: sleep(5) after Doses**
   - Set Refills: "1"
   - **WAIT: sleep(5) after Refills**

9. **Apply Rules and Review**
   - Click Apply Rules
   - **WAIT: sleep(5) after Apply Rules**
   - Click Reviewed
   - **WAIT: sleep(5) after Reviewed**
   - Click Accept Changes (if present)

### **Phase 4: Data Validation**
10. **Validate ALL Four Sections (Patient, Medication, Rx Details, Prescriber)**
    - **CRITICAL: ALL checkboxes may be off-screen as page scrolls**
    - **ALWAYS use click_validation_checkbox() helper for ALL 4 checkboxes**
    - Pattern for each checkbox:
      ```
      checkbox = debug_element_search(selector, name)
      if checkbox:
          click_validation_checkbox(checkbox, name)
      sleep(5)
      ```
    
11. **Patient Section**
    - Find: //input[@data-test-id='202303231536300910155360']
    - Use: click_validation_checkbox(patient_checkbox, "Patient checkbox")
    - **WAIT: sleep(5)**

12. **Medication Section**
    - Find: //input[@data-test-id='20230324144929033857959']
    - Use: click_validation_checkbox(medication_checkbox, "Medication checkbox")
    - **WAIT: sleep(5)**

13. **Rx Details Section**
    - Find: //input[@data-test-id='20230324171608002687320']
    - Use: click_validation_checkbox(rx_details_checkbox, "Rx Details checkbox")
    - **WAIT: sleep(5)**

14. **Prescriber Section**
    - Find: //input[@data-test-id='202303271403440493899139']
    - Use: click_validation_checkbox(prescriber_checkbox, "Prescriber checkbox")
    - **WAIT: sleep(5)**

15. **Proceed to Trend Processing**
    - Scroll to Next button: next_btn.scroll_into_view_if_needed()
    - Click Next using enhanced_click()
    - **WAIT: sleep(5) after clicking Next**

### **Phase 5: Post-Order Processing**
16. **Close and Search for Edit Messages**
    - **CRITICAL: Close button appears AFTER Next is clicked**
    - Use retry loop with 15 attempts (30 seconds)
    - Wait for Close button to become visible
    - Click Close using enhanced_click()
    - **WAIT: sleep(5) after Close**
    - Advanced search for "Pending-EditMessages" status
    - Click Begin for edit processing

17. **Submit Edit Changes**
    - Click Submit
    - Close window

18. **Rph Verification Process**
    - Advanced search for "Rph Verification In Progress" status
    - Click Begin for verification
    - Perform multiple verification clicks (5 verification buttons)

19. **DUR Resolution**
    - Click Next
    - Fill DUR comment: "RPh Approved Professional Judgement"
    - Click Submit

20. **Final Status Selection**
    - Advanced search for "Select a Status" status
    - Complete final processing steps
"""

    # Build enhanced page elements section if provided
    page_elements_section = ""
    if page_elements:
        # Enhanced element mapping for better selector selection
        data_test_id_map = page_elements.get('data_test_id_map', {})
        priority_selectors = page_elements.get('priority_selectors', [])
        
        page_elements_section = f"""
    <PAGE_ELEMENTS>
    Available elements on the page (PRIORITIZE data-test-id selectors):
    
    **CRITICAL: Always use data-test-id selectors when available for maximum stability**
    
    Data-test-id elements: {len(page_elements.get('data_test_ids', []))} found
    {json.dumps(page_elements.get('data_test_ids', [])[:15], indent=2)}  # First 15 shown
    
    **INTELLIGENT ELEMENT MAPPING (Use these exact selectors):**
    {json.dumps(data_test_id_map, indent=2)}
    
    **PRIORITY SELECTORS (Use in this order):**
    {json.dumps(priority_selectors, indent=2)}
    
    Name attributes: {len(page_elements.get('name_attributes', []))} found
    {json.dumps(page_elements.get('name_attributes', [])[:10], indent=2)}  # First 10 shown
    
    ID attributes: {len(page_elements.get('id_attributes', []))} found
    {json.dumps(page_elements.get('id_attributes', [])[:10], indent=2)}  # First 10 shown
    
    Buttons: {len(page_elements.get('buttons', []))} found
    Inputs: {len(page_elements.get('inputs', []))} found
    Links: {len(page_elements.get('links', []))} found
    
    **SELECTOR PRIORITY ORDER:**
    1. Use data_test_id_map selectors FIRST (most reliable)
    2. Use priority_selectors SECOND (pre-validated)
    3. Fall back to name/id/xpath selectors LAST
    
    Use these selectors in your generated code with find_element_across_frames()
    </PAGE_ELEMENTS>
    """
    
    user_input = f"""
    Application name: RxP
    
    <INFO>
    patient_id: {patient_id}
    USERNAME: LAN_ID 
    PASSWORD: PASSWORD
    </INFO>
    
    {page_elements_section}

    <AUTOMATION_STEPS>
    {steps}
    </AUTOMATION_STEPS>
    
    <REQUIREMENTS>
    1. Use find_element_across_frames() for ALL element lookups (searches across iframes)
    2. Use robust_click(), robust_fill(), robust_select_option() instead of direct Playwright methods
    
    **CRITICAL DATA-TEST-ID PRIORITY REQUIREMENTS:**
    3. ALWAYS use rxp_element_reference_database selectors FIRST (proven working selectors)
    4. Use data_test_id_map SECOND for intelligent element mappings
    5. Use priority_selectors THIRD for pre-validated selectors  
    6. ONLY use name/id/xpath as LAST resort when data-test-id not available
    7. Example: Use '[data-test-id="20180715225236062436158"]' for RxHome ID field
    
    8. Use xpath for buttons with text ONLY when no data-test-id available: '//button[normalize-space()="Text"]'
    9. Always use the utility functions from rxp_agent_utils
    10. Replace any hardcoded patient ID with the variable PATIENT_ID = "{patient_id}"
    11. Generate ONLY the test function, no extra utility functions
    
    **SELECTOR SELECTION PRIORITY (MANDATORY ORDER):**
    - 1st Choice: rxp_element_reference_database selectors (proven working selectors)
    - 2nd Choice: data_test_id_map selectors (intelligent mappings)
    - 3rd Choice: priority_selectors (pre-validated)  
    - 4th Choice: data-test-id from PAGE_ELEMENTS data_test_ids
    - 5th Choice: name attributes (fallback)
    - 6th Choice: id attributes (fallback)
    - 7th Choice: xpath (last resort)
    
    **DROPDOWN SELECTION REQUIREMENTS (CRITICAL):**
    - ALWAYS use the FULL option text from the steps, not abbreviated versions
    - Example: Use "0 - No Product Selection Indicated", NOT just "0"
    - Example: Use "NDC" not "N"
    - The robust_select_option() function requires exact text match with the visible option text
    - Check the rxp_element_reference_database for the correct full text to use
    
    **WAIT STRATEGY REQUIREMENTS (CRITICAL):**
    11. Set extended timeouts: page.set_default_timeout(60000) and page.set_default_navigation_timeout(60000)
    12. After page.goto() - ALWAYS use: page.wait_for_load_state('networkidle', timeout=60000)
    13. After clicks that navigate/load content - use: page.wait_for_load_state('networkidle', timeout=30000)
    14. Before interacting with dynamic elements - use: element.wait_for(state='visible', timeout=30000)
    15. For checking element state - use: element.is_visible(), element.is_enabled()
    16. **CRITICAL: Add sleep(5) between ALL major steps for stability**
    17. Use page.wait_for_timeout() ONLY as absolute last resort (prefer networkidle/element waits)
    18. For elements that may take time - wrap in try-except with retry logic and extended timeouts
    19. Add comprehensive debug logging for element searches and wait operations
    20. **PATTERN: Always use page.wait_for_load_state('networkidle') THEN sleep(5) after actions**
    
    **ADVANCED SEARCH WORKFLOW REQUIREMENTS (CRITICAL):**
    18. CRITICAL: Begin button is in MAIN PAGE, NOT Advanced Search page after opening case
    19. Close Advanced Search window after opening case and return to main page
    20. Use main page context selectors for Begin button
    21. Verify page context before looking for elements
    
    **WINDOW/POPUP HANDLING REQUIREMENTS (ABSOLUTELY CRITICAL):**
    22. **ALWAYS USE advanced_search() utility function for Advanced Search workflow**
    23. The advanced_search() function handles ALL window switching internally - DO NOT do it manually
    24. Example usage:
        ```python
        from rxp_agent_utils import advanced_search
        
        # This handles clicking Advanced Search, switching windows, searching, and closing popup
        advanced_search(
            page=page,
            element_name='[data-test-id="20201119155820006856367"]',  # Open Case button selector
            status_name="New-Unassigned",  # Status to filter by (or empty string for any)
            db_status_name="New-Unassigned",  # DB status (usually same as status_name)
            PATIENT_ID=PATIENT_ID
        )
        # After this call, you're back on the main page and case is opened
        ```
    25. ONLY do manual window handling if you absolutely cannot use advanced_search()
    26. If manual handling is required:
        a. Use page.context.expect_page() to wait for new window
        b. Or get windows = page.context.pages after clicking and wait for len(windows) > 1
        c. Switch to new window: adv_search_page.bring_to_front()
        d. Use adv_search_page for ALL popup element searches
        e. Close popup: adv_search_page.close() and return to main page
    27. The RxHome ID field exists ONLY in the Advanced Search popup, NOT in main page
    28. The Search button exists ONLY in the Advanced Search popup, NOT in main page
    
    **SESSION LOCK HANDLING REQUIREMENTS (CRITICAL):**
    29. ALWAYS check for and handle session locks before proceeding with automation
    30. Use handle_session_lock(page) function after login and before any case operations
    31. Call handle_session_lock() after opening a case and before clicking Begin button
    32. Session locks commonly occur when same user is logged in from multiple locations
    33. Example usage:
        ```python
        from rxp_agent_utils import handle_session_lock
        
        # After login and before case operations
        handle_session_lock(page)
        
        # After opening case and before Begin button
        handle_session_lock(page)
        ```
    
    **ERROR HANDLING REQUIREMENTS:**
    34. Always check if element exists before interaction: if not element: raise Exception()
    35. Use try-except for operations that might fail
    36. Include descriptive error messages with selector info
    37. Add print statements for logging: [LOG], [ERROR], [WARNING], [SUCCESS]
    38. ALWAYS include debug_element_search() function in generated code for troubleshooting
    39. Use multiple selector fallbacks for critical elements like login, search, and navigation buttons
    40. Include screenshot capability for debugging complex failures
    41. ALWAYS use enhanced_element_finding_patterns for critical buttons (Begin, Submit, etc.)
    42. Include text-based search as fallback when standard selectors fail
    43. Use multiple click strategies (normal, force, JS) for stubborn elements
    
    **VALIDATION CHECKBOX REQUIREMENTS (CRITICAL):**
    44. ALL validation checkboxes (Patient, Medication, Rx Details, Prescriber) may be off-screen
    45. ALWAYS create a click_validation_checkbox() helper function for ALL checkboxes
    46. Use zoom + scroll + JavaScript click pattern for maximum reliability
    47. Example pattern - ALWAYS INCLUDE THIS HELPER:
        ```python
        def click_validation_checkbox(checkbox, checkbox_name):
            """Enhanced checkbox clicking with zoom + scroll + multiple strategies."""
            print(f"[LOG] Clicking {checkbox_name}...")
            
            try:
                # Zoom out to see checkbox
                page.evaluate("document.body.style.zoom = '0.75'")
                sleep(1)
                
                # Scroll into view
                checkbox.scroll_into_view_if_needed()
                sleep(2)
                
                # Try JavaScript click (most reliable)
                checkbox.evaluate("(el) => { el.checked = true; el.click(); }")
                print(f"[LOG] ✅ {checkbox_name} checked (JavaScript)")
                
                # Reset zoom
                page.evaluate("document.body.style.zoom = '1.0'")
                sleep(1)
                return True
                
            except Exception as e1:
                print(f"[WARNING] JavaScript click failed: {e1}")
                try:
                    # Try force click
                    checkbox.click(force=True, timeout=10000)
                    print(f"[LOG] ✅ {checkbox_name} checked (force click)")
                    page.evaluate("document.body.style.zoom = '1.0'")
                    return True
                except Exception as e2:
                    print(f"[WARNING] Force click failed: {e2}")
                    try:
                        # Try enhanced_click
                        if enhanced_click(checkbox, checkbox_name):
                            print(f"[LOG] ✅ {checkbox_name} checked (enhanced_click)")
                            page.evaluate("document.body.style.zoom = '1.0'")
                            return True
                    except:
                        pass
                    
                    # Always reset zoom
                    try:
                        page.evaluate("document.body.style.zoom = '1.0'")
                    except:
                        pass
                    
                    print(f"[WARNING] Could not check {checkbox_name}")
                    return False
        ```
    48. **Usage for ALL 4 checkboxes:**
        ```python
        # Patient checkbox
        patient_checkbox = debug_element_search("//input[@data-test-id='202303231536300910155360']", "Patient checkbox")
        if patient_checkbox:
            click_validation_checkbox(patient_checkbox, "Patient checkbox")
        sleep(5)
        
        # Medication checkbox
        medication_checkbox = debug_element_search("//input[@data-test-id='20230324144929033857959']", "Medication checkbox")
        if medication_checkbox:
            click_validation_checkbox(medication_checkbox, "Medication checkbox")
        sleep(5)
        
        # Rx Details checkbox
        rx_details_checkbox = debug_element_search("//input[@data-test-id='20230324171608002687320']", "Rx Details checkbox")
        if rx_details_checkbox:
            click_validation_checkbox(rx_details_checkbox, "Rx Details checkbox")
        sleep(5)
        
        # Prescriber checkbox
        prescriber_checkbox = debug_element_search("//input[@data-test-id='202303271403440493899139']", "Prescriber checkbox")
        if prescriber_checkbox:
            click_validation_checkbox(prescriber_checkbox, "Prescriber checkbox")
        sleep(5)
        ```
    49. **SPECIAL HANDLING for Next button (may be below fold):**
        ```python
        next_btn.scroll_into_view_if_needed()
        sleep(2)
        if enhanced_click(next_btn, "Next button"):
            print("[LOG] Clicked Next")
        ```
    
    **CLICK TIMEOUT ERROR HANDLING (CRITICAL):**
    50. ALWAYS include enhanced_click() helper function in generated code to handle hover timeouts
    51. Use enhanced_click() for ALL buttons to avoid hover timeouts
    52. The enhanced_click() function tries 4 strategies:
        1. robust_click (hover + click)
        2. click(force=True) - skips actionability checks
        3. JavaScript click - bypasses Playwright entirely
        4. scroll_into_view + click - ensures element is in viewport
    53. Example usage:
        ```python
        if enhanced_click(common_sig_btn, "Common SIG button"):
            print("[LOG] Successfully clicked")
        else:
            print("[WARNING] Click failed with all strategies")
        ```
    
    **DYNAMIC ELEMENT WAITING (CRITICAL):**
    54. Some elements appear AFTER clicking another button (e.g., Close appears after Next)
    55. Use retry loop with multiple attempts for elements that load dynamically:
        ```python
        # Close button appears after Next is clicked
        close_btn = None
        max_attempts = 15
        for attempt in range(1, max_attempts + 1):
            element = find_element_across_frames(page, selector)
            if element and element.is_visible(timeout=2000):
                close_btn = element
                break
            sleep(2)
            page.wait_for_load_state("networkidle", timeout=5000)
        
        if not close_btn:
            screenshot(page, "element_not_found")
            raise Exception("Element not found after retries")
        ```
    </REQUIREMENTS>
"""
    messages = [SystemMessage(system_prompt_script_generation), HumanMessage(user_input)]
    
    # Invoke LLM with tools
    print("[LOG] Invoking LLM with tool support...")
    response = llm_with_tools.invoke(messages)
    
    # Check if LLM made tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"[LOG] LLM made {len(response.tool_calls)} tool calls:")
        for tool_call in response.tool_calls:
            print(f"  - Tool: {tool_call['name']}")
            print(f"    Args: {tool_call['args']}")
    
    # Extract the generated code
    llm_code = response.content
    parsed_code = extract_python_code(llm_code)
    
    print("\n[LOG] Generated code preview:")
    print("=" * 80)
    print(parsed_code[:500] + "..." if len(parsed_code) > 500 else parsed_code)
    print("=" * 80)
    
    # Replace the placeholder values with actual patient_id
    parsed_code = parsed_code.replace("{patient_id}", f'"{patient_id}"')
    
    return parsed_code


def generate_rxp_code_with_page_inspection(patient_id, steps, page=None):
    """
    Enhanced version that uses inspect_current_page if a page object is provided.
    
    Example usage:
        from playwright.sync_api import sync_playwright
        from inspect_current_page import inspect_current_page
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto("https://your-rxp-url.com")
            
            # Inspect the page to get available elements
            page_elements = inspect_current_page(page)
            
            # Generate code with element awareness
            code = generate_rxp_code_with_page_inspection("17161379", steps, page)
            
            browser.close()
    
    Args:
        patient_id: Patient ID for the test
        steps: Test steps to automate
        page: Optional Playwright page object for inspection
        
    Returns:
        Generated Playwright code
    """
    page_elements = None
    
    if page:
        print("[LOG] Page object provided, inspecting page elements...")
        try:
            from inspect_current_page import inspect_current_page
            page_elements = inspect_current_page(page)
            print(f"[LOG] Found {len(page_elements.get('data_test_ids', []))} data-test-id elements")
            print(f"[LOG] Found {len(page_elements.get('buttons', []))} buttons")
            print(f"[LOG] Found {len(page_elements.get('inputs', []))} input fields")
        except Exception as e:
            print(f"[WARNING] Could not inspect page: {e}")
            print("[LOG] Continuing without page element inspection...")
    
    return generate_rxp_code(patient_id, steps, page_elements)


# Example usage - basic code generation without page inspection
if __name__ == "__main__":
    print("Generating RxP automation code...")
    code = generate_rxp_code("17161379", steps)
    print("---------CODE--------------",code)
    print("\n[SUCCESS] Code generated!")
    
    # To use with page inspection, uncomment and modify:
    # from playwright.sync_api import sync_playwright
    # with sync_playwright() as p:
    #     browser = p.chromium.launch()
    #     page = browser.new_page()
    #     page.goto("https://sprxp-qa.express-scripts.com/sprxp/")
    #     code = generate_rxp_code_with_page_inspection("17161379", steps, page)
    #     browser.close()

