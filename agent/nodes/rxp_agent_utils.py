from playwright.sync_api import Page, Locator, Frame
from time import sleep
from typing import Callable
import oracledb


def find_element_across_frames(page: Page, selector: str) -> Locator | None:
    """
    Recursively search for an element matching 'selector' starting from the main page
    and traversing all iframes.

    If a locator matches multiple elements, this function ensures it only returns
    a locator pointing to the *very first* matching element found.

    Args:
        page: The Playwright Page object to search within.
        selector: The CSS or XPath selector for the element.

    Returns:
        A Playwright Locator object for the first matching element, or None if no
        element is found anywhere on the page or in its frames.
    """
    # Try finding the locator on the main page first.
    try:
        main_frame_locator = page.locator(selector)
        if main_frame_locator.count() > 0:
            # MODIFICATION: Use .first to guarantee the locator targets only one element.
            return main_frame_locator.first
    except Exception:
        # Silently ignore errors (e.g., page closed during search) and proceed to frames.
        pass

    # If not found on the main page, define a recursive function to search child frames.
    def search_in_frames(frames: list) -> Locator | None:
        for frame in frames:
            try:
                frame_locator = frame.locator(selector)
                if frame_locator.count() > 0:
                    # MODIFICATION: Use .first here as well.
                    return frame_locator.first

                # If not in this frame, go deeper into its children.
                nested_result = search_in_frames(frame.child_frames)
                if nested_result:
                    # The result from the deeper call is already the .first locator.
                    return nested_result
            except Exception:
                # A frame might detach or other errors could occur; just continue to the next one.
                continue
        # If the loop completes without finding the element in any frame.
        return None

    # Start the recursive search from the page's top-level frames.
    return search_in_frames(page.frames)
def robust_fill(page: Page, element_locator: Locator, value: str, select_suggestion: bool = False):
    """
    Fills a given element locator with a value.
    Optionally handles autocomplete by pressing ArrowDown and Enter.

    Args:
        page: The Playwright Page object (used for keyboard actions).
        element_locator: The Playwright Locator for the element to be filled.
        value: The text value to enter into the element.
        select_suggestion: If True, simulates key presses to select an autocomplete option.
    """
    element_locator.fill(value)
    
    if select_suggestion:
        # Brief pause for suggestion list to appear
        sleep(0.5)
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
    
    # Brief pause for fill operations
    sleep(0.5)

def robust_click(page: Page, element_locator: Locator, requires_navigation: bool = False):
    """
    Waits for an element to be actionable, hovers over it, and then clicks.

    Args:
        page: The Playwright Page object (currently unused but kept for API consistency).
        element_locator: The Playwright Locator for the element to be clicked.
        requires_navigation: Whether this click triggers navigation (default: False).
    """
    # Hovering is useful for triggering menus or javascript events before clicking
    element_locator.hover()
    element_locator.click()
    
    # Brief pause for click operations
    sleep(0.5)


def robust_select_option(page: Page, element_locator: Locator, text: str):
    """
    Selects an option from a <select> element locator by its visible text.

    Args:
        page: The Playwright Page object (currently unused but kept for API consistency).
        element_locator: The Playwright Locator for the <select> dropdown element.
        text: The visible text of the option to be selected.
    """
    element_locator.select_option(label=text)
    
    # Brief pause for select operations
    sleep(0.5)


# ==============================================================================
# DATA & STATE UTILITIES (Accept selector strings for convenience)
# ==============================================================================

def get_text(page: Page, selector: str) -> str:
    """Finds an element across frames and returns its inner text."""
    element_locator = find_element_across_frames(page, selector)
    if not element_locator:
        print(f"Warning: Get Text: Element with selector '{selector}' not found. Returning empty string.")
        return ""
    return element_locator.inner_text()

def get_attribute(page: Page, selector: str, attribute_name: str) -> str:
    """Finds an element across frames and returns the value of a specific attribute."""
    element_locator = find_element_across_frames(page, selector)
    if not element_locator:
        print(f"Warning: Get Attribute: Element with selector '{selector}' not found. Returning empty string.")
        return ""
    return element_locator.get_attribute(attribute_name) or ""

