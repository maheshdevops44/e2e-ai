 
 
import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import from nodes
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from nodes.agent_utils import find_element_across_frames, robust_fill
from time import sleep
from datetime import datetime,timedelta
from playwright.sync_api import sync_playwright
import sys
import os
import pytest
from playwright.sync_api import Page, expect


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
def page_with_video(browser):
    video_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", 'videos'))
    os.makedirs(video_dir, exist_ok=True)
    print("****************************",video_dir)
    context = browser.new_context(record_video_dir=video_dir)
    page = context.new_page()
    yield page
    page.close()
    context.close()

def screenshot(page, name):
    screenshot_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", 'screenshots'))
    os.makedirs(screenshot_dir, exist_ok=True)
    print(f"[SCREENSHOT] {name}.png")
    page.screenshot(path=os.path.join(screenshot_dir, f"{name}.png"))
    

from time import sleep

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
    print("[LOG] TESTING INITIATED FOR INTAKE APPLICATION")
    initial_url = "https://spcia-qa.express-scripts.com/spcia"
    COMMON_INTAKE_ID = "CMNINTAKE08212025105220254216083"
    PATIENT_ID = "17164202"
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD

    page = page_with_video
    page.goto(initial_url)
    sleep(5)

    # Step 1: Login
    username_elem = find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username_elem:
        print("[ERROR] Username input not found")
        raise Exception("Username input not found")
    username_elem.fill(USERNAME)
    print("[LOG] Filled username with LAN_ID")
    screenshot(page, "step_1_filled_username")
    sleep(2)

    password_elem = find_element_across_frames(page, 'input[name="Password"]')
    if not password_elem:
        print("[ERROR] Password input not found")   
        raise Exception("Password input not found")
    password_elem.fill(PASSWORD)
    print("[LOG] Filled password with PASSWORD")
    screenshot(page, "step_1_filled_password")
    sleep(2)

    login_btn = find_element_across_frames(page, 'button#sub')
    if not login_btn:
        print("[ERROR] Login button not found")   
        raise Exception("Login button not found")
    login_btn.click()
    print("[LOG] Clicked on Login button")
    screenshot(page, "step_1_clicked_login")
    sleep(8)

    # Step 2: Search Intake ID in top-right search box
    search_box = find_element_across_frames(page, '(//input[@id="24dbd519"])[1]')
    if not search_box:
        print("[ERROR] search box for Intake ID not found")
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
        print("[ERROR]  T-ID link in search result table not found")
        raise Exception("First T-ID link in search result table not found")
    t_id_link.click()
    print(f"[LOG] Clicked T-ID link")
    screenshot(page, "step_3_clicked_tid_link")
    sleep(10)

    # Step 4: Click 'Update Task (Intake)'
    update_task_elem = find_element_across_frames(page, '//a[contains(text(),"Update Task (Intake)")]')
    if not update_task_elem:
        update_task_elem = find_element_across_frames(page, '//span[contains(text(),"Update Task (Intake)")]')
    if not update_task_elem:
        print("[ERROR]  Update Task (Intake) link not found")
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

    # Step 6: Drug Lookup (Drug tab is default page)
    drug_search_icon = find_element_across_frames(page, '//img[contains(@data-click,"DrugLookup")]')
    if not drug_search_icon:
        print("[ERROR]  Drug Lookup search icon not found")
        raise Exception("Drug Lookup search icon not found")
    drug_search_icon.click()
    print("[LOG] Clicked Drug Lookup search icon")
    screenshot(page, "step_6_clicked_drug_lookup_search_icon")
    sleep(5)

    # Step 7: Drug Lookup popup - clear button
    clear_btn = find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_17"]')
    if not clear_btn:
        print("[ERROR]  Drug Lookup popup - clear button not found")
        raise Exception("Drug Lookup popup - clear button not found")
    clear_btn.click()
    print("[LOG] Clicked clear in Drug Lookup popup")
    screenshot(page, "step_7_clicked_clear_drug_lookup")
    sleep(2)

    # Drug Lookup popup - enter Drug Name and Search
    drug_name_input = find_element_across_frames(page, "input[name='$PpyTempPage$pDrugName']")
    if not drug_name_input:
        print("[ERROR]  Drug name input not found in Drug Lookup popup")
        raise Exception("Drug name input not found in Drug Lookup popup")
    drug_name_input.fill("00378696093")
    print("[LOG] Filled Drug Name: 00378696093")
    screenshot(page, "step_7_filled_drug_name")
    sleep(2)

    search_btn = find_element_across_frames(page, '//button[@name="TherapyAndDrugLookup_pyWorkPage.Document.DrugList(1)_18"]')
    if not search_btn:
        print("[ERROR]  Drug Lookup popup - search button not found")
        raise Exception("Drug Lookup popup - search button not found")
    search_btn.click()
    print("[LOG] Clicked Search in Drug Lookup popup")
    screenshot(page, "step_7_clicked_search_drug_lookup")
    sleep(5)

    # Select first radio option (humira radio)
    humira_radio = find_element_across_frames(page, '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]')
    if not humira_radio:
        print("[ERROR]  Drug selection radio button not found")
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
        print("[ERROR]  Drug submit button not found")
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
        print("[ERROR]  Update Task (Intake) link not found for open task again")
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
        print("[ERROR]  Therapy Type input not found")
        raise Exception("Therapy Type input not found")
    therapy_type_input.fill("GLAT")
    print("[LOG] Filled Therapy Type with GLAT")
    screenshot(page, "step_9_filled_therapy_type")
    sleep(2)

    place_of_service_dropdown = find_element_across_frames(page, "select[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
    if not place_of_service_dropdown:
        place_of_service_dropdown = find_element_across_frames(page, "input[name='$PpyWorkPage$pDocument$pDrugList$l1$pPOSDescription']")
    if not place_of_service_dropdown:
        print("[ERROR]  Place of Service dropdown not found")
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
        print("[ERROR]  Patient search icon not found")
        raise Exception("Patient search icon not found")
    patient_search_icon.click()
    print("[LOG] Clicked Patient search icon")
    screenshot(page, "step_10_clicked_patient_search_icon")
    sleep(2)

    patient_clear_btn = find_element_across_frames(page, "//button[@name='PatientLookUp_pyWorkPage.Document.Patient_26']")
    if not patient_clear_btn:
        print("[ERROR]  Patient search clear button not found")
        raise Exception("Patient search clear button not found")
    patient_clear_btn.click()
    print("[LOG] Clicked clear in Patient search")
    screenshot(page, "step_10_clicked_patient_clear")
    sleep(2)

    patient_id_input = find_element_across_frames(page, "input[name='$PpyTempPage$pPatientID']")
    if not patient_id_input:
        print("[ERROR]  Patient ID input not found in Patient search")
        raise Exception("Patient ID input not found in Patient search")
    patient_id_input.fill("17164199")
    print("[LOG] Filled Patient ID: 17164199")
    screenshot(page, "step_10_filled_patient_id")
    sleep(2)

    patient_search_btn = find_element_across_frames(page, "//button[contains(text(),'Search')]")
    if not patient_search_btn:
        print("[ERROR]  Patient search button not found")
        raise Exception("Patient search button not found")
    patient_search_btn.click()
    print("[LOG] Clicked Search in Patient search popup")
    screenshot(page, "step_10_clicked_patient_search")
    sleep(5)

    patient_radio = find_element_across_frames(page, "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[./td[4]//span[text()='555']]/td[2]//input[@type='radio']")
    if not patient_radio:
        patient_radio = find_element_across_frames(page, "//table[contains(@grid_ref_page,'pyWorkPage.Document.Patient')]/tbody/tr[contains(@class,'Row')]/td[4]/div/span[text()='555']/ancestor::tr/td[2]//input[@type='radio']")
    if not patient_radio:
        print("[ERROR]  Patient record radio with SB=555 not found")
        raise Exception("Patient record radio with SB=555 not found")
    patient_radio.click()
    print("[LOG] Selected patient record with SB=555")
    screenshot(page, "step_10_selected_patient_record")
    sleep(2)

    submit_patient_btn = find_element_across_frames(page, "//button[@id='ModalButtonSubmit']")
    if not submit_patient_btn:
        print("[ERROR]  Submit button not found in patient search popup")
        raise Exception("Submit button not found in patient search popup")
    submit_patient_btn.click()
    print("[LOG] Clicked Submit in Patient search popup")
    screenshot(page, "step_10_clicked_submit_patient")
    sleep(5)

    address_dropdown = find_element_across_frames(page, "#ded594e9")
    if not address_dropdown:
        print("[ERROR]  Address dropdown not found")
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
        print("[ERROR]  Team dropdown not found")
        raise Exception("Team dropdown not found")
    try:
        if hasattr(team_dropdown, "input_value") and team_dropdown.input_value().strip() == "":
            options = team_dropdown.locator("option:not([value=''])")
            if options.count() > 0:
                first_option_value = options.first.get_attribute("value")
                team_dropdown.select_option(first_option_value)
                print(f"[LOG] Selected team: {first_option_value}")
            else:
                print("No non-blank team options found.")
            sleep(1)
        else:
            team_dropdown.fill("TEAM 1")
            print("[LOG] Filled TEAM 1 in Team dropdown")
    except Exception:
        try:
            team_dropdown.fill("TEAM 1")
            print("[LOG] Filled TEAM 1 in Team dropdown (fallback)")
        except Exception:
            print("[LOG] Could not fill/select Team in Team dropdown")
    screenshot(page, "step_11_filled_team")
    sleep(2)

    # Step 12: Click Submit
    task_submit_btn = find_element_across_frames(page, "button[name='CommonFlowActionButtons_pyWorkPage_17']")
    if not task_submit_btn:
        print("[ERROR] Task Submit button not found")
        raise Exception("Task Submit button not found")
    task_submit_btn.click()
    print("[LOG] Clicked Submit to complete Intake T-Task id")
    screenshot(page, "step_12_clicked_submit")
    sleep(5)

    print("[LOG] Automation completed for Intake test scenario.")

from nodes.agent_utils import find_element_across_frames
from time import sleep
from datetime import datetime, timedelta

def test_step_clearance(page_with_video):
    print("[LOG] TESTING INITIATED FOR CLEARANCE APPLICATION")

    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD
    initial_url = "https://clearance-qa.express-scripts.com/spclr"
    PATIENT_ID = 17164202
    page = page_with_video

    page.goto(initial_url)
    sleep(2)

    # Step 1: Login to Clearance
    username = find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username:
        print("[ERROR] Username input not found")
        raise Exception("Username input not found")
    username.fill(USERNAME)
    sleep(1)

    password = find_element_across_frames(page, 'input[name="Password"]')
    if not password:
        print("[ERROR] Password input not found")
        raise Exception("Password input not found")
    password.fill(PASSWORD)
    sleep(1)

    login_btn = find_element_across_frames(page, 'button#sub')
    if not login_btn:
        print("[ERROR] Login button not found")
        raise Exception("Login button not found")
    login_btn.click()
    sleep(8)

    # Step 2: Search for Patient Case
    search_cases = find_element_across_frames(page, 'a[name="SearchUtilities_pyDisplayHarness_5"]')
    if not search_cases:
        print("[ERROR] Search Cases button not found")
        raise Exception("Search Cases button not found")
    search_cases.click()
    sleep(3)

    patient_id_input = find_element_across_frames(page, 'input[name="$PpyDisplayHarness$pCaseSearchCriteria$pPatient$pPatientIDNumeric"]')
    if not patient_id_input:
        print("[ERROR] Patient ID input not found")
        raise Exception("Patient ID input not found")
    patient_id_input.fill(PATIENT_ID)
    sleep(1)

    max_attempts = 100
    attempt = 0
    while attempt < max_attempts:
        search_btn = find_element_across_frames(page, 'button[name="SearchCases_pyDisplayHarness.CaseSearchCriteria_14"]')
        if not search_btn:
            print("[ERROR] Search button not found")
            raise Exception("Search button not found")
        search_btn.click()
        sleep(30)

        ie_task_link = find_element_across_frames(page, "//table[@pl_prop='D_GetWorkCases.pxResults']/tbody/tr[2]/td[1]//a")
        if ie_task_link:
            ie_task_link.click()
            sleep(13)
            break

        attempt += 1

    if attempt >= max_attempts:
        print("[ERROR] IE Task ID link not found after maximum attempts")
        raise Exception("IE Task ID link not found after maximum attempts")

    # Step 4: Enter Place of Service (POS)
    pos_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pPlaceOfService"]')
    if not pos_input:
        print("[ERROR] Place of Service input not found")
        raise Exception("Place of Service input not found")
    pos_input.fill("12")
    sleep(1)

    # Step 5: Enter New Payer 1 - Payer Information
    bin_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pBankIDNumber"]')
    if not bin_input:
        print("[ERROR] BIN input not found")
        raise Exception("BIN input not found")
    bin_input.fill("610140")
    sleep(2)

    pcn_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pPCN"]')
    if not pcn_input:
        print("[ERROR] PCN input not found")
        raise Exception("PCN input not found")
    pcn_input.click()
    pcn_input.fill("D0TEST")
    sleep(2)

    group_number_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pAdditionalPayers$l1$pGroupNumber"]')
    if not group_number_input:
        print("[ERROR] Group Number input not found")
        raise Exception("Group Number input not found")
    group_number_input.click()
    group_number_input.fill("D0TEST")
    sleep(2)

    save_payee_btn = find_element_across_frames(page, 'button[data-test-id="PayerInfoScreen-Button-Search"]')
    if not save_payee_btn:
        print("[ERROR] Save Payee button not found")
        raise Exception("Save Payee button not found")
    save_payee_btn.click()
    sleep(3)

    # Step 6: Enter Policy Information
    cardholder_input = find_element_across_frames(page, '//span/input[@id="6a329411"]')
    if not cardholder_input:
        print("[ERROR] Cardholder ID input not found")
        raise Exception("Cardholder ID input not found")
    cardholder_input.fill("555757575")
    sleep(1)

    person_code_input = find_element_across_frames(page, '//div/input[@id="a451c2d0"]')
    if not person_code_input:
        print("[ERROR] Person Code input not found")
        raise Exception("Person Code input not found")
    person_code_input.fill("001")
    sleep(2)

    effective_date_input = find_element_across_frames(page, '//span/input[@class="inactvDtTmTxt"]')
    if not effective_date_input:
        print("[ERROR] Insurance Effective Date input not found")
        raise Exception("Insurance Effective Date input not found")
    today = datetime.now().strftime("%m/%d/%Y")
    effective_date_input.fill(today)
    sleep(1)

    end_date_input = find_element_across_frames(page, 'input[data-test-id="20171109141147048668261"]')
    if not end_date_input:
        print("[ERROR] End Date input not found")
        raise Exception("End Date input not found")
    end_date = (datetime.now() + timedelta(days=2)).strftime("%m/%d/%Y")
    end_date_input.fill(end_date)
    sleep(1)

    relationship_dropdown = find_element_across_frames(page, '//div/select[@data-test-id="20171115143211077239541"]')
    if not relationship_dropdown:
        print("[ERROR] Relationship dropdown not found")
        raise Exception("Relationship dropdown not found")
    relationship_dropdown.select_option(label="1 - Self")
    sleep(1)

    save_policy_btn = find_element_across_frames(page, 'button[data-test-id="20200305121820016323290"]')
    save_policy_btn.click()
    sleep(10)

    # Step 7: Confirm Insurance Banner
    next_btn = find_element_across_frames(page, 'button[name="CommonFlowActionButtons_pyWorkPage_31"]')
    if not next_btn:
        print("[ERROR] Next button not found")
        raise Exception("Next button not found")
    next_btn.click()
    sleep(60)

    # Step 8: CoPay and Billing Split Setup
    drug_checkbox = find_element_across_frames(page, '//span[@class="checkbox"]//input[@type="checkbox"]')
    if not drug_checkbox:
        print("[ERROR] Drug field checkbox not found")
        raise Exception("Drug field checkbox not found")
    if not drug_checkbox.is_checked():
        drug_checkbox.check()
    sleep(60)

    primary_payer_input = find_element_across_frames(page, 'input[data-test-id="202006170412060535921"]')
    if not primary_payer_input:
        print("[ERROR] Primary Payer Service input not found")
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
            print("[ERROR] CoPay input not found")
            raise Exception("CoPay input not found")
    copay_input.select_option(value="P")
    sleep(3)

    # Step 10: Complete the Clearance Task
    finish_btn = find_element_across_frames(page, '//span/button[text()="Finish"]')
    if not finish_btn:
        print("[ERROR] Finish button not found")
        raise Exception("Finish button not found")
    finish_btn.click()
    sleep(15)

from nodes.rxp_agent_utils import find_element_across_frames, robust_fill, advanced_search, robust_click, robust_select_option, switch_to_window_by_index, find_and_click_begin_button_with_retry, validate_section_and_check
from time import sleep

def test_step_rxp(page_with_video):

    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD
    PATIENT_ID = 17164202

    page = page_with_video

    # Step 1: Login to RxP
    page.goto("https://sprxp-qa.express-scripts.com/sprxp")
    print("[LOG] Navigated to RxP login page")
    page.wait_for_load_state("networkidle")
    sleep(5)

    username_input = find_element_across_frames(page, "input#txtUserID")
    if not username_input:
        raise Exception("Element 'Username Input' not found with selector: 'input#txtUserID'")
    robust_fill(page, username_input, USERNAME)
    print("[LOG] Username filled")
    sleep(5)

    password_input = find_element_across_frames(page, "input#txtPassword")
    if not password_input:
        raise Exception("Element 'Password Input' not found with selector: 'input#txtPassword'")
    robust_fill(page, password_input, PASSWORD)
    print("[LOG] Password filled")
    sleep(5)

    login_button = find_element_across_frames(page, "button#sub")
    if not login_button:
        raise Exception("Element 'Login' button not found with selector: 'button#sub'")
    robust_click(page, login_button)
    print("[LOG] Clicked Login button")
    page.wait_for_load_state("networkidle")
    sleep(5)

    # Step 2: Advanced Search for patient
    element_name = "//span[contains(text(), 'Referral')]/ancestor::tr//button[@data-test-id='20201119155820006856367']"
    status_name = "Referral"
    advanced_search(page, element_name, status_name, PATIENT_ID)
    sleep(5)

    # Step 3: Begin Referral Task
    find_and_click_begin_button_with_retry(page, "Begin")
    sleep(10)

    # Step 4: Link Image in Viewer
    link_image_btn = find_element_across_frames(page, "//button[normalize-space(.)='Link Image in Viewer']")
    if not link_image_btn:
        raise Exception("Element 'Link Image in Viewer' button not found")
    robust_click(page, link_image_btn)
    print("[LOG] Clicked 'Link Image in Viewer'")
    page.wait_for_load_state("networkidle")
    sleep(5)

    # Step 5: Select DAW code = 0
    daw_dropdown = find_element_across_frames(
        page, "//*[normalize-space(text())='DAW Code']/ancestor-or-self::*[contains(@class,'dataLabelFor')]/following-sibling::*//select"
    )
    if not daw_dropdown:
        raise Exception("Element 'DAW Code Dropdown' not found")
    robust_select_option(page, daw_dropdown, "0 - No Product Selection Indicated")
    print("[LOG] Selected DAW code '0 - No Product Selection Indicated'")
    sleep(5)

    # Step 6: Search and select drug (GLAT, NDC: 00378696093)
    search_drug_btn = find_element_across_frames(page, "[data-test-id='20170901173456065136464']")
    if not search_drug_btn:
        raise Exception("Element 'Search Drug' button not found")
    robust_click(page, search_drug_btn)
    print("[LOG] Clicked 'Search Drug' button")
    page.wait_for_load_state("networkidle")
    sleep(5)

    ndc_dropdown = find_element_across_frames(page, "[data-test-id='20200925062850019643650']")
    if not ndc_dropdown:
        raise Exception("Element 'NDC Dropdown' not found")
    robust_select_option(page, ndc_dropdown, "NDC")
    print("[LOG] Selected NDC search option")
    sleep(5)

    drug_search_input = find_element_across_frames(page, "//input[@name='$PDrugSearch$ppySearchText']")
    if not drug_search_input:
        raise Exception("Element 'Drug Search Input' not found")
    robust_fill(page, drug_search_input, "00378696093")
    print("[LOG] Entered NDC '00378696093'")
    sleep(5)

    modal_search_btn = find_element_across_frames(page, "//button[normalize-space(text())='Search']")
    if not modal_search_btn:
        raise Exception("Element 'Modal Search Button' not found")
    robust_click(page, modal_search_btn)
    print("[LOG] Clicked Drug Search in modal")
    page.wait_for_load_state("networkidle")
    sleep(5)

    drug_row = find_element_across_frames(page, '//*[@id="$PDrugSearchResults$ppxResults$l1"]/td[3]')
    if not drug_row:
        raise Exception("Drug result row not found")
    robust_click(page, drug_row)
    print("[LOG] Selected GLAT drug row by NDC")
    sleep(5)

    submit_drug_btn = find_element_across_frames(
        page, "//button[@data-test-id='201707060845020891147506' and normalize-space()='Submit']"
    )
    if not submit_drug_btn:
        raise Exception("Element 'Submit' button in modal not found")
    robust_click(page, submit_drug_btn)
    print("[LOG] Clicked 'Submit' in drug search modal")
    page.wait_for_load_state("networkidle")
    sleep(20)

    # Step 7: Common SIG, select appropriate SIG for GLAT
    common_sig_btn = find_element_across_frames(page, "//button[normalize-space(.)='Common SIG']")
    if not common_sig_btn:
        raise Exception("Common SIG button not found")
    robust_click(page, common_sig_btn)
    print("[LOG] Clicked 'Common SIG' button")
    sleep(5)

    # Select SIG for GLAT
    sig_option = find_element_across_frames(page, "//span[normalize-space(text())='INJECT 40 MG (0.4 ML) UNDER THE SKIN EVERY 2 WEEKS']")
    if not sig_option:
        sig_option = find_element_across_frames(page, "//span[normalize-space(text())='INJECT 20 MG (1 ML) UNDER THE SKIN DAILY']")
    if not sig_option:
        raise Exception("SIG option for GLAT not found")
    robust_click(page, sig_option)
    print("[LOG] SIG option selected")
    sleep(5)

    # Step 8: Enter Rx Details
    qty_input = find_element_across_frames(page, 'input[data-test-id="2019062103515309648629"]')
    if not qty_input:
        raise Exception("Qty input not found")
    robust_fill(page, qty_input, "1")
    print("[LOG] Qty set to 1")
    sleep(5)

    days_input = find_element_across_frames(page, 'input[data-test-id="20190621040342079260489"]')
    if not days_input:
        raise Exception("Days Supply input not found")
    robust_fill(page, days_input, "30")
    print("[LOG] Days Supply set to 30")
    sleep(5)

    doses_input = find_element_across_frames(page, 'input[data-test-id="20190621040342079263702"]')
    if not doses_input:
        raise Exception("Doses input not found")
    robust_fill(page, doses_input, "1")
    print("[LOG] Doses set to 1")
    sleep(5)

    refills_input = find_element_across_frames(page, 'input[data-test-id="2019062104034207926431"]')
    if not refills_input:
        raise Exception("Refills input not found")
    robust_fill(page, refills_input, "1")
    print("[LOG] Refills set to 1")
    sleep(5)

    # Step 9: Apply Rules & Reviewed
    apply_rules_btn = find_element_across_frames(page, "//button[normalize-space(.)='Apply Rules']")
    if not apply_rules_btn:
        raise Exception("Element 'Apply Rules' button not found")
    robust_click(page, apply_rules_btn)
    print("[LOG] Clicked 'Apply Rules'")
    page.wait_for_load_state("networkidle")
    sleep(3)

    reviewed_btn = find_element_across_frames(page, "//button[normalize-space(.)='Reviewed']")
    if not reviewed_btn:
        raise Exception("Element 'Reviewed' button not found")
    robust_click(page, reviewed_btn)
    print("[LOG] Clicked 'Reviewed'")
    page.wait_for_load_state("networkidle")
    sleep(5)

    # Step 10: Accept Changes
    accept_changes_btn = find_element_across_frames(page, "//button[normalize-space(.)='Accept Changes']")
    if accept_changes_btn:
        robust_click(page, accept_changes_btn)
        print("[LOG] Clicked 'Accept Changes'")
        page.wait_for_load_state("networkidle")
        sleep(5)

    # Step 11: Verify Patient, Medication, Rx Details and Prescriber sections; checkboxes if valid
    patient_fields = [
        ("Full Name", "//span[normalize-space()='Full name']/following-sibling::div/span"),
        ("DOB", "//span[normalize-space()='DOB']/following-sibling::div/span"),
        ("Gender", "//span[normalize-space()='Gender']/following-sibling::div/span"),
        ("Age", "//span[normalize-space()='Age']/following-sibling::div/span"),
        ("Address", "//span[normalize-space()='Address']/following-sibling::div/span"),
        ("Phone", "//span[normalize-space()='Phone']/following-sibling::div/span"),
    ]
    patient_checkbox = "//input[@data-test-id='202303231536300910155360']"
    validate_section_and_check(page, patient_fields, patient_checkbox)
    sleep(5)

    med_fields = [
        ("Prescribed Drug", "//span[normalize-space()='Prescribed Drug']/following-sibling::div/span"),
        ("Dispensed Drug", "//span[normalize-space()='Dispensed Drug']/following-sibling::div/span"),
        ("Dispensed Drug Comments", "//span[normalize-space()='Dispensed Drug Comments']/following-sibling::div/span"),
    ]
    opt_med_fields = ["Dispensed Drug Comments"]
    med_checkbox = "//input[@data-test-id='20230324144929033857959']"
    validate_section_and_check(page, med_fields, med_checkbox, opt_med_fields)
    sleep(5)

    rx_details_fields = [
        ("SIG Text", "//span[normalize-space()='SIG Text']/following-sibling::div/span"),
        ("Prescribed Quantity", "//span[normalize-space()='Prescribed Quantity']/following-sibling::div/span"),
        ("Prescribed Days Supply", "//span[normalize-space()='Prescribed Days Supply']/following-sibling::div/span"),
        ("Prescribed Doses", "//span[normalize-space()='Prescribed Doses']/following-sibling::div/span"),
        ("Prescribed Refills", "//span[normalize-space()='Prescribed Refills']/following-sibling::div/span"),
        ("Dispensed Quantity", "//span[normalize-space()='Dispensed Quantity']/following-sibling::div/span"),
        ("Dispensed Days Supply", "//span[normalize-space()='Dispensed Days Supply']/following-sibling::div/span"),
        ("Dispensed Doses", "//span[normalize-space()='Dispensed Doses']/following-sibling::div/span"),
        ("Dispensed Refills", "//span[normalize-space()='Dispensed Refills']/following-sibling::div/span"),
        ("Date Written", "//span[normalize-space()='Date Written']/following-sibling::div/span"),
        ("Rx Expires", "//span[normalize-space()='Rx Expires']/following-sibling::div/span"),
        ("DAW Code", "//span[normalize-space()='DAW Code']/following-sibling::div/span"),
        ("Rx Origin Code", "//span[normalize-space()='Rx Origin Code']/following-sibling::div/span"),
    ]
    rx_details_checkbox = "//input[@data-test-id='20230324171608002687320']"
    validate_section_and_check(page, rx_details_fields, rx_details_checkbox)
    sleep(5)

    prescriber_fields = [
        ("Prescriber", "//span[@data-test-id='202008271512120392583911']"),
        ("Prescriber ID", "//div[normalize-space()='Prescriber ID']/following-sibling::div//span[@class='esitextinput']"),
        ("Address", "//span[normalize-space()='Address']/following-sibling::div//span[contains(@class, 'esitextinput')]"),
        ("Phone", "//span[normalize-space()='Phone']/following-sibling::div/span[contains(@class, 'esitextinput')]"),
        ("NPI", "//span[normalize-space()='NPI']/following-sibling::div/span"),
        ("DEA", "//span[normalize-space()='DEA']/following-sibling::div/span"),
    ]
    prescriber_checkbox = "//input[@data-test-id='202303271403440493899139']"
    validate_section_and_check(page, prescriber_fields, prescriber_checkbox)
    sleep(5)

    # Step 12: Ensure Prescriber NPI and Fax fields
    fax_element = find_element_across_frames(page, "//span[normalize-space()='Fax']/following-sibling::div/span")
    if fax_element and not fax_element.inner_text().strip():
        fax_na_checkbox = find_element_across_frames(page, "//span[normalize-space()='Fax N/A']/following::input[@type='checkbox'][1]")
        if fax_na_checkbox:
            robust_click(page, fax_na_checkbox)
            print("[LOG] Clicked Fax N/A checkbox")
        sleep(5)

    # Step 13: Click Next for Trend Processing
    next_btn = find_element_across_frames(page, "//button[normalize-space()='Next >>']")
    if not next_btn:
        raise Exception("Next button not found")
    sleep(2)
    robust_click(page, next_btn)
    print("[LOG] Clicked Next for Trend Processing")
    page.wait_for_load_state("networkidle")
    sleep(5)

    # Step 14: Banner and Close
    sleep(10)
    close_btn = find_element_across_frames(page, "//button[normalize-space() = 'Close']")
    if not close_btn:
        raise Exception("Close button not found")
    robust_click(page, close_btn)
    print("[LOG] Clicked close button")
    page.wait_for_load_state("networkidle")
    sleep(30)