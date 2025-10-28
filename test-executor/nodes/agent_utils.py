from playwright.sync_api import Page, Locator, Frame
from time import sleep
from typing import Callable

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
            print(main_frame_locator.first)
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

def robust_fill(page: Page, selector: str, value: str, select_suggestion: bool = False):
    """
    Finds an element across all frames and fills it with a value.
    Optionally handles autocomplete by pressing ArrowDown and Enter.
    """
    print(f"Attempting to fill element '{selector}' with value '{value}'.")
    element_locator = find_element_across_frames(page, selector)
    if not element_locator:
        raise Exception(f"Robust Fill: Element with selector '{selector}' not found.")
    
    element_locator.fill(value)
    
    if select_suggestion:
        print("Selecting first autocomplete suggestion.")
        sleep(0.5)  # Brief pause for suggestion list to appear
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        
    print(f"Successfully filled '{selector}'.")

# In agent_utils.py

def robust_click(page: Page, selector: str):
    """
    Finds an element across all frames, waits for it to be actionable,
    hovers over it, and then clicks.
    """
    print(f"Attempting to click element '{selector}'.")
    element_locator = find_element_across_frames(page, selector)
    if not element_locator:
        raise Exception(f"Robust Click: Element with selector '{selector}' not found.")
        
    # Hovering is useful for triggering menus or javascript events before clicking
    element_locator.hover()
    element_locator.click()
    print(f"Successfully clicked '{selector}'.")

# In agent_utils.py

def robust_select_option(page: Page, selector: str, text: str):
    """
    Finds a <select> element across all frames and selects an option by its visible text.
    """
    print(f"Attempting to select option '{text}' from dropdown '{selector}'.")
    element_locator = find_element_across_frames(page, selector)
    if not element_locator:
        raise Exception(f"Robust Select: Dropdown with selector '{selector}' not found.")
        
    element_locator.select_option(label=text)
    print(f"Successfully selected option '{text}' from '{selector}'.")

# In agent_utils.py

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
    return element_locator.is_visible() if element_locator else False


# In agent_utils.py

def switch_to_window_by_index(page: Page, index: int) -> Page:
    """
    Switches focus to a browser window/tab by its index.
    Returns the new page object.
    """
    print(f"Attempting to switch to window at index {index}.")
    try:
        all_pages = page.context.pages
        if index < len(all_pages):
            target_page = all_pages[index]
            target_page.bring_to_front()
            print(f"Successfully switched to window/tab at index {index}.")
            return target_page
        else:
            raise Exception(f"Window index {index} is out of bounds. Only {len(all_pages)} windows exist.")
    except Exception as e:
        print(f"An error occurred during window switch: {e}")
        # Return the original page to prevent crashing the script
        return page
    
def wait_for_page_ready(page, selector, timeout=60):
    import time
    start = time.time()
    while time.time() - start < timeout:
        el = find_element_across_frames(page, selector)
        if el:
            return el
        sleep(1)
    raise Exception(f"Timeout waiting for selector: {selector}")

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