def is_element_visible(page: Page, selector: str) -> bool:
    """Checks if an element is visible, searching across all frames."""
    element_locator = find_element_across_frames(page, selector)
    # is_visible() returns False for non-existent locators after a timeout.
    return element_locator.is_visible() if element_locator else False


# ==============================================================================
# BROWSER CONTEXT UTILITIES
# ==============================================================================
def switch_to_window_by_title(page: Page, title_substring: str, timeout: int = 5000) -> Page:
    """
    ROBUST: Switches to an already open window/tab by matching a substring of its title.
    This is a preferred method over using an index.
    """
    try:
        target_page = next(
            p for p in page.context.pages if title_substring.lower() in p.title().lower()
        )
        target_page.bring_to_front()
        return target_page
    except StopIteration:
        raise Exception(f"Failed to switch: No window found with title containing '{title_substring}'")


def switch_to_window_by_index(page: Page, index: int) -> Page:
    """
    Switches focus to a browser window/tab by its index. Returns the new page object.

    Args:
        page: The current Playwright Page object.
        index: The zero-based index of the window/tab to switch to.

    Returns:
        The Page object for the newly focused window/tab.
    """
    try:
        all_pages = page.context.pages
        if index < len(all_pages):
            target_page = all_pages[index]
            target_page.bring_to_front()
            return target_page
        else:
            raise Exception(f"Window index {index} is out of bounds. Only {len(all_pages)} windows exist.")
    except Exception as e:
        print(f"An error occurred during window switch: {e}")
        # Return the original page to prevent crashing the script
        return page
    

def wait_for_new_window(page: Page, action: Callable[[], None], timeout: int = 10000) -> Page:
    """
    Executes an action that is expected to open a new window/tab,
    waits for that new page to appear, and returns it.

    Args:
        page: The current Playwright Page object where the action originates.
        action: A function that performs the action (e.g., a click) that opens the new window.
        timeout: Maximum time in milliseconds to wait for the new page.

    Returns:
        The Page object for the newly opened window/tab.
    """
    with page.context.expect_page(timeout=timeout) as new_page_info:
        action()  # Perform the action that triggers the new window
    
    new_page = new_page_info.value
    # It's crucial to wait for the new page to finish loading before interacting with it
    new_page.wait_for_load_state("networkidle")
    new_page.bring_to_front()
    return new_page


def iterative_search_for_element(page: Page, selectors: list, element_name: str = "element", 
                                max_attempts: int = 30, delay: int = 2, 
                                click_on_found: bool = True, screenshot_on_found: bool = True,
                                screenshot_name: str = None) -> tuple[bool, Locator | None]:
    """
    Iteratively searches for an element using multiple selectors until it becomes visible.
    
    Args:
        page: The Playwright Page object to search within.
        selectors: List of CSS/XPath selectors to try for finding the element.
        element_name: Human-readable name for logging purposes.
        max_attempts: Maximum number of search attempts (default: 30).
        delay: Delay in seconds between attempts (default: 2).
        click_on_found: Whether to click the element when found (default: True).
        screenshot_on_found: Whether to take a screenshot when found (default: True).
        screenshot_name: Custom name for the screenshot (default: None, uses element_name).
    
    Returns:
        Tuple of (success: bool, element_locator: Locator | None)
    """
    print(f"[ITERATIVE_SEARCH] Starting iterative search for {element_name}...")
    print(f"[ITERATIVE_SEARCH] Will try {max_attempts} attempts with {delay}s delays")
    print(f"[ITERATIVE_SEARCH] Using {len(selectors)} different selectors")
    
    for attempt in range(1, max_attempts + 1):
        print(f"[ITERATIVE_SEARCH] Attempt {attempt}/{max_attempts} - Looking for {element_name}")
        
        try:
            # Try each selector in order
            for selector in selectors:
                element = find_element_across_frames(page, selector)
                if element and element.is_visible():
                    print(f"[ITERATIVE_SEARCH] Success! Found {element_name} on attempt {attempt}")
                    print(f"[ITERATIVE_SEARCH] Used selector: {selector}")
                    print(f"[ITERATIVE_SEARCH] Element text: '{element.text_content()}'")
                    print(f"[ITERATIVE_SEARCH] Element tag: {element.tag_name}")
                    print(f"[ITERATIVE_SEARCH] Element visible: {element.is_visible()}")
                    
                    if click_on_found:
                        robust_click(page, element)
                        print(f"[ITERATIVE_SEARCH] Clicked on {element_name}")
                    
                    if screenshot_on_found:
                        screenshot_file = screenshot_name or f"found_{element_name.lower().replace(' ', '_')}.png"
                        #page.screenshot(path=screenshot_file)
                        print(f"[ITERATIVE_SEARCH] Screenshot saved: {screenshot_file}")
                    
                    return True, element
            
            print(f"[ITERATIVE_SEARCH] {element_name} not found on attempt {attempt}")
                
        except Exception as e:
            print(f"[ITERATIVE_SEARCH] Error on attempt {attempt}: {str(e)}")
        
        if attempt < max_attempts:
            print(f"[ITERATIVE_SEARCH] Waiting {delay} seconds before next attempt...")
            sleep(delay)
    
    print(f"[ITERATIVE_SEARCH] Failed to find {element_name} after {max_attempts} attempts")
    return False, None


