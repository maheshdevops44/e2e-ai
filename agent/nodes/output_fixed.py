from .agent_utils import find_element_across_frames, robust_fill
from time import sleep
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import sys
import os
import pytest
from playwright.sync_api import Page, expect
import time

from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
# The .env file is in the root config directory
dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path)

# Get environment variables
LAN_ID = os.getenv("LAN_ID")
LAN_PASSWORD = os.getenv("LAN_PASSWORD")

def retry_find_and_click_element(page, selector, max_attempts=90, delay=2, element_name="element"):
    """
    Retry mechanism to find and click an element until it appears.
    
    Args:
        page: Playwright page object
        selector: CSS selector or XPath to find the element
        max_attempts: Maximum number of attempts (default: 90 for 3 minutes)
        delay: Delay between attempts in seconds (default: 2)
        element_name: Name of the element for logging purposes
    
    Returns:
        True if element was found and clicked, False otherwise
    """
    print(f"[RETRY] Starting retry mechanism for {element_name} (will try for 3 minutes)")
    print(f"[RETRY] Using selector: {selector}")
    
    for attempt in range(1, max_attempts + 1):
        print(f"[RETRY] Attempt {attempt}/{max_attempts} - Looking for {element_name}")
        
        try:
            element = find_element_across_frames(page, selector)
            if element:
                print(f"[RETRY] Success! Found {element_name} on attempt {attempt}")
                print(f"[RETRY] Element text: '{element.text_content()}'")
                print(f"[RETRY] Element tag: {element.tag_name}")
                print(f"[RETRY] Element visible: {element.is_visible()}")
                sleep(60)
                element.click()
                print(f"[RETRY] Clicked on {element_name}")
                return True
            else:
                print(f"[RETRY] {element_name} not found on attempt {attempt}")
        except Exception as e:
            print(f"[RETRY] Error on attempt {attempt}: {str(e)}")
        
        if attempt < max_attempts:
            print(f"[RETRY] Waiting {delay} seconds before next attempt...")
            sleep(delay)
    
    print(f"[RETRY] Failed to find {element_name} after {max_attempts} attempts (3 minutes)")
    return False

@pytest.fixture
def browser():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        yield browser
        browser.close()

@pytest.fixture
def page_with_video(browser):
    video_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'videos'))
    os.makedirs(video_dir, exist_ok=True)
    print("****************************",video_dir)
    context = browser.new_context(record_video_dir=video_dir)
    page = context.new_page()
    yield page
    page.close()
    context.close()  

import time

def sleep(seconds):
    time.sleep(seconds)

def screenshot(page, name):
    page.screenshot(path=f"{name}.png")

def handle_popups(page):
    try:
        modal_close_btn = page.locator('button[aria-label="Close"], .modal-close, .dialog-close').first
        if modal_close_btn and modal_close_btn.is_visible():
            modal_close_btn.click(timeout=3000)
            print("Closed modal dialog")
            sleep(1)
    except:
        pass
    
