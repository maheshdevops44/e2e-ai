 
from nodes.agent_utils import find_element_across_frames, robust_fill
from time import sleep
from datetime import datetime,timedelta
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
    COMMON_INTAKE_ID = "CMNINTAKE07292025113208122766172"
    PATIENT_ID = "17045256"
    USERNAME = LAN_ID
    PASSWORD = LAN_PASSWORD

    page = page_with_video
    page.goto(initial_url)
    print("[LOG] Navigated to Intake application URL")
    sleep(5)

    # Step 1: Login
    username_elem = find_element_across_frames(page, 'input[name="UserIdentifier"]')
    if not username_elem:
        raise Exception("Username input not found")
    username_elem.fill(USERNAME)
    print("[LOG] Filled username with LAN ID")
    screenshot(page, "step_1_filled_username")
    sleep(2)

    password_elem = find_element_across_frames(page, 'input[name="Password"]')
    if not password_elem:
        raise Exception("Password input not found")
    password_elem.fill(PASSWORD)
    print("[LOG] Filled password with LAN PASSWORD")
    screenshot(page, "step_1_filled_password")
    sleep(2)

    login_btn = find_element_across_frames(page, 'button#sub')
    if not login_btn:
        raise Exception("Login button not found")
    login_btn.click()
    print("[LOG] Clicked on Login button")
    screenshot(page, "step_1_clicked_login")
    sleep(8)

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
    print(f"[LOG] Clicked T-ID link")
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

    # Step 6: Drug Lookup - click Drug Search icon (Drug tab is default)
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

    # Drug Lookup popup - enter Drug Name and Search button
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

    # Select first radio (humira)
    humira_radio = find_element_across_frames(page, '//table[contains(@grid_ref_page,".DrugList")]/tbody/tr/td//input[@type="radio"]')
    if not humira_radio:
        raise Exception("Drug selection radio button not found")
    humira_radio.click()
    print("[LOG] Selected first radio for searched drug")
    screenshot(page, "step_7_selected_drug_radio")
    sleep(2)

    # Drug submit
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
    try:
        # if input is blank, try selecting first non-blank option
        if hasattr(team_dropdown, "input_value") and (team_dropdown.input_value() is not None) and team_dropdown.input_value().strip() == "":
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
        print("[LOG] Could not fill/select TEAM 1 in Team dropdown")
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
    PATIENT_ID = "17045256"
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
    patient_id_input.fill(PATIENT_ID)
    sleep(1)

    max_attempts = 5
    attempt = 0
    while attempt < max_attempts:
        search_btn = find_element_across_frames(page, 'button[name="SearchCases_pyDisplayHarness.CaseSearchCriteria_14"]')
        if not search_btn:
            raise Exception("Search button not found")
        search_btn.click()
        sleep(30)
        ie_task_link = find_element_across_frames(page, "//table[@pl_prop='D_GetWorkCases.pxResults']/tbody/tr[2]/td[1]//a")
        if ie_task_link:
            ie_task_link.click()
            sleep(13)
            break
        attempt += 1
        print("Searching : IE task link not found, will retry in 30 seconds...")
    if attempt >= max_attempts:
        raise Exception("IE Task ID link not found after maximum attempts")

    # Step 4: Enter Payer Section Details
    pos_input = find_element_across_frames(page, 'input[name="$PpyWorkPage$pPlaceOfService"]')
    if not pos_input:
        raise Exception("Place of Service input not found")
    pos_input.fill("12")
    sleep(1)

    # Step 5: Enter New Payer 1 – Payer Information
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