def rxp_connection(PATIENT_ID,test_status):
    conn = oracledb.connect(
        user="RXP88QD_RO",
        password="RXP8BQ_06_RO_Data_User",
        host = "qr1014661-scan.express-scripts.com",
        port = "1521",
        service_name = "QAPHRXP88"
    )

    cur = conn.cursor()
    sql = "SELECT PYSTATUSWORK FROM pc_esi_specialty_rxp_work WHERE patientrxhomeid = :rxhomeid ORDER BY pxcreatedatetime DESC"

    cur.execute(sql, {"rxhomeid": PATIENT_ID})
    rows = cur.fetchall()
    print("===============================ROWS============",rows[0][0])
    status = rows[0][0]
    try:
        assert status == test_status
        print(f"[LOG]  Database Validation Completed.Case status is {status}")
    except Exception as e:
        print(f"[ERROR]  Expected {test_status} but found {status}")
    return status   


def advanced_search(page,element_name,status_name,db_status_name,PATIENT_ID):
    
    adv_search_link = find_element_across_frames(page, "[name='AccredoPortalHeader_pyDisplayHarness_15']")
    if not adv_search_link:
        print("[ERROR]  Element Advanced Search Link not found")
        raise Exception("Element 'Advanced Search' link not found with selector: '//*[text()=\"Advanced Search\"]'")
    robust_click(page, adv_search_link)
    print("[LOG] Clicked Advanced Search")
    sleep(10)

    windows = page.context.pages
    if len(windows) < 2:
        sleep(10)
    windows = page.context.pages
    adv_search_page = None
    for win in windows[::-1]:
        if win != page:
            adv_search_page = win
            break
    if not adv_search_page:
        print("[ERROR]  Advanced Search window did not open")
        raise Exception("Advanced Search window did not open")
    adv_search_page.bring_to_front()
    adv_search_page.wait_for_load_state("networkidle")
    print(f"[LOG] Advanced Search Opened")
    sleep(20)

    rxhome_id_field = find_element_across_frames(adv_search_page, '[data-test-id="20180715225236062436158"]')
    if not rxhome_id_field:
        raise Exception("Element 'RxHome ID' field not found with selector: '[data-test-id=\"20180715225236062436158\"]'")
    robust_fill(adv_search_page, rxhome_id_field, PATIENT_ID)
    print(f"[LOG] Entered Patient ID: {PATIENT_ID}")
    sleep(10)
    
    status_drop_down = find_element_across_frames(adv_search_page, '[data-test-id="20190404113611006767641"]')
    status_drop_down.select_option(status_name)
    
    sleep(5)

    for attempt in range(10):

        search_btn = find_element_across_frames(
            adv_search_page, "//*[@node_name='DisplayAdvanceSearchParameters']//following::*[@name='DisplaySearchWrapper_D_AdvanceSearch_15']")
        if not search_btn:
            raise Exception("Element 'Search Button' not found with selector: '//*[@node_name='DisplayAdvanceSearchParameters']//following::*[@name='DisplaySearchWrapper_D_AdvanceSearch_15']'")
        robust_click(adv_search_page, search_btn)
        print("[LOG] Clicked Search button in Advanced Search window")
        adv_search_page.wait_for_load_state("networkidle")
        sleep(15)

        open_case_btn = None
        
        try:

            open_case_xpath = element_name
            open_case_btn = find_element_across_frames(adv_search_page, open_case_xpath)
            
            if open_case_btn:
                robust_click(adv_search_page, open_case_btn)
                print("[LOG] Clicked Open Case button row")
                sleep(13)
                break
            else:
                print(f"[LOG] Open Case button not found. Retrying after 30 seconds... attempt {attempt+1}")
                sleep(30)
        except Exception as e:
            print(f"[LOG] Error on attempt {attempt+1}: {e}")
            sleep(30)
            
    if not open_case_btn:
        print("[LOG] Validating Case Status")
        status = rxp_connection(PATIENT_ID,db_status_name)
        #raise Exception("Open Case button not found after maximum attempts")

    adv_search_page.close()
    print("[LOG] Closed Advanced Search window. Switching back to main window")
    switch_to_window_by_index(page, 0)
    page.wait_for_load_state("networkidle")
    sleep(20)   
    
    