def test_step_intake(page_with_video):
    initial_url = "https://spcia-qa.express-scripts.com/spcia"
    COMMON_INTAKE_ID = "CMNINTAKE07292025113222766962186"
    PATIENT_ID = "17045279"
    
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD
    
    print("**************",PASSWORD)

    print("++++++++++++++++++++++++",USERNAME)
    print("+++++++++++++++++++++++++",PASSWORD)

    page = page_with_video
    page.goto(initial_url)
    sleep(5)

    # Step 1: Login
    username_elem = find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username_elem:
        raise Exception("Username input not found")
    username_elem.fill(USERNAME)
    print("[LOG] Filled username with QASEE1")
    screenshot(page, "step_1_filled_username")
    sleep(2)

    password_elem = find_element_across_frames(page, 'input[name="Password"]')
    if not password_elem:
        raise Exception("Password input not found")
    password_elem.fill(PASSWORD)
    print("[LOG] Filled password with ******")
    screenshot(page, "step_1_filled_password")
    sleep(2)

    login_btn = find_element_across_frames(page, 'button#sub')
    if not login_btn:
        raise Exception("Login button not found")
    login_btn.click()
    print("[LOG] Clicked on Login button")
    screenshot(page, "step_1_clicked_login")
    sleep(8)
    
    # launch_link = find_element_across_frames(page, 'a[title="Launch portal"]')
    # if not launch_link:
    #     launch_link = find_element_across_frames(page, 'a[data-test-id="20140927131516034349915"]')
    # if not launch_link:
    #         launch_link = find_element_across_frames(page, 'a[name="pzStudioHeader_pyDisplayHarness_7"]')
    # launch_link.click()
    # page.keyboard.press("Enter")
    # sleep(30)

    # Step 2: Search for Intake ID in top-right search box
    search_box = find_element_across_frames(page, '(//input[@id="24dbd519"])[1]')
    if not search_box:
        raise Exception("Top-right search box for Intake ID not found")
    search_box.fill(COMMON_INTAKE_ID)
    print(f"[LOG] Entered Common Intake ID: {COMMON_INTAKE_ID}")
    screenshot(page, "step_2_filled_common_intake_id")
    sleep(10)
    search_box.press("Enter")
    print("[LOG] Pressed Enter in intake search box")
    screenshot(page, "step_2_pressed_enter_searchbox")
    sleep(20)

    # Step 3: Click first T-ID link in search result table
    t_id_link = find_element_across_frames(page, '(//*[@id="bodyTbl_right"]/tbody/tr[2]/td[3]/div/span)')
    if not t_id_link:
        raise Exception("First T-ID link in search result table not found")
    t_id_text = t_id_link.inner_text() if hasattr(t_id_link, "inner_text") else "T-ID"
    t_id_link.click()
    print(f"[LOG] Clicked T-ID link: {t_id_text}")
    screenshot(page, "step_3_clicked_tid_link")
    sleep(10)

    # Step 4: Click 'Update Task (Intake)'
    update_task_elem = find_element_across_frames(page, '//a[contains(text(),"Update Task (Intake)")]')
    if not update_task_elem:
        update_task_elem = find_element_across_frames(page, '//span[contains(text(),"Update Task (Intake)")]')
    if not update_task_elem:
        raise Exception("Update Task (Intake) link not found")
    update_task_elem.click()
    print("[LOG] Clicked Update Task (Intake)")
    screenshot(page, "step_4_clicked_update_task_intake")
    sleep(5)
    handle_popups(page)
    sleep(5)

    # Step 5: Close EIS Image Window (close modal)
    handle_popups(page)
    print("[LOG] Closed EIS Image Window if present")
    screenshot(page, "step_5_closed_eis_image_window")
    sleep(5)

    # Step 6: Drug Lookup (Click Search icon in Drug tab, Drug tab is default)
    drug_search_icon = find_element_across_frames(page, '//img[contains(@data-click,"DrugLookup")]')
    if not drug_search_icon:
        raise Exception("Drug Lookup search icon not found")
    drug_search_icon.click()
    print("[LOG] Clicked Drug Lookup search icon")
    screenshot(page, "step_6_clicked_drug_lookup_search_icon")
    sleep(5)

    # Step 7: Drug Lookup popup - clear button
    clear_btn = find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_17"]')
    if not clear_btn:
        raise Exception("Drug Lookup popup - clear button not found")
    clear_btn.click()
    print("[LOG] Clicked clear in Drug Lookup popup")
    screenshot(page, "step_7_clicked_clear_drug_lookup")
    sleep(2)

    # Drug Lookup popup - enter Drug Name and Search
    drug_name_input = find_element_across_frames(page, "input[name='$PpyTempPage$pDrugName']")
    if not drug_name_input:
        raise Exception("Drug name input not found in Drug Lookup popup")
    drug_name_input.fill("00074055402")
    print("[LOG] Filled Drug Name: 00074055402")
    screenshot(page, "step_7_filled_drug_name")
    sleep(2)

    search_btn = find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18"]')
    if not search_btn:
        raise Exception("Drug Lookup popup - search button not found")
    search_btn.click()
    print("[LOG] Clicked Search in Drug Lookup popup")
    screenshot(page, "step_7_clicked_search_drug_lookup")
    sleep(5)

    # Select first radio option (humira radio)
    humira_radio = find_element_across_frames(page, '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]')
    if not humira_radio:
        raise Exception("Drug selection radio button not found")
    humira_radio.click()
    print("[LOG] Selected first radio for searched drug")
    screenshot(page, "step_7_selected_drug_radio")
    sleep(2)

    # Drug submit button
    drug_submit_btn = find_element_across_frames(page, "//*[@name='DrugLookUpModalTabUI_pyWorkPage.Document.DrugList(1)_96']")
    if not drug_submit_btn:
        drug_submit_btn = find_element_across_frames(page, "//button[text()='Submit']")
    if not drug_submit_btn:
        raise Exception("Drug submit button not found")
    drug_submit_btn.click()
    print("[LOG] Clicked Submit in Drug Lookup popup")
    screenshot(page, "step_7_clicked_submit_drug_lookup")
    sleep(5)

    # Step 8: Open Task Again (Update Task (Intake) with status "Pending Progress")
    update_task_link = find_element_across_frames(page, '//a[contains(text(),"Update Task (Intake)")]')
    if not update_task_link:
        update_task_link = find_element_across_frames(page, '//span[contains(text(),"Update Task (Intake)")]')
    if not update_task_link:
        raise Exception("Update Task (Intake) link not found for open task again")
    update_task_link.click()
    print("[LOG] Clicked Update Task (Intake) again for Pending Progress")
    screenshot(page, "step_8_clicked_update_task_again")
    sleep(5)
    handle_popups(page)
    sleep(5)

    # Step 9: Fill Therapy Type and Place of Service in Drug tab
    therapy_type_input = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pTherapyType']")
    if not therapy_type_input:
        raise Exception("Therapy Type input not found")
    therapy_type_input.fill("HUMA")
    print("[LOG] Filled Therapy Type with HUMA")
    screenshot(page, "step_9_filled_therapy_type")
    sleep(2)

    place_of_service_dropdown = find_element_across_frames(page, "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
    if not place_of_service_dropdown:
        place_of_service_dropdown = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
    if not place_of_service_dropdown:
        raise Exception("Place of Service dropdown not found")
    try:
        place_of_service_dropdown.select_option(label="Home")
        print("[LOG] Selected Place of Service: Home")
    except Exception:
        place_of_service_dropdown.fill("Home")
        print("[LOG] Filled Place of Service: Home (fallback input)")
    screenshot(page, "step_9_selected_place_of_service")
    sleep(2)

    # Step 10: Link Patient Record
    patient_tab_elem = find_element_across_frames(page, "(//h3[text()='Patient Details'])[1]")
    if patient_tab_elem:
        patient_tab_elem.click()
        print("[LOG] Clicked Patient Details tab")
        screenshot(page, "step_10_clicked_patient_tab")
        sleep(1)
        # If patient_tab_elem is still visible/clickable, click again else pass
        patient_tab_elem2 = find_element_across_frames(page, "(//h3[text()='Patient Details'])[1]")
        if patient_tab_elem2:
            try:
                patient_tab_elem2.click()
                print("[LOG] Clicked Patient Details tab again")
            except Exception:
                pass
    else:
        print("[LOG] Patient Details tab not found, continuing.")
    sleep(1)

    patient_search_icon = find_element_across_frames(page, 'img[data-template=""][data-click*="PatientLookUp"]')
    if not patient_search_icon:
        raise Exception("Patient search icon not found")
    patient_search_icon.click()
    print("[LOG] Clicked Patient search icon")
    screenshot(page, "step_10_clicked_patient_search_icon")
    sleep(2)

    patient_clear_btn = find_element_across_frames(page, "//button[@name='PatientLookUp_pyWorkPage.Document.Patient_26']")
    if not patient_clear_btn:
        raise Exception("Patient search clear button not found")
    patient_clear_btn.click()
    print("[LOG] Clicked clear in Patient search")
    screenshot(page, "step_10_clicked_patient_clear")
    sleep(2)

    patient_id_input = find_element_across_frames(page, "input[name='$PpyTempPage$pPatientID']")
    if not patient_id_input:
        raise Exception("Patient ID input not found in Patient search")
    patient_id_input.fill(PATIENT_ID)
    print(f"[LOG] Filled Patient ID: {PATIENT_ID}")
    screenshot(page, "step_10_filled_patient_id")
    sleep(2)

    patient_search_btn = find_element_across_frames(page, "//button[contains(text(),'Search')]")
    if not patient_search_btn:
        raise Exception("Patient search button not found")
    patient_search_btn.click()
    print("[LOG] Clicked Search in Patient search popup")
    screenshot(page, "step_10_clicked_patient_search")
    sleep(5)

    patient_radio = find_element_across_frames(page, "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[./td[4]//span[text()='555']]/td[2]//input[@type='radio']")
    if not patient_radio:
        patient_radio = find_element_across_frames(page, "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')]/td[4]/div/span[text()='555']/ancestor::tr/td[2]//input[@type='radio']")
    if not patient_radio:
        raise Exception("Patient record radio with SB=555 not found")
    patient_radio.click()
    print("[LOG] Selected patient record with SB=555")
    screenshot(page, "step_10_selected_patient_record")
    sleep(2)

    submit_patient_btn = find_element_across_frames(page, "//button[@id='ModalButtonSubmit']")
    if not submit_patient_btn:
        raise Exception("Submit button not found in patient search popup")
    submit_patient_btn.click()
    print("[LOG] Clicked Submit in Patient search popup")
    screenshot(page, "step_10_clicked_submit_patient")
    sleep(5)

    # From Address List, select any address (first index)
    address_dropdown = find_element_across_frames(page, "#ded594e9")
    if not address_dropdown:
        raise Exception("Address dropdown not found")
    try:
        address_dropdown.select_option(index=1)
        print("[LOG] Selected address from Address List (index 1)")
    except Exception:
        print("[LOG] Could not select from address dropdown, trying fallback click.")
        address_dropdown.click()
    screenshot(page, "step_10_selected_address")
    sleep(2)

    # Step 11: Complete Prescriber/Category Team tab
    prescriber_tab_elem = find_element_across_frames(page, "(//h3[text()='Prescriber / Category / Team'])[1]")
    if prescriber_tab_elem:
        prescriber_tab_elem.click()
        print("[LOG] Clicked Prescriber / Category / Team tab")
        screenshot(page, "step_11_clicked_prescriber_category_team_tab")
        sleep(2)
    team_dropdown = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pTeamName']")
    if not team_dropdown:
        raise Exception("Team dropdown not found")
    if hasattr(team_dropdown, "input_value") and team_dropdown.input_value().strip() == "":
        # Try select first non-blank option
        options = team_dropdown.locator("option:not([value=''])")
        if options.count() > 0:
            first_option_value = options.first.get_attribute("value")
            team_dropdown.select_option(first_option_value)
            print(f"[LOG] Selected team: {first_option_value}")
        else:
            print("No non-blank team options found.")
        sleep(1)
    else:
        try:
            team_dropdown.fill("TEAM 1")
            print("[LOG] Filled TEAM 1 in Team dropdown")
        except Exception:
            print("[LOG] Could not fill TEAM 1 in Team dropdown")
    screenshot(page, "step_11_filled_team")
    sleep(2)

    # Step 12: Click Submit
    task_submit_btn = find_element_across_frames(page, "button[name='CommonFlowActionButtons_pyWorkPage_17']")
    if not task_submit_btn:
        raise Exception("Task Submit button not found")
    task_submit_btn.click()
    print("[LOG] Clicked Submit to complete Intake T-Task id")
    screenshot(page, "step_12_clicked_submit")
    sleep(5)

    print("[LOG] Automation completed for Intake test scenario.")

from .agent_utils import find_element_across_frames
from time import sleep
from datetime import datetime, timedelta

def test_step_clearance(page_with_video):
    
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD
    
    initial_url = "https://clearance-qa.express-scripts.com/spclr"
    page = page_with_video
    page.goto(initial_url)
    sleep(2)

    # Step 1: Login
    username = find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username:
        raise Exception("Username input not found")
    username.fill(USERNAME)
    sleep(1)

    password = find_element_across_frames(page, 'input[name="Password"]')
    if not password:
        raise Exception("Password input not found")
    password.fill(PASSWORD)
    sleep(1)

    login_btn = find_element_across_frames(page, 'button#sub')
    if not login_btn:
        raise Exception("Login button not found")
    login_btn.click()
    sleep(4)

    # Step 2: Search for the Patient Case
    search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
    if not search_cases:
        raise Exception("Search Cases link not found")
    search_cases.click()
    sleep(3)


    patient_id_input = find_element_across_frames(page, 'input[name="$PpyDisplayHarness$pCaseSearchCriteria$pPatient$pPatientIDNumeric"]')
    if not patient_id_input:
        raise Exception("Patient ID input not found")
    patient_id_input.fill("17045279")
    sleep(1)
    
    max_attempts = 5  # Increased since we're waiting longer between attempts
    attempt = 0
    
    while attempt < max_attempts:
        # Click search button
        search_btn = find_element_across_frames(page, 'button[name="SearchCases_pyDisplayHarness.CaseSearchCriteria_14"]')
        if not search_btn:
            raise Exception("Search button not found")
        search_btn.click()
        
        # Wait 30 seconds for results to load
        sleep(30)
        
        # Try to find IE task link
        ie_task_link = find_element_across_frames(page, '//table[@pl_prop=\'D_GetWorkCases.pxResults\']/tbody/tr[2]/td[1]//a')
        if ie_task_link:
            ie_task_link.click()
            sleep(13)
            break
        
        attempt += 1
        print(f"Search attempt {attempt}: IE task link not found, will retry in 30 seconds...")
        # No additional sleep needed since we already waited 30 seconds above
    
    if attempt >= max_attempts:
        raise Exception("IE Task ID link not found after maximum attempts")

    # Step 4: Enter Place of Service ID
    pos_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pPlaceOfService"]')
    if not pos_input:
        raise Exception("Place of Service input not found")
    pos_input.fill("12")
    sleep(1)

    # Step 5: Enter Payer 1 - Payer Information
    bin_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pBankIDNumber"]')
    if not bin_input:
        raise Exception("BIN input not found")
    bin_input.fill("610144")
    sleep(2)

    pcn_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pPCN"]')
    if not pcn_input:
        raise Exception("PCN input not found")
    pcn_input.click()
    pcn_input.fill("D0TEST")
    sleep(2)

    group_number_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pGroupNumber"]')
    if not group_number_input:
        raise Exception("Group Number input not found")
    group_number_input.click()
    group_number_input.fill("RTA")
    sleep(2)

    save_payee_btn = find_element_across_frames(page, 'button[data-test-id="PayerInfoScreen-Button-Search"]')
    if not save_payee_btn:
        raise Exception("Save Payee button not found")
    save_payee_btn.click()
    sleep(3)

    # Step 6: Enter Policy Information
    cardholder_input = find_element_across_frames(page, '//span/input[@id="6a329411"]')
    if not cardholder_input:
        raise Exception("Cardholder ID input not found")
    cardholder_input.fill("555123123")
    sleep(1)

    person_code_input = find_element_across_frames(page, '//div/input[@id="a451c2d0"]')
    if not person_code_input:
        raise Exception("Person Code input not found")
    person_code_input.fill("001")
    sleep(2)

    effective_date_input = find_element_across_frames(page, '//span/input[@class="inactvDtTmTxt"]')
    if not effective_date_input:
        raise Exception("Insurance Effective Date input not found")
    today = datetime.now().strftime("%m/%d/%Y")
    effective_date_input.fill(today)
    sleep(1)

    end_date_input = find_element_across_frames(page, 'input[data-test-id="20171109141147048668261"]')
    if not end_date_input:
        raise Exception("End Date input not found")
    end_date = (datetime.now() + timedelta(days=2)).strftime("%m/%d/%Y")
    end_date_input.fill(end_date)
    sleep(1)

    relationship_dropdown = find_element_across_frames(page, '//div/select[@data-test-id="20171115143211077239541"]')
    if not relationship_dropdown:
        raise Exception("Relationship dropdown not found")
    relationship_dropdown.select_option(label="1 - Self")
    sleep(1)

    save_policy_btn = find_element_across_frames(page, 'button[data-test-id="20200305121820016323290"]')
    if not save_policy_btn:
        raise Exception("Save Policy button not found")
    save_policy_btn.click()
    sleep(10)

    # Step 7: Confirm Insurance Banner - Click Next
    next_btn = find_element_across_frames(page, 'button[name="CommonFlowActionButtons_pyWorkPage_31"]')
    if not next_btn:
        raise Exception("Next button not found")
    next_btn.click()
    sleep(10)

    # Step 8: CoPay and Billing Split Setup
    drug_checkbox = find_element_across_frames(page, '//span[@class="checkbox"]//input[@type="checkbox"]')
    if not drug_checkbox:
        raise Exception("Drug field checkbox not found")
    if not drug_checkbox.is_checked():
        drug_checkbox.check()
    sleep(3)

    primary_payer_input = find_element_across_frames(page, 'input[data-test-id="202006170412060535921"]')
    if not primary_payer_input:
        raise Exception("Primary Payer Service input not found")
    primary_payer_input.clear()
    primary_payer_input.fill("71504")
    sleep(3)
    page.keyboard.press("ArrowDown")
    sleep(2)
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    sleep(5)

    # Step 9: Co-Pay Split Setup
    copay_input = find_element_across_frames(page, 'select[data-test-id="20200313110855039235493"]')
    if not copay_input:
        copay_input = find_element_across_frames(page, 'select[name="$PpyWorkPage$pBillingSplitServices$l1$pCoPay$l1$pAssignCoPayTo"]')
        if not copay_input:
            raise Exception("CoPay input not found")
    copay_input.select_option(value="P")
    sleep(3)

    # Step 10: Complete the Clearance Task
    finish_btn = find_element_across_frames(page, '//span/button[text()="Finish"]')
    if not finish_btn:
        raise Exception("Finish button not found")
    finish_btn.click()
    sleep(15)

    # Step 11: Repeat steps for NR Case
    # Go back to Search Cases
    search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
    if not search_cases:
        raise Exception("Search Cases link not found (NR repeat)")
    search_cases.click()
    sleep(3)

    patient_id_input = find_element_across_frames(page, 'input[name="$PpyDisplayHarness$pCaseSearchCriteria$pPatient$pPatientIDNumeric"]')
    if not patient_id_input:
        raise Exception("Patient ID input not found (NR repeat)")
    patient_id_input.fill("16859438")
    sleep(1)

    search_btn = find_element_across_frames(page, 'button[name="SearchCases_pyDisplayHarness.CaseSearchCriteria_14"]')
    if not search_btn:
        raise Exception("Search button not found (NR repeat)")
    search_btn.click()
    sleep(4)

    # Find NR- case row (assuming it's now at row 2) with retry mechanism
    nr_selector = '//table[@pl_prop=\'D_GetWorkCases.pxResults\']/tbody/tr[2]/td[1]//a'
    if not retry_find_and_click_element(page, nr_selector, max_attempts=90, delay=2, element_name="NR Task ID link"):
        raise Exception("NR Task ID link not found after retry attempts")
    sleep(18)

    # Repeat Steps 4-10 for NR case

    pos_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pPlaceOfService"]')
    if not pos_input:
        raise Exception("Place of Service input not found (NR)")
    pos_input.fill("12")
    sleep(1)

    bin_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pBankIDNumber"]')
    if not bin_input:
        raise Exception("BIN input not found (NR)")
    bin_input.fill("610144")
    sleep(2)

    pcn_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pPCN"]')
    if not pcn_input:
        raise Exception("PCN input not found (NR)")
    pcn_input.click()
    pcn_input.fill("D0TEST")
    sleep(2)

    group_number_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pGroupNumber"]')
    if not group_number_input:
        raise Exception("Group Number input not found (NR)")
    group_number_input.click()
    group_number_input.fill("RTA")
    sleep(2)

    save_payee_btn = find_element_across_frames(page, 'button[data-test-id="PayerInfoScreen-Button-Search"]')
    if not save_payee_btn:
        raise Exception("Save Payee button not found (NR)")
    save_payee_btn.click()
    sleep(3)

    cardholder_input = find_element_across_frames(page, '//span/input[@id="6a329411"]')
    if not cardholder_input:
        raise Exception("Cardholder ID input not found (NR)")
    cardholder_input.fill("555123123")
    sleep(1)

    person_code_input = find_element_across_frames(page, '//div/input[@id="a451c2d0"]')
    if not person_code_input:
        raise Exception("Person Code input not found (NR)")
    person_code_input.fill("001")
    sleep(2)

    effective_date_input = find_element_across_frames(page, '//span/input[@class="inactvDtTmTxt"]')
    if not effective_date_input:
        raise Exception("Insurance Effective Date input not found (NR)")
    today = datetime.now().strftime("%m/%d/%Y")
    effective_date_input.fill(today)
    sleep(1)

    end_date_input = find_element_across_frames(page, 'input[data-test-id="20171109141147048668261"]')
    if not end_date_input:
        raise Exception("End Date input not found (NR)")
    end_date = (datetime.now() + timedelta(days=2)).strftime("%m/%d/%Y")
    end_date_input.fill(end_date)
    sleep(1)

    relationship_dropdown = find_element_across_frames(page, '//div/select[@data-test-id="20171115143211077239541"]')
    if not relationship_dropdown:
        raise Exception("Relationship dropdown not found (NR)")
    relationship_dropdown.select_option(label="1 - Self")
    sleep(1)

    save_policy_btn = find_element_across_frames(page, 'button[data-test-id="20200305121820016323290"]')
    if not save_policy_btn:
        raise Exception("Save Policy button not found (NR)")
    save_policy_btn.click()
    sleep(10)

    next_btn = find_element_across_frames(page, 'button[name="CommonFlowActionButtons_pyWorkPage_31"]')
    if not next_btn:
        raise Exception("Next button not found (NR)")
    next_btn.click()
    sleep(10)

    drug_checkbox = find_element_across_frames(page, '//span[@class="checkbox"]//input[@type="checkbox"]')
    if not drug_checkbox:
        raise Exception("Drug field checkbox not found (NR)")
    if not drug_checkbox.is_checked():
        drug_checkbox.check()
    sleep(3)

    primary_payer_input = find_element_across_frames(page, 'input[data-test-id="202006170412060535921"]')
    if not primary_payer_input:
        raise Exception("Primary Payer Service input not found (NR)")
    primary_payer_input.clear()
    primary_payer_input.fill("71504")
    sleep(3)
    page.keyboard.press("ArrowDown")
    sleep(2)
    page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")
    sleep(5)

    copay_input = find_element_across_frames(page, 'select[data-test-id="20200313110855039235493"]')
    if not copay_input:
        copay_input = find_element_across_frames(page, 'select[name="$PpyWorkPage$pBillingSplitServices$l1$pCoPay$l1$pAssignCoPayTo"]')
        if not copay_input:
            raise Exception("CoPay input not found (NR)")
    copay_input.select_option(value="P")
    sleep(3)

    finish_btn = find_element_across_frames(page, '//span/button[text()="Finish"]')
    if not finish_btn:
        raise Exception("Finish button not found (NR)")
    finish_btn.click()
    sleep(15)
    
from .agent_utils import find_element_across_frames, robust_fill, robust_click, robust_select_option, switch_to_window_by_index
from time import sleep
from playwright.sync_api import Page, expect

def validate_section_and_check(page: Page, fields_to_check: list, checkbox_selector: str, optional_fields: list = []):
    """
    A reusable function to validate a list of fields in a section.
    
    It checks if each field is populated. If all required fields are valid,
    it clicks the provided checkbox.

    Args:
        page: The Playwright page object.
        fields_to_check: A list of tuples, where each tuple is (FieldName, FieldSelector).
        checkbox_selector: The selector for the section's confirmation checkbox.
        optional_fields: A list of field names that are allowed to be empty.
    """
    is_section_fully_populated = True
    print(f"\n--- Validating Section ---")

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
        robust_click(page, checkbox)
        print("[LOG] SUCCESS: All required fields were populated. Section checkbox has been ticked.")
    else:
        print("[LOG] SKIPPING CHECKBOX: One or more required fields were not populated. Flagging for review.")

# def test_step_rxp(page_with_video):
    
        
#     USERNAME = LAN_ID
#     PASSWORD = LAN_PASSWORD
    
#     page = page_with_video
    
#     page.goto("https://sprxp-qa.express-scripts.com/sprxp/")

#     # Step 1: Navigate to the RxP login page
    
#     print("[LOG] Navigated to RxP login page: https://sprxp-qa.express-scripts.com/sprxp/")
#     page.wait_for_load_state("networkidle")
#     page.screenshot(path="step_1_navigate_to_login.png")

#     # Step 1.1: Enter username
#     username_input = find_element_across_frames(page, 'input#txtUserID')
#     if not username_input:
#         raise Exception("Element 'Username Input' not found with selector: 'input#txtUserID'")
#     robust_fill(page, username_input, USERNAME)
#     print("[LOG] Filled username with 'C9G5JS'")
#     page.screenshot(path="step_2_fill_username.png")

#     # Step 1.2: Enter password
#     password_input = find_element_across_frames(page, 'input#txtPassword')
#     if not password_input:
#         raise Exception("Element 'Password Input' not found with selector: 'input#txtPassword'")
#     robust_fill(page, password_input, PASSWORD)
#     print("[LOG] Filled password")
#     page.screenshot(path="step_3_fill_password.png")

#     # Step 1.3: Click Login button
#     login_button = find_element_across_frames(page, 'button#sub')
#     if not login_button:
#         raise Exception("Element 'Login Button' not found with selector: 'button#sub'")
#     robust_click(page, login_button)
#     print("[LOG] Clicked login button")
#     page.wait_for_load_state("networkidle", timeout=60000)
#     page.screenshot(path="step_4_click_login.png")

    
    
# from .agent_utils import find_element_across_frames
# from time import sleep
# ##from playwright_zoom import setBrowserZoom

# def test_step_crm(page_with_video):
#     initial_url = "https://spcrmqa-internal.express-scripts.com/spcrm88/"
            
#     USERNAME = LAN_ID
#     PASSWORD = LAN_PASSWORD
#     # Step 1: Launch and Login to CRM
    
#     page = page_with_video
#     page.goto(initial_url)
#     print("[LOG] Navigated to URL: " + initial_url)
#     page.screenshot(path="step_1_navigate_to_url.png")
#     sleep(5)
# ##    page.evaluate("document.body.style.zoom='80%'")
#     # if client:
#     #     # Set the page zoom level (0.8 = 80%)
#     #     # This uses the CDP command 'Emulation.setPageScaleFactor'
#     #     client.send("Emulation.setPageScaleFactor", {"pageScaleFactor": 0.8})
#  ##   setBrowserZoom(page, 80)

#     username = find_element_across_frames(page, "#txtUserID")
#     if not username:
#         raise Exception("Username input not found")
#     username.fill(USERNAME)
#     print("[LOG] Filled 'Username' with 'C9G5JS'")
#     page.screenshot(path="step_2_fill_username.png")
#     sleep(1)

#     password = find_element_across_frames(page, "#txtPassword")
#     if not password:
#         raise Exception("Password input not found")
#     password.fill(PASSWORD)
#     print("[LOG] Filled 'Password'")
#     page.screenshot(path="step_3_fill_password.png")
#     sleep(1)

#     login_btn = find_element_across_frames(page, "#sub")
#     if not login_btn:
#         raise Exception("Login button not found")
#     login_btn.click()
#     print("[LOG] Clicked 'Login' button")
#     page.screenshot(path="step_4_clicked_login.png")
#     sleep(3)

#     # Step 2: Access Patient Verification & Caller Info

# ##    page.evaluate("document.body.style.zoom='80%'")
#     new_btn = find_element_across_frames(page, '//a[normalize-space(.)="New"]')
    
#     if not new_btn:
#         raise Exception("New button not found")
#     new_btn.click()
#     print("[LOG] Clicked 'New' button")
#     page.screenshot(path="step_5_clicked_new.png")
#     sleep(2)

    
#     sim_ws_btn = find_element_across_frames(page, "//*[text()='Simulate Workspace Interaction']")
#     if not sim_ws_btn:
#         raise Exception("Simulate Workspace Interaction button not found")
#     sim_ws_btn.click()
#     print("[LOG] Clicked 'Simulate Workspace Interaction'")
#     page.screenshot(path="step_6_clicked_simulate_workspace.png")
#     sleep(2)

#     patient_id_field = find_element_across_frames(page, 'input[id="a3f8064b"]')
#     if not patient_id_field:
#         raise Exception("Patient ID field not found")
#     # Try to clear pre-populated fields if any
#     try:
#         patient_id_field.fill("")
#         sleep(1)
#     except Exception:
#         pass
#     patient_id_field.fill("17045280")
#     print("[LOG] Filled 'Patient ID' with '17045280'")
#     page.screenshot(path="step_7_fill_patient_id.png")
#     sleep(1)
#     ##17057856

#     call_intent_field = find_element_across_frames(page, 'input[id="5e9cabab"]')
#     if not call_intent_field:
#         raise Exception("Call_intent_field field not found")
#     # Try to clear pre-populated fields if any
#     try:
#         call_intent_field.fill("")
#         sleep(1)
#     except Exception:
#         pass
  
#     prsecrition_no_field = find_element_across_frames(page, 'input[id="418aff81"]')
#     if not prsecrition_no_field:
#         raise Exception("Prsecrition_no_field field not found")
#     # Try to clear pre-populated fields if any
#     try:
#         prsecrition_no_field.fill("")
#         sleep(1)
#     except Exception:
#         pass

#     fill_no_field = find_element_across_frames(page, 'input[id="ac6e34af"]')
#     if not fill_no_field:
#         raise Exception("Fill_no_field field not found")
#     # Try to clear pre-populated fields if any
#     try:
#         fill_no_field.fill("")
#         sleep(1)
#     except Exception:
#         pass

#     service_branch_field = find_element_across_frames(page, 'input[id="28d60f5c"]')
#     if not service_branch_field:
#         raise Exception("Service_branch_field field not found")
#     # Try to clear pre-populated fields if any
#     try:
#         service_branch_field.fill("")
#         sleep(2)
#     except Exception:
#         pass

#     # Click Next button
#     next_btn = find_element_across_frames(page, "[data-test-id='20201223000248034111750']")
#     if not next_btn:
#         raise Exception("Next button on Simulate Workspace not found")
#     next_btn.click()
#     print("[LOG] Clicked 'Next' button on Simulate Workspace")
#     page.screenshot(path="step_8_clicked_next_on_simulate_workspace.png")
#     sleep(8)

#     # Step 3: Verification & Medication Details
#     # Select first three checkboxes under Verification Methods
#     verification_checkbox_1 = find_element_across_frames(page, "(//input[@type='checkbox'])[1]")
#     verification_checkbox_2 = find_element_across_frames(page, "(//input[@type='checkbox'])[2]")
#     verification_checkbox_3 = find_element_across_frames(page, "(//input[@type='checkbox'])[3]")
#     if not verification_checkbox_1 or not verification_checkbox_2 or not verification_checkbox_3:
#         raise Exception("Verification method checkboxes not found")
#     verification_checkbox_1.check()
#     print("[LOG] Checked first verification checkbox")
#     page.screenshot(path="step_9_checked_verification_checkbox_1.png")
#     sleep(0.5)
#     verification_checkbox_2.check()
#     print("[LOG] Checked second verification checkbox")
#     page.screenshot(path="step_10_checked_verification_checkbox_2.png")
#     sleep(0.5)
#     verification_checkbox_3.check()
#     print("[LOG] Checked third verification checkbox")
#     page.screenshot(path="step_11_checked_verification_checkbox_3.png")
#     sleep(0.5)

#     # Select 'Patient' from Relationship to Patient drop-down
#     rel_to_patient_dropdown = find_element_across_frames(page, "//*[text()='Relationship to Patient']/ancestor-or-self::*[contains(@class,'dataLabelFor')]/following-sibling::*//select")
#     if not rel_to_patient_dropdown:
#         raise Exception("Relationship to Patient dropdown not found")
#     rel_to_patient_dropdown.select_option(label="Patient")
#     print("[LOG] Selected 'Patient' from 'Relationship to Patient' dropdown")
#     page.screenshot(path="step_12_selected_relationship_to_patient.png")
#     sleep(1)


# ## Medication function:
#     found = False

#     # Locate the main table using the provided full XPath
#     table_xpath = "/html/body/div[2]/form/div[3]/div/section/div/div/div/div/div/div/div/div/div/div/div/div[2]/div/div/div/div/div/span/div/div[1]/div[2]/div/div/div/div[1]/div/div/div/div/div/span/div/div/div/table/tbody/tr/td/div/div/div[1]/table/tbody/tr/td[2]/div/table"
#     table_locator = find_element_across_frames(page,f"xpath={table_xpath}")

#     # Ensure the table is visible and loaded
#     # table_locator.wait_for()

#     # Find all rows within the table's tbody, explicitly using XPath
#     rows = table_locator.locator("xpath=./tbody/tr[contains(@class,'Row')]").all()

#     for row_locator in rows:
#         # Locate the 'Medication' span with data-test-id within the current row
#         medication_span = row_locator.locator("span[data-test-id='201710241151280460732434']")

#         # Check if the span exists and contains the text 'HUMIRA'
#         if medication_span.count() > 0 and medication_span.text_content().strip() == "HUMIRA":
#             # Locate the checkbox with id="pySelected1" within the same row
#             checkbox = row_locator.locator("input#pySelected1[type='checkbox']")

#             if checkbox.count() > 0:  # Check if the checkbox exists
#                 checkbox.check()  # Use .check() for checkboxes
#                 print(f"[LOG] Checkbox for 'HUMIRA' checked.")
#                 page.screenshot(path="step_13_checked_humira_checkbox.png")
#                 found = True
#                 break
#             else:
#                 raise Exception(f"Checkbox with id='pySelected1' for 'HUMIRA' not found in the row with Medication.")
    
#     if not found:
#         raise Exception("Patient record with 'HUMIRA' in 'Medication' column not found.")
#     sleep(1)


#     # page.pause()
#     # Choose No radio button for "Has the patient missed doses..."
#     risk_radio_no = find_element_across_frames(page, "(//*[text()='No'])[1]")
#     if not risk_radio_no:
#         raise Exception("No radio button for missed dose risk not found")
#     risk_radio_no.click()
#     print("[LOG] Clicked 'No' for missed dose risk")
#     page.screenshot(path="step_14_clicked_no_for_missed_dose.png")
#     sleep(1)

#     # Click Next
#     next_btn2 = find_element_across_frames(page, "[data-test-id='20201223000248034111750']")
#     if not next_btn2:
#         raise Exception("Next button after Verification & Medication not found")
#     next_btn2.click()
#     print("[LOG] Clicked 'Next' button after Verification & Medication")
#     page.screenshot(path="step_15_clicked_next_after_verification.png")
#     sleep(15)

#     # Step 4: Schedule Order Task
#     add_task_btn = find_element_across_frames(page, "//button[@data-test-id='2014111401004903823658']")
#     if not add_task_btn:
#         raise Exception("Add Task button not found")
#     add_task_btn.click()
#     print("[LOG] Clicked 'Add Task' button")
#     page.screenshot(path="step_16_clicked_add_task.png")
#     sleep(3)

#     schedule_order_option = find_element_across_frames(page, "//*[text()='Schedule Order' and @class='Add_task']")
#     if not schedule_order_option:
#         raise Exception("Schedule Order option not found")
#     schedule_order_option.click()
#     print("[LOG] Clicked 'Schedule Order' option")
#     page.screenshot(path="step_17_clicked_schedule_order_option.png")
#     sleep(3)

#     confirm_add_task_btn = find_element_across_frames(page, "(//*[text()='Add tasks'])[2]")
#     if not confirm_add_task_btn:
#         raise Exception("Add task(s) button not found")
#     confirm_add_task_btn.click()
#     print("[LOG] Clicked 'Add tasks' button to confirm")
#     page.screenshot(path="step_18_confirmed_add_tasks.png")
#     sleep(20)
#     ##sleep(60)

#     yes_radio = find_element_across_frames(page, "//label[contains(@class, 'radioLabel') and contains(@class, 'rb_standard') and contains(@class, 'rb_')]")
    
#     if not yes_radio:
#         raise Exception("Patient Medication not displayed")
#     yes_radio.click()
#     print("[LOG] Clicked 'Yes' radio button for Patient Medication")
#     page.screenshot(path="step_19_clicked_yes_for_patient_medication.png")
#     # print('patient_med done')
#     sleep(4)

    
#     # ##Patient Decline:
#     patient_declines_checkbox = find_element_across_frames(page, "//input[@data-test-id='202007080356410453224916']")
    
#     if not patient_declines_checkbox:
#         raise Exception("Patient decline check not displayed")
#     patient_declines_checkbox.click()
#     print("[LOG] Checked 'Patient declines' checkbox")
#     page.screenshot(path="step_20_checked_patient_declines.png")
#     # print('patient_decline done')
#     sleep(3)

#     # Click on Review
#     review_btn = find_element_across_frames(page, "//button[@data-test-id='2020121801252208389436']")
    
#     if not review_btn:
#         raise Exception("Review button not found.")
    
#     review_btn.click()
#     print("[LOG] Clicked 'Review' button")
#     page.screenshot(path="step_21_clicked_review.png")
#     # print('review done')
#     sleep(30)



#     # Click on Estimated review:
#     estimated_resp_text = find_element_across_frames(page, "//input[@data-test-id='202208101045470657482784']")
    
#     if not estimated_resp_text:
#         raise Exception("Estimated patient responsibility warning not found on Review Screen")
    
#     estimated_resp_text.click()
#     print("[LOG] Clicked estimated patient responsibility warning")
#     page.screenshot(path="step_22_clicked_estimated_responsibility.png")
#     # print('review done')
#     sleep(6)

#     # Click on Modify Supplies
#     modify_supplies_link = find_element_across_frames(page, "//a[@data-test-id='20201222234640063946826']")
    
#     if not modify_supplies_link:
#         raise Exception("'Modify Supplies' link not found")
    
#     modify_supplies_link.click()
#     print("[LOG] Clicked 'Modify Supplies' link")
#     page.screenshot(path="step_23_clicked_modify_supplies.png")
#     # print('review done')
#     sleep(3)


#     ##Pop up window:
#     ##//button[@data-test-id='20141008160437053510472' and text()='Submit']
#     submit_review_supplies = find_element_across_frames(page, "//button[@data-test-id='20141008160437053510472' and text()='Submit']")
    
#     if not submit_review_supplies:
#         raise Exception("Submit button in Review supplies pop up not found")
    
#     submit_review_supplies.click()
#     print("[LOG] Clicked 'Submit' in Review Supplies pop-up")
#     page.screenshot(path="step_24_submitted_review_supplies_popup.png")
#     # print('review done')
#     sleep(3)

#     # Click on Review2
#     review_btn2 = find_element_across_frames(page, "//button[@data-test-id='20201218012522083910607']")
    
#     if not review_btn2:
#         raise Exception("Second Review button not found after submitting supplies")
    
#     review_btn2.click()
#     print("[LOG] Clicked second 'Review' button")
#     page.screenshot(path="step_25_clicked_second_review.png")
#     # print('review done')
#     sleep(3)

#     # Click on Next steps
#     review_next_steps_btn = find_element_across_frames(page, "//button[@data-test-id='20201218012522083910607']")
    
#     if not review_next_steps_btn:
#         raise Exception("'Review' button under Next Steps not found")
    
#     review_next_steps_btn.click()
#     print("[LOG] Clicked 'Review' button under Next Steps")
#     page.screenshot(path="step_26_clicked_review_under_next_steps.png")
#     # print('review done')
#     sleep(3)

#     clinical_transfer_yes = find_element_across_frames(page, "//label[@for='f5130791Yes' and text()='Yes']")
    
#     if not clinical_transfer_yes:
#         raise Exception("'Yes' radio button for Clinical Transfer question not found")
#     clinical_transfer_yes.click()
#     print("[LOG] Clicked 'Yes' for Clinical Transfer question")
#     page.screenshot(path="step_27_clicked_yes_for_clinical_transfer.png")
#     # print('patient_med done')
#     sleep(3)



#     pharmacist_radio = find_element_across_frames(page, "//label[@for='d5e175ceTransferred- Accepted RPH Counseling' and contains(.,'Transferred- Accepted RPH Counseling')]")
    
#     if not pharmacist_radio:
#         raise Exception("Any radio button under Pharmacist Transfer Response not found")
#     pharmacist_radio.click()
#     print("[LOG] Clicked radio button under Pharmacist Transfer Response")
#     page.screenshot(path="step_28_clicked_pharmacist_transfer_response.png")
#     # print('patient_med done')
#     sleep(3)

#     # Click on Next steps
#     address_check_btn = find_element_across_frames(page, "//button[@data-test-id='2020122223395908963337']")
    
#     if not address_check_btn:
#         raise Exception("Address Check button not found")
    
#     address_check_btn.click()
#     print("[LOG] Clicked 'Address Check' button")
#     page.screenshot(path="step_29_clicked_address_check.png")
#     # print('review done')
#     sleep(3)


#     ##Verify address:
#     address_confirmed_btn = find_element_across_frames(page, "//button[@data-test-id='ESIButton' and text()='Address CONFIRMED']")
    
#     if not address_confirmed_btn:
#         raise Exception("'Address confirmed' on Verify Address Modal not found")
    
#     address_confirmed_btn.click()
#     print("[LOG] Clicked 'Address CONFIRMED' button")
#     page.screenshot(path="step_30_clicked_address_confirmed.png")
#     # print('review done')
#     sleep(3)

#     # Click on Submit
#     submit_btn = find_element_across_frames(page, "//button[@data-test-id='20201218012522083911187']")
    
#     if not submit_btn:
#         raise Exception("Submit button not found on Clinical Transfer page")
    
#     submit_btn.click()
#     print("[LOG] Clicked final 'Submit' button")
#     page.screenshot(path="step_31_clicked_final_submit.png")
#     # print('review done')