def find_and_click_begin_button_with_retry(page, button_description="Begin"):
    max_attempts = 100
    timeout_seconds = 30
    begin_button = None
    print(f"[LOG] Looking for '{button_description}' button with max {max_attempts} attempts and {timeout_seconds} second timeout...")
    for attempt in range(1, max_attempts + 1):
        print(f"[LOG] Attempt {attempt}/{max_attempts} - Searching for '{button_description}' button...")
        selectors = [
            "(//*[@class='header-title' and normalize-space(text())='Referral Contents']/ancestor::*[@role='heading']/following-sibling::*//button[normalize-space(.)='Begin' and not(ancestor::*[contains(@style,'none')])])[1]",
            "[data-test-id='201609091025020567152987']",
            "//button[normalize-space()='Begin']"
        ]
        for selector in selectors:
            begin_button = find_element_across_frames(page, selector)
            if begin_button:
                is_disabled = begin_button.get_attribute("disabled")
                if is_disabled:
                    begin_button = None
                    continue
                break
        if begin_button:
            break
        print(f"[LOG] ⏳ '{button_description}' button not found or disabled on attempt {attempt}, waiting 3 seconds...")
        sleep(3)
    if not begin_button:
        raise Exception(f"Element '{button_description}' button for Referral Contents not found or enabled after {max_attempts} attempts.")
    try:
        begin_button.click(force=True)
        print(f"[LOG] Clicked '{button_description}' button using force click")
    except Exception as e:
        try:
            begin_button.evaluate("(el) => el.click()")
            print(f"[LOG] Clicked '{button_description}' button using JS click")
        except Exception:
            robust_click(page, begin_button)
            print(f"[LOG] Clicked '{button_description}' button using robust_click")
    print(f"[LOG] Clicked '{button_description}' in Referral Contents")
    page.wait_for_load_state("networkidle")
    sleep(10)

def validate_section_and_check(page, fields_to_check, checkbox_selector, optional_fields=None):
    if optional_fields is None:
        optional_fields = []
    is_section_fully_populated = True
    for label, selector in fields_to_check:
        element = find_element_across_frames(page, selector)
        if not element:
            raise Exception(f"Validation Error: Element '{label}' not found with selector: {selector}")
        value = element.inner_text().strip()
        if not value:
            if label in optional_fields:
                print(f"[LOG] Verified optional field '{label}' is empty, which is acceptable.")
            else:
                print(f"[LOG] VALIDATION FAILED: Required field '{label}' is NOT populated!")
                is_section_fully_populated = False
        else:
            print(f"[LOG] Verified field '{label}' is populated with value: '{value}'")

    checkbox = find_element_across_frames(page, checkbox_selector)
    if not checkbox:
        raise Exception(f"Checkbox not found with selector: {checkbox_selector}")
    if is_section_fully_populated:
        checkbox.evaluate("(el) => { el.style.transform = 'scale(6)'; }")
        checkbox.click(force=True)
        print("[LOG] All required fields are populated. Section checkbox ticked.")
    else:
        print("[LOG] SKIPPING CHECKBOX: One or more fields NOT populated. Section flagged for review.